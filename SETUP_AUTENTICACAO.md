# Setup inicial de autenticacao

Este guia configura o primeiro ambiente autenticado do Prospector. O Clerk e
um servico externo de identidade; o Neon e o banco; este repositorio contem a
aplicacao FastAPI que conecta os dois.

## O que e criado em cada lugar

| Local | O que fica la |
|---|---|
| Clerk Dashboard | Usuarios, credenciais, verificacao de e-mail, convites e sessoes |
| Neon | Tabela `app_users`, papel (`admin`/`member`) e status de acesso |
| Este projeto | Variaveis de ambiente, validacao do JWT, cookie local, telas e endpoints |
| Vercel | Variaveis de producao e a URL publica que recebe o webhook |

Voce nao cria usuarios diretamente no banco. A conta inicial e criada no
Clerk e sincronizada para `app_users` quando o webhook ou o primeiro login for
processado.

## Preciso criar um projeto no Clerk?

Crie uma aplicacao/instancia dedicada para este sistema no
[Clerk Dashboard](https://dashboard.clerk.com). Nao e necessario criar uma
aplicacao nova a cada deploy: use a instancia de desenvolvimento para sua
maquina e a instancia de producao para a Vercel, com suas respectivas chaves.

Se voce ja possui uma aplicacao Clerk para outro produto, prefira uma nova
aplicacao para evitar misturar usuarios, convites e configuracoes. O Clerk nao
substitui o banco Neon e nao precisa ser instalado dentro deste repositorio.

## 1. Criar e configurar a aplicacao Clerk

No Dashboard Clerk:

1. Crie a aplicacao `Prospector` ou abra a aplicacao dedicada ja existente.
2. Em **User & Authentication**, habilite entrada por e-mail e senha.
3. Habilite a verificacao de e-mail.
4. Em **Access mode**, selecione **Invite-only**. Esse e o controle que
   impede cadastros sem convite.
5. Nesta tela de e-mail, mantenha **Sign-up with email**, **Require email
   address** e **Verify at sign-up** habilitados. A verificacao por codigo de
   e-mail pode ficar habilitada; ela e usada durante a ativacao do convite.
6. Mantenha **Sign-in with email** habilitado e habilite a autenticacao por
   senha na aba **Password**. Para exigir somente e-mail e senha, deixe
   **Email verification code** e **Email verification link** desabilitados na
   secao de sign-in.
7. Deixe Phone, Username, Passkeys e provedores sociais desabilitados nesta
   primeira versao.
8. Copie as chaves e URLs da instancia para os nomes abaixo:
   - Publishable key: `CLERK_PUBLISHABLE_KEY`
   - Frontend API URL: `CLERK_FRONTEND_API_URL`
   - Secret key: `CLERK_SECRET_KEY`
   - JWT public key: `CLERK_JWT_KEY`

Use as chaves de desenvolvimento localmente. Nunca coloque `CLERK_SECRET_KEY`
ou `CLERK_WEBHOOK_SIGNING_SECRET` em HTML, JavaScript, Git ou no
`CLERK_PUBLISHABLE_KEY`.

## 2. Criar o administrador inicial

Ainda no Clerk:

1. Abra **Users** e crie manualmente sua conta com o e-mail de administrador.
2. Conclua a verificacao de e-mail e defina a senha.
3. Copie o `User ID`, no formato `user_...`.
4. Use esse valor em `CLERK_ADMIN_USER_ID`.

O ID e a unica fonte de bootstrap do papel administrativo. Nao existe um
formulario publico de cadastro de administrador.

## 3. Preparar o ambiente local

Na raiz deste projeto:

```bash
cp .env.example .env
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Preencha o `.env` com o Neon e as chaves da instancia de desenvolvimento:

```env
DATABASE_URL=postgresql://...neon.tech/...?sslmode=require
GOOGLE_MAPS_API_KEY=...
APP_ENV=development
APP_URL=http://localhost:8000
SESSION_SECRET_KEY=uma-chave-aleatoria-longa
CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_FRONTEND_API_URL=https://sua-instancia.clerk.accounts.dev
CLERK_SECRET_KEY=sk_test_...
CLERK_JWT_KEY="-----BEGIN PUBLIC KEY-----
...
-----END PUBLIC KEY-----"
CLERK_ADMIN_USER_ID=user_...
CLERK_WEBHOOK_SIGNING_SECRET=whsec_...
```

Mantenha as aspas da chave PEM exatamente como no exemplo. Sem elas, o
`python-dotenv` pode ler somente o cabecalho da chave e o login retornara
`401 Token de sessao invalido`.

Gere o segredo da sessao, em vez de reutilizar uma senha:

```bash
openssl rand -hex 32
```

## 4. Criar a estrutura no Neon

Com o `DATABASE_URL` apontando para o banco correto, execute a migracao uma
vez:

```bash
alembic upgrade head
```

A revisao `20260821_00` preserva `businesses` quando ela ja existe e a cria
somente se o Neon estiver vazio. A revisao `20260821_01` cria `app_users` e a
`20260821_02` garante as colunas de avaliacao de `businesses`; nenhuma delas
apaga os leads existentes.

Depois, inicie a aplicacao:

```bash
uvicorn main:app --reload
```

Abra <http://localhost:8000>. Uma pessoa sem sessao sera enviada para
`/login`. Depois do login, o navegador troca o JWT do Clerk por um cookie local
e o administrador deve conseguir abrir `/admin/users`.

## 5. Configurar o webhook

O webhook precisa de uma URL publica. Por isso, ha duas opcoes:

- **Producao:** configure depois que a aplicacao estiver publicada, usando
  `https://seu-dominio.com/webhooks/clerk`.
- **Desenvolvimento:** use um tunel HTTPS, como ngrok, apontando para
  `http://localhost:8000`, se quiser testar sincronizacao local.

No Clerk, crie um webhook para essa URL e assine somente:

- `user.created`
- `user.updated`
- `user.deleted`

Copie o signing secret gerado para `CLERK_WEBHOOK_SIGNING_SECRET`. O endpoint
verifica a assinatura Svix antes de alterar o Neon e aceita eventos repetidos
com seguranca.

## 6. Publicar na Vercel

1. Configure o projeto na Vercel e defina todas as variaveis de producao em
   **Settings -> Environment Variables**.
2. Use as chaves da instancia de producao do Clerk.
3. Defina `APP_URL` como a URL final, sem barra no final, por exemplo
   `https://prospector.exemplo.com`.
4. Aponte `CLERK_FRONTEND_API_URL` para a instancia de producao.
5. Inclua essa URL nas origens autorizadas do Clerk.
6. Execute `alembic upgrade head` usando o `DATABASE_URL` de producao antes
   do primeiro acesso autenticado.
7. Atualize o webhook para
   `https://prospector.exemplo.com/webhooks/clerk` e salve o novo segredo nas
   variaveis da Vercel.
8. Faca o redeploy.

Nao reutilize o `CLERK_WEBHOOK_SIGNING_SECRET` de desenvolvimento no ambiente
de producao se o Clerk gerar um segredo diferente para o endpoint de producao.

## 7. Convidar a equipe

Depois de entrar como administrador:

1. Abra `/admin/users`.
2. Informe o e-mail da pessoa e envie o convite.
3. O Clerk enviara o link para definicao de senha e verificacao.
4. O novo perfil aparecera como `member` apos o evento do Clerk ou no primeiro
   login.

Membros podem buscar, consultar historico e exportar leads. Somente o
administrador pode excluir leads, convidar pessoas ou alterar status de acesso.

## Diagnostico rapido

| Sintoma | Verificacao |
|---|---|
| A aplicacao nao inicia | `SESSION_SECRET_KEY` esta preenchida? |
| Login mostra configuracao ausente | Confira `CLERK_PUBLISHABLE_KEY` e `CLERK_FRONTEND_API_URL` |
| JWT rejeitado | `APP_URL`, `CLERK_JWT_KEY` e a origem autorizada precisam corresponder ao ambiente |
| Usuario autenticado sem acesso | Rode `alembic upgrade head` e confira `CLERK_ADMIN_USER_ID` |
| Usuarios nao sincronizam | Verifique a URL publica, os eventos e o signing secret do webhook |
| Convite nao aparece | Confira a chave secreta de Backend API e o status do convite no Clerk |
