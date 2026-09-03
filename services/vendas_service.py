from repositories.parcela_repo import (
    adicionar_parcelas,
    buscar_valor_total_vendas,
    calcular_total_pago,
    listar_parcelas_por_cliente,
    somar_valor_parcelas_da_venda,
)
from repositories.venda_repo import (
    adicionar_venda,
    buscar_venda_por_id,
    listar_clientes,
    listar_vendas,
)
from services.financeiro_service import registrar_pagamento_parcela_atomic


def criar_venda_service(
    cliente: str,
    tipo: str,
    valor_total: float,
    comentario: str | None,
    data: str,
    usuario_id: int,
) -> dict:
    if not cliente.strip():
        raise ValueError("Informe o nome do cliente.")
    if valor_total <= 0:
        raise ValueError("O valor da venda deve ser maior que zero.")

    venda_id = adicionar_venda(cliente.strip(), tipo, valor_total, comentario, data, usuario_id)
    venda = buscar_venda_por_id(venda_id, usuario_id)
    return _venda_para_dict(venda)


def listar_vendas_formatadas(usuario_id: int) -> list[dict]:
    return [_venda_para_dict(venda) for venda in listar_vendas(usuario_id)]


def listar_clientes_service(usuario_id: int) -> list[str]:
    return listar_clientes(usuario_id)


def adicionar_parcelas_para_venda(
    venda_id: int,
    quantidade: int,
    valor: float,
    status: str,
    data: str,
    usuario_id: int,
) -> dict:
    venda = buscar_venda_por_id(venda_id, usuario_id)
    if venda is None:
        raise ValueError("Venda nao encontrada.")
    if quantidade <= 0:
        raise ValueError("A quantidade de parcelas deve ser maior que zero.")
    if valor <= 0:
        raise ValueError("O valor da parcela deve ser maior que zero.")

    valor_total_venda = float(venda[3])
    valor_ja_parcelado = somar_valor_parcelas_da_venda(venda_id, usuario_id)
    valor_novo_total = quantidade * valor

    if valor_ja_parcelado + valor_novo_total > valor_total_venda:
        raise ValueError("A soma das parcelas ultrapassa o valor total da venda.")

    adicionar_parcelas(venda_id, quantidade, valor, status, data, usuario_id)
    return {
        "venda_id": venda_id,
        "quantidade": quantidade,
        "valor_parcela": float(valor),
        "status": status,
        "data": data,
        "valor_total_venda": valor_total_venda,
        "valor_ja_parcelado": float(valor_ja_parcelado),
    }


def listar_parcelas_por_cliente_formatadas(cliente: str, usuario_id: int) -> dict:
    parcelas = listar_parcelas_por_cliente(cliente, usuario_id)
    total_pago = calcular_total_pago(cliente, usuario_id)
    valor_total = buscar_valor_total_vendas(cliente, usuario_id)
    return {
        "cliente": cliente,
        "parcelas": [
            {
                "id": parcela_id,
                "venda_id": venda_id,
                "valor": float(valor),
                "status": status,
                "data": data,
            }
            for parcela_id, venda_id, valor, status, data in parcelas
        ],
        "resumo": {
            "total_pago": float(total_pago),
            "valor_total_vendas": float(valor_total),
            "ainda_falta": float(valor_total - total_pago),
        },
    }


def registrar_pagamento_parcela_service(parcela_id: int, usuario_id: int) -> bool:
    return registrar_pagamento_parcela_atomic(parcela_id, usuario_id)


def _venda_para_dict(venda: tuple | None) -> dict:
    if venda is None:
        return {}
    return {
        "id": venda[0],
        "cliente": venda[1],
        "tipo": venda[2],
        "valor_total": float(venda[3]),
        "comentario": venda[4],
        "data": venda[5],
    }
