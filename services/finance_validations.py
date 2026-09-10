from datetime import date


def validar_data_financeira(valor: str) -> str:
    try:
        date.fromisoformat(valor)
    except (TypeError, ValueError) as exc:
        raise ValueError("Informe uma data valida.") from exc
    return valor


def limpar_descricao(valor: str | None) -> str | None:
    descricao = valor.strip() if valor else ""
    return descricao or None
