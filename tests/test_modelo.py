from datetime import datetime, timezone
from app.modelo import Tarefa


def criar_tarefa_mock():
    return Tarefa(
        titulo="Tarefa teste",
        data_criacao=datetime.now().replace(microsecond=0),
    )


def test_nova_tarefa():
    t = criar_tarefa_mock()

    assert t.get_id() is None
    assert t.titulo == "Tarefa teste"
    assert t.descricao is None
    assert isinstance(t.data_criacao, datetime)
    assert t.data_criacao.microsecond == 0
    assert t.data_conclusao is None
    assert t.concluida is False


# Implementar teste unitário para verificar se a tarefa foi concluida


def test_tarefa_concluida():
    t = criar_tarefa_mock()

    t.finalizar()
    assert t.concluida is True
    assert isinstance(t.data_conclusao, datetime)
    assert t.data_conclusao.tzinfo == timezone.utc
    assert t.data_conclusao.microsecond == 0
