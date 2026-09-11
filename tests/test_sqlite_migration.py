import sqlite3
import unittest
from pathlib import Path

from scripts.migrate_sqlite_to_postgres import (
    inspect_source,
    resolve_known_orphans,
    validate_source_integrity,
)


class SqliteMigrationTests(unittest.TestCase):
    def setUp(self):
        self.source = Path(__file__).resolve().parents[1] / "storage" / "test_legacy_source.db"
        self.source.unlink(missing_ok=True)

    def tearDown(self):
        self.source.unlink(missing_ok=True)

    def test_analisa_banco_valido_sem_alterar_arquivo(self):
        connection = sqlite3.connect(self.source)
        connection.executescript(
            """
            CREATE TABLE usuarios (
                id INTEGER PRIMARY KEY, usuario TEXT, email TEXT, senha TEXT, tipo_perfil TEXT
            );
            CREATE TABLE contas (
                id INTEGER PRIMARY KEY, nome TEXT, tipo TEXT, saldo_inicial REAL,
                ativo INTEGER, principal INTEGER, usuario_id INTEGER
            );
            INSERT INTO usuarios VALUES (7, 'Teste', 'teste@example.com', 'hash', 'Apenas Financeiro');
            INSERT INTO contas VALUES (9, 'Conta', 'digital', 10.25, 1, 0, 7);
            """
        )
        connection.commit()
        connection.close()

        source, counts = inspect_source(self.source)
        try:
            self.assertEqual(counts, {"usuarios": 1, "contas": 1})
            self.assertEqual(validate_source_integrity(source), [])
        finally:
            source.close()

    def test_detecta_relacionamento_orfao_antes_da_importacao(self):
        connection = sqlite3.connect(self.source)
        connection.executescript(
            """
            CREATE TABLE usuarios (
                id INTEGER PRIMARY KEY, usuario TEXT, email TEXT, senha TEXT, tipo_perfil TEXT
            );
            CREATE TABLE transacoes (
                id INTEGER PRIMARY KEY, valor REAL, tipo TEXT, categoria_id INTEGER,
                conta_id INTEGER, comentario TEXT, data TEXT, usuario_id INTEGER
            );
            INSERT INTO transacoes VALUES (3, 20, 'saida', NULL, NULL, '', '2026-09-11', 99);
            """
        )
        connection.commit()
        connection.close()

        source, _ = inspect_source(self.source)
        try:
            problems = validate_source_integrity(source)
            self.assertEqual(len(problems), 1)
            self.assertIn("transacoes.id=3", problems[0])
            self.assertIn("usuarios.id", problems[0])
        finally:
            source.close()

    def test_flag_ignora_somente_os_tres_orfaos_conhecidos(self):
        connection = sqlite3.connect(self.source)
        connection.executescript(
            """
            CREATE TABLE usuarios (
                id INTEGER PRIMARY KEY, usuario TEXT, email TEXT, senha TEXT, tipo_perfil TEXT
            );
            CREATE TABLE transacoes (
                id INTEGER PRIMARY KEY, valor REAL, tipo TEXT, categoria_id INTEGER,
                conta_id INTEGER, comentario TEXT, data TEXT, usuario_id INTEGER
            );
            CREATE TABLE vendas (
                id INTEGER PRIMARY KEY, cliente TEXT, tipo TEXT, valor_total REAL,
                comentario TEXT, data TEXT, usuario_id INTEGER
            );
            INSERT INTO transacoes VALUES (1, 100, 'entrada', NULL, NULL, '', '2026-05-06', 1);
            INSERT INTO transacoes VALUES (2, 100, 'entrada', NULL, NULL, '', '2026-05-10', 2);
            INSERT INTO vendas VALUES (2, 'Rodrigo', 'Venda', 1000, '', '2026-05-07', 1);
            """
        )
        connection.commit()
        connection.close()

        source, _ = inspect_source(self.source)
        try:
            with self.assertRaisesRegex(RuntimeError, "--skip-known-orphans"):
                resolve_known_orphans(source, skip_known_orphans=False)
            self.assertEqual(
                resolve_known_orphans(source, skip_known_orphans=True),
                {("transacoes", 1), ("transacoes", 2), ("vendas", 2)},
            )
        finally:
            source.close()

    def test_flag_recusa_orfao_novo(self):
        connection = sqlite3.connect(self.source)
        connection.executescript(
            """
            CREATE TABLE usuarios (
                id INTEGER PRIMARY KEY, usuario TEXT, email TEXT, senha TEXT, tipo_perfil TEXT
            );
            CREATE TABLE transacoes (
                id INTEGER PRIMARY KEY, valor REAL, tipo TEXT, categoria_id INTEGER,
                conta_id INTEGER, comentario TEXT, data TEXT, usuario_id INTEGER
            );
            INSERT INTO transacoes VALUES (1, 999, 'entrada', NULL, NULL, '', '2026-05-06', 1);
            INSERT INTO transacoes VALUES (9, 20, 'saida', NULL, NULL, '', '2026-09-11', 99);
            """
        )
        connection.commit()
        connection.close()

        source, _ = inspect_source(self.source)
        try:
            with self.assertRaisesRegex(RuntimeError, "orfaos nao autorizados"):
                resolve_known_orphans(source, skip_known_orphans=True)
        finally:
            source.close()

    def test_flag_recusa_registro_conhecido_alterado(self):
        connection = sqlite3.connect(self.source)
        connection.executescript(
            """
            CREATE TABLE usuarios (
                id INTEGER PRIMARY KEY, usuario TEXT, email TEXT, senha TEXT, tipo_perfil TEXT
            );
            CREATE TABLE transacoes (
                id INTEGER PRIMARY KEY, valor REAL, tipo TEXT, categoria_id INTEGER,
                conta_id INTEGER, comentario TEXT, data TEXT, usuario_id INTEGER
            );
            INSERT INTO transacoes VALUES (1, 999, 'entrada', NULL, NULL, '', '2026-05-06', 1);
            """
        )
        connection.commit()
        connection.close()

        source, _ = inspect_source(self.source)
        try:
            with self.assertRaisesRegex(RuntimeError, "registro transacoes.id=1 mudou"):
                resolve_known_orphans(source, skip_known_orphans=True)
        finally:
            source.close()


if __name__ == "__main__":
    unittest.main()
