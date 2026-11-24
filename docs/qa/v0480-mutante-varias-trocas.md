---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-mutante-varias-trocas
commit: c102d6403eeccd5c7dce72fd6ca72abdabb51d0a
parecer: aprovado
escopo: incremental
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

## Delta da volta (E162.7): e18a5b07..3671c052
Mudou no domínio do QA: `bin/forge-mutante` (`par_que_nao_sobrevive`: o mutante de várias trocas que morre só vale se cada par, sozinho e com os mesmos testes, sobrevive; senão `inválido`, rc 2), 2 testes novos em `tests/test_forge_mutante.py` (par-isca que morre sozinho, sondas S2 e S3 do #846; par que não roda sozinho) e as specs `v0480-mutante-varias-trocas-2.json` (M9 a M16) e `-3.json` (M17, M18). Sem UX nem contrato de API.

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Par-isca que morre sozinho invalida o conjunto morto | `Execucao.test_par_isca_que_morre_sozinho_torna_o_mutante_invalido` | par 2 morre sozinho (S2: troca de retorno; S3: troca de outra guarda); sem cópia sobrando | passou; vermelho na base; M13 a M18 morreram |
| Par que não roda sozinho (sintaxe quebrada) é inválido | `Execucao.test_par_que_nao_roda_sozinho_torna_o_mutante_invalido` | cada par é válido só junto | passou; vermelho na base |

Vermelho: `bin/forge-testes --vermelho e18a5b07 --modulos test_forge_mutante` (base = head do parecer anterior, código sem a correção, testes mantidos). Saída: `contagem: não prova (passa na base)=151; prova (asserção)=2`; os 151 já existentes (incluindo os 5 do parecer anterior) seguem passando no HEAD, nenhum caiu.

Mutação do delta: `bin/forge-mutante <spec-1> <spec-2> <spec-3> --processos 3 --ids M13,M14,M15,M16,M17,M18` (rev=3671c05271cd), rc 0:
```
M13 · morreu · bin/forge-mutante:977
M14 · morreu · bin/forge-mutante:979
M15 · morreu · bin/forge-mutante:992
M16 · morreu · bin/forge-mutante:996
M17 · morreu · bin/forge-mutante:995
M18 · morreu · bin/forge-mutante:997
```
Conferi contra o diff: as linhas de guarda novas (condição `morreu` com mais de uma troca, retorno do motivo, `not motivo`, a classe do par, o texto de morre sozinho) têm mutante; sem sobrevivente.

`forge-mutante --conferir --todas` no head: 26 linhas e rc 1, igual ao parecer anterior (as 26 specs antigas com `de` repetido, anteriores ao PR); nenhuma spec nova entrou. Sem suíte local; a inteira roda no CI do PR (`R-QA`).

## Delta da 2ª volta (E162.11): 3671c052..191484ef
Mudou no domínio do QA: `bin/forge-mutante` (`MAXIMO_DE_TROCAS` de 8 para 2, mensagem "de 2 pares"), o teste de validação ajustado (3 pares agora inválido, 8 pares removido), 1 teste novo (`Execucao.test_isca_de_tres_pares_e_recusada_antes_de_rodar`, sonda S4 do #846: rc 2, "spec inválida; nada foi executado", nada rodou) e o M19 na spec `-3`. Sem UX nem contrato de API.

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Isca de 3 pares (cada par sobrevive sozinho, o conjunto morre) é recusada antes de rodar | `Execucao.test_isca_de_tres_pares_e_recusada_antes_de_rodar` | 3 pares, logo acima do teto; sem cópia em `$TMPDIR`; sem "morreu" | passou; vermelho na base; M19 morreu |
| Só 2 pares valem; 1, 3, tamanhos diferentes e o resto são inválidos | `ValidacaoDaSpec.test_varias_trocas_em_listas_do_mesmo_tamanho_valem_e_o_resto_e_invalido` | 1, 2 e 3 pares | passou; vermelho na base; M19 e M1 morreram |

Vermelho: `bin/forge-testes --vermelho 3671c052 --modulos test_forge_mutante` (4 min 2 s; base = head do parecer anterior). Fim da saída: `contagem: não prova (passa na base)=152; prova (asserção)=2`; um deles: `tests.test_forge_mutante.ValidacaoDaSpec.test_varias_trocas_em_listas_do_mesmo_tamanho_valem_e_o_resto_e_invalido · H=ok · B=falha · prova (asserção)`; o outro é o teste novo da isca de 3 (os dois únicos novos ou mudados). Nenhum caiu no HEAD.

Mutação: `bin/forge-mutante <spec-1> <spec-2> <spec-3> --processos 3 --ids M1,M19`, rc 0:
```
forge-mutante: pedido=v0480-mutante-varias-trocas rev=191484effc2a spec=f478fa67… spec=3b9ea228… spec=626e3bfe…
M1 · morreu · bin/forge-mutante:409
M19 · morreu · bin/forge-mutante:135
```
Conferi contra o diff: a única linha de guarda mudada é o teto (L135); a mensagem de L367 é texto e o teste novo a afirma. Sem sobrevivente.

`forge-mutante --conferir --todas` no head: 26 linhas e rc 1, igual ao parecer anterior (as 26 specs antigas com `de` repetido); nenhuma spec nova entrou. Sem suíte local; a inteira roda no CI do PR (`R-QA`).

## Delta da 3ª volta (E162.15): 191484ef..c102d640
Mudou no domínio do QA: `bin/forge-mutante` (`par_com`: a saída do mutante de 2 pares e a `coberta` do `--cobertura` nomeiam o outro par, `(par com <arquivo>:<linha>)`, A3 da segurança do #846), 1 teste novo e 3 ajustados em `tests/test_forge_mutante.py`, specs `v0480-mutante-varias-trocas-3.json` (M20 a M23) e `v0478-mutante-pulado.json` (P6 realinhado a `{onde}`). Sem UX nem contrato de API.

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| `par_com` nomeia só o trecho presente e some sem nenhum | `Cobertura.test_par_com_nomeia_so_o_trecho_presente_e_some_sem_nenhum` | trecho ausente, só ausentes, lista vazia | passou; vermelho (API ausente na base); M20 e M21 morreram |
| Mutante de 2 pares que morre nomeia as duas linhas | `Execucao.test_par_escudo_que_morre_nomeia_as_duas_linhas` | par-escudo (outra condição) sai com as duas linhas | passou; vermelho na base; M20 e M22 morreram |
| `coberta` do `--cobertura` nomeia o outro par | `Cobertura.test_cada_troca_do_mutante_de_varias_cobre_a_sua_condicao` (ajustado) | o par é o outro, não o próprio | passou; vermelho na base; M23 morreu |
| Saídas inválidas e sem veredito mantêm o sufixo | `test_par_isca_que_morre_sozinho...`, `test_par_que_nao_roda_sozinho...` (ajustados) | linha com `(par com ...)` em inválido | passaram; vermelho na base; P6 morreu |

Vermelho: `bin/forge-testes --vermelho 191484ef --modulos test_forge_mutante` (165 s). A saída abre com `vermelho: base=191484effc2a head=c102d6403eec módulos=test_forge_mutante (restrito por --modulos)` e fecha com `contagem: não prova (passa na base)=151; prova (API ausente)=1; prova (asserção)=4`, rc 0; nenhum teste caiu no HEAD.

Mutação do delta, rc 0 nas duas chamadas (uma por pedido):
```
forge-mutante: pedido=v0480-mutante-varias-trocas rev=c102d6403eec spec=f478fa67… spec=3b9ea228… spec=8b7d2b65…
M20 · morreu · bin/forge-mutante:436
M21 · morreu · bin/forge-mutante:437
M22 · morreu · bin/forge-mutante:981
M23 · morreu · bin/forge-mutante:768
forge-mutante: pedido=v0478-mutante-pulado rev=c102d6403eec spec=06898d33…
P6 · morreu · bin/forge-mutante:988
```
Conferi contra o diff: as linhas de guarda novas (`par_com` com filtro e retorno vazio, `onde` só com par, `par` da expansão no `--cobertura`) têm mutante; sem sobrevivente.

`forge-mutante --conferir --todas`: head c102d640 e base 191484ef dão a mesma saída (`diff` vazio), 26 linhas e rc 1 nos dois; são as 26 specs antigas com `de` repetido, anteriores ao PR. Sem suíte local; a inteira roda no CI do PR (`R-QA`).
