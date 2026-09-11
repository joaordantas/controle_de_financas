# Identidade externa da Nivra

Este documento registra o estado dos nomes públicos e os cuidados necessários para manter GitHub, Vercel e Neon alinhados sem alterar credenciais ou nomes técnicos internos.

## Estado verificado

| Serviço | Nome anterior | Estado atual |
| --- | --- | --- |
| GitHub | `joaordantas/controle_de_financas` | `joaordantas/Nivra` — concluído |
| Vercel | `controle-de-financas` | projeto `nivra` — concluído |
| Neon | `nivra-db` | manter `nivra-db` |

O domínio de produção confirmado na Vercel é `nivra-finance.vercel.app`.

## Remote do GitHub

Em cada cópia local existente, use o endereço canônico confirmado pelo GitHub:

```bash
git remote set-url origin https://github.com/joaordantas/Nivra.git
git remote -v
```

Confirme que fetch e push apontam para `https://github.com/joaordantas/Nivra.git`. Os links absolutos do README e do changelog também devem abrir o repositório renomeado.

## Vercel

O projeto `nivra` já está conectado a `joaordantas/Nivra` e à branch `main`. Se o domínio precisar ser substituído no futuro:

1. abra o projeto `nivra` na Vercel;
2. acesse **Settings > Domains**;
3. adicione ou selecione um domínio que esteja realmente disponível;
4. aguarde a configuração ficar válida;
5. teste a interface, `/api/health` e `/docs` nesse endereço;
6. somente então substitua `nivra-finance.vercel.app` no README e nos demais materiais públicos.

Não presuma que `nivra.vercel.app` estará disponível.

## Configurações que permanecem iguais

- o banco Neon continua como `nivra-db`;
- `DATABASE_URL`, `DATABASE_URL_UNPOOLED` e `APP_ENV` mantêm os mesmos nomes;
- nenhuma credencial ou connection string deve ser alterada ou copiada para o frontend;
- o nome da pasta local, dos pacotes, dos imports, das chaves de armazenamento e das migrations pode permanecer técnico.

## Verificação final

- `git remote -v` mostra o endereço canônico do repositório Nivra;
- a Vercel continua conectada a `joaordantas/Nivra` e à branch `main`;
- `nivra-finance.vercel.app` responde como domínio de produção;
- as variáveis de ambiente continuam presentes nos ambientes usados pelo projeto;
- um deploy novo abre a interface Nivra e conecta à API e ao Neon normalmente;
- os dados persistem após o deploy.
