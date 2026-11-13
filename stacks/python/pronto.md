# "Pronto" e convenções verificáveis — stack python

O `forge-init` usa o comando abaixo como padrão do "pronto" do projeto (`--pronto` sobrescreve); o `forge adotar` prefere o que o projeto já tem.

Comando sugerido: `ruff check . && ruff format --check . && mypy src && python -m pytest`

Detecção: `pyproject.toml`, `requirements.txt`, `setup.py`, `setup.cfg`

Pronto existente: `tox.ini` com `[tox]` → `tox`; `pyproject.toml` com `[tool.pytest` → `python -m pytest`; `pytest.ini` com `[pytest]` → `python -m pytest`

Ele precisa rodar, e falhar se algo falhar: lint e formatação (ruff) · tipos (mypy) · testes (pytest). Reporte o resultado real.

## Código
- Dicas de tipo em toda função pública; `mypy --strict` no código novo; `# type: ignore` só com o código do erro e o motivo.
- Sem `print` esquecido (use o log); lint e formatação automáticos, e o CI falha se não passarem.
- Ambiente isolado por projeto (venv); nada instalado no Python do sistema.

## Pirâmide de testes
| Nível | Ferramenta | Quem escreve | Onde |
|---|---|---|---|
| Unitário | pytest | `python-backend` | `tests/` |
| Integração de API | pytest + cliente de teste do framework | `python-backend` | `tests/` |
| E2E | a ferramenta da ADR do projeto | `qa-engineer` | `e2e/` |

## Vermelho antes do verde e mutação
- Vermelho: `git stash push -- <arquivos de produção>` e `python -m pytest <teste>` precisa falhar; depois `git stash pop`.
- Mutação (gratuita): `forge-mutante` com o executor `unittest` quando os testes são unittest; com pytest, `mutmut` só nos arquivos do diff. A meta fica em `docs/engineering/praticas.md` e só sobe.

## CI
Insumos da skill `ci-cd` para o `devops-engineer`: Python da versão do `requires-python`; cache derivado do lockfile; instalação travada (com hash); jobs na ordem lint e tipos, testes, build do pacote ou da imagem; a checagem de pareceres (`forge-check pr`) em job próprio, obrigatório para o merge e fora do `needs` dos jobs de testes, para o parecer faltando não esconder o resultado da suíte; imagem base `python` fixada por digest, em multi-stage, com usuário não root.

### Dependabot (ecossistema de pacotes)
Copie para o fim de `updates:` do `.github/dependabot.yml` do projeto; horário, `cooldown` e grupos seguem o modelo em `templates/projeto/.github/dependabot.yml`:

```yaml
  - package-ecosystem: "pip"
    directory: "/"
    target-branch: develop
    schedule:
      interval: "daily"
      time: "06:00"
      timezone: "America/Sao_Paulo"
    open-pull-requests-limit: 5
    cooldown:
      semver-major-days: 7
      semver-minor-days: 1
      semver-patch-days: 1
    groups:
      rotina:
        update-types: ["minor", "patch"]
      maiores:
        patterns: ["*"]
        update-types: ["major"]
    ignore: []
```
