---
tipo: qa
contrato: 1
pedido: lote-mutante
branch: melhoria/lote-mutante
commit: 786505960a19cb0ec3ba4ae30f454031625e75c7
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-26
---
# QA: lote-mutante

Escopo: MUTANTE-TETO (várias specs por pedido) e MUTANTE-ID-ASCII (id de teste com identificador Python). Base b6eb84f, head 7865059. Pedido toca `bin/`: mutantes declarados conferidos contra o diff. PA-7 (`docs/engineering/achados-recorrentes.md`): sem itens.

## Achados
- A1 (bloqueante) bin/forge-mutante:382 · guarda mudada sem mutante declarado: `any("executor" not in dados ...)`; mutante à mão (`if False and`, `all(`) sobrevive e nenhum teste exercita a rota "sem executor e sem tests/test_*.py" (classe: guarda alterada sem mutante).
- A2 (bloqueante) bin/forge-mutante:212 · guarda nova `isinstance(teste, str)` sem mutante declarado; removida, spec com `"testes":[1]` quebra com AttributeError em vez de "spec inválida" rc 2, e nenhum teste cai (mutante sobrevive) (classe: guarda alterada sem mutante).
- A3 (recomendado) bin/forge-mutante:215 · `partes[0] == "tests"` sem mutante dedicado (o M6 troca só o `all(...)`); mutante à mão morreu, só falta declarar.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1 mais de uma spec, teto 8 por spec | ValidacaoDaSpec.test_varias_specs_do_pedido_passam_de_oito_sem_subir_o_teto_por_spec; Execucao.test_duas_specs_do_mesmo_pedido_rodam_juntas_com_o_hash_de_cada_uma | 8 por spec (9 recusa), 14 no total | passou |
| E1 pedido diferente, id repetido, conjunto vazio | test_varias_specs_com_pedido_diferente_ou_id_repetido_sao_invalidas | vazio, repetido | passou |
| E1 spec inválida barra tudo | Execucao.test_segunda_spec_invalida_barra_tudo_antes_de_rodar | permissão de rodar | passou |
| E2 id não ASCII válido, lixo recusado | ValidacaoDaSpec.test_id_de_teste_com_identificador_python_nao_ascii_e_valido; Execucao.test_teste_com_nome_nao_ascii_roda_e_mata | hífen, espaço, NBSP, dígito inicial, `tests` sozinho | passou |

## Cenários e resultado real
- `python3 -m unittest tests.test_forge_mutante`: 35 testes, OK.
- `bin/forge-mutante tests/mutantes/lote-mutante.json`: rc=0, M1..M7 morreram (linhas 228, 231, 225, 226, 222, 215, 215).
- Vermelho (`forge-testes --vermelho b6eb84f --modulos test_forge_mutante`): rc=0; provam 6 testes novos (4 por asserção, 2 por API ausente `validar_specs`), contagem `prova (API ausente)=2; prova (asserção)=4`; nenhum cai no HEAD.
- À mão, duas specs do mesmo pedido (4+8=12 mutantes, passa de 8): rc=1 só porque o mutante `NA` sobreviveu de propósito; os outros 11 morreram, ambos os hashes `spec=` impressos. `NA` usa o id real não ASCII `tests.test_forge_mutante.Veredito.test_falha_por_asserção_mata_e_tudo_verde_sobrevive`: aceito e executado.
- Pedido diferente: rc=2 "as specs são de pedidos diferentes"; mesma spec duas vezes: rc=2 "id repetido"; sem spec: rc=2.
- Mutantes extras à mão (7): X2 (`partes[0]`), X6 (só a primeira spec), X7 (só o hash da primeira) morreram; X1 (isinstance), X3 e X4 (linha do executor) sobreviveram; X5 (`if not args.spec`) sobrevive e é equivalente (spec vazia cai em "nenhuma spec", rc 2).
- Árvore do autor intocada; sondas em `$TMPDIR/qa-engineer-lote-mutante/`.

## Para a revalidação
Declarar os mutantes de A1, A2 e A3 em `tests/mutantes/lote-mutante.json` e somar os testes que os matem (spec sem `executor` num repositório sem `tests/test_*.py` sai 2 com "sem leitor de veredito"; `testes` com item não string é inválido, rc 2).
