---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-mutante-varias-trocas
commit: e18a5b07c706a2e559c6dabb5b17fb357b51097e
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-24
---
# QA: v0478 (E162.3, mutante com várias trocas, PR #846)

Base 0733715a, head e18a5b07 (código testado; sem commit de parecer na frente). Mudança em `bin/forge-mutante` (várias trocas por mutante: `de` e `para` em listas de 2 a 8 pares, aplicadas juntas), 5 testes novos em `tests/test_forge_mutante.py`, duas specs de mutante novas e o realinhamento de duas specs antigas (`v047-mutante-avisos` CF5, `vel-p1p10` M6) às linhas movidas. Sem UX nem contrato de API: as obrigações são as da regra MUTANTE-VARIAS-TROCAS (A1 do review do #829) e a da spec de uma troca seguir igual.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Spec de várias trocas válida só em listas do mesmo tamanho, de 2 a 8, textos não vazios, `de` sem repetir e diferente do `para` | `ValidacaoDaSpec.test_varias_trocas_em_listas_do_mesmo_tamanho_valem_e_o_resto_e_invalido` | 1 par, 2 pares, 8 pares, 9 pares, tamanhos diferentes, lista vazia, não texto, `de` vazio, `de` repetido, misto texto/lista | passou; vermelho na base; M1 a M6 morreram |
| Guardas que se cobrem só morrem com as trocas juntas | `Execucao.test_guardas_que_se_cobrem_so_morrem_com_as_trocas_juntas` | cada troca sozinha sobrevive, juntas morrem; sem cópia sobrando em `$TMPDIR` | passou; vermelho na base |
| `de` ausente ou sobreposto entre as trocas é mutante inválido (rc 2), com o trecho na mensagem | `Execucao.test_varias_trocas_com_um_trecho_ausente_ou_sobreposto_sao_invalidas` | 0 ocorrências do 2.º `de`; trechos que se tocam | passou; M7, M8, M10, M11 morreram |
| `--cobertura` conta cada par como um mutante do mesmo id | `Cobertura.test_cada_troca_do_mutante_de_varias_cobre_a_sua_condicao` | duas condições, dois pares, mesmo id | passou |
| `--conferir` confere cada `de`, não só o primeiro | `Conferir.test_varias_trocas_confere_cada_trecho` | só o 2.º trecho sai do lugar: rc 1 com ele nomeado | passou; M12 morreu |
| Spec de uma troca segue igual (R-QA, sem regressão) | os 146 testes já existentes do módulo | n/a | passaram (`não prova (passa na base)=146`) |

## Cenários e resultado real
- Módulo `test_forge_mutante` inteiro, via `forge-testes --vermelho` abaixo: 151 testes, nenhum caiu no HEAD. Sem suíte local; a inteira roda no CI do PR (`R-QA`).
- `forge-mutante --conferir --todas`: antes (base 0733715a) e depois (head), mesma saída, 26 linhas e rc 1 nos dois (`diff` vazio). São as 26 specs antigas com `de` repetido, anteriores ao PR; nenhuma spec nova ou realinhada entrou na lista, ou seja, CF5 e M6 seguem batendo nas linhas movidas.
- `forge-mutante --cobertura --base 0733715a`: toda condição mudada tem mutante (`coberta`, 11 linhas; CF5 e M12 dividem a linha 800); `isenta` do `ocorrencias != 1` com motivo que cruza; sem `não coberto`, sem `isenta velha`.

## Vermelho antes do verde
`bin/forge-testes --vermelho 0733715a --modulos test_forge_mutante` (3 min 6 s). Resumo da saída: `contagem: não prova (passa na base)=146; prova (asserção)=5`. Os 5 testes novos falham na base (H=ok, B=falha), listados como `prova (asserção)`; o primeiro: `tests.test_forge_mutante.ValidacaoDaSpec.test_varias_trocas_em_listas_do_mesmo_tamanho_valem_e_o_resto_e_invalido · H=ok · B=falha · prova (asserção)`. Nenhum teste cai no HEAD.

## Mutação (specs do autor, 12 mutantes em 2 arquivos, 8 + 4)
`bin/forge-mutante tests/mutantes/v0480-mutante-varias-trocas.json tests/mutantes/v0480-mutante-varias-trocas-2.json --processos 3`:
```
forge-mutante: pedido=v0480-mutante-varias-trocas rev=e18a5b07c706 spec=f478fa67… spec=c625f6d9…
M1 · morreu · bin/forge-mutante:406
M2 · morreu · bin/forge-mutante:410 · (erro) o teste declarado deu erro sob o mutante e passa sem ele
M3 · morreu · bin/forge-mutante:363
M4 · morreu · bin/forge-mutante:367
M5 · morreu · bin/forge-mutante:369
M6 · morreu · bin/forge-mutante:371
M7 · morreu · bin/forge-mutante:416
M8 · morreu · bin/forge-mutante:424
M9 · morreu · bin/forge-mutante:433
M10 · morreu · bin/forge-mutante:508
M11 · morreu · bin/forge-mutante:512
M12 · morreu · bin/forge-mutante:800
```
Todos morreram, nenhum sobrevivente. Conferi a lista contra o diff: as linhas de guarda mudadas (`trocas`, os três ramos de `validar_spec`, `vezes_fora_de_uma`, `sufixo_do_trecho`, `linha_do_equivalente`, `mutar` com contagem e sobreposição, `desencontros_da_spec`) têm mutante; `--cobertura` confirma. M2 morre por erro com o controle verde, veredito válido.

## Observações
- A ordem das trocas no arquivo não importa: `mutar` ordena por posição e aplica do fim para o começo; a linha da saída é a do primeiro par declarado.
- `mutantes_do_diff` expande cada par em um mutante com o mesmo id (cobertura); a spec de uma troca passa pelo mesmo caminho sem mudar de forma.
