# Catálogo Ousamais

## 🚀 Stack

- **Sync**: Python + GitHub Actions (cron diário)
- **Banco**: Supabase (PostgreSQL)
- **Frontend**: HTML estático na Vercel

---

## ✅ Passo a Passo

### 1. Criar conta no Supabase

1. Acesse https://supabase.com e clique em **Start your project**
2. Faça login com GitHub
3. Crie um **Organization** (pode ser pessoal)
4. Crie um **New project**
   - Name: `catalogo-ousamais`
   - Database Password: anote em algum lugar seguro
   - Region: **South America (São Paulo)** 
   - Pricing Plan: **Free**

### 2. Configurar o banco

1. No painel do Supabase, vá em **SQL Editor**
2. Clique em **New query**
3. Cole o conteúdo do arquivo `supabase/schema.sql`
4. Clique em **Run**

### 3. Pegar as credenciais

1. No painel do Supabase, vá em **Settings** > **API**
2. Anote:
   - **Project URL** (URL)
   - **anon public** key (Key)

### 4. Criar repositório no GitHub

1. Acesse https://github.com
2. Clique em **+** > **New repository**
3. Nome: `catalogo-ousamais`
4. Marque **Public** ou **Private**
5. Não inicie com README
6. Clique em **Create repository**

No terminal:

```bash
cd "C:\Users\Usuario\Documents\Script Ofertas"
git init
git add .
git commit -m "primeiro commit"
git remote add origin https://github.com/SEU_USUARIO/catalogo-ousamais.git
git branch -M main
git push -u origin main
```

### 5. Configurar Secrets no GitHub

1. No repositório do GitHub, vá em **Settings** > **Secrets and variables** > **Actions**
2. Clique em **New repository secret**
3. Adicione:

| Nome | Valor |
|------|-------|
| `SUPABASE_URL` | URL do projeto (ex: https://xxxxx.supabase.co) |
| `SUPABASE_KEY` | anon public key |
| `MARGEM_LUCRO` | 1.30 |

### 6. Testar GitHub Action

1. No GitHub, vá em **Actions**
2. Clique no workflow **Sync Catálogo**
3. Clique em **Run workflow** (botão azul)
4. Aguarde a execução

### 7. Verificar no Supabase

1. No Supabase, vá em **Table Editor**
2. A tabela `produtos` deve aparecer com os dados

### 8. Deploy na Vercel

1. Acesse https://vercel.com e faça login com GitHub
2. Clique em **Add New** > **Project**
3. Selecione o repositório `catalogo-ousamais`
4. Em **Environment Variables**, adicione:

| Nome | Valor |
|------|-------|
| `SUPABASE_URL` | URL do projeto |
| `SUPABASE_KEY` | anon public key |

5. Clique em **Deploy**

### 9. Pronto!

Seu catálogo estará disponível em: `https://catalogo-ousamais.vercel.app`

O sync roda automático todo dia às 06h e 18h (horário de Brasília).

---

## ⚙️ Comandos úteis

### Rodar sync manual (local)

```bash
set SUPABASE_URL=sua_url
set SUPABASE_KEY=sua_key
python sync_catalogo.py
```

### Rodar ofertas no Telegram

```bash
python ofertas_bot_v2.py
```
