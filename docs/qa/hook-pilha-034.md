---
tipo: qa
contrato: 1
pedido: hook-pilha-034
branch: melhoria/hook-msg-segmento
commit: dde743b95b2424cbdafacc18cfd303dd8193f198
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-05
---
# QA: hook-pilha-034 (E1.4, pilha de hooks inteira)

Base: develop d9b26bb. Código testado: dde743b, topo das 7 branches; o HEAD 5edf63c só soma os pareceres de review e de segurança (ambos aprovados), sem mudar código. Os critérios são os do pedido (E1, E2 e E3); não há especificação de UX.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1: `\` + quebra de linha no meio da palavra recusa nos dois hooks | fixtures `continuacao-linha-107` a `-111` e `-112` (parecer); sonda própria: `g$'\x68' repo de\⏎lete`, `g$'\x69't pu\⏎sh`, `$'\x67'it push origin ma\⏎in` | continuação no meio da palavra | passou, rc 2 |
| E1: `$'…'` decodificado até o primeiro NUL | fixtures `-098` a `-105`; sonda: `gh $'repo\0x' delete`, `$'gh\0' repo delete`, `$'g\x69t\0' push origin main` | NUL no começo, no meio e no fim | passou, rc 2 |
| E1: NUL legítimo segue liberado | fixture `-106`; sonda: `printf $'a\0b'`, `echo $'a\0b' && git status` | falso positivo | passou, rc 0 |
| E1: formas compostas até o ponto fixo; teto falha fechado | `test_formas_compostas_ate_o_ponto_fixo_e_teto_fecha`, mutantes M42, M44 e M45 | teto de rodadas | passou, mutantes mortos |
| E1: `bash -c`, `eval` e `sh -c` com `$'…'` | sonda própria nos dois hooks; fixtures `-38` a `-91` | aninhamento | passou, rc 2 |
| E1: casos legítimos liberados | sonda: `git status && \⏎git log`, `echo $'\x67\x68'`, `printf '%s' $"gh" repo view`, `echo `date``, `gh repo view`, `gh pr view 1` | falso positivo | passou, rc 0 |
| E2: R7 e R8 do rótulo afrouxa-regra recusam; outro rótulo libera | fixtures `rotulo-variavel-r7-*` (3) e `rotulo-variavel-r8-*` (4), em `test_fixtures_da_trilha_034` | `#` em expansão antes da crase; `$'…'` antes da crase; aspa escapada | passou |
| E2: `tests.test_hook_ansi_c` mata o M4 (`hooks/_comum.py:1894`) | `tests.test_hook_ansi_c` e mutante M4 | guarda da aspa escapada | passou, M4 morreu |
| E3: a reaplicação das branches não muda o comportamento | `test_fixtures` (todas as fixtures dos dois hooks) e a suíte do push | n/a | passou |

## Cenários e resultado real
Ambiente: worktree `/root/.forge-contrib/wt/hook-msg-segmento`, HEAD 5edf63c, código dde743b.

- **Suíte inteira (D-5), sem rodar de novo (R-TETO):** `/tmp/push-hook-topo.log`, do push do topo com o código de dde743b: `Ran 968 tests`, `Ran 1654 tests`, `Ran 2622 tests in 1989.698s (2 processos)`, `OK (skipped=30)`, `push_rc=0`.
- **`python3 -m unittest tests.test_hook_ansi_c`:** `OK`, rc 0.
- **Fixtures dos dois hooks:** `python3 -m unittest tests.test_hooks.Hooks.test_fixtures tests.test_hooks.Hooks.test_fixtures_da_trilha_034`: `Ran 2 tests in 470.101s`, `OK`.
- **Sonda própria** (montagem das fixtures, comando trocado): as recusas saem com rc 2 e as liberações com rc 0, como na tabela. No `parecer`, `g$'\x68' pr mer\⏎ge docs/x`, `bash -c $'gh pr m\x65rge 1'` e `eval $'…'` recusam; `$'gh\0' pr merge 1` recusa por R-CONTRIB; `gh pr view 1` e `echo $'a\0b' && gh pr view 1` liberam. Sem `$'…'`, `gh pr m\x65rge` é texto literal e libera, como no bash.
- **Mutantes:** `bin/forge-mutante tests/mutantes/hook-conformidade-034-*.json --processos 2` (rev 5edf63c32e03, 8 specs): 43 mutantes, 43 `morreu`, rc 0 (entre eles M3, M4, M43, M44, M45 e M46).
- **Lista de mutantes contra o diff:** `bin/forge-mutante --cobertura --base d9b26bb3e6b11e7d45c8b7ed81c7da7a8a325503` dá toda linha de guarda mudada em `hooks/` como `coberta`, sem nenhuma `não coberto`. As duas `isenta` (`hooks/_comum.py:360` e `:378`) têm motivo lido: a quebra que sobra é conferida pela forma juntada, e a forma repetida só repete o mesmo caminho.
- **Vermelho antes do verde:** `bin/forge-testes --vermelho d9b26bb3e6b11e7d45c8b7ed81c7da7a8a325503 --modulos test_hooks --prazo 1500`, rc 0. Abre com `vermelho: base=d9b26bb3e6b1 head=5edf63c32e03 módulos=test_hooks (restrito por --modulos)` e fecha com `contagem: não prova (passa na base)=67; prova (API ausente)=4; prova (asserção)=8; pulado=1`. Nenhum teste cai no HEAD. Provam, entre outros, `test_fixtures`, `test_fixtures_da_trilha_034`, `test_ansi_c_decodifica_como_o_bash`, `test_formas_compostas_ate_o_ponto_fixo_e_teto_fecha` e `test_marcador_critico_tambem_na_forma_juntada`. O pulado (`test_erro_interno_com_lista_de_permissao_falha_fechado`) fica pulado também na base, não vem da pilha. Em `test_hook_ansi_c` (`--modulos test_hook_ansi_c`, rc 1), os 9 testes passam na base: o módulo já existe lá, e o M4 é que prova o reforço dele.

## Conferência do PA-7
Li `docs/engineering/achados-recorrentes.md`. A lista de mutantes cobre o diff (AR-1), o ramo de falha de guarda tem fixture que prova pela ação (AR-2), e a mascara do shell não esconde código nas sondas (AR-6). O review e a segurança já registraram os A1 e A2 (review) e o A1 (segurança) como recomendações anteriores à pilha, em cartão; não são regressão e não os reabro.

## Bugs
Nenhum aberto; sem arquivo em `docs/qa/bugs/`.

## Parecer
Aprovado. No código dde743b os repros do E1 e do E2 recusam, os casos legítimos passam, a suíte inteira do push passou, os testes novos provam contra a base e os 43 mutantes morreram.
