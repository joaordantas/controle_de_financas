import os
import unittest
from datetime import date


TEST_DB_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "storage", "test_accounts.db")
)
os.environ["FINANCE_DB_PATH"] = TEST_DB_PATH

from database.connection import get_connection
from database.schema import criar_banco
from services.cartao_service import (
    alterar_status_cartao_service,
    atualizar_cartao_service,
    atualizar_compra_service,
    calcular_ciclo_fatura,
    calcular_status_fatura,
    criar_cartao_service,
    criar_compra_service,
    deletar_compra_service,
    listar_cartoes_formatados,
    listar_faturas_service,
    obter_fatura_service,
    pagar_fatura_service,
)
from services.categoria_service import criar_categoria_service
from services.conta_service import (
    alterar_status_conta_service,
    criar_conta_service,
    definir_conta_principal_service,
    listar_contas_formatadas,
)
from services.transacao_service import obter_resumo_financeiro


class Phase3ATests(unittest.TestCase):
    def setUp(self):
        if os.path.exists(TEST_DB_PATH):
            os.remove(TEST_DB_PATH)
        criar_banco()
        conn = get_connection()
        conn.execute(
            "INSERT INTO usuarios (id, usuario, email, senha) VALUES (1, 'Teste', 'teste@example.com', 'hash')"
        )
        conn.execute(
            "INSERT INTO usuarios (id, usuario, email, senha) VALUES (2, 'Outro', 'outro@example.com', 'hash')"
        )
        conn.commit()
        conn.close()
        self.conta_1 = criar_conta_service("Conta 1", "digital", 2000, 1)
        self.conta_2 = criar_conta_service("Conta 2", "corrente", 500, 1)
        self.categoria_1 = criar_categoria_service("Alimentacao", 1)
        self.categoria_2 = criar_categoria_service("Categoria externa", 2)

    def tearDown(self):
        if os.path.exists(TEST_DB_PATH):
            os.remove(TEST_DB_PATH)

    def criar_cartao(self, usuario_id: int = 1, limite: float = 1000) -> dict:
        return criar_cartao_service(usuario_id, "Cartao teste", limite, 13, 20)

    def test_conta_principal_troca_atomica_e_unica(self):
        primeira = definir_conta_principal_service(self.conta_1["id"], 1)
        self.assertTrue(primeira["principal"])
        definir_conta_principal_service(self.conta_2["id"], 1)
        contas = listar_contas_formatadas(1, True)
        principais = [conta for conta in contas if conta["principal"]]
        self.assertEqual(len(principais), 1)
        self.assertEqual(principais[0]["id"], self.conta_2["id"])

    def test_conta_principal_valida_usuario_atividade_e_desativacao(self):
        conta_outro = criar_conta_service("Externa", "digital", 0, 2)
        with self.assertRaisesRegex(ValueError, "Conta nao encontrada"):
            definir_conta_principal_service(conta_outro["id"], 1)

        conta_zero = criar_conta_service("Zerada", "dinheiro", 0, 1)
        alterar_status_conta_service(conta_zero["id"], False, 1)
        with self.assertRaisesRegex(ValueError, "inativa"):
            definir_conta_principal_service(conta_zero["id"], 1)

        reativada = alterar_status_conta_service(conta_zero["id"], True, 1)
        self.assertFalse(reativada["principal"])
        definir_conta_principal_service(conta_zero["id"], 1)
        desativada = alterar_status_conta_service(conta_zero["id"], False, 1)
        self.assertFalse(desativada["principal"])
        self.assertFalse(any(conta["principal"] for conta in listar_contas_formatadas(1, True)))

    def test_usuario_sem_principal_continua_funcionando(self):
        self.assertFalse(any(conta["principal"] for conta in listar_contas_formatadas(1)))

    def test_ciclo_antes_no_dia_e_depois_do_fechamento(self):
        antes = calcular_ciclo_fatura("2026-09-12", 13, 20)
        no_dia = calcular_ciclo_fatura("2026-09-13", 13, 20)
        depois = calcular_ciclo_fatura("2026-09-14", 13, 20)
        self.assertEqual((antes["ano_referencia"], antes["mes_referencia"]), (2026, 9))
        self.assertEqual(no_dia["data_fechamento"], "2026-09-13")
        self.assertEqual((depois["ano_referencia"], depois["mes_referencia"]), (2026, 10))

    def test_ciclo_trata_fevereiro_e_dezembro_janeiro(self):
        fevereiro = calcular_ciclo_fatura("2027-02-28", 31, 5)
        virada = calcular_ciclo_fatura("2026-12-14", 13, 20)
        self.assertEqual(fevereiro["data_fechamento"], "2027-02-28")
        self.assertEqual(fevereiro["data_vencimento"], "2027-03-05")
        self.assertEqual((virada["ano_referencia"], virada["mes_referencia"]), (2027, 1))

    def test_status_da_fatura_e_derivado(self):
        self.assertEqual(calcular_status_fatura("2026-09-13", "2026-09-20", 0, 100, date(2026, 9, 13)), "aberta")
        self.assertEqual(calcular_status_fatura("2026-09-13", "2026-09-20", 0, 100, date(2026, 9, 14)), "fechada")
        self.assertEqual(calcular_status_fatura("2026-09-13", "2026-09-20", 0, 100, date(2026, 9, 21)), "vencida")
        self.assertEqual(calcular_status_fatura("2026-09-13", "2026-09-20", 100, 100, date(2026, 9, 21)), "paga")

    def test_cartao_criacao_edicao_status_e_isolamento(self):
        cartao = self.criar_cartao()
        atualizado = atualizar_cartao_service(cartao["id"], 1, "Novo nome", 1500, 10, 18)
        self.assertEqual(atualizado["nome"], "Novo nome")
        self.assertEqual(atualizado["limite_total"], 1500)
        inativo = alterar_status_cartao_service(cartao["id"], 1, False)
        self.assertFalse(inativo["ativo"])
        with self.assertRaisesRegex(ValueError, "Cartao nao encontrado"):
            atualizar_cartao_service(cartao["id"], 2, "Invasao", 1000, 10, 18)

    def test_compra_calcula_fatura_e_limite(self):
        cartao = self.criar_cartao()
        compra = criar_compra_service(
            cartao["id"], 1, 250, "Mercado", self.categoria_1["id"], "2026-09-12"
        )
        fatura = obter_fatura_service(compra["fatura_id"], 1)
        cartao_atual = listar_cartoes_formatados(1)[0]
        self.assertEqual(fatura["valor_total"], 250)
        self.assertEqual(fatura["mes_referencia"], 9)
        self.assertEqual(cartao_atual["limite_utilizado"], 250)
        self.assertEqual(cartao_atual["limite_disponivel"], 750)
        self.assertEqual(obter_resumo_financeiro(1)["saidas"], 250)

    def test_compra_valida_categoria_limite_e_cartao_ativo(self):
        cartao = self.criar_cartao(limite=100)
        with self.assertRaisesRegex(ValueError, "Categoria nao encontrada"):
            criar_compra_service(cartao["id"], 1, 10, "Compra", self.categoria_2["id"], "2026-09-10")
        with self.assertRaisesRegex(ValueError, "Limite insuficiente"):
            criar_compra_service(cartao["id"], 1, 101, "Compra", self.categoria_1["id"], "2026-09-10")
        alterar_status_cartao_service(cartao["id"], 1, False)
        with self.assertRaisesRegex(ValueError, "Cartao ativo"):
            criar_compra_service(cartao["id"], 1, 10, "Compra", self.categoria_1["id"], "2026-09-10")

    def test_edicao_e_exclusao_de_compra_recalculam_fatura(self):
        cartao = self.criar_cartao()
        compra = criar_compra_service(cartao["id"], 1, 100, "Original", self.categoria_1["id"], "2026-09-12")
        atualizada = atualizar_compra_service(
            compra["id"], cartao["id"], 1, 180, "Atualizada", self.categoria_1["id"], "2026-09-14"
        )
        self.assertNotEqual(atualizada["fatura_id"], compra["fatura_id"])
        self.assertEqual(obter_fatura_service(atualizada["fatura_id"], 1)["valor_total"], 180)
        self.assertTrue(deletar_compra_service(compra["id"], 1))
        self.assertEqual(listar_cartoes_formatados(1)[0]["limite_utilizado"], 0)

    def test_pagamento_reduz_conta_libera_limite_e_nao_duplica_despesa(self):
        cartao = self.criar_cartao()
        compra = criar_compra_service(cartao["id"], 1, 300, "Compra", self.categoria_1["id"], "2026-09-10")
        resumo_antes = obter_resumo_financeiro(1)
        paga = pagar_fatura_service(compra["fatura_id"], self.conta_1["id"], 1, "2026-09-20")
        conta = next(conta for conta in listar_contas_formatadas(1) if conta["id"] == self.conta_1["id"])
        self.assertEqual(paga["status"], "paga")
        self.assertEqual(conta["saldo_atual"], 1700)
        self.assertEqual(listar_cartoes_formatados(1)[0]["limite_disponivel"], 1000)
        self.assertEqual(obter_resumo_financeiro(1), resumo_antes)

    def test_pagamento_duplicado_e_de_outro_usuario_sao_impedidos(self):
        cartao = self.criar_cartao()
        compra = criar_compra_service(cartao["id"], 1, 100, "Compra", self.categoria_1["id"], "2026-09-10")
        conta_outro = criar_conta_service("Externa", "digital", 1000, 2)
        with self.assertRaisesRegex(ValueError, "Conta de pagamento nao encontrada"):
            pagar_fatura_service(compra["fatura_id"], conta_outro["id"], 1, "2026-09-20")
        pagar_fatura_service(compra["fatura_id"], self.conta_1["id"], 1, "2026-09-20")
        with self.assertRaisesRegex(ValueError, "ja foi paga"):
            pagar_fatura_service(compra["fatura_id"], self.conta_1["id"], 1, "2026-09-20")
        with self.assertRaisesRegex(ValueError, "Fatura nao encontrada"):
            pagar_fatura_service(compra["fatura_id"], conta_outro["id"], 2, "2026-09-20")

    def test_fatura_paga_preserva_compras_e_historico(self):
        cartao = self.criar_cartao()
        compra = criar_compra_service(cartao["id"], 1, 80, "Compra", self.categoria_1["id"], "2026-09-10")
        pagar_fatura_service(compra["fatura_id"], self.conta_1["id"], 1, "2026-09-20")
        with self.assertRaisesRegex(ValueError, "fatura paga"):
            atualizar_compra_service(compra["id"], cartao["id"], 1, 90, "Editar", self.categoria_1["id"], "2026-09-10")
        with self.assertRaisesRegex(ValueError, "fatura paga"):
            deletar_compra_service(compra["id"], 1)
        self.assertGreaterEqual(len(listar_faturas_service(cartao["id"], 1)), 1)


if __name__ == "__main__":
    unittest.main()
