from repositories.conta_repo import buscar_conta_por_id, criar_conta, listar_contas_com_saldo


TIPOS_DE_CONTA = {"corrente", "poupanca", "digital", "dinheiro", "outro"}


def criar_conta_service(nome: str, tipo: str, saldo_inicial: float, usuario_id: int) -> dict:
    nome_limpo = nome.strip()
    if not nome_limpo:
        raise ValueError("Informe um nome para a conta.")
    if tipo not in TIPOS_DE_CONTA:
        raise ValueError("Tipo de conta invalido.")

    conta_id = criar_conta(nome_limpo, tipo, saldo_inicial, usuario_id)
    return {
        "id": conta_id,
        "nome": nome_limpo,
        "tipo": tipo,
        "saldo_inicial": float(saldo_inicial),
        "saldo_atual": float(saldo_inicial),
        "ativo": True,
    }


def listar_contas_formatadas(usuario_id: int) -> list[dict]:
    return [
        {
            "id": conta_id,
            "nome": nome,
            "tipo": tipo,
            "saldo_inicial": float(saldo_inicial),
            "saldo_atual": float(saldo_atual),
            "ativo": bool(ativo),
        }
        for conta_id, nome, tipo, saldo_inicial, ativo, saldo_atual
        in listar_contas_com_saldo(usuario_id)
    ]


def obter_conta_ativa(conta_id: int, usuario_id: int) -> tuple | None:
    return buscar_conta_por_id(conta_id, usuario_id)
