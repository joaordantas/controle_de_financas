from repositories.transacao_repo import (
    adicionar_transacao,
    calcular_resumo,
    listar_transacoes,
)


def criar_transacao_service(
    valor: float,
    tipo: str,
    categoria_id: int | None,
    comentario: str | None,
    data: str,
    usuario_id: int,
) -> dict:
    if valor <= 0:
        raise ValueError("O valor da transacao deve ser maior que zero.")
    if tipo not in {"entrada", "saida"}:
        raise ValueError("Tipo de transacao invalido.")

    adicionar_transacao(valor, tipo, categoria_id, comentario, data, usuario_id)
    return {
        "valor": float(valor),
        "tipo": tipo,
        "categoria_id": categoria_id,
        "comentario": comentario,
        "data": data,
        "usuario_id": usuario_id,
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
        }
        for transacao_id, valor, tipo, categoria, comentario, data in transacoes
    ]


def obter_resumo_financeiro(usuario_id: int) -> dict:
    entradas, saidas, saldo = calcular_resumo(usuario_id)
    return {
        "entradas": float(entradas),
        "saidas": float(saidas),
        "saldo": float(saldo),
    }
