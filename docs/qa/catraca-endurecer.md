---
tipo: qa
contrato: 1
pedido: catraca-endurecer
branch: melhoria/catraca-endurecer
commit: fb5028ea246f6f884260c96ad6ed9e24019093cc
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-20
---
# QA: catraca falha fechada sem diff e protege a regra de release

Ambiente: worktree da branch (HEAD 52d2873, que só acrescenta pareceres sobre o commit fb5028e; `tests/` e `tests/catraca.py` iguais). API falsa do harness de `tests/test_catraca.py`, sem rede e sem custo (`R-CUSTO`).

## Suíte
| Verificação | Resultado |
|---|---|
| `python3 -m unittest discover -s tests -q` | 1017 testes, OK (206 s) |
| `scripts/validar-plugin.sh` | Validation passed (manifesto e plugin) |
| Teste instável (falhou e passou sem mudança) | nenhum observado |

## Critério (pedido) -> teste -> resultado
| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1: `git diff` falho vira violação, rc 1 | `test_git_diff_com_erro_vira_violacao`, `test_alterados_levanta_quando_o_git_diff_falha` | base inexistente (lista vazia não vale) | passa |
| E1: rc 1 pelo `main`, inclusive com rótulo | `test_base_inexistente_deixa_a_catraca_vermelha_mesmo_com_rotulo` | rótulo do dono não libera | passa |
| E1: rótulo do dono não libera com base válida | `test_git_diff_falho_com_base_valida_e_rotulo_do_dono_nao_libera` | dono definido + rótulo + diff falho | passa |
| E1: caminho do rótulo por conteúdo (S-16) | `test_git_diff_falho_no_head_rotulado_nao_libera_pelo_conteudo` (controle rc 0 com git sadio, rc 1 com diff falho) | head rotulado | passa |
| E2: `scripts/conferir-release.py` pede o rótulo | `test_regra_de_release_e_protegida`, `test_mudanca_em_arquivo_protegido_barra` [conferir-release] | arquivo protegido | passa |
| Com o git funcionando nada muda | demais 1010 testes da catraca e da suíte, e o controle rc 0 acima | não regressão | passa |

## Vermelho antes do verde
Comando: cópia de `git archive HEAD` em `$TMPDIR` com `tests/catraca.py` de ef71b3c, `python3 -m unittest tests.test_catraca` (161 testes): 4 falhas e 3 erros.
- FAIL `test_git_diff_com_erro_vira_violacao`, `test_base_inexistente_deixa_a_catraca_vermelha_mesmo_com_rotulo`, `test_regra_de_release_e_protegida`, `test_mudanca_em_arquivo_protegido_barra` [scripts/conferir-release.py]: comportamento (lista vazia, arquivo fora de PROTEGIDOS).
- ERROR `test_alterados_levanta_quando_o_git_diff_falha`, `test_git_diff_falho_com_base_valida_e_rotulo_do_dono_nao_libera`, `test_git_diff_falho_no_head_rotulado_nao_libera_pelo_conteudo`: `ErroDeDiff` não existe na versão antiga; falham por ausência da API.
- Guardas (só impedem regressão futura): o teste de base válida e o do conteúdo S-16 dependem da guarda `SEM_LISTA in x`; o vermelho real dela vem da mutação abaixo, não da versão antiga.

## Mutação no diff (manual, cópia em `$TMPDIR`)
- Remover `or SEM_LISTA in x` de `tests/catraca.py`: falha só `test_git_diff_falho_com_base_valida_e_rotulo_do_dono_nao_libera` (a guarda é necessária e testada).
- Trocar `scripts/conferir-release.py` por outra entrada em PROTEGIDOS: falham os dois testes de E2.
- Nenhum mutante sobreviveu.

## Achados
