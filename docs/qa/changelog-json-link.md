---
tipo: qa
contrato: 1
pedido: changelog-json-link
branch: melhoria/changelog-json-link
commit: 3f3b7deb8bd8823b380eb514b74281a82d7a213f
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-24
---
# QA: changelog-json-link

Revalidação por delta (`128ab04..3f3b7de`): o código de produção não mudou desde `705d5a9`; a volta acrescentou só o teste `test_chave_version_repetida_com_a_versao_nova_no_ultimo_valor_falha_sem_gravar_nada` e um comentário em `tests/test_changelog.py`. A1 (bloqueante da rodada anterior) está resolvido. Sonda em `$TMPDIR/qa-cjl/`, nunca no `~/Forge`.

## Achados
- A2 (recomendado) bin/forge-changelog:1 · o pedido toca `bin/` e a branch não traz a spec de mutantes declarada pelo autor (`tests/mutantes/`); a lista foi escrita pelo QA (6 mutantes, um por guarda mudada). Não bloqueia: todos morrem com a lista corrigida.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1 (A1): chave `version` aninhada antes da de topo recusa sem gravar | `Release.test_chave_version_aninhada_antes_da_de_topo_falha_sem_gravar_nada`; sonda n-aninhada, n-aninhada-dev, n-aspa-chave | chave aninhada, chave com aspa escapada | passou (M4 morreu) |
| E1 (A1): chave repetida recusa sem gravar | `Release.test_chave_version_repetida_falha_sem_gravar_nada`, `..._repetida_com_a_versao_nova_no_ultimo_valor_falha_sem_gravar_nada`; sonda n-repetida, n-repetida-outra | chave repetida | passou (M1 morreu com o teste novo; A1 resolvido) |
| E1 (A1): aspa escapada no valor recusa sem gravar | `Release.test_aspa_escapada_no_valor_da_version_falha_sem_gravar_nada`; sonda n-aspa-valor | valor com aspa escapada | passou (M6 morreu) |
| E2 (A2): `CHANGELOG.md` link simbólico (inclusive quebrado) recusa antes de escrever | `Release.test_changelog_link_simbolico_e_recusado_sem_gravar_nada`, `..._quebrado_e_recusado`; sonda n-link-changelog, n-link-changelog-quebrado | link, link quebrado | passou (M3 morreu) |
| E2 (A2): `CHANGELOG.md` fora da raiz recusa | `Release.test_changelog_que_resolve_fora_da_raiz_e_recusado_sem_gravar_nada`; sonda n-fora-raiz-changelog | fora da raiz | passou (M2 e M3 morreram) |
| Regressão: manifestos link, quebrado, fora da raiz, JSON inválido, sem `version` | testes `Release.test_manifesto_*`; sonda n-link-manifesto(-quebrado), n-link-dev(-quebrado), n-dir-link-*, n-json-invalido, n-sem-version | idem | passou (M2 e M5 morreram) |
| Release feliz, com e sem `dev/`, resto do JSON intacto | `Release.test_sobe_a_versao_dos_dois_manifestos_quando_o_dev_existe`, `test_sem_o_manifesto_dev_a_release_nao_cria_nada`; sonda pos-semdev, pos-comdev | manifesto dev ausente | passou |

## Cenários e resultado real
- `python3 -m unittest tests.test_changelog`: 42 testes, OK (skipped=1: `test_fragmentos_novos_desta_branch_tem_o_nome_dela`, a worktree está em HEAD solto, não em `melhoria/*`). `test_versao_igual_a_do_forge`: OK.
- Vermelho antes do verde: `bin/forge-testes --vermelho d150ec87b004f6f5561a65aa130bb16cf454473c` rc=0; `vermelho: base=d150ec87b004 head=3f3b7deb8bd8`; `contagem: não prova (passa na base)=602; prova (asserção)=7; pulado=1`; o teste novo: `H=ok · B=falha · prova (asserção)`.
- Ponta a ponta (`$TMPDIR/qa-cjl/sonda.sh`, saída em `run3.log`, script da branch, repositório de sonda): 3 casos felizes (com e sem `dev/`: os dois manifestos na 0.2.0, resto do JSON intacto, fragmento apagado; mais a aspa escapada em valor de outra chave, aceita corretamente) e 17 recusas, todas com rc=1, snapshot idêntico e fragmento preservado: versão aninhada (raiz e dev), repetida (`version` e outra chave), aspa escapada na chave e no valor, link e link quebrado no `CHANGELOG.md`, no manifesto da raiz e no de `dev/`, diretório `.claude-plugin` e `dev` como link, `CHANGELOG.md` apontando para fora da raiz, sem `version`, JSON inválido.
- Mutação (`bin/forge-mutante`), spec com o M1 apontando para o teste novo (`mutantes-cjl3.json`), rc=0:
```
M1 · morreu · bin/forge-changelog:90
M2 · morreu · bin/forge-changelog:97
M3 · morreu · bin/forge-changelog:142
M4 · morreu · bin/forge-changelog:124
M5 · morreu · bin/forge-changelog:111
M6 · morreu · bin/forge-changelog:123
```
  Com a spec antiga (M1 apontando só para o teste velho) o M1 segue sobrevivendo, o que confirma que o teste novo é quem prova o gancho.
- Fora do escopo, já em cartão (CHANGELOG-D-LINK): `changelog.d` como link de diretório e versão aninhada com o manifesto já na versão alvo.
