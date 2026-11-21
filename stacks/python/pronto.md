# "Pronto" e convenções verificáveis — stack python

O `forge-init` usa o comando abaixo como padrão do "pronto" do projeto (`--pronto` sobrescreve); o `forge adotar` prefere o que o projeto já tem.

Comando sugerido: `ruff check . && ruff format --check . && mypy src && python -m pytest`

Pronto rápido: `ruff check . && ruff format --check . && mypy src`

Pronto completo: o comando sugerido, que o autor roda antes de entregar e o CI roda em todo PR. O rápido (lint, formatação e tipos) é o que o `forge-init` grava no `.githooks/pre-push.local`, e o pre-push o roda antes de cada envio que muda código (envio só de texto, parecer ou junção com a develop passa sem ele).

Detecção: `pyproject.toml`, `requirements.txt`, `setup.py`, `setup.cfg`

Versões: as de Python da matriz `python-version` do CI do projeto; sem matriz, a do `requires-python`. O autor roda os testes rápidos em cada uma antes de entregar (`python<X.Y>` do PATH que se diz dessa versão), um log por versão com `head=` e `rc=`; sem o intérprete, a versão não é verde.

Instalação na cópia (`forge-copia --instalar`, `instalar.json`): só com o lockfile `requirements.lock` (uma linha por pacote com `--hash`, gerado por `pip-compile --generate-hashes`); instala com `--require-hashes --no-deps` e o pacote local com `--no-deps`. Sem `requirements.lock` não instala e avisa.

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
- Prova da entrega (META85, `forge-check entrega --mutantes <log> --pronto <log>`, etapa codigo com código): cada comando acima (mutação e pronto) roda com log que abre com o head e fecha com o rc, `{ echo head=$(git rev-parse HEAD); <comando>; } > <log> 2>&1 && echo rc=0 >> <log> || echo rc=1 >> <log>`; sem os dois logs verdes no head entregue, a entrega volta antes do parecer.

## CI
Insumos da skill `ci-cd` para o `devops-engineer`: Python da versão do `requires-python`; cache derivado do lockfile; instalação travada (com hash); jobs na ordem lint e tipos, testes, build do pacote ou da imagem; a checagem de pareceres (`forge-check pr`) em job próprio, obrigatório para o merge e fora do `needs` dos jobs de testes, para o parecer faltando não esconder o resultado da suíte; no agregador, o job de pareceres pulado ou cancelado em PR reprova (só `success` passa; `skipped` vale fora de PR), sem `!contains(failure)`; imagem base `python` fixada por digest, em multi-stage, com usuário não root. Suíte em partes por unidade de teste, não por arquivo (`pytest-split` com pesos; só ferramenta gratuita, `R-CUSTO`), com os pesos regravados a cada release e o N da matriz igual ao do argumento da parte e ao da soma; o agregador leva o nome do check exigido e reprova perna pulada ou cancelada (as pernas têm nome livre).

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
