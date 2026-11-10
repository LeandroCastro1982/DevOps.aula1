"""Aplicação para o módulo de extensão DevOps"""

from datetime import datetime, timezone
from functools import lru_cache
from typing import Annotated, List
import os

from fastapi import FastAPI, Depends
from sqlmodel import SQLModel, Session, create_engine, select

from .modelo import Tarefa


@lru_cache
def obter_engine():
    """Cria o engine quando a aplicação realmente precisar do banco."""
    configuracao = {
        "DATABASE_USERNAME": os.environ.get("DATABASE_USERNAME"),
        "DATABASE_PASSWORD": os.environ.get("DATABASE_PASSWORD"),
        "DATABASE_ADDRESS": os.environ.get("DATABASE_ADDRESS"),
        "DATABASE": os.environ.get("DATABASE"),
    }
    ausentes = [nome for nome, valor in configuracao.items() if not valor]
    if ausentes:
        raise RuntimeError(
            "Variáveis de ambiente do banco ausentes: " + ", ".join(ausentes)
        )

    return create_engine(
        "mysql+pymysql://"
        f"{configuracao['DATABASE_USERNAME']}:{configuracao['DATABASE_PASSWORD']}"
        f"@{configuracao['DATABASE_ADDRESS']}:3306/{configuracao['DATABASE']}"
    )


def criar_sessao():
    """Função utilitária para criar sessão no banco de dados"""
    with Session(obter_engine()) as s:
        yield s


SESSAO = Annotated[Session, Depends(criar_sessao)]


async def inicializacao(_: FastAPI):
    """Função para incialização da API e do banco de dados"""
    SQLModel.metadata.create_all(obter_engine())
    yield


APP = FastAPI(lifespan=inicializacao)
TAREFAS = []


# GET /tarefas: Lista todas as tarefas (somente id e titulo)
@APP.get("/tarefas")
async def tarefas(sessao: SESSAO) -> List[Tarefa]:
    """Rota para listar as tarefas."""

    lista_tarefas = sessao.exec(select(Tarefa).offset(0)).all()

    return lista_tarefas


# POST /tarefas: Cria tarefa
@APP.post("/tarefas", status_code=201)
async def post_tarefa(sessao: SESSAO, titulo: str, descricao: str = None):
    """Rota para criar uma tarefa."""
    data = datetime.now().astimezone(timezone.utc).replace(microsecond=0)
    tarefa_nova = Tarefa(
        titulo=titulo,
        descricao=descricao,
        data_criacao=data,
    )

    sessao.add(tarefa_nova)
    sessao.commit()
    sessao.refresh(tarefa_nova)

    return {"mensagem": "OK"}


# GET /tarefas/{id_tarefa}: Visualizar tarefa específica
@APP.get("/tarefas/{id_tarefa}")
async def tarefa_especifica(sessao: SESSAO, id_tarefa: int) -> Tarefa:
    """Rota para visualizar uma tarefa específica"""
    # select * from tarefas where id == id_tarefa
    regra = select(Tarefa).where(Tarefa.id == id_tarefa)
    resultado = sessao.exec(regra).all()

    if resultado:
        return resultado[0]

    return {"mensagem": "Tarefa não existe"}


# PUT /tarefas/{id}: Atualiza tarefa específica
@APP.put("/tarefas/{id_tarefa}")
async def concluir_tarefa(sessao: SESSAO, id_tarefa: int):
    """Rota para concluir uma tarefa."""

    # Atualizar a rota para suportar o SQLModel/Conexão com BD
    # Usar select para filtrar as tarefas com base no ID e se estiver concluída
    # Atualizar usando sessao.add, sessao.commit, sessao.refresh

    regra = select(Tarefa).where(Tarefa.id == id_tarefa)
    resultado = sessao.exec(regra).all()

    if not resultado:
        return {"mensagem": "Tarefa não existe"}

    if resultado[0].concluida is True:
        return {"mensagem": "Tarefa já finalizada"}

    resultado[0].finalizar()

    sessao.add(resultado[0])
    sessao.commit()
    sessao.refresh(resultado[0])

    return {"mensagem": "Tarefa atualizada"}


# DELETE /tarefas/{id_tarefa}: Exclui tarefa
@APP.delete("/tarefas/{id_tarefa}")
async def apagar_tarefa(sessao: SESSAO, id_tarefa: int):
    """Rota para apagar tarefa."""

    regra = select(Tarefa).where(Tarefa.id == id_tarefa)
    resultado = sessao.exec(regra).all()

    if not resultado:
        return {"mensagem": "Tarefa não existe"}

    tarefa = resultado[0]

    sessao.delete(tarefa)
    sessao.commit()

    return {"mensagem": "Tarefa apagada"}


@APP.get("/")
async def index():
    """Rota raíz."""
    return {"mensagem": "Olá, mundo!"}


# 1. Implementar uma rota chamada "/autor" que retorna
# um dicionário no formato {"mensagem": SEU NOME COMPLETO}
@APP.get("/autor")
async def autor():
    """Rota para retornar o autor da aplicação"""
    return {"mensagem": "Pedro Rocha Horchulhack"}


# 2. Criar um teste unitário para verificar se a rota
# está produzindo o resultado esperado

# 3. Verificar se o código está no padrão do PyLint

# 4. Enviar o código para o repositório (git push)
