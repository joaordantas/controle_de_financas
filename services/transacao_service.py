from repositories.transacao_repo import (
    adicionar_transacao,
    atualizar_transacao,
    buscar_transacao_por_id,
    calcular_resumo,
    deletar_transacao,
    listar_transacoes,
)
from services.categoria_service import obter_categoria
from services.conta_service import obter_conta_ativa
from services.finance_validations import limpar_descricao, validar_data_financeira


def _validar_transacao(
    valor: float,
    tipo: str,
    categoria_id: int | None,
    data: str,
    usuario_id: int,
    conta_id: int | None,
) -> None:
    if valor <= 0:
        raise ValueError("O valor da transacao deve ser maior que zero.")
    if tipo not in {"entrada", "saida"}:
        raise ValueError("Tipo de transacao invalido.")
    validar_data_financeira(data)
    if conta_id is not None and obter_conta_ativa(conta_id, usuario_id) is None:
        raise ValueError("Conta nao encontrada.")
    if categoria_id is not None and obter_categoria(categoria_id, usuario_id) is None:
        raise ValueError("Categoria nao encontrada.")


def _formatar_transacao(transacao: tuple) -> dict:
    (
        transacao_id,
        valor,
        tipo,
        categoria_id,
        categoria,
        comentario,
        data,
        conta_id,
        conta,
    ) = transacao
    return {
        "id": transacao_id,
        "valor": float(valor),
        "tipo": tipo,
        "categoria_id": categoria_id,
        "categoria": categoria,
        "comentario": comentario,
        "data": data,
        "conta_id": conta_id,
        "conta": conta,
    }


def criar_transacao_service(
    valor: float,
    tipo: str,
    categoria_id: int | None,
    comentario: str | None,
    data: str,
    usuario_id: int,
    conta_id: int | None = None,
) -> dict:
    _validar_transacao(valor, tipo, categoria_id, data, usuario_id, conta_id)
    transacao_id = adicionar_transacao(
        valor,
        tipo,
        categoria_id,
        limpar_descricao(comentario),
        data,
        usuario_id,
        conta_id,
    )
    transacao = buscar_transacao_por_id(transacao_id, usuario_id)
    if transacao is None:
        raise ValueError("Transacao nao encontrada.")
    return _formatar_transacao(transacao)


def atualizar_transacao_service(
    transacao_id: int,
    valor: float,
    tipo: str,
    categoria_id: int | None,
    comentario: str | None,
    data: str,
    usuario_id: int,
    conta_id: int | None,
) -> dict:
    if buscar_transacao_por_id(transacao_id, usuario_id) is None:
        raise ValueError("Transacao nao encontrada.")
    _validar_transacao(valor, tipo, categoria_id, data, usuario_id, conta_id)
    atualizar_transacao(
        transacao_id,
        valor,
        tipo,
        categoria_id,
        limpar_descricao(comentario),
        data,
        conta_id,
        usuario_id,
    )
    transacao = buscar_transacao_por_id(transacao_id, usuario_id)
    if transacao is None:
        raise ValueError("Transacao nao encontrada.")
    return _formatar_transacao(transacao)


def deletar_transacao_service(transacao_id: int, usuario_id: int) -> bool:
    return deletar_transacao(transacao_id, usuario_id)


def listar_transacoes_formatadas(usuario_id: int) -> list[dict]:
    return [_formatar_transacao(transacao) for transacao in listar_transacoes(usuario_id)]


def obter_resumo_financeiro(usuario_id: int) -> dict:
    entradas, saidas, saldo = calcular_resumo(usuario_id)
    return {"entradas": entradas, "saidas": saidas, "saldo": saldo}
