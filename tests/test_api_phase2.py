import unittest

from fastapi.testclient import TestClient

from tests.db_support import remove_test_database, reset_test_database
from backend.main import app


class Phase2ApiTests(unittest.TestCase):
    def setUp(self):
        reset_test_database()
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()
        remove_test_database()

    def _register(self, name: str, email: str) -> int:
        response = self.client.post(
            "/api/auth/register",
            json={"usuario": name, "email": email, "senha": "senha123"},
        )
        self.assertEqual(response.status_code, 201, response.text)
        return int(response.json()["id"])

    def test_fluxo_financeiro_e_isolamento_entre_usuarios(self):
        user_a = self._register("Usuario A", "a@example.com")
        user_b = self._register("Usuario B", "b@example.com")

        login = self.client.post(
            "/api/auth/login", json={"email": "A@example.com", "senha": "senha123"}
        )
        self.assertEqual(login.status_code, 200, login.text)
        self.assertEqual(login.json()["id"], user_a)

        category_a = self.client.post(
            "/api/categories", json={"nome": "Alimentacao", "usuario_id": user_a}
        ).json()
        self.client.post(
            "/api/categories", json={"nome": "Privada B", "usuario_id": user_b}
        )
        account_a_1 = self.client.post(
            "/api/accounts",
            json={"nome": "Conta A", "tipo": "digital", "saldo_inicial": 1000, "usuario_id": user_a},
        ).json()
        account_a_2 = self.client.post(
            "/api/accounts",
            json={"nome": "Reserva A", "tipo": "poupanca", "saldo_inicial": 100, "usuario_id": user_a},
        ).json()
        account_b = self.client.post(
            "/api/accounts",
            json={"nome": "Conta B", "tipo": "digital", "saldo_inicial": 500, "usuario_id": user_b},
        ).json()

        expense = self.client.post(
            "/api/transactions",
            json={
                "valor": 80,
                "tipo": "saida",
                "categoria_id": category_a["id"],
                "comentario": "Mercado",
                "data": "2026-09-11",
                "usuario_id": user_a,
                "conta_id": account_a_1["id"],
            },
        )
        self.assertEqual(expense.status_code, 201, expense.text)
        expense_id = expense.json()["id"]

        income_b = self.client.post(
            "/api/transactions",
            json={
                "valor": 200,
                "tipo": "entrada",
                "data": "2026-09-11",
                "usuario_id": user_b,
                "conta_id": account_b["id"],
            },
        )
        self.assertEqual(income_b.status_code, 201, income_b.text)

        forbidden = self.client.post(
            "/api/transactions",
            json={
                "valor": 10,
                "tipo": "saida",
                "data": "2026-09-11",
                "usuario_id": user_b,
                "conta_id": account_a_1["id"],
            },
        )
        self.assertEqual(forbidden.status_code, 400)

        transfer = self.client.post(
            "/api/transfers",
            json={
                "conta_origem_id": account_a_1["id"],
                "conta_destino_id": account_a_2["id"],
                "valor": 100,
                "descricao": "Reserva",
                "data": "2026-09-11",
                "usuario_id": user_a,
            },
        )
        self.assertEqual(transfer.status_code, 201, transfer.text)

        transactions_a = self.client.get(
            "/api/transactions", params={"usuario_id": user_a}
        ).json()
        transactions_b = self.client.get(
            "/api/transactions", params={"usuario_id": user_b}
        ).json()
        self.assertEqual([item["id"] for item in transactions_a], [expense_id])
        self.assertEqual(len(transactions_b), 1)
        self.assertEqual(
            self.client.get("/api/categories", params={"usuario_id": user_a}).json(),
            [category_a],
        )

        updated = self.client.put(
            f"/api/transactions/{expense_id}",
            json={
                "valor": 90,
                "tipo": "saida",
                "categoria_id": category_a["id"],
                "comentario": "Mercado atualizado",
                "data": "2026-09-11",
                "usuario_id": user_a,
                "conta_id": account_a_1["id"],
            },
        )
        self.assertEqual(updated.status_code, 200, updated.text)
        self.assertEqual(updated.json()["valor"], 90)
        self.assertEqual(
            self.client.get("/api/transactions/summary", params={"usuario_id": user_a}).json(),
            {"entradas": 0.0, "saidas": 90.0, "saldo": -90.0},
        )

        self.assertEqual(
            self.client.delete(
                f"/api/transfers/{transfer.json()['id']}", params={"usuario_id": user_a}
            ).status_code,
            204,
        )
        self.assertEqual(
            self.client.delete(
                f"/api/transactions/{expense_id}", params={"usuario_id": user_a}
            ).status_code,
            204,
        )
        self.assertEqual(
            self.client.get("/api/transactions", params={"usuario_id": user_a}).json(), []
        )


if __name__ == "__main__":
    unittest.main()
