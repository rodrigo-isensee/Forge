# Forge — desenvolvimento da fábrica

Este repositório **é** a fábrica: o plugin `forge` do Claude Code com o Jarvis, o time de agentes, as skills, o processo e os modelos de projeto. Ele é usado por N projetos; qualquer mudança aqui afeta todos eles.

## Regras invioláveis
- **A `main` é do usuário.** Nenhum agente faz commit, merge ou push na `main`; tudo chega por PR validado e mesclado pelo usuário. O hook `.githooks/pre-push` bloqueia envios para a `main` (ative com `git config core.hooksPath .githooks`).
- **Neutralidade:** nada específico de um projeto (nomes, regras de negócio, stack fixa) entra em agentes, skills, docs ou modelos. O teste `Neutralidade` e a lista `termos_proibidos` em `tests/config.json` garantem isso.
- **Regras da fábrica protegidas por teste:** os trechos em `invariantes` (`tests/config.json`) não podem sumir. Afrouxar ou remover um item exige destaque no título do PR e o motivo.
- **Toda mudança passa pelos testes** (`python3 -m unittest discover -s tests -v`) e pela validação do plugin (`claude plugin validate . --strict`). Mudança em `agents/` ou `skills/` também roda as avaliações de comportamento (`evals/`) no CI.
- **Versão:** toda mudança que chega à `main` sobe a versão em `.claude-plugin/plugin.json` (SemVer: correção → patch, melhoria compatível → minor, quebra para os projetos → major) e ganha entrada no `CHANGELOG.md`. O CI confere que as duas batem.

## Estrutura
| Pasta | O quê |
|---|---|
| `.claude-plugin/` | `plugin.json` (manifesto e versão) e `marketplace.json` (o próprio repo é o marketplace) |
| `agents/` | Jarvis e o time (`forge:<nome>`) |
| `skills/` | Skills do time e `iniciar-projeto` |
| `docs/` | Processo da fábrica: melhoria contínua, economia de tokens, padrão de documentação, pesquisa de práticas |
| `templates/projeto/` | Modelo copiado para cada projeto pelo `bin/forge-init` |
| `bin/` | `forge-init` (fica no PATH enquanto o plugin está ativo) |
| `scripts/` | Atalho `jarvis` e o instalador dele |
| `tests/` | Testes estruturais (biblioteca padrão do Python) |
| `evals/` | Avaliações de comportamento dos agentes (`claude plugin eval`) |

## Como testar localmente
```bash
python3 -m unittest discover -s tests -v
claude plugin validate . --strict
claude --plugin-dir . --agent forge:jarvis        # sessão usando esta cópia do Forge
claude plugin eval . --trust-plugin --threshold 0.75 --max-cost-usd 5   # comportamento (custa uso de IA)
```

## Autonomia
Os agentes podem melhorar o Forge por iniciativa própria (ver "Autonomia para melhorar o Forge e os projetos" em `agents/jarvis.md`), sempre por branch, testes verdes e PR validado pelo usuário.
