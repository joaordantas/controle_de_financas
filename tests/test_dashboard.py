import unittest

from fastapi.testclient import TestClient

from backend.main import app
from database.connection import get_connection
from services.cartao_service import criar_cartao_service, criar_compra_service
from services.categoria_service import criar_categoria_service
from services.conta_service import criar_conta_service
from services.transacao_service import criar_transacao_service
from tests.auth_support import authenticate_existing_user
from tests.db_support import remove_test_database, reset_test_database


class DashboardApiTests(unittest.TestCase):
    def setUp(self):
        reset_test_database()
        conn = get_connection()
        conn.execute(
            "INSERT INTO usuarios (id, usuario, email, senha) VALUES (1, 'Teste', 'teste@example.com', 'hash')"
        )
        conn.execute(
            "INSERT INTO usuarios (id, usuario, email, senha) VALUES (2, 'Outro', 'outro@example.com', 'hash')"
        )
        conn.commit()
        conn.close()
        self.client = TestClient(app)
        authenticate_existing_user(self.client, 1)

    def tearDown(self):
        self.client.close()
        remove_test_database()

    def get_profit(self, inicio: str, fim: str):
        return self.client.get(
            "/api/dashboard/profit",
            params={"data_inicio": inicio, "data_fim": fim},
        )

    def test_usuario_com_conta_e_sem_movimentacoes_retorna_zeros(self):
        criar_conta_service("Nubank", "digital", 7.22, 1)

        profit = self.get_profit("2026-09-01", "2026-09-30")
        accounts = self.client.get("/api/accounts")

        self.assertEqual(profit.status_code, 200, profit.text)
        self.assertEqual(profit.json(), {"entrada": 0.0, "saida": 0.0, "lucro": 0.0})
        self.assertEqual(accounts.status_code, 200, accounts.text)
        self.assertEqual(accounts.json()[0]["saldo_atual"], 7.22)

    def test_profit_soma_receitas_despesas_e_compras_do_periodo(self):
        conta = criar_conta_service("Conta", "digital", 0, 1)
        categoria = criar_categoria_service("Alimentacao", 1)
        criar_transacao_service(1000, "entrada", None, "Salario", "2026-09-02", 1, conta["id"])
        criar_transacao_service(100, "saida", categoria["id"], "Mercado", "2026-09-03", 1, conta["id"])
        criar_transacao_service(200, "saida", categoria["id"], "Fora do periodo", "2026-08-31", 1, conta["id"])
        cartao = criar_cartao_service(1, "Cartao", 1000, 13, 20)
        criar_compra_service(cartao["id"], 1, 50, "Compra", categoria["id"], "2026-09-04")

        conta_outro = criar_conta_service("Conta externa", "digital", 0, 2)
        criar_transacao_service(999, "entrada", None, "Outro usuario", "2026-09-05", 2, conta_outro["id"])

        response = self.get_profit("2026-09-01", "2026-09-11")

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json(), {"entrada": 1000.0, "saida": 150.0, "lucro": 850.0})

    def test_periodo_sem_movimentacoes_e_isolamento(self):
        conta_outro = criar_conta_service("Conta externa", "digital", 0, 2)
        criar_transacao_service(300, "entrada", None, "Outro usuario", "2026-09-05", 2, conta_outro["id"])

        vazio = self.get_profit("2026-10-01", "2026-10-31")
        with TestClient(app) as client_outro:
            authenticate_existing_user(client_outro, 2)
            outro_usuario = client_outro.get(
                "/api/dashboard/profit",
                params={"data_inicio": "2026-09-01", "data_fim": "2026-09-30"},
            )

        self.assertEqual(vazio.status_code, 200, vazio.text)
        self.assertEqual(vazio.json(), {"entrada": 0.0, "saida": 0.0, "lucro": 0.0})
        self.assertEqual(outro_usuario.status_code, 200, outro_usuario.text)
        self.assertEqual(outro_usuario.json(), {"entrada": 300.0, "saida": 0.0, "lucro": 300.0})
