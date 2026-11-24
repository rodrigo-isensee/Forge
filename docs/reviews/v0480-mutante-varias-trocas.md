---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-mutante-varias-trocas
commit: e18a5b07c706a2e559c6dabb5b17fb357b51097e
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0478 (E162.2, PR #846, mutante com várias trocas)

## Escopo lido
Diff `0733715a..e18a5b07`: `bin/forge-mutante` (+55/-22 no código, dentro do teto H1), duas specs novas (`v0480-mutante-varias-trocas.json` M1-M12 e `-2.json`), realinhamento de CF5 (`v047-mutante-avisos.json`) e M6 (`vel-p1p10.json`), 5 testes novos em `tests/test_forge_mutante.py` e o fragmento do changelog.

## Conferências
- **Spec de uma troca segue igual:** `trocas()` devolve `[(de, para)]` quando os dois são texto; validação, `mutar`, `linha_do_equivalente` e `desencontros_da_spec` caem no mesmo caminho de antes, e `sufixo_do_trecho` só acrescenta o trecho na mensagem quando há mais de um par. Lista de 1 par, tamanhos diferentes, lista com texto e mais de 8 pares são recusados (teste `test_varias_trocas_em_listas_do_mesmo_tamanho_valem_e_o_resto_e_invalido`). Os testes antigos de uma troca seguem verdes sem edição.
- **CF5 realinhado:** mesma guarda (`!= 1` em `desencontros_da_spec`, zero ocorrências é desencontro), mesma troca (`!= 1` → `> 1`) e o mesmo teste; só o `m["de"]` virou `de` do laço. Rodado: `CF5 · morreu · bin/forge-mutante:800`.
- **M6 realinhado:** a guarda "trecho do equivalente que não aparece uma vez é inválido" saiu de `linha_do_equivalente` para `vezes_fora_de_uma`, que ela chama; mesma troca (`!= 1` → `< 1`) e o mesmo teste do equivalente com trecho repetido. Rodado: `M6 · morreu · bin/forge-mutante:416`. A função agora também serve `mutar`, e a direção oposta (`> 1`) é a M7 da spec nova.
- **Guardas do diff:** cada linha de guarda nova ou mudada (`trocas`, `validar_spec`, `vezes_fora_de_uma`, `sufixo_do_trecho`, `linha_do_equivalente`, `mutar` com a sobreposição, `desencontros_da_spec`) tem um mutante declarado com teste de comportamento do ramo de falha. `--cobertura` expande cada par como mutante do mesmo id só em `mutantes_do_diff`, que só a cobertura usa; a execução aplica as trocas juntas, do fim para o começo, com a sobreposição recusada antes.
- **Ferramentas:** `bin/forge-mutante --conferir --base 0733715a` → `conferidas: o trecho de cada spec do diff está no lugar`. `python3 -m unittest tests.test_forge_mutante` → `Ran 151 tests ... OK` (módulo tocado; sem suíte local).
- **CI do PR #846 no head e18a5b07:** no momento do review, catraca, bateria (passos), bateria (verificações longas), instalação e suíte 3.12 parte 5/5 verdes; as demais partes da suíte pendentes; `bateria (pareceres)` vermelha por falta dos pareceres, que este commit começa a suprir. O merge segue preso ao CI verde (`R-FLUXO`).

## Parecer
Aprovado. Faz o que a E162.1 pede (várias trocas juntas para guardas que se cobrem), sem mudar a spec de uma troca; os realinhamentos de CF5 e M6 provam a mesma guarda com o mesmo teste, e os dois mutantes morrem no head revisado. Sem achados.
