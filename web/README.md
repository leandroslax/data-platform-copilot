# Frontend Demo

O frontend demo em [web/](/Users/leandrosantos/Downloads/data-platform-copilot/web/) usa React + Vite para consumir a API do copilot.

## O que ele mostra hoje

- lista de datasets vindos da API
- detalhe de dataset com colunas reais
- painel de jobs
- chat com perguntas sobre datasets, jobs e Novadrive
- busca semântica no catálogo persistido de metadados

## Configuração

Variáveis suportadas no build:

- `VITE_API_BASE_URL`: URL base da API, incluindo `/api/v1`
- `VITE_BASE_PATH`: base path do Vite para publicação estática

Exemplo local:

```bash
cd web
npm install
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1 npm run dev
```

## Publicação

O repositório agora inclui workflow de GitHub Pages em:

- [.github/workflows/deploy-frontend.yml](/Users/leandrosantos/Downloads/data-platform-copilot/.github/workflows/deploy-frontend.yml)

No build automático de Pages, o frontend usa:

- `VITE_BASE_PATH=/data-platform-copilot/`
- `VITE_API_BASE_URL=https://data-platform-copilot-api-914371024790.us-central1.run.app/api/v1`
