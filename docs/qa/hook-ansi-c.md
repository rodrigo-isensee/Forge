---
tipo: qa
contrato: 1
pedido: hook-ansi-c
branch: melhoria/hook-ansi-c
commit: 3707e280ce4e3ff11bc28b79b6ab75820d920b27
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-27
---
# QA: hook-ansi-c

Base do diff: 770c19a3c3f64d0f132eb358232e126e69e33b2e. Pedido sem especificação de UX: a obrigação é o E1 do pedido (cartão LEITOR-ANSI-C). Rodado em paralelo com review e segurança (ACELERA-RODADA); este parecer vale para o head acima.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1 os dois casos do cartão saem 2 | test_os_dois_casos_do_cartao_saem_2 | `\'` dentro de `$'…'` seguido de `;` | passou |
| E1 o bash roda mesmo o 2º comando (premissa do furo) | test_o_bash_roda_o_segundo_comando | n/a | passou |
| E1 aspa escapada em outra posição da linha | test_a_aspa_escapada_mais_adiante_na_linha_tambem_falha_fechado | depois de `&&`, após `\\`, dentro de `$(…)` | passou |
| E1 sem regressão | test_controles_a_decisao_de_hoje_nao_muda | `\n`, `\\`, `\\'` de fecho, `\'` fora do ansi | passou |
| E1 `\\` antes do fecho não é aspa escapada | test_barra_barra_antes_do_fecho_nao_e_aspa_escapada | `\\'` (barra + fecho) | passou |
| E1 marca só no ansi | test_o_leitor_fiel_marca_so_a_aspa_escapada | aspas simples e duplas com `\'` | passou |

## Cenários e resultado real
- `python3 -m unittest tests.test_hook_ansi_c`: 6 testes, OK.
- `python3 -m unittest tests.test_hooks`: 51 testes, OK (117 s).
- `bin/forge-mutante tests/mutantes/hook-ansi-c.json`: A1..A5 morreram, saída 0. Conferência contra o diff: três linhas de guarda mudadas (cláusula em `leituras`, marca no ramo ansi, retorno de `palavras_do_texto`), cobertas por A1, A3 e A2; A4 e A5 cobrem o salto da barra e o escopo ao ansi. Nenhuma linha de guarda sem mutante.
- Mutação à mão: removida a cláusula `palavras_do_texto(comando).aspa_escapada` de `leituras` numa cópia em `$TMPDIR`; conformidade saiu 0 nos dois casos (`echo $'it\'s'; cat .env\'` e `echo $'it\'s'; rm -rf .git \'`), o que prova que o teste depende da cláusula.
- `bash --norc --noprofile -c` em diretório temporário: caso 1 imprime `it's` e depois o conteúdo de `.env'` (o `cat` rodou); caso 2 imprime `it's` e remove `.git` (o `rm` rodou).
- Vermelho antes do verde: o mutante A1 equivale à base para esse comportamento e os dois testes citados caem; não rodei `forge-testes --vermelho` (fora da instrução do brief, que limita a suíte ao item).
- PA-7: `docs/engineering/achados-recorrentes.md` sem linhas ("nenhum ainda"); nada a conferir.
- Acessibilidade e E2E de UI: n/a (hook de linha de comando).

## Observações (não bloqueantes)
- O leitor fiel marca `aspa_escapada` e a decisão é falhar fechado: comandos legítimos com `$'…\'…'` seguido de outro comando passam a ser recusados com a mensagem de aspas sem par. Comportamento declarado no pedido.
