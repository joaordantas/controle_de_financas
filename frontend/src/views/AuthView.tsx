import { useState } from "react";
import type { FormEvent } from "react";

import { api } from "../api";
import type { User } from "../types";

interface AuthViewProps {
  onLogin: (user: User) => void;
}

export function AuthView({ onLogin }: AuthViewProps) {
  const [tab, setTab] = useState<"login" | "cadastro">("login");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const [loginEmail, setLoginEmail] = useState("");
  const [loginSenha, setLoginSenha] = useState("");

  const [usuario, setUsuario] = useState("");
  const [cadastroEmail, setCadastroEmail] = useState("");
  const [cadastroSenha, setCadastroSenha] = useState("");
  const [tipoPerfil, setTipoPerfil] = useState("Apenas Financeiro");

  async function handleLogin(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setMessage("");
    setError("");
    try {
      const user = await api.login(loginEmail, loginSenha);
      onLogin(user);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Nao foi possivel entrar.");
    } finally {
      setLoading(false);
    }
  }

  async function handleRegister(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setMessage("");
    setError("");
    try {
      const user = await api.register({
        usuario,
        email: cadastroEmail,
        senha: cadastroSenha,
        tipo_perfil: tipoPerfil,
      });
      setMessage("Conta criada com sucesso. Voce ja entrou automaticamente.");
      onLogin(user);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Nao foi possivel cadastrar.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="auth-shell">
      <section className="hero-panel">
        <p className="eyebrow">Migracao gradual</p>
        <h1>Seu projeto agora tem uma base React + FastAPI para evoluir.</h1>
        <p>
          Esta tela foi pensada para ser simples de entender e servir como estudo de
          componentes, formularios e consumo de API.
        </p>
      </section>

      <section className="auth-card">
        <div className="tabs">
          <button className={tab === "login" ? "tab active" : "tab"} onClick={() => setTab("login")}>
            Entrar
          </button>
          <button
            className={tab === "cadastro" ? "tab active" : "tab"}
            onClick={() => setTab("cadastro")}
          >
            Criar conta
          </button>
        </div>

        {error ? <p className="feedback error">{error}</p> : null}
        {message ? <p className="feedback success">{message}</p> : null}

        {tab === "login" ? (
          <form className="form-grid" onSubmit={handleLogin}>
            <label>
              Email
              <input value={loginEmail} onChange={(event) => setLoginEmail(event.target.value)} />
            </label>
            <label>
              Senha
              <input
                type="password"
                value={loginSenha}
                onChange={(event) => setLoginSenha(event.target.value)}
              />
            </label>
            <button className="primary-button" disabled={loading} type="submit">
              {loading ? "Entrando..." : "Entrar"}
            </button>
          </form>
        ) : (
          <form className="form-grid" onSubmit={handleRegister}>
            <label>
              Nome de usuario
              <input value={usuario} onChange={(event) => setUsuario(event.target.value)} />
            </label>
            <label>
              Email
              <input
                value={cadastroEmail}
                onChange={(event) => setCadastroEmail(event.target.value)}
              />
            </label>
            <label>
              Senha
              <input
                type="password"
                value={cadastroSenha}
                onChange={(event) => setCadastroSenha(event.target.value)}
              />
            </label>
            <label>
              Perfil
              <select value={tipoPerfil} onChange={(event) => setTipoPerfil(event.target.value)}>
                <option>Apenas Financeiro</option>
                <option>Autonomo (Servicos)</option>
                <option>Motorista / Entregador</option>
              </select>
            </label>
            <button className="primary-button" disabled={loading} type="submit">
              {loading ? "Criando..." : "Criar conta"}
            </button>
          </form>
        )}
      </section>
    </main>
  );
}
