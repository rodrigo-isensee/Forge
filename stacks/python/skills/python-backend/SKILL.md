---
name: python-backend
description: Convenções de back-end Python do projeto - estrutura em camadas, validação com pydantic, tratamento de erros, contrato de API, testes com pytest e segurança. Use ao criar ou alterar código do servidor em Python.
---

# Back-end Python

## Stack padrão (quando o projeto ainda não definir outra)
- Python 3.12+, dependências no `pyproject.toml`, travadas num lockfile versionado
- FastAPI (ou o framework que o projeto já usa) com pydantic para validação
- SQLAlchemy 2 com Alembic para migrações
- pytest para testes; ruff para lint e formatação; mypy estrito no código novo

## Estrutura
```
src/<pacote>/
  <recurso>/
    rotas.py         # rotas e modelos de entrada/saída
    servico.py       # regra de negócio (sem HTTP)
    repositorio.py   # acesso a dados
    esquemas.py      # modelos pydantic
  comum/ (erros, config, log)
  app.py
tests/<recurso>/test_*.py
```

## Convenções de API
- REST, recursos no plural, kebab-case na rota (`/api/v1/order-items/{id}`), JSON em camelCase pelo alias do modelo.
- Erro sempre como `{"error": {"code": "...", "message": "...", "details": []}}`; 500 sem detalhe interno na resposta.
- Paginação `?page=1&pageSize=20` → `{"data": [...], "meta": {"page", "pageSize", "total"}}`.

## Erros e configuração
- `AppError(code, message, status)` lançada pelo serviço; um handler global converte e loga os 5xx.
- Configuração por variáveis de ambiente validadas na partida (`pydantic-settings`); `.env.example` atualizado e `.env` fora do git.

## Testes
- Serviço com repositório falso; rota com o cliente de teste do framework, cobrindo sucesso, validação e autorização.
- Banco de teste descartável por sessão; nada de dado real.
- Vermelho antes do verde: o teste novo falha sem o código de produção.

## Segurança
- Senha com argon2 (`argon2-cffi`); comparação de segredo com `hmac.compare_digest`.
- Nada de `eval`, `exec`, `pickle` ou `yaml.load` sem `SafeLoader` com entrada externa; `subprocess` só com lista e sem `shell=True`.
- Log estruturado sem dado sensível; CORS restrito às origens conhecidas; limite de taxa na autenticação.
