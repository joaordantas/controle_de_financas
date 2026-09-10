import os
import unittest


TEST_DB_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "storage", "test_accounts.db")
)
os.environ["FINANCE_DB_PATH"] = TEST_DB_PATH

from database.connection import get_connection
from database.schema import criar_banco
from services.categoria_service import (
    criar_categoria_service,
    deletar_categoria_service,
    renomear_categoria_service,
)
from services.conta_service import (
    alterar_status_conta_service,
    atualizar_conta_service,
    criar_conta_service,
    listar_contas_formatadas,
)
from services.transacao_service import (
    atualizar_transacao_service,
    criar_transacao_service,
    deletar_transacao_service,
    obter_resumo_financeiro,
)
from services.transferencia_service import (
    atualizar_transferencia_service,
    criar_transferencia_service,
    deletar_transferencia_service,
)


class AccountBalanceTests(unittest.TestCase):
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

    def tearDown(self):
        if os.path.exists(TEST_DB_PATH):
            os.remove(TEST_DB_PATH)

    def test_transferencia_altera_contas_sem_alterar_resumo(self):
        origem = criar_conta_service("Conta A", "digital", 1000, 1)
        destino = criar_conta_service("Conta B", "corrente", 100, 1)

        criar_transacao_service(100, "saida", None, "Mercado", "2026-09-10", 1, origem["id"])
        criar_transacao_service(50, "entrada", None, "Reembolso", "2026-09-10", 1, destino["id"])
        criar_transferencia_service(origem["id"], destino["id"], 200, None, "2026-09-10", 1)

        contas = {conta["nome"]: conta["saldo_atual"] for conta in listar_contas_formatadas(1)}
        self.assertEqual(contas["Conta A"], 700)
        self.assertEqual(contas["Conta B"], 350)
        self.assertEqual(sum(contas.values()), 1050)
        self.assertEqual(
            obter_resumo_financeiro(1),
            {"entradas": 50.0, "saidas": 100.0, "saldo": -50.0},
        )

    def test_usuario_nao_pode_usar_conta_de_outro_usuario(self):
        conta_usuario_1 = criar_conta_service("Minha conta", "digital", 100, 1)
        conta_usuario_2 = criar_conta_service("Conta externa", "digital", 100, 2)

        with self.assertRaisesRegex(ValueError, "Conta nao encontrada"):
            criar_transacao_service(10, "saida", None, None, "2026-09-10", 1, conta_usuario_2["id"])

        with self.assertRaisesRegex(ValueError, "Conta de destino nao encontrada"):
            criar_transferencia_service(
                conta_usuario_1["id"], conta_usuario_2["id"], 10, None, "2026-09-10", 1
            )

    def test_editar_e_excluir_transacao_recalcula_saldos(self):
        conta = criar_conta_service("Principal", "digital", 1000, 1)
        categoria = criar_categoria_service("Alimentacao", 1)
        transacao = criar_transacao_service(
            100, "saida", categoria["id"], "Mercado", "2026-09-10", 1, conta["id"]
        )

        atualizada = atualizar_transacao_service(
            transacao["id"], 250, "saida", categoria["id"], "Compras", "2026-09-11", 1, conta["id"]
        )
        self.assertEqual(atualizada["valor"], 250)
        self.assertEqual(listar_contas_formatadas(1)[0]["saldo_atual"], 750)
        self.assertEqual(obter_resumo_financeiro(1)["saidas"], 250)

        self.assertTrue(deletar_transacao_service(transacao["id"], 1))
        self.assertEqual(listar_contas_formatadas(1)[0]["saldo_atual"], 1000)
        self.assertEqual(obter_resumo_financeiro(1)["saidas"], 0)

    def test_editar_e_excluir_transferencia_recalcula_contas(self):
        origem = criar_conta_service("Origem", "digital", 500, 1)
        destino = criar_conta_service("Destino", "corrente", 100, 1)
        transferencia = criar_transferencia_service(
            origem["id"], destino["id"], 100, "Reserva", "2026-09-10", 1
        )

        atualizar_transferencia_service(
            transferencia["id"], destino["id"], origem["id"], 50, "Devolucao", "2026-09-11", 1
        )
        contas = {conta["nome"]: conta["saldo_atual"] for conta in listar_contas_formatadas(1)}
        self.assertEqual(contas, {"Origem": 550, "Destino": 50})

        self.assertTrue(deletar_transferencia_service(transferencia["id"], 1))
        contas = {conta["nome"]: conta["saldo_atual"] for conta in listar_contas_formatadas(1)}
        self.assertEqual(contas, {"Origem": 500, "Destino": 100})

    def test_conta_pode_ser_editada_e_so_desativada_com_saldo_zero(self):
        conta = criar_conta_service("Carteira", "dinheiro", 20, 1)
        atualizada = atualizar_conta_service(conta["id"], "Dinheiro", "dinheiro", 0, 1)
        self.assertEqual(atualizada["nome"], "Dinheiro")
        self.assertEqual(atualizada["saldo_atual"], 0)

        inativa = alterar_status_conta_service(conta["id"], False, 1)
        self.assertFalse(inativa["ativo"])
        self.assertEqual(listar_contas_formatadas(1), [])
        self.assertEqual(len(listar_contas_formatadas(1, True)), 1)

        alterar_status_conta_service(conta["id"], True, 1)
        criar_transacao_service(10, "entrada", None, "Ajuste", "2026-09-10", 1, conta["id"])
        with self.assertRaisesRegex(ValueError, "saldo antes de desativar"):
            alterar_status_conta_service(conta["id"], False, 1)

    def test_categoria_nao_duplica_e_nao_e_excluida_quando_esta_em_uso(self):
        conta = criar_conta_service("Principal", "digital", 100, 1)
        categoria = criar_categoria_service("Mercado", 1)
        with self.assertRaisesRegex(ValueError, "Ja existe"):
            criar_categoria_service(" mercado ", 1)

        renomeada = renomear_categoria_service(categoria["id"], "Alimentacao", 1)
        self.assertEqual(renomeada["nome"], "Alimentacao")
        criar_transacao_service(
            10, "saida", categoria["id"], "Compra", "2026-09-10", 1, conta["id"]
        )
        with self.assertRaisesRegex(ValueError, "em uso"):
            deletar_categoria_service(categoria["id"], 1)


if __name__ == "__main__":
    unittest.main()
