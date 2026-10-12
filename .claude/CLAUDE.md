# Forge — desenvolvimento da fábrica

Este repositório **é** a fábrica: o plugin `forge` do Claude Code com o Jarvis, o time de agentes, as skills, o processo e os modelos de projeto. Ele é usado por N projetos; qualquer mudança aqui afeta todos eles.

## Regras invioláveis
Texto único de cada regra com ID em `docs/regras/` (ADR 0002); aqui, o resumo para quem mantém a fábrica.
- **Fluxo de branches** (`R-FLUXO`, `R-MAIN`, `R-VERIFY`): `melhoria/*` → `develop` → `homolog` → `main`. Nada pula degrau (o CI confere) e ninguém envia direto para essas três branches (o hook `.githooks/pre-push` bloqueia; ative com `git config core.hooksPath .githooks`).
  - **`develop`:** bateria rápida — testes estruturais, shellcheck, validação do plugin, instalação de ponta a ponta. O `tech-lead` mescla com tudo verde.
  - **`homolog`:** a mesma bateria, de novo, sobre o conjunto que vai para a `main`. O `tech-lead` promove `develop` → `homolog` por PR com tudo verde.
  - **`main`:** a versão usada por **todos os projetos**. Só muda pelo PR `homolog` → `main`, **mesclado pelo usuário**. Depois do merge, a release `vX.Y.Z` é publicada.
- **Sem custo de dinheiro real** (`R-CUSTO`): nada no Forge (CI, testes, scripts, fluxo) consome API paga ou serviço cobrado. Não se adiciona nada que custe dinheiro sem autorização expressa do dono do Forge.
- **Retroalimentação:** melhorias descobertas em qualquer projeto chegam aqui por PR na `develop` (ver "Fábrica × projeto" em `agents/jarvis.md`).
- **Neutralidade** (`R-NEUTRO`): nada específico de um projeto (nomes, regras de negócio, stack fixa) entra em agentes, skills, docs ou modelos. O teste `Neutralidade` e a lista `termos_proibidos` em `tests/config.json` garantem isso.
- **Regras da fábrica protegidas por teste:** os trechos em `invariantes` (`tests/config.json`) não podem sumir; as regras com ID são verificadas na fonte e os agentes precisam citar o ID. Afrouxar ou remover um item exige destaque no título do PR e o motivo.
- **Toda mudança passa pelos testes** (`python3 -m unittest discover -s tests -v`) e pela validação do plugin (`claude plugin validate . --strict`).
- **Versão:** toda mudança que chega à `main` sobe a versão em `.claude-plugin/plugin.json` (SemVer: correção → patch, melhoria compatível → minor, quebra para os projetos → major) e ganha entrada no `CHANGELOG.md`. O CI confere que as duas batem.

## Estrutura
| Pasta | O quê |
|---|---|
| `.claude-plugin/` | `plugin.json` (manifesto e versão) e `marketplace.json` (o próprio repo é o marketplace) |
| `agents/` | Jarvis e o time (`forge:<nome>`) |
| `skills/` | Skills do time e `iniciar-projeto` |
| `stacks/<nome>/` | Pacote de stack (`agents/`, `skills/`, `seguranca.md`, `pronto.md`), listado em `plugin.json`; só aqui entra linguagem ou framework (ADR 0001) |
| `docs/` | Processo da fábrica: regras com ID (`docs/regras/`), ADRs, melhoria contínua, economia de tokens, padrão de documentação, pesquisa de práticas |
| `templates/projeto/` | Modelo copiado para cada projeto pelo `bin/forge-init` |
| `bin/` | `forge-init` (fica no PATH enquanto o plugin está ativo) |
| `scripts/` | Atalho `jarvis` e o instalador dele |
| `tests/` | Testes estruturais (biblioteca padrão do Python) |

## Como testar localmente
```bash
python3 -m unittest discover -s tests -v
claude plugin validate . --strict
claude --plugin-dir . --agent forge:jarvis        # sessão usando esta cópia do Forge
```

## Autonomia
Os agentes podem melhorar o Forge por iniciativa própria (ver "Autonomia para melhorar o Forge e os projetos" em `agents/jarvis.md`), sempre por branch, testes verdes e PR validado pelo usuário.
