from repositories.limite_repo import definir_limite, listar_limites_do_mes


def salvar_limite(categoria_id: int, valor: float, mes: str, usuario_id: int) -> dict:
    if valor <= 0:
        raise ValueError("O limite deve ser maior que zero.")
    definir_limite(categoria_id, valor, mes, usuario_id)
    return {
        "categoria_id": categoria_id,
        "valor": float(valor),
        "mes": mes,
        "usuario_id": usuario_id,
    }


def listar_limites_formatados(mes: str, usuario_id: int) -> list[dict]:
    limites = listar_limites_do_mes(mes, usuario_id)
    return [
        {
            "categoria": nome,
            "limite": float(limite),
            "gasto": float(gasto),
            "percentual": float(gasto / limite) if limite else 0.0,
        }
        for nome, limite, gasto in limites
    ]
