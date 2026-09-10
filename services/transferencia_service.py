from repositories.transferencia_repo import (
    atualizar_transferencia,
    buscar_transferencia_por_id,
    criar_transferencia,
    deletar_transferencia,
    listar_transferencias,
)
from services.conta_service import obter_conta_ativa
from services.finance_validations import limpar_descricao, validar_data_financeira


def _validar_transferencia(
    conta_origem_id: int,
    conta_destino_id: int,
    valor: float,
    data: str,
    usuario_id: int,
) -> None:
    if valor <= 0:
        raise ValueError("O valor da transferencia deve ser maior que zero.")
    if conta_origem_id == conta_destino_id:
        raise ValueError("Escolha contas diferentes para a transferencia.")
    validar_data_financeira(data)
    if obter_conta_ativa(conta_origem_id, usuario_id) is None:
        raise ValueError("Conta de origem nao encontrada.")
    if obter_conta_ativa(conta_destino_id, usuario_id) is None:
        raise ValueError("Conta de destino nao encontrada.")


def _formatar_transferencia(transferencia: tuple) -> dict:
    (
        transferencia_id,
        conta_origem_id,
        conta_origem,
        conta_destino_id,
        conta_destino,
        valor,
        descricao,
        data,
    ) = transferencia
    return {
        "id": transferencia_id,
        "conta_origem_id": conta_origem_id,
        "conta_origem": conta_origem,
        "conta_destino_id": conta_destino_id,
        "conta_destino": conta_destino,
        "valor": float(valor),
        "descricao": descricao,
        "data": data,
    }


def criar_transferencia_service(
    conta_origem_id: int,
    conta_destino_id: int,
    valor: float,
    descricao: str | None,
    data: str,
    usuario_id: int,
) -> dict:
    _validar_transferencia(conta_origem_id, conta_destino_id, valor, data, usuario_id)
    transferencia_id = criar_transferencia(
        conta_origem_id,
        conta_destino_id,
        valor,
        limpar_descricao(descricao),
        data,
        usuario_id,
    )
    transferencia = buscar_transferencia_por_id(transferencia_id, usuario_id)
    if transferencia is None:
        raise ValueError("Transferencia nao encontrada.")
    return _formatar_transferencia(transferencia)


def atualizar_transferencia_service(
    transferencia_id: int,
    conta_origem_id: int,
    conta_destino_id: int,
    valor: float,
    descricao: str | None,
    data: str,
    usuario_id: int,
) -> dict:
    if buscar_transferencia_por_id(transferencia_id, usuario_id) is None:
        raise ValueError("Transferencia nao encontrada.")
    _validar_transferencia(conta_origem_id, conta_destino_id, valor, data, usuario_id)
    atualizar_transferencia(
        transferencia_id,
        conta_origem_id,
        conta_destino_id,
        valor,
        limpar_descricao(descricao),
        data,
        usuario_id,
    )
    transferencia = buscar_transferencia_por_id(transferencia_id, usuario_id)
    if transferencia is None:
        raise ValueError("Transferencia nao encontrada.")
    return _formatar_transferencia(transferencia)


def deletar_transferencia_service(transferencia_id: int, usuario_id: int) -> bool:
    return deletar_transferencia(transferencia_id, usuario_id)


def listar_transferencias_formatadas(usuario_id: int) -> list[dict]:
    return [
        _formatar_transferencia(transferencia)
        for transferencia in listar_transferencias(usuario_id)
    ]
