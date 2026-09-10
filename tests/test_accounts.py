import os
import unittest


TEST_DB_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "storage", "test_accounts.db")
)
os.environ["FINANCE_DB_PATH"] = TEST_DB_PATH

from database.connection import get_connection
from database.schema import criar_banco
from services.conta_service import criar_conta_service, listar_contas_formatadas
from services.transacao_service import criar_transacao_service, obter_resumo_financeiro
from services.transferencia_service import criar_transferencia_service


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


if __name__ == "__main__":
    unittest.main()
