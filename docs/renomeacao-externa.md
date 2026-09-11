# Renomeação externa para Nivra

Este guia prepara a mudança dos nomes públicos dos serviços sem alterar credenciais, banco de dados ou nomes técnicos internos. Execute cada parte somente no painel correspondente.

## Estado desejado

| Serviço | Nome atual | Nome desejado |
| --- | --- | --- |
| GitHub | `joaordantas/controle_de_financas` | `joaordantas/nivra` |
| Vercel | `controle-de-financas` | `nivra` |
| Neon | `nivra-db` | manter `nivra-db` |

## GitHub

1. Confirme que todas as mudanças desejadas já foram enviadas para a branch `main`.
2. Abra o repositório no GitHub e acesse **Settings > General**.
3. Na seção do nome do repositório, altere `controle_de_financas` para `nivra`.
4. Confirme a renomeação no GitHub.
5. Somente depois disso, atualize o remote no computador:

```bash
git remote set-url origin https://github.com/joaordantas/nivra.git
git remote -v
```

6. Confirme que fetch e push apontam para `https://github.com/joaordantas/nivra.git`.
7. Confirme que os links absolutos do README e do changelog abrem o repositório renomeado.
8. Verifique a integração Git da Vercel e confirme que ela continua vinculada ao repositório renomeado e à branch `main`.

O GitHub normalmente mantém redirecionamentos para o nome anterior, mas os links do projeto devem ser atualizados depois que o novo endereço estiver ativo.

## Vercel

1. Abra o projeto atual na Vercel.
2. Acesse **Settings > General** e altere o nome do projeto para `nivra`.
3. Confirme a alteração e aguarde a atualização do projeto.
4. Abra **Settings > Domains** e anote o domínio de produção que a Vercel realmente disponibilizou.
5. Não presuma que `nivra.vercel.app` estará disponível.
6. Após confirmar o endereço real, adicione-o ao README e a qualquer documentação pública pertinente.
7. Faça um novo deploy da branch `main` e valide a página inicial, `/api/health` e `/docs`.

## Configurações que permanecem iguais

- o banco Neon continua como `nivra-db`;
- `DATABASE_URL`, `DATABASE_URL_UNPOOLED` e `APP_ENV` mantêm os mesmos nomes;
- nenhuma credencial ou connection string deve ser alterada ou copiada para o frontend;
- o nome da pasta local, dos pacotes, dos imports e das migrations pode permanecer técnico.

## Verificação final

- o novo endereço do GitHub abre o repositório correto;
- `git remote -v` mostra o novo endereço para fetch e push;
- a Vercel continua conectada ao GitHub e à branch `main`;
- o domínio real da Vercel foi confirmado antes de atualizar a documentação;
- as variáveis de ambiente continuam presentes em Production, Preview e Development conforme a configuração usada;
- um deploy novo abre a interface Nivra e conecta à API e ao Neon normalmente;
- os dados persistem após o deploy.
