"""Aplicação para o módulo de extensão DevOps"""

from datetime import datetime, timezone
from typing import Annotated, List
import os

import requests
from fastapi import FastAPI, Depends
from sqlmodel import SQLModel, Session, create_engine, select
from requests.exceptions import ConnectionError as RequestConnectionError

from .modelo import Tarefa

DATABASE_USERNAME = os.environ.get("DATABASE_USERNAME")
DATABASE_PASSWORD = os.environ.get("DATABASE_PASSWORD")
DATABASE_ADDRESS = os.environ.get("DATABASE_ADDRESS")
DATABASE = os.environ.get("DATABASE")
if DATABASE_USERNAME is None:
    print("DATABASE_USERNAME está faltando")
    exit(1)

if DATABASE_PASSWORD is None:
    print("DATABASE_PASSWORD está faltando")
    exit(1)

if DATABASE_ADDRESS is None:
    print("DATABASE_ADDRESS está faltando")
    exit(1)

if DATABASE is None:
    print("DATABASE está faltando")
    exit(1)


ENGINE = create_engine(f"mysql+pymysql://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_ADDRESS}:3306/{DATABASE}")

def criar_sessao():
    with Session(ENGINE) as s:
        yield s

SESSAO = Annotated[Session, Depends(criar_sessao)]

async def inicializacao(api: FastAPI):
    SQLModel.metadata.create_all(ENGINE)
    yield


APP = FastAPI(lifespan=inicializacao)
TAREFAS = []

x'
# POST /tarefas: Cria tarefa
@APP.post("/tarefas", status_code=201)
async def post_tarefa(sessao: SESSAO, titulo: str, descricao: str = None):
    """Rota para criar uma tarefa."""
    tarefa_nova = Tarefa(
        titulo=titulo,
        descricao=descricao,
        data_criacao=datetime.now().astimezone(timezone.utc),
    )

    sessao.add(tarefa_nova)
    sessao.commit()
    sessao.refresh(tarefa_nova)

    return {"mensagem": "OK"}


# GET /tarefas/{id_tarefa}: Visualizar tarefa específica
@APP.get("/tarefas/{id_tarefa}")
async def tarefa_especifica(id_tarefa: int):
    """Rota para visualizar uma tarefa específica"""
    # 1. Selecionar a tarefa de ID recebido como parâmetro
    # 2. Retornar todos os dados da tarefa
    # 3. Caso a tarefa não exista, você tem que mostrar que a tarefa não existe

    for tarefa in TAREFAS:
        if id_tarefa == tarefa.get_id():
            return tarefa

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

    return {"mensagem": "Tarefa removida"}


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
