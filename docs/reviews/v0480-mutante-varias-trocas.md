---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-mutante-varias-trocas
commit: 3671c05271cd1760044a2bdc874b064cd28e835a
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0478 (E162.2 e E162.6, PR #846, mutante com várias trocas)

## Escopo lido
Diff `0733715a..e18a5b07`: `bin/forge-mutante` (+55/-22 no código, dentro do teto H1), duas specs novas (`v0480-mutante-varias-trocas.json` M1-M12 e `-2.json`), realinhamento de CF5 (`v047-mutante-avisos.json`) e M6 (`vel-p1p10.json`), 5 testes novos em `tests/test_forge_mutante.py` e o fragmento do changelog.

## Conferências
- **Spec de uma troca segue igual:** `trocas()` devolve `[(de, para)]` quando os dois são texto; validação, `mutar`, `linha_do_equivalente` e `desencontros_da_spec` caem no mesmo caminho de antes, e `sufixo_do_trecho` só acrescenta o trecho na mensagem quando há mais de um par. Lista de 1 par, tamanhos diferentes, lista com texto e mais de 8 pares são recusados (teste `test_varias_trocas_em_listas_do_mesmo_tamanho_valem_e_o_resto_e_invalido`). Os testes antigos de uma troca seguem verdes sem edição.
- **CF5 realinhado:** mesma guarda (`!= 1` em `desencontros_da_spec`, zero ocorrências é desencontro), mesma troca (`!= 1` → `> 1`) e o mesmo teste; só o `m["de"]` virou `de` do laço. Rodado: `CF5 · morreu · bin/forge-mutante:800`.
- **M6 realinhado:** a guarda "trecho do equivalente que não aparece uma vez é inválido" saiu de `linha_do_equivalente` para `vezes_fora_de_uma`, que ela chama; mesma troca (`!= 1` → `< 1`) e o mesmo teste do equivalente com trecho repetido. Rodado: `M6 · morreu · bin/forge-mutante:416`. A função agora também serve `mutar`, e a direção oposta (`> 1`) é a M7 da spec nova.
- **Guardas do diff:** cada linha de guarda nova ou mudada (`trocas`, `validar_spec`, `vezes_fora_de_uma`, `sufixo_do_trecho`, `linha_do_equivalente`, `mutar` com a sobreposição, `desencontros_da_spec`) tem um mutante declarado com teste de comportamento do ramo de falha. `--cobertura` expande cada par como mutante do mesmo id só em `mutantes_do_diff`, que só a cobertura usa; a execução aplica as trocas juntas, do fim para o começo, com a sobreposição recusada antes.
- **Ferramentas:** `bin/forge-mutante --conferir --base 0733715a` → `conferidas: o trecho de cada spec do diff está no lugar`. `python3 -m unittest tests.test_forge_mutante` → `Ran 151 tests ... OK` (módulo tocado; sem suíte local).
- **CI do PR #846 no head e18a5b07:** no momento do review, catraca, bateria (passos), bateria (verificações longas), instalação e suíte 3.12 parte 5/5 verdes; as demais partes da suíte pendentes; `bateria (pareceres)` vermelha por falta dos pareceres, que este commit começa a suprir. O merge segue preso ao CI verde (`R-FLUXO`).

## Revalidação E162.6 (volta E162.5, head 3671c052)
Delta lido: `forge-check parecer delta docs/reviews/v0480-mutante-varias-trocas.md`, intervalo `e18a5b07..3671c052`; no domínio: `bin/forge-mutante`, `changelog.d/v0480-mutante-varias-trocas.md`, `tests/mutantes/v0480-mutante-varias-trocas-2.json` (M13-M16), `tests/mutantes/v0480-mutante-varias-trocas-3.json` (M17-M18, novo) e `tests/test_forge_mutante.py` (2 testes novos).
- **A1 da segurança (par-isca):** `provar` (`bin/forge-mutante:977`) chama, no mutante de várias trocas morto, `par_que_nao_sobrevive` (`:985`): cada par sozinho na cópia do mutante restaurada do commit, com os mesmos testes e `erro_mata=True`; o par que morre, sai sem veredito ou não aplica sozinho torna o mutante `inválido` (rc 2). A cópia é só do mutante e é descartada (o teste confere `$TMPDIR` vazio). As sondas S2 e S3 viraram `test_par_isca_que_morre_sozinho_torna_o_mutante_invalido`; o par que quebra a sintaxe sozinho, `test_par_que_nao_roda_sozinho_torna_o_mutante_invalido`. Custo: N+1 rodadas só para mutante de lista morto, até 8 pares.
- **Guardas do delta:** uma por linha, M13 (`> 1`), M14 (`if sozinho`), M15 (`if motivo`), M16 (`!= "sobreviveu"`), M17 (`registro is None`), M18 (texto do motivo); `-2.json` fica em 8 mutantes e o resto foi para `-3.json`. O commit `3671c052` só tira a repetição de `m["testes"], trabalho / f"` para o trecho do M9 da v0457 seguir único.
- **Ferramentas no head 3671c052:** `python3 -m unittest tests.test_forge_mutante` → `Ran 153 tests ... OK`; `bin/forge-mutante --conferir --base 0733715a` → `conferidas: o trecho de cada spec do diff está no lugar`; `bin/forge-mutante tests/mutantes/v0480-mutante-varias-trocas-2.json --ids M13,M14,M15,M16` → os quatro `morreu` (`:977`, `:979`, `:992`, `:996`); `bin/forge-mutante tests/mutantes/v0480-mutante-varias-trocas-3.json` → `M17 · morreu · bin/forge-mutante:995` e `M18 · morreu · bin/forge-mutante:997`; `--cobertura --base e18a5b07` rc 0. Nenhuma spec do repositório usa a forma em lista hoje, então a regra nova não invalida mutante existente. Código do delta: +20 linhas, dentro do teto H1. Suíte inteira: CI do PR #846.

## Parecer
Na E162.2 (head e18a5b07), aprovado: faz o que a E162.1 pede (várias trocas juntas para guardas que se cobrem), sem mudar a spec de uma troca; os realinhamentos de CF5 e M6 provam a mesma guarda com o mesmo teste, e os dois mutantes morrem no head revisado. Na revalidação E162.6, reprovado no head 3671c052: o par-isca de 2 pares está fechado, com teste de abuso e um mutante por guarda, mas a checagem só de cada par sozinho não prova que todo par é necessário com 3 ou mais pares (A1 abaixo, o mesmo defeito do A2 da segurança no mesmo head, `docs/security/v0480-mutante-varias-trocas.md`, sonda S4). Na volta, a correção mais simples é limitar `MAXIMO_DE_TROCAS` a 2, o que torna a checagem atual suficiente; se 3+ pares forem precisos, cada conjunto sem o par n também tem de sobreviver, com a S4 como teste em `Execucao` e mutante na guarda nova.

## Achados
- A1 (bloqueante) bin/forge-mutante:989 · com 3+ pares [guarda sem teste, A, B], A e B se cobrindo, cada par sobrevive sozinho e o conjunto morre por A+B: sai `morreu` na linha da guarda sem teste (rc 0). Mesmo defeito do A2 da segurança (S4). Correção: limitar a 2 pares ou exigir que o conjunto sem cada par sobreviva.
