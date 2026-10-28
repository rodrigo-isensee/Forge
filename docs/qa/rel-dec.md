---
tipo: qa
contrato: 1
pedido: rel-dec
branch: melhoria/rel-dec
commit: fcc5980ee53f58cb021b7c96e19ca81d712d07e8
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-28
---
# QA: rel-dec

Escopo: QA (`R-QA`) da integração só na hora do merge (REL-R4) e do merge automático da promoção develop → homolog (REL-D1A). Diff `ed7fbd8...fcc5980` (7 arquivos): `docs/regras/R-FLUXO.md`, `agents/tech-lead.md`, `docs/promocao-integrador.md`, `scripts/promover-homolog.py`, `tests/test_promover_homolog.py`, `tests/config.json`, `changelog.d/rel-dec.md`. Roda em paralelo com o review e a segurança (ACELERA-RODADA "A", item 4). Sem plano antecipado (pedido de controle sem especificação de UX); as obrigações vêm do escopo E1/E2 do pedido `REL-DEC`.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1: `R-FLUXO` e `tech-lead` dizem "só na hora do merge", com `forge-check pr` conferindo o merge simulado | invariantes de `tests/config.json` (`tests.test_forge`, 435 testes) | trecho antigo removido e novo exigido na fonte | passou |
| E1: `forge-check pr` de fato faz merge simulado (a regra não promete o que a ferramenta não faz) | leitura de `bin/forge-check` (`merge-tree --write-tree`, linhas 395-406) | `n/a` | passou |
| E2: o script imprime `gh pr merge develop --auto --merge --match-head-commit <sha>` com tudo verde | `tests.test_promover_homolog.Execucao` (caminho verde), 25 testes | sha preso por `--match-head-commit`; script continua sem chamar `pr merge` | passou |
| E2: o script não mescla nem aplica rótulo | mesmos testes (`assertNotIn("pr merge", chamadas)`, `--force`) | permissão: main e rótulo do dono | passou |
| E2: merge automático desligado cai no merge com tudo verde | leitura: texto em `R-FLUXO.md:13`, `agents/tech-lead.md:32`, `docs/promocao-integrador.md:18`, linha 7 do script | `n/a` | passou (só texto, não há código a testar) |
| E2: a main fica só com o usuário | `R-FLUXO.md:13` ("Só a `homolog`") e `main` inalterada na linha 14 | permissão | passou |

## Cenários e resultado real
- `python3 -m unittest tests.test_promover_homolog`: 25 testes, OK.
- `python3 -m unittest tests.test_forge`: 435 testes, OK (inclui as invariantes trocadas: `só na hora do merge` em `agents/tech-lead.md`; `confere o merge simulado` e `Atualize a branch com a integração só na hora do merge` em `docs/regras/R-FLUXO.md`; os três existem na fonte, e os trechos antigos "uma vez, antes do review" e "Depois do QA só se atualiza" não aparecem mais em `agents/`, `docs/regras/` nem `skills/`).
- Troca de invariante: três trechos trocados, nenhum removido sem substituto; o título do PR precisa do destaque de afrouxamento (`R-FLUXO`, rótulo `afrouxa-regra`), a cargo do tech-lead no PR.
- Vermelho antes do verde (`forge-testes --vermelho ed7fbd80ba9b57562442a20c9cfa479a1a5c94c7 --modulos test_promover_homolog --prazo 300`), rc=0: `contagem: não prova (passa na base)=24; prova (asserção)=1`. O teste que prova é o do caminho verde (`Execucao`), que falha na base por esperar `--auto` na saída. A suíte completa não rodou fora do pre-push (brief).
- Sonda do hook `hooks/parecer.py` com `gh pr merge develop --auto --merge --match-head-commit abc` em repositório vazio: rc=0 (sem a branch develop; ver recomendação 2).
- PA-7 (`docs/engineering/achados-recorrentes.md`): conferido; nenhuma classe repetida neste diff.
- Mutação: o pedido não toca `bin/`, `hooks/`, `.githooks/` nem `tests/catraca.py`; não há spec de mutantes a rodar.

## Recomendações (não bloqueiam)
1. As invariantes guardam a troca de REL-R4, mas nenhuma guarda o texto novo da promoção com `--auto --merge` em `docs/regras/R-FLUXO.md:13` e `agents/tech-lead.md:32`; um revert silencioso passaria nos testes. A E2 só tem prova no script.
2. O `--auto` junto de `--match-head-commit` não tem teste no hook `parecer.py` (o teste existente cobre `gh pr merge develop` simples); vale um caso com as duas opções.
3. Nenhum teste cobre a linha `[7]` do `--dry-run` com o texto novo.

## Bugs
Nenhum.
