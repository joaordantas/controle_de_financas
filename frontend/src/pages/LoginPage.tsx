import { useAuth } from "../app/providers";
import { AuthView } from "../views/AuthView";

export function LoginPage() {
  const { login } = useAuth();
  return <AuthView onLogin={login} />;
}
