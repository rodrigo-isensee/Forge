---
tipo: qa
contrato: 1
pedido: hook-ansi-c
branch: melhoria/hook-ansi-c
commit: f3d1fd092979c2bb8eb0af09db16e33909f94154
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-27
---
# QA: hook-ansi-c

Base do diff: 770c19a3c3f64d0f132eb358232e126e69e33b2e. Pedido sem especificação de UX: as obrigações são o E1 do pedido (cartão LEITOR-ANSI-C) e as decisões da volta 1 (A1 da segurança pela opção b; A1 e A2 do review). Rodado em paralelo com review e segurança (ACELERA-RODADA); este parecer vale para o head acima e substitui o do commit 3707e28.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1 os dois casos do cartão saem 2 | test_os_dois_casos_do_cartao_saem_2 | `\'` dentro de `$'…'` seguido de `;` | passou |
| E1 o bash roda mesmo o 2º comando (premissa do furo) | test_o_bash_roda_o_segundo_comando | n/a | passou |
| E1 aspa escapada em outra posição da linha | test_a_aspa_escapada_mais_adiante_na_linha_tambem_falha_fechado | depois de `&&`, após `\\`, dentro de `$(…)` | passou |
| E1 sem regressão | test_controles_a_decisao_de_hoje_nao_muda | `\n`, `\\`, `\\'` de fecho, `\'` fora do ansi; variantes aninhadas legítimas | passou |
| E1 `\\` antes do fecho não é aspa escapada | test_barra_barra_antes_do_fecho_nao_e_aspa_escapada | `\\'` (barra + fecho) | passou |
| E1 marca só no ansi | test_o_leitor_fiel_marca_so_a_aspa_escapada | aspas simples e duplas com `\'` | passou |
| Segurança A1: nível aninhado entre aspas duplas | test_o_nivel_aninhado_entre_aspas_duplas_sai_2 | `bash -c`, `sh -c`, `eval` com `\$'…\\'…'` | passou |
| Review A1: hook no mapa de testes | cobertura de `bin/forge-testes --listar hooks/_comum.py` | regra `hooks/.*` | passou (lista test_hook_ansi_c) |

## Cenários e resultado real
- `python3 -m unittest tests.test_hook_ansi_c tests.test_testes_tocados`: 90 testes, OK (test_hook_ansi_c tem 9, todos ok).
- `bin/forge-mutante tests/mutantes/hook-ansi-c.json`, saída 0: A1 hooks/_comum.py:1734, A2 :1154, A3 :1059, A4 :1060, A5 :1050, A6 :1093, A7 :990, A8 :992, todos "morreu". Conferência contra o diff: linhas de guarda mudadas (cláusula em `leituras`, retorno de `palavras_do_texto`, marca no ramo ansi, salto da barra, marca no nível 0 e as duas guardas de `_ansi_com_aspa_escapada`) têm mutante cada; nenhuma sem mutante.
- Vermelho antes do verde (à mão, cópia em `$TMPDIR` com `hooks/_comum.py` da base 770c19a e o resto do head): `python3 -m unittest tests.test_hook_ansi_c` dá `Ran 9 tests ... FAILED (failures=9, errors=1)` (os dois casos do cartão, as posições adiante na linha, as quatro variantes aninhadas e o leitor fiel, que nem existe na base). `forge-testes --vermelho 770c19a…` estourou o prazo de 550 s (rc=143, "sem veredito"): não vale como vermelho; o vermelho acima o substitui.
- Variantes aninhadas do parecer de segurança, `bash --norc --noprofile -c` em pasta temporária com `.env` falso e `.git` falso, e o hook `conformidade` real (papel `forge:node-backend`): `bash -c "…cat .env \\'"` imprime `it's` e o `.env` (o 2º comando rodou), hook saiu 2; `bash -c "…rm -rf .git \\'"` apaga o `.git` falso, hook saiu 2; `eval "…cat .env \\'"` imprime o `.env`, hook saiu 2. Variante `sh -c`: o `sh` (dash) não entende `$'…'` e não roda o 2º comando, mas o hook recusa (2) do mesmo jeito (falha fechado).
- `bin/forge-testes --listar hooks/_comum.py` lista `test_hook_ansi_c`.
- PA-7: `docs/engineering/achados-recorrentes.md` sem linhas ("nenhum ainda"); nada a conferir.
- Acessibilidade e E2E de UI: n/a (hook de linha de comando).

## Observações (não bloqueantes)
- O leitor marca `aspa_escapada` e falha fechado: comandos legítimos com `$'…\'…'` (ou `\$'…\'…'` entre aspas duplas) seguidos de outro comando passam a ser recusados. Comportamento declarado no pedido e nas decisões da volta 1.
- A2 da segurança (`hooks/pesado.py:90`) e a correção exata do A1 (a) ficam nos cartões PESADO-ANSI-C e pós-HOOK-CD, por decisão registrada; fora deste parecer.
