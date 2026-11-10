# Segurança — stack python

Checklists por camada que a skill `cyber-security` aplica quando o projeto declara a stack `python`. Mesma evidência (`arquivo:linha`) e mesma severidade da skill.

## API
Entrada validada por modelo pydantic com campos extras proibidos (`extra="forbid"`); limite de tamanho do corpo e tempo máximo por requisição; erros sem traceback na resposta (`debug` desligado fora do ambiente local); autorização por rota e por recurso (OWASP API1/API5); CORS restrito; limite de taxa nas rotas públicas; webhook, quando houver, autenticado por segredo com `hmac.compare_digest` antes de processar o corpo; logs sem dado pessoal nem segredo.

## Código
Sem `eval`/`exec`, `pickle`/`marshal` de origem externa, `yaml.load` sem `SafeLoader`, `subprocess` com `shell=True` ou texto montado com entrada, `tempfile.mktemp`, `random` para segredo (use `secrets`), caminho de arquivo vindo do usuário sem normalizar e conferir a raiz, `assert` como controle de acesso (some com `-O`).

## Banco
Consultas parametrizadas ou pelo ORM (nada de f-string em SQL nem `text()` com entrada); papéis com privilégio mínimo; migrações revisadas; dados de teste sem dado real.

## Cadeia de suprimentos
Dependências declaradas no `pyproject.toml` com lockfile versionado e instalação com hash conferido; `pip-audit` (ou `osv-scanner` sobre o lockfile); licenças permissivas; atenção a pacote recém-publicado, com nome parecido com outro conhecido ou com um mantenedor só.

## SAST da stack
`bandit` e as regras do Semgrep para Python (quando a licença das regras permitir); ruff com as regras de segurança (`S`). Busca dirigida por: `subprocess`/`os.system` com entrada, `eval`/`exec`, `pickle`, `yaml.load`, SQL montado com texto, `requests` sem `timeout` e `verify=False`. Só ferramentas já instaladas; o CI do projeto as roda.
