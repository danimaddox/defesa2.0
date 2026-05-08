# API REST – Defesa Civil M'Boi Mirim

Documentação da integração da API REST ao projeto **defesa2.0**, desenvolvida para o Projeto Integrador UNIVESP.

---

## O que é e para que serve

Antes da API, o sistema só podia ser acessado por um navegador, por uma pessoa, em uma tela. Com a API REST, os dados das ocorrências ficam disponíveis em formato JSON — um formato universal que qualquer sistema consegue ler.

Na prática, isso permite:

- Um **aplicativo mobile** buscar as ocorrências e exibir no mapa
- Um **painel externo** (Power BI, Looker Studio, etc.) consumir as estatísticas automaticamente
- Outro **sistema da prefeitura** integrar com o nosso sem intervenção manual
- Um **frontend moderno** (React, Vue) consumir os dados sem depender dos templates Django

A API não substitui nada que já existe — ela é uma camada a mais em cima do mesmo banco de dados (Supabase) que o sistema já usava.

---

## O que foi adicionado ao projeto

```
defesa2.0/
├── api/                          ← pasta nova com toda a API
│   ├── __init__.py
│   ├── apps.py                   ← configuração do app Django
│   ├── models.py                 ← modelo Ocorrencia com validações
│   ├── serializers.py            ← converte objetos Django em JSON
│   ├── views.py                  ← lógica dos endpoints
│   └── urls.py                   ← rotas da API
├── defesacivil_sqlite/
│   ├── settings.py               ← MODIFICADO: adicionadas configs da API
│   └── urls.py                   ← MODIFICADO: adicionada rota /api/
└── requirements.txt              ← MODIFICADO: novas dependências
```

**Dependências novas adicionadas ao `requirements.txt`:**
- `djangorestframework` — framework que fornece toda a estrutura da API
- `django-filter` — permite filtrar resultados por parâmetros na URL
- `django-cors-headers` — permite que outros domínios acessem a API

---

## Como rodar localmente

> Siga os passos na ordem. Se o projeto já estava rodando antes, comece do passo 3.

**Passo 1 — Criar o ambiente virtual (só na primeira vez):**
```powershell
python -m venv .venv
```

**Passo 2 — Ativar o ambiente virtual:**
```powershell
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1

# Mac/Linux
source .venv/bin/activate
```

Quando ativado corretamente, o terminal mostra `(.venv)` no início da linha.

**Passo 3 — Instalar as dependências:**
```powershell
python -m pip install -r requirements.txt
```

**Passo 4 — Rodar as migrations** (cria as tabelas novas da API no banco):
```powershell
python manage.py migrate
```

**Passo 5 — Subir o servidor:**
```powershell
python manage.py runserver
```

**Passo 6 — Acessar no navegador:**
```
http://localhost:8000/api/ocorrencias/
```

O Django REST Framework já fornece uma interface visual (chamada Browsable API) onde dá para ver e testar os endpoints direto pelo navegador, sem precisar de nenhuma ferramenta extra.

---

## Como funciona no Render (produção)

O projeto já estava hospedado no Render em `https://defesa2-0.onrender.com`. Como a API usa o mesmo banco (Supabase) e as mesmas configurações, ela sobe automaticamente junto com o deploy normal.

**Para publicar as mudanças:**

1. Commitar todos os arquivos modificados/novos no Git
2. Fazer push para o GitHub
3. O Render detecta o push e faz o redeploy automaticamente
4. Após o deploy, a API estará disponível em:

```
https://defesa2-0.onrender.com/api/ocorrencias/
```

Não é necessário nenhuma configuração extra no Render — as variáveis de banco já estão no `settings.py` e as dependências novas estão no `requirements.txt`.

---

## Endpoints disponíveis

A URL base da API é `/api/`. Todos os endpoints retornam JSON.

### 1. Listar ocorrências
```
GET /api/ocorrencias/
```

Retorna todas as ocorrências paginadas (50 por página). Aceita diversos filtros pela URL.

**Filtros disponíveis:**

| Parâmetro        | Exemplo                           | O que faz                        |
|------------------|-----------------------------------|----------------------------------|
| `bairro`         | `?bairro=Jardim`                  | Busca parcial no nome do bairro  |
| `motivo`         | `?motivo=Alagamento`              | Filtra por motivo exato          |
| `area_risco`     | `?area_risco=3`                   | Filtra pelo nível exato (0 a 4)  |
| `area_risco_min` | `?area_risco_min=2`               | Nível de risco maior ou igual    |
| `distrito`       | `?distrito=Jd. Ângela`            | Filtra por distrito              |
| `data_inicio`    | `?data_inicio=2025-01-01`         | Ocorrências a partir desta data  |
| `data_fim`       | `?data_fim=2025-12-31`            | Ocorrências até esta data        |
| `search`         | `?search=Rua das Flores`          | Busca livre em endereço/bairro   |
| `ordering`       | `?ordering=-data`                 | Ordenação (- = decrescente)      |
| `page`           | `?page=2`                         | Navega entre páginas             |

**Exemplo de resposta:**
```json
{
  "count": 120,
  "next": "http://localhost:8000/api/ocorrencias/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "numero": 1042,
      "sigrc": 5678,
      "endereco": "Rua das Flores, 100",
      "bairro": "Jd. Ângela",
      "distrito": "Jd. Ângela",
      "area_risco": 3,
      "motivo": "Deslizamento",
      "data": "2025-03-15",
      "latitude": "-23.6812345",
      "longitude": "-46.7234567",
      "criado_em": "2025-03-15T14:30:00Z",
      "atualizado_em": "2025-03-15T14:30:00Z"
    }
  ]
}
```

---

### 2. Detalhe de uma ocorrência
```
GET /api/ocorrencias/{id}/
```

Retorna todos os dados de uma ocorrência específica pelo ID.

---

### 3. Dados para mapa
```
GET /api/ocorrencias/mapa/
```

Versão compacta da listagem — retorna só os campos necessários para plotar marcadores em um mapa. Aceita os mesmos filtros do endpoint principal.

**Exemplo de uso:**
```
GET /api/ocorrencias/mapa/?area_risco_min=3
```

**Resposta:**
```json
{
  "count": 12,
  "results": [
    {
      "id": 1,
      "numero": 1042,
      "bairro": "Jd. Ângela",
      "motivo": "Deslizamento",
      "area_risco": 3,
      "data": "2025-03-15",
      "latitude": "-23.6812345",
      "longitude": "-46.7234567"
    }
  ]
}
```

---

### 4. Estatísticas
```
GET /api/ocorrencias/estatisticas/
```

Retorna dados agregados e agrupados — útil para gráficos e painéis. Aceita filtros de data para recortes temporais.

**Exemplo de uso:**
```
GET /api/ocorrencias/estatisticas/?data_inicio=2025-01-01&data_fim=2025-12-31
```

**Resposta:**
```json
{
  "total_ocorrencias": 120,
  "por_motivo": [
    {"motivo": "Deslizamento", "total": 45},
    {"motivo": "Alagamento", "total": 30}
  ],
  "por_bairro": [
    {"bairro": "Jd. Ângela", "total": 70},
    {"bairro": "Jd. São Luis", "total": 50}
  ],
  "por_risco": [
    {"area_risco": 0, "total": 10},
    {"area_risco": 3, "total": 55},
    {"area_risco": 4, "total": 12}
  ],
  "por_mes": [
    {"mes": "2025-01", "total": 8},
    {"mes": "2025-02", "total": 22}
  ]
}
```

---

### 5. Criar, atualizar e remover ocorrências

Essas operações **exigem autenticação** via token (veja a seção abaixo).

```
POST   /api/ocorrencias/          → cria nova ocorrência
PUT    /api/ocorrencias/{id}/     → atualiza completamente
PATCH  /api/ocorrencias/{id}/     → atualiza só os campos enviados
DELETE /api/ocorrencias/{id}/     → remove
```

---

## Autenticação

Leituras (`GET`) são **públicas** — qualquer pessoa pode consultar sem precisar de login.

Escritas (`POST`, `PUT`, `PATCH`, `DELETE`) exigem um **token de acesso**.

**Como gerar um token para um usuário:**
```powershell
python manage.py drf_create_token nome_do_usuario
```

**Como usar o token nas requisições:**
```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4
```

---

## Como testar sem precisar de código

Com o servidor rodando (`python manage.py runserver`), acesse qualquer endpoint no navegador. O Django REST Framework mostra uma interface visual onde dá para ver os dados e até testar filtros direto na URL:

```
http://localhost:8000/api/ocorrencias/
http://localhost:8000/api/ocorrencias/mapa/
http://localhost:8000/api/ocorrencias/estatisticas/
http://localhost:8000/api/ocorrencias/?motivo=Alagamento
http://localhost:8000/api/ocorrencias/?area_risco_min=3&data_inicio=2025-01-01
```
