---
tipo: qa
contrato: 1
pedido: changelog-json-link
branch: melhoria/changelog-json-link
commit: 977bad027392431c9b0268cb312705b34f64a64e
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-24
---
# QA: changelog-json-link

Código conferido: `705d5a9` (os commits seguintes só trazem pareceres). Sonda em `$TMPDIR/qa-cjl/`, nunca no `~/Forge`.

## Achados
- A1 (bloqueante) tests/test_changelog.py:188 · classe: teste que não prova a guarda. Mutante M1 (`if False:` no gancho, bin/forge-changelog:90) sobrevive: o teste cai na outra guarda; `{"version":"0.1.0","k":1,"version":"0.2.0"}` seria gravado. Falta teste com repetida cujo último valor é a versão nova.
- A2 (recomendado) bin/forge-changelog:1 · o pedido toca `bin/` e a branch não traz a spec de mutantes declarada pelo autor; a lista abaixo foi escrita pelo QA (6 mutantes, um por guarda mudada) e a saída 0 do autor não existe para conferir.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1 (A1): chave `version` aninhada antes da de topo recusa sem gravar | `Release.test_chave_version_aninhada_antes_da_de_topo_falha_sem_gravar_nada`; sonda n-aninhada, n-aninhada-dev, n-aspa-chave | chave aninhada, chave com aspa escapada | passou (M4 morreu) |
| E1 (A1): chave repetida recusa sem gravar | `Release.test_chave_version_repetida_falha_sem_gravar_nada`; sonda n-repetida, n-repetida-outra | chave repetida | teste passa, mas não prova o gancho (M1 sobreviveu): A1 |
| E1 (A1): aspa escapada no valor recusa sem gravar | `Release.test_aspa_escapada_no_valor_da_version_falha_sem_gravar_nada`; sonda n-aspa-valor | valor com aspa escapada | passou (M6 morreu) |
| E2 (A2): `CHANGELOG.md` link simbólico (inclusive quebrado) recusa antes de escrever | `Release.test_changelog_link_simbolico_e_recusado_sem_gravar_nada`, `..._quebrado_e_recusado`; sonda n-link-changelog, n-link-changelog-quebrado | link, link quebrado | passou (M3 morreu) |
| E2 (A2): `CHANGELOG.md` fora da raiz recusa | `Release.test_changelog_que_resolve_fora_da_raiz_e_recusado_sem_gravar_nada`; sonda n-fora-raiz-changelog | fora da raiz | passou (M2 e M3 morreram) |
| Regressão: manifestos link, quebrado, fora da raiz, JSON inválido, sem `version` | testes `Release.test_manifesto_*`; sonda n-link-manifesto(-quebrado), n-link-dev(-quebrado), n-dir-link-*, n-json-invalido, n-sem-version | idem | passou (M2 e M5 morreram) |
| Release feliz, com e sem `dev/`, resto do JSON intacto | `Release.test_sobe_a_versao_dos_dois_manifestos_quando_o_dev_existe`, `test_sem_o_manifesto_dev_a_release_nao_cria_nada`; sonda pos-semdev, pos-comdev | manifesto dev ausente | passou |

## Cenários e resultado real
- `python3 -m unittest tests.test_changelog`: 41 testes, OK (skipped=1: `test_fragmentos_novos_desta_branch_tem_o_nome_dela`, a worktree está em HEAD solto, não em `melhoria/*`). `test_versao_igual_a_do_forge` (`tests/test_forge.py:154`): OK.
- Vermelho antes do verde: `bin/forge-testes --vermelho d150ec87b004f6f5561a65aa130bb16cf454473c` rc=0; `contagem: não prova (passa na base)=602; prova (asserção)=6; pulado=1`; os 6 testes novos: `H=ok · B=falha · prova (asserção)`.
- Ponta a ponta (`$TMPDIR/qa-cjl/sonda.sh`, saída em `run2.log`, script da branch, repositório de sonda): 2 casos felizes (com e sem `dev/`: os dois manifestos na 0.2.0, resto do JSON intacto, fragmento apagado) e 17 recusas, todas com rc=1, snapshot de todos os arquivos idêntico e fragmento preservado: versão aninhada (raiz e dev), repetida (`version` e outra chave), aspa escapada na chave e no valor, link e link quebrado no `CHANGELOG.md`, no manifesto da raiz e no de `dev/`, diretório `.claude-plugin` e `dev` como link, `CHANGELOG.md` apontando para fora da raiz, sem `version`, JSON inválido. Caso extra: aspa escapada dentro de valor de outra chave (`"x \"version\": \"9"`) é aceito, e corretamente (a troca acerta a chave de topo).
- Mutação (spec do QA em `$TMPDIR/qa-cjl/mutantes-cjl.json`, `bin/forge-mutante`, rc=1):
```
M1 · sobreviveu · bin/forge-changelog:90
M2 · morreu · bin/forge-changelog:97
M3 · morreu · bin/forge-changelog:142
M4 · morreu · bin/forge-changelog:124
M5 · morreu · bin/forge-changelog:111
M6 · morreu · bin/forge-changelog:123
```
- Fora do escopo, já em cartão: `changelog.d` como link de diretório e versão aninhada com o manifesto já na versão alvo.
