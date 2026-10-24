---
tipo: qa
contrato: 1
pedido: hook-raiz-contrib
branch: melhoria/hook-raiz-contrib
commit: 2e408dafc562acae86c6c6cf385cd1d42fada5c7
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-23
---
# QA: hook-raiz-contrib

Pedido HOOK-RAIZ-CONTRIB (E1): o hook `conformidade` passa a proteger `~/.forge-contrib/<pasta>/docs/pedidos/` e `.../docs/briefs/` só para o jarvis. Código conferido: `1fa5946`; HEAD testado `2e408da` (só soma os pareceres de review e segurança). Diff contra `139a3b4`: `hooks/conformidade.py` (`casa()` com `*` por uma pasta; pré-filtro de citações), `hooks/conformidade.json` (2 entradas), 4 fixtures, `docs/hooks.md`, fragmento de changelog.

## Achados
- A1 (recomendado) tests/hooks/conformidade/pasta-contrib-pedido-jarvis-libera.json:1 · o `*` valer uma pasta só (`~/.forge-contrib/wt/wt-a/docs/pedidos/`, com cwd fora do projeto, libera) não tem fixture: mutantes M2 (`[^/]+`→`.+`) e M3 (`re.match`→`re.search`) sobrevivem; sem efeito de segurança (só bloquearia a mais).
- A2 (recomendado) tests/mutantes/hook-raiz-contrib.json:1 · o pedido toca `hooks/` e a branch não traz spec de mutantes declarados; o QA escreveu seis (abaixo) fora da árvore, mas a declaração é do autor.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1: tech-lead recusado em `~/.forge-contrib/<pasta>/docs/pedidos/` | fixture `pasta-contrib-pedido-tech-lead-bloqueia` + sonda ponta a ponta (tech-lead, qa, dev; Write, `>` e `tee`) | permissão (papel não jarvis); pasta `forge` e `outra` | passou |
| E1: tech-lead recusado em `.../docs/briefs/` | fixture `pasta-contrib-brief-tech-lead-bloqueia` + sonda | permissão | passou |
| E1: jarvis (e sessão principal sem `agent_type`) aceito nos dois | fixtures `...-jarvis-libera` + sonda (Write, Bash) | permissão | passou |
| E1: entradas de hoje (`~/.forge-contrib/docs/pedidos/` e `briefs/`) mantidas | sonda, pasta `docs` | regressão | passou |
| Agente numa worktree de `~/.forge-contrib/wt/` segue normal | sonda: Write e Bash em `wt/wt-a/src/a.py` por tech-lead, qa e dev | `*` = uma pasta | passou |
| Caminho com `..` (`forge/x/../docs/pedidos/y.md`) | sonda | traversal | passou (recusa) |
| Suíte existente sem regressão | `tests.test_hooks` | n/a | passou |

## Cenários e resultado real
- `python3 -m unittest tests.test_hooks`: 43 testes, OK (inclui `test_fixtures` sobre 875 fixtures, as 4 novas dentre elas).
- Ponta a ponta com `HOME=$TMPDIR/qa-hookraiz/home` (nunca a área real), hook da branch, pastas `forge`, `outra` e `docs`, para pedidos e briefs: tech-lead, qa e dev (backend) recusados por Write, `echo >` e `tee` (rc 2, motivo R-CONFORMIDADE); jarvis e sessão sem `agent_type` aceitos (rc 0) nas três vias. Worktree `wt/wt-a`: src aceito para os três papéis.
- Vermelho antes do verde: `forge-testes --vermelho 139a3b4` completo estourou o prazo (rc 124, sem veredito); refeito com `--modulos test_hooks --prazo 500`, rc 0: `tests.test_hooks.Hooks.test_fixtures · H=ok · B=falha · prova (asserção)`; contagem: não prova=42, prova=1.
- Mutação (spec do QA em `$TMPDIR/qa-hookraiz/mut.json`, teste `test_fixtures`), saída 1: M1 `if "*" in caminho` morreu; M2 sobreviveu (A1); M3 sobreviveu (A1); M4 (`rsplit` do pré-filtro) sobreviveu, equivalente aceito: a entrada genérica `docs/pedidos/` já gera a citação `docs/pedidos` que casa qualquer comando que cite a pasta; M5 e M6 (entradas do JSON) morreram. M2 e M3 só ampliariam a recusa, daí recomendado e não bloqueante.
- E2 do pedido (conferido no histórico): `forge-check` lê só `~/.forge-contrib/docs/briefs/`, fora do escopo (cartão FORGE-CHECK-RAIZ-PASTA).
