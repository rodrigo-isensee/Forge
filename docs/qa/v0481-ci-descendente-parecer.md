---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-ci-descendente-parecer
commit: 2364a43b8de4d3fbc87343bd2a7ffa73d9d46c04
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 1
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-25
---
# QA: v0481-ci-descendente-parecer (E8.12, G3.7)

Clone `/root/.forge-contrib/wt/v0481-ci-descendente-parecer-qa`, no head `2364a43b` (igual ao remoto). Diff contra `eeb81062`: `bin/forge-check` (+34), 2 skills, mutantes, 2 arquivos de teste. A lógica da regra está correta; o que reprova é o CI do PR, que não ficou verde.

## Achados
- A1 (bloqueante) skills/qa-testing/SKILL.md:46 · a frase G3.7 leva o `qa-engineer` a 21650 caracteres, teto 21480 (`docs/regras/orcamento.json`); `test_orcamento_instrucao` cai (suíte 3/5, py3.14; local reproduz, base eeb81062 passa). O teste também acusa tech-lead 57 marcadores, teto 56. Encurte as skills.
- A2 (recomendado) bin/forge-check:2197 · `git diff` honra `diff.ignoreSubmodules=all` (config ou `.gitmodules`): um gitlink fora das pastas some do diff e passa (sonda: True). Some `--ignore-submodules=none`. No CI padrão não vale.

## Critério -> teste -> resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Linha nova `- ci: <sha40> verde via <sha40>` aceita com descendente só de pareceres | `LeOCiVia.test_descendente_so_de_pareceres_vale`, `test_cmd_pr_aceita_o_via_so_de_pareceres` | próprio sha (diff vazio); `commit:` curto | passou |
| Descendente que não descende, sha inexistente, base | `test_nao_descendente_ou_sha_inexistente_nao_vale` | ancestral, irmão, sha inexistente | passou |
| Outro caminho no diff recusa | `test_outro_caminho_no_diff_nao_vale` | 1 arquivo fora das pastas | passou |
| Renomeação para pasta de parecer | `test_renomeacao_para_a_pasta_do_parecer_nao_vale` | origem escondida por `-M` | passou |
| git que falha recusa | `test_erro_do_git_diff_falha_fechado` | rc 128 | passou |
| Primeiro sha != `commit:`, `vermelho`, ressalva, `commit:` vazio ou fora da forma | `test_outro_sha_outro_estado_ou_commit_invalido_nao_vale` | vazio é prefixo de tudo | passou |
| Forma antiga, `.github` e checks do head no merge não mudam | `LeOCiNoCmdPr` e `ProvaDaSuiteBase` herdados (módulo inteiro, 8 + herdados) | n/a | passou local |
| Brief, esqueleto e skills citam a forma | `ChecksForaDaLinhaDoCi.test_brief_esqueleto_e_skills_citam_a_forma_via` | n/a | passou |
| CI do PR verde no head | check-runs do run 45586618198 | n/a | FALHOU: `suíte (python 3.14, parte 3/5)` (A1); `bateria (pareceres)` e `catraca` falham, fora da linha, esperam o parecer; demais suítes ainda pendentes na leitura |

## Sondas de abuso (repo descartável em `$TMPDIR`, chamando `so_pareceres_ate`)
Recusaram (False): `docs/QA/` e `Docs/QA/` (maiúsculas), `docs/qa-x/` (prefixo), código apagado, symlink em `docs/qa` mais código mudado, `.gitmodules` na raiz, merge commit que traz código, chmod em código, `docs/qa` trocado por link para `bin`, gitlink em `bin/sub`. Aceitaram (True, corretos): só parecer, merge `-s ours` (árvore idêntica), nome com acento e `..x` dentro de `docs/qa/`, symlink/gitlink/apagado dentro das pastas (não mudam código). Fonte de verdade é a árvore (diff de duas árvores), então merge no meio e renomeação não enganam. Exceção: A2.

O caso da marca 0.47.18: a branch não existe mais no remoto; o equivalente é `test_cmd_pr_aceita_o_via_so_de_pareceres` (cmd_pr com via) e a sonda do merge. O run verde de `via` em si não é verificável pelo portão (só a linha é conferida): a honestidade do `- ci:` segue com quem o grava.

## Vermelho antes do verde
Base `eeb81062` com `tests/test_forge_check_pr.py` do head, `-k LeOCiVia`: `FAILED (failures=2, errors=8)`; no head, `Ran 8 tests ... OK`. A saída de `forge-testes --vermelho eeb81062` não concluiu a tempo e não é citada.

## Mutantes (`bin/forge-mutante` das 2 specs)
```
forge-mutante: pedido=v0481-ci-descendente-parecer rev=2364a43b8de4 spec=f0b1f221... spec=187417af...
M1 · morreu · bin/forge-check:2188
M2 · morreu · bin/forge-check:2195
M3 · morreu · bin/forge-check:2197
M4 · morreu · bin/forge-check:2198
M5 · morreu · bin/forge-check:2198
M6 · morreu · bin/forge-check:2205
M7 · morreu · bin/forge-check:2204
M8 · morreu · bin/forge-check:2227
M9 · morreu · bin/forge-check:2203 · (erro) o teste declarado deu erro sob o mutante e passa sem ele
```
Cada linha de guarda mudada tem mutante; nenhum sobrevivente.

## Revalidação
Corrigido A1, o parecer novo grava `- ci: <sha40> verde` (ou `via`, só de pareceres) quando o `gh pr checks` do head ficar verde fora das 3 checagens da linha.
