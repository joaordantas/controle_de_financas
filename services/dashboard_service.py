from repositories.dashboard_repo import (
    a_receber_por_cliente,
    lucro_por_periodo,
    total_a_receber,
)


def obter_lucro_por_periodo(data_inicio: str, data_fim: str, usuario_id: int) -> dict:
    return lucro_por_periodo(data_inicio, data_fim, usuario_id)


def obter_total_a_receber(usuario_id: int) -> float:
    return float(total_a_receber(usuario_id))


def obter_a_receber_por_cliente(usuario_id: int) -> list[dict]:
    dados = a_receber_por_cliente(usuario_id)
    return [
        {"cliente": cliente, "valor_pendente": float(valor)}
        for cliente, valor in dados
    ]
