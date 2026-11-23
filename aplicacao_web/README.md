# Aplicação web — TI Contagem (CNAE 62)

Dashboard SvelteKit que lê o MySQL gerado pelo pipeline e exibe mapa (Leaflet), KPIs e lista de estabelecimentos.

## Pré-requisitos

1. Docker Desktop ligado
2. Banco criado e schema importado (na raiz do TCC):

```powershell
docker compose up -d
# aguardar healthy
Get-Content ..\pipeline_para_obtencao_de_dados\sql_gerado\schema_aplicacao.sql -Raw -Encoding UTF8 |
  docker exec -i tcc-mysql mysql -utcc -ptcc_senha --default-character-set=utf8mb4 tcc_contagem_ti
```

## Configuração

Copie `.env.example` para `.env` (já há um `.env` local com os valores do `docker-compose.yml`).

| Variável | Padrão | Uso |
|---|---|---|
| `MYSQL_HOST` | `127.0.0.1` | Host |
| `MYSQL_PORT` | `3307` | Porta publicada pelo Docker |
| `MYSQL_USER` / `MYSQL_PASSWORD` | `tcc` / `tcc_senha` | Credenciais |
| `MYSQL_DATABASE` | `tcc_contagem_ti` | Banco |

## Desenvolvimento

```powershell
npm install
npm run dev
```

Abra http://127.0.0.1:5173/

## Endpoints

- `GET /api/resumo` — KPIs e agregações
- `GET /api/estabelecimentos?q=&cnae=&porte=&mei=` — lista filtrada
