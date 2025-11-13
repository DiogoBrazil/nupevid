# NUPEVID - Sistema de Atendimentos

**Núcleo de Prevenção e Enfrentamento à Violência Doméstica e Familiar contra a Mulher**  
**7º Batalhão de Polícia Militar de Rondônia**

Sistema web para registro de atendimentos e acompanhamento de medidas protetivas da Patrulha Maria da Penha.

---

## 🎯 Sobre o Sistema

O NUPEVID é um sistema desenvolvido para digitalizar e otimizar o processo de registro e acompanhamento de atendimentos às vítimas de violência doméstica e familiar protegidas por medidas protetivas de urgência.

### Objetivos

- ✅ Eliminar o processo manual de registro em papel
- ✅ Reduzir retrabalho e erros de transcrição
- ✅ Permitir cadastro imediato durante visitas domiciliares
- ✅ Coletar dados geoespaciais para análises futuras
- ✅ Facilitar consultas e relatórios sobre atendimentos

---

## 🚀 Funcionalidades

- ✅ **Autenticação segura** para policiais militares
- ✅ **Cadastro de vítimas** com endereço completo
- ✅ **Registro de atendimentos/visitas** domiciliares
- ✅ **Integração com API de CEP** (BrasilAPI)
- ✅ **Captura de geolocalização** com alta precisão
- ✅ **Visualização no Google Maps**
- ✅ **Listagem e consulta** de atendimentos
- ✅ **Validações rigorosas** de dados

---

## 🛠️ Tecnologias

- **Backend**: Python 3.10+ com FastHTML
- **ORM**: SQLAlchemy 2.0
- **Migrações**: Alembic
- **Banco de Dados**: PostgreSQL 14+
- **Gerenciador de Pacotes**: uv (ultra-rápido)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **APIs Externas**: 
  - BrasilAPI (consulta de CEP)
  - Google Maps (visualização de coordenadas)
  - Geolocation API (captura de localização)

---

## 📋 Pré-requisitos

- Python 3.10 ou superior
- PostgreSQL 14 ou superior
- [uv](https://github.com/astral-sh/uv) - gerenciador de pacotes Python

### Instalando o uv
```bash
# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Via pip (alternativa)
pip install uv

# Via Homebrew (macOS)
brew install uv
```

---

## 🚀 Instalação

### 1. Clone o repositório
```bash
git clone <url-do-repositorio>
cd nupevid
```

### 2. Crie o ambiente virtual e instale dependências

Com o **uv**, isso é feito em um único comando super rápido:
```bash
# Criar ambiente virtual e instalar todas as dependências
uv venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate  # Windows

# Instalar dependências do projeto
uv pip install -e .

# Ou instalar diretamente do pyproject.toml
uv pip sync
```

### 3. Configure o banco de dados PostgreSQL
```bash
# Conecte ao PostgreSQL
psql -U postgres

# Crie o banco de dados
CREATE DATABASE nupevid;

# Saia do psql
\q
```

### 4. Configure as variáveis de ambiente

Copie o arquivo `.env.example` para `.env`:
```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas configurações:
```env
DB_NAME=nupevid
DB_USER=postgres
DB_PASSWORD=sua_senha_aqui
SECRET_KEY=sua-chave-secreta-mude-em-producao
```

### 5. Execute as migrações do Alembic
```bash
# Aplicar todas as migrações
alembic upgrade head

# Verificar migração atual
alembic current
```

### 6. Execute a aplicação
```bash
python app/main.py
```

### 7. Acesse o sistema
```
http://localhost:8000
```

---

## 📝 Comandos Úteis

### UV - Gerenciamento de Dependências
```bash
# Adicionar uma nova dependência
uv install nome-do-pacote

# Adicionar dependência de desenvolvimento
uv install --dev nome-do-pacote
```

### Alembic (Migrações)
```bash
# Criar nova migração após alterar models
alembic revision --autogenerate -m "descrição da alteração"

# Aplicar migrações pendentes
alembic upgrade head

# Reverter última migração
alembic downgrade -1

# Ver histórico de migrações
alembic history

# Ver SQL que será executado (sem aplicar)
alembic upgrade head --sql
```

### Desenvolvimento
```bash
# Executar em modo debug
python app/main.py

---

## 🔧 Desenvolvimento

### Adicionando novas dependências
```bash
# Adicionar ao projeto
uv install nome-do-pacote

# Atualizar pyproject.toml manualmente ou usar:
# Edite pyproject.toml e adicione em [project.dependencies]
# Depois execute:
uv sync
```

---

## 👤 Primeiro Acesso

1. Acesse `http://localhost:8000`
2. Clique em "Criar conta"
3. Preencha:
   - Nome completo do policial
   - Matrícula (9 dígitos, iniciando com 1000)
   - E-mail institucional
   - Senha (mínimo 6 caracteres)
   - Posto/Graduação
4. Faça login com as credenciais criadas

---

## 🔒 Segurança

- ✅ Senhas armazenadas com **bcrypt hash**
- ✅ Sessões assinadas criptograficamente
- ✅ Validação de matrícula (padrão PM-RO)
- ✅ Validação de e-mail
- ✅ Proteção de rotas com autenticação

---

## 📊 Estrutura do Banco de Dados

### Tabela `users`
Policiais que utilizam o sistema

### Tabela `victims`
Vítimas atendidas pela patrulha

### Tabela `attendances`
Registros de visitas/atendimentos realizados

---

## 🚀 Deploy em Produção

### Preparação
```bash
# 1. Garantir que está usando ambiente virtual
source .venv/bin/activate

# 2. Sincronizar dependências
uv sync

# 3. Aplicar migrações
alembic upgrade head

# 4. Configurar variáveis de ambiente de produção
# Edite .env com configurações de produção

# 5. Executar
python app/main.py
```

## 📄 Licença

Sistema desenvolvido para uso interno do **7º Batalhão de Polícia Militar de Rondônia**.