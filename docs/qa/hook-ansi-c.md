---
tipo: qa
contrato: 1
pedido: hook-ansi-c
branch: melhoria/hook-ansi-c
commit: aadbcc165229e21e9af00d2c09d802dac7936ea7
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-27
---
# QA: hook-ansi-c

Base do diff: 770c19a3c3f64d0f132eb358232e126e69e33b2e. Pedido sem especificação de UX: as obrigações são o E1 do pedido (cartão LEITOR-ANSI-C) e as decisões da volta 1 (A1 da segurança pela opção b; A1 e A2 do review). Rodado em paralelo com review e segurança (ACELERA-RODADA); este parecer vale para o head acima (merge da develop 03de011 sobre a volta 1 f3d1fd0) e substitui o do commit f3d1fd0.

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

## Cenários e resultado real (revalidação por delta, head aadbcc1)
- Delta f3d1fd0..aadbcc1: hooks/_comum.py e tests/test_hook_ansi_c.py sem mudança desde o head aprovado; fora do que veio da develop (03de011), só tests/test_testes_tocados.py mudou (contagem 26 para 27 e `test_hook_ansi_c` na lista; `git diff 03de011 HEAD` confirma 4 linhas) e bin/forge-testes (`test_hook_ansi_c` na tupla FORGE_CHECK e na regra `hooks/.*`, já aprovado na volta 1).
- `python3 -m unittest tests.test_testes_tocados tests.test_hook_ansi_c`: 90 testes, OK.
- `bin/forge-testes --listar hooks/_comum.py`: `dirigido (..., test_hook_ansi_c, ...)`.
- `bin/forge-mutante tests/mutantes/hook-ansi-c.json` (rev aadbcc165229), saída 0: A1 :1734, A2 :1154, A3 :1059, A4 :1060, A5 :1050, A6 :1093, A7 :990, A8 :992, todos "morreu". Linhas de guarda do diff com mutante cada, sem lacuna.
- Vermelho antes do verde e as variantes `bash -c`/`sh -c`/`eval` com o hook real: inalterados, valem do parecer anterior (código e teste idênticos; hooks/_comum.py do head igual ao de f3d1fd0).
- PA-7: `docs/engineering/achados-recorrentes.md` sem linhas; nada a conferir.
- Acessibilidade e E2E de UI: n/a (hook de linha de comando).

## Observações (não bloqueantes)
- O leitor marca `aspa_escapada` e falha fechado: comandos legítimos com `$'…\'…'` (ou `\$'…\'…'` entre aspas duplas) seguidos de outro comando passam a ser recusados. Comportamento declarado no pedido e nas decisões da volta 1.
- A2 da segurança (`hooks/pesado.py:90`) e a correção exata do A1 (a) ficam nos cartões PESADO-ANSI-C e pós-HOOK-CD, por decisão registrada; fora deste parecer.
