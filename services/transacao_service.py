from repositories.transacao_repo import (
    adicionar_transacao,
    calcular_resumo,
    listar_transacoes,
)
from services.conta_service import obter_conta_ativa


def criar_transacao_service(
    valor: float,
    tipo: str,
    categoria_id: int | None,
    comentario: str | None,
    data: str,
    usuario_id: int,
    conta_id: int | None = None,
) -> dict:
    if valor <= 0:
        raise ValueError("O valor da transacao deve ser maior que zero.")
    if tipo not in {"entrada", "saida"}:
        raise ValueError("Tipo de transacao invalido.")
    if conta_id is not None and obter_conta_ativa(conta_id, usuario_id) is None:
        raise ValueError("Conta nao encontrada.")

    adicionar_transacao(valor, tipo, categoria_id, comentario, data, usuario_id, conta_id)
    return {
        "valor": float(valor),
        "tipo": tipo,
        "categoria_id": categoria_id,
        "comentario": comentario,
        "data": data,
        "usuario_id": usuario_id,
        "conta_id": conta_id,
    }


def listar_transacoes_formatadas(usuario_id: int) -> list[dict]:
    transacoes = listar_transacoes(usuario_id)
    return [
        {
            "id": transacao_id,
            "valor": float(valor),
            "tipo": tipo,
            "categoria": categoria,
            "comentario": comentario,
            "data": data,
            "conta_id": conta_id,
            "conta": conta,
        }
        for transacao_id, valor, tipo, categoria, comentario, data, conta_id, conta in transacoes
    ]


def obter_resumo_financeiro(usuario_id: int) -> dict:
    entradas, saidas, saldo = calcular_resumo(usuario_id)
    return {
        "entradas": float(entradas),
        "saidas": float(saidas),
        "saldo": float(saldo),
    }
