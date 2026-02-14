# 🌐 LotoScope Web Application

## 📁 Estrutura do Projeto

```
web/
├── backend/                    # Backend Flask/FastAPI
│   ├── app.py                 # Aplicação principal
│   ├── routes/                # Rotas da API
│   ├── services/              # Serviços de negócio
│   └── utils/                 # Utilitários
├── frontend/                  # Frontend Web
│   ├── templates/             # Templates HTML
│   ├── static/                # Arquivos estáticos
│   │   ├── css/              # Estilos CSS
│   │   └── js/               # Scripts JavaScript
│   └── index.html            # Página principal
├── database/                  # Scripts de banco de dados
│   ├── procedures/           # Stored procedures
│   └── migrations/           # Migrações
├── shared/                   # Código compartilhado
│   ├── models/              # Modelos de dados
│   └── config/              # Configurações
└── README.md                # Este arquivo
```

## 🎯 Funcionalidades Principais

### ✅ **Gerador Interativo de Combinações**
- Grid interativo 1-25 para seleção de números
- Suporte a jogos de 15-20 números
- Seleção de 0-14 números fixos
- Cálculo dinâmico de probabilidades

### 📊 **Cálculos em Tempo Real**
- Probabilidade de acerto atualizada instantaneamente
- Total de combinações possíveis
- Impacto de cada número fixo

### 🎲 **Geração Inteligente**
- Integração com procedure SQL otimizada
- Filtros avançados (primos, fibonacci, etc.)
- Validação de seleções

## 🚀 Como Executar

### Backend:
```bash
cd backend
pip install -r requirements.txt
python app.py
```

### Frontend:
- Abrir `frontend/index.html` no navegador
- Ou servir via servidor web local

## 📋 APIs Disponíveis

- `GET /api/calculate-probability` - Calcula probabilidades
- `POST /api/generate-combinations` - Gera combinações
- `GET /api/base-stats` - Estatísticas da base
- `POST /api/validate-selection` - Valida seleção

## 🔧 Configuração

Ver arquivos em `shared/config/` para configurações de:
- Banco de dados
- Parâmetros da aplicação
- Filtros padrão

---
**Desenvolvido para LotoScope - Sistema Inteligente de Lotofácil**