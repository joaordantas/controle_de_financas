from repositories.transferencia_repo import criar_transferencia, listar_transferencias
from services.conta_service import obter_conta_ativa


def criar_transferencia_service(
    conta_origem_id: int,
    conta_destino_id: int,
    valor: float,
    descricao: str | None,
    data: str,
    usuario_id: int,
) -> dict:
    if valor <= 0:
        raise ValueError("O valor da transferencia deve ser maior que zero.")
    if conta_origem_id == conta_destino_id:
        raise ValueError("Escolha contas diferentes para a transferencia.")
    if obter_conta_ativa(conta_origem_id, usuario_id) is None:
        raise ValueError("Conta de origem nao encontrada.")
    if obter_conta_ativa(conta_destino_id, usuario_id) is None:
        raise ValueError("Conta de destino nao encontrada.")

    transferencia_id = criar_transferencia(
        conta_origem_id,
        conta_destino_id,
        valor,
        descricao.strip() if descricao else None,
        data,
        usuario_id,
    )
    return {
        "id": transferencia_id,
        "conta_origem_id": conta_origem_id,
        "conta_destino_id": conta_destino_id,
        "valor": float(valor),
        "descricao": descricao.strip() if descricao else None,
        "data": data,
    }


def listar_transferencias_formatadas(usuario_id: int) -> list[dict]:
    return [
        {
            "id": transferencia_id,
            "conta_origem_id": conta_origem_id,
            "conta_origem": conta_origem,
            "conta_destino_id": conta_destino_id,
            "conta_destino": conta_destino,
            "valor": float(valor),
            "descricao": descricao,
            "data": data,
        }
        for (
            transferencia_id,
            conta_origem_id,
            conta_origem,
            conta_destino_id,
            conta_destino,
            valor,
            descricao,
            data,
        ) in listar_transferencias(usuario_id)
    ]
