---
tipo: qa
contrato: 1
pedido: rel-dec
branch: melhoria/rel-dec
commit: 767f38738032796b9de22b05a81d91b1258e4bec
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-28
---
# QA: rel-dec

Escopo: QA (`R-QA`) da integração só na hora do merge (REL-R4) e do merge automático da promoção develop → homolog (REL-D1A), volta 2. Diff `ed7fbd8...767f387`: `docs/regras/R-FLUXO.md`, `agents/tech-lead.md`, `docs/promocao-integrador.md`, `scripts/promover-homolog.py`, `tests/test_promover_homolog.py`, `tests/config.json`, `changelog.d/rel-dec.md` (mais pareceres). Sem plano antecipado (pedido de controle sem especificação de UX); as obrigações vêm do escopo E1/E2 do pedido `REL-DEC` e das decisões do dono. Revalida o parecer anterior (`fcc5980`) sobre o delta `fcc5980..767f387` (`b2a7f1d`, `767f387`) e o diff inteiro.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1: `R-FLUXO` e `tech-lead` dizem "só na hora do merge" e o `forge-check pr` confere o merge simulado | invariantes de `tests/config.json` (`RegrasInviolaveis.test_trechos_obrigatorios`) | trecho antigo fora, novo exigido na fonte | passou |
| E2 (A1 do review): checks pendentes imprime o comando `--auto --merge --match-head-commit <sha>`, rc 0, sem `pr merge` | `Execucao.test_check_pendente_imprime_o_merge_automatico_sem_mesclar` | pendente; sha preso; script não mescla | passou |
| E2: nenhum check ainda imprime o comando, rc 0 | `Execucao.test_sem_checks_ainda_imprime_o_merge_automatico` | vazio (zero checks) | passou |
| E2: tudo verde imprime o comando e não mescla nem usa `--force` | `Execucao` (caminho verde) | permissão: o script nunca mescla | passou |
| Check vermelho continua rc 1 sem comando de merge | `Execucao.test_check_vermelho_para` | vermelho | passou |
| Catraca vermelha: rc 3, sem comando, nunca aplica o rótulo | `Execucao` (catraca vermelha; `assertNotIn("pr edit")`) | permissão: rótulo do dono | passou |
| E2 (A3): comando único com `--match-head-commit` em `R-FLUXO.md:13`, `tech-lead.md:32`, `promocao-integrador.md:18` | leitura do diff, igual ao que o script imprime (linha 213) | `n/a` | passou |
| A5: o limite "só a `homolog`, a `main` fica com o usuário" existe na fonte | invariante nova em `tests/config.json` (`docs/regras/R-FLUXO.md`) | main do usuário | passou |

## Cenários e resultado real
- `python3 -m unittest tests.test_promover_homolog`: 25 testes, OK.
- `python3 -m unittest tests.test_forge.RegrasInviolaveis`: OK (a invariante nova casa com `R-FLUXO.md:13`).
- Mutante à mão da invariante nova: troquei por `X` a frase nova de `R-FLUXO.md:13` que limita o merge automático à homolog, numa cópia em `$TMPDIR`; `RegrasInviolaveis.test_trechos_obrigatorios` caiu (FAILED, 1 falha, a regex não casou). A invariante guarda o limite.
- Vermelho antes do verde (`bin/forge-testes --vermelho ed7fbd80ba9b57562442a20c9cfa479a1a5c94c7 --modulos test_promover_homolog --prazo 250`), rc=0: `contagem: não prova (passa na base)=22; prova (asserção)=3`. Os três que provam são o caminho verde, o pendente e o sem-check (`test_sem_checks_ainda_imprime_o_merge_automatico`: H=ok, B=falha); nenhum cai no HEAD.
- Suíte completa não rodada fora do pre-push (brief); só os testes do item.
- PA-7 (`docs/engineering/achados-recorrentes.md`): conferido, sem linhas AR; nenhuma classe repetida neste diff.
- Mutação (`forge-mutante`): o pedido não toca `bin/`, `hooks/`, `.githooks/` nem `tests/catraca.py`; não há spec a rodar.

## Recomendações (não bloqueiam)
1. `--auto` com `--match-head-commit` não tem teste no hook `parecer.py` (o teste existente cobre `gh pr merge develop` simples); o review confirmou a passagem por leitura.
2. Nenhum teste cobre a linha `[7]` do `--dry-run` com o texto novo.
3. Catraca vermelha com check pendente ao mesmo tempo sai com 3 (rótulo do dono) e não imprime o comando `--auto`; coerente com "o rótulo é do dono", só registrado.

## Bugs
Nenhum.
