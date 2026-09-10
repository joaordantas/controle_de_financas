from repositories.conta_repo import (
    alterar_status_conta,
    atualizar_conta,
    buscar_conta_por_id,
    criar_conta,
    listar_contas_com_saldo,
)


TIPOS_DE_CONTA = {"corrente", "poupanca", "digital", "dinheiro", "outro"}


def _validar_dados_conta(nome: str, tipo: str) -> str:
    nome_limpo = nome.strip()
    if not nome_limpo:
        raise ValueError("Informe um nome para a conta.")
    if tipo not in TIPOS_DE_CONTA:
        raise ValueError("Tipo de conta invalido.")
    return nome_limpo


def _formatar_conta(conta: tuple) -> dict:
    conta_id, nome, tipo, saldo_inicial, ativo, saldo_atual = conta
    return {
        "id": conta_id,
        "nome": nome,
        "tipo": tipo,
        "saldo_inicial": float(saldo_inicial),
        "saldo_atual": float(saldo_atual),
        "ativo": bool(ativo),
    }


def criar_conta_service(nome: str, tipo: str, saldo_inicial: float, usuario_id: int) -> dict:
    nome_limpo = _validar_dados_conta(nome, tipo)
    conta_id = criar_conta(nome_limpo, tipo, saldo_inicial, usuario_id)
    return {
        "id": conta_id,
        "nome": nome_limpo,
        "tipo": tipo,
        "saldo_inicial": float(saldo_inicial),
        "saldo_atual": float(saldo_inicial),
        "ativo": True,
    }


def listar_contas_formatadas(usuario_id: int, incluir_inativas: bool = False) -> list[dict]:
    return [
        _formatar_conta(conta)
        for conta in listar_contas_com_saldo(usuario_id, incluir_inativas)
    ]


def obter_conta(conta_id: int, usuario_id: int, somente_ativa: bool = True) -> tuple | None:
    return buscar_conta_por_id(conta_id, usuario_id, somente_ativa)


def obter_conta_ativa(conta_id: int, usuario_id: int) -> tuple | None:
    return obter_conta(conta_id, usuario_id, True)


def atualizar_conta_service(
    conta_id: int,
    nome: str,
    tipo: str,
    saldo_inicial: float,
    usuario_id: int,
) -> dict:
    nome_limpo = _validar_dados_conta(nome, tipo)
    if obter_conta(conta_id, usuario_id, False) is None:
        raise ValueError("Conta nao encontrada.")
    atualizar_conta(conta_id, nome_limpo, tipo, saldo_inicial, usuario_id)
    conta = obter_conta(conta_id, usuario_id, False)
    if conta is None:
        raise ValueError("Conta nao encontrada.")
    return _formatar_conta(conta)


def alterar_status_conta_service(conta_id: int, ativo: bool, usuario_id: int) -> dict:
    conta = obter_conta(conta_id, usuario_id, False)
    if conta is None:
        raise ValueError("Conta nao encontrada.")
    if not ativo and abs(float(conta[5])) >= 0.005:
        raise ValueError("Transfira ou ajuste o saldo antes de desativar esta conta.")
    alterar_status_conta(conta_id, ativo, usuario_id)
    atualizada = obter_conta(conta_id, usuario_id, False)
    if atualizada is None:
        raise ValueError("Conta nao encontrada.")
    return _formatar_conta(atualizada)
