import pytest

from fastapi.testclient import TestClient
from app.api import APP, criar_sessao
from datetime import datetime, timezone
from sqlmodel import SQLModel, Session, create_engine

BANCO = create_engine("sqlite:///banco.db", connect_args={"check_same_thread": False})


@pytest.fixture(name="sessao")
def fixture_sessao():
    SQLModel.metadata.create_all(BANCO)

    with Session(BANCO) as s:
        yield s

    SQLModel.metadata.drop_all(BANCO)


@pytest.fixture(name="cliente")
def fixture_cliente(sessao: Session):
    def get_sessao():
        return sessao

    APP.dependency_overrides[criar_sessao] = get_sessao

    cliente = TestClient(APP)
    yield cliente

    APP.dependency_overrides.clear()


def test_index(cliente: TestClient):
    resposta = cliente.get("/")
    assert resposta.status_code == 200
    assert resposta.json() == {"mensagem": "Olá, mundo!"}


# 1. Implementar um teste unitário para a rota /tarefas (GET)
def test_tarefas_get(cliente: TestClient):
    resposta = cliente.get("/tarefas")
    assert resposta.status_code == 200

    # Testando se a rota retorna uma lista vazia
    assert resposta.json() == []


# 2. Implementar um teste unitário para a rota /tarefas (POST)
def test_tarefas_post(cliente: TestClient):
    resposta = cliente.post("/tarefas?titulo=teste&descricao=teste")

    assert resposta.status_code == 201
    assert resposta.json() == {"mensagem": "OK"}

    resposta = cliente.get("/tarefas")
    tarefa = resposta.json()[0]
    assert tarefa["_id"] == 1
    assert tarefa["descricao"] == "teste"
    assert tarefa["concluida"] is False
    assert tarefa["titulo"] == "teste"
    assert tarefa["data_conclusao"] is None
    assert isinstance(
        datetime.fromisoformat(tarefa["data_criacao"].replace("Z", "+00:00")),
        datetime,
    )


# 3. Implementar um teste unitário para a rota /tarefas/{id} (PUT)
def test_tarefas_put(cliente: TestClient):
    # Crio a tarefa
    cliente.post("/tarefas?titulo=teste&descricao=teste")
    resposta = cliente.get("/tarefas/1")
    data_criacao = resposta.json()["data_criacao"]

    # Finalizo a tarefa
    resposta = cliente.put("/tarefas/1")
    assert resposta.json() == {"mensagem": "Tarefa atualizada"}

    resposta = cliente.put("/tarefas/0")
    assert resposta.json() == {"mensagem": "Tarefa não existe"}

    resposta = cliente.get("/tarefas/1")
    assert resposta.status_code == 200
    tarefa = resposta.json()
    assert set(tarefa) == {
        "_id",
        "descricao",
        "data_criacao",
        "concluida",
        "titulo",
        "data_conclusao",
    }
    assert tarefa["_id"] == 1
    assert tarefa["descricao"] == "teste"
    assert tarefa["data_criacao"] == data_criacao
    assert tarefa["concluida"] is True
    assert tarefa["titulo"] == "teste"
    data_conclusao = datetime.fromisoformat(
        tarefa["data_conclusao"].replace("Z", "+00:00")
    )
    assert data_conclusao.tzinfo == timezone.utc
    assert data_conclusao.microsecond == 0


# 5. Implementar um teste unitário para a rota /tarefas/{id} (DELETE)
def test_tarefas_delete(cliente: TestClient):
    # Crio a tarefa
    resposta = cliente.post("/tarefas?titulo=teste&descricao=teste")

    resposta = cliente.delete("/tarefas/0")
    assert resposta.json() == {"mensagem": "Tarefa não existe"}

    resposta = cliente.delete("/tarefas/1")
    assert resposta.json() == {"mensagem": "Tarefa apagada"}

    resposta = cliente.get("/tarefas")
    assert resposta.json() == []


def test_autor(cliente: TestClient):
    resposta = cliente.get("/autor")

    assert resposta.status_code == 200
    assert resposta.json() == {"mensagem": "Pedro Rocha Horchulhack"}
