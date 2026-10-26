---
tipo: qa
contrato: 1
pedido: lote-mutante
branch: melhoria/lote-mutante
commit: 0fb6a2cc0128c838928220be41bc16a837c3d2a0
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-26
---
# QA: lote-mutante

Escopo: revalidação (volta 1) de MUTANTE-TETO (várias specs por pedido) e MUTANTE-ID-ASCII (id de teste com identificador Python). Base b6eb84f, head 0fb6a2c. Pedido toca `bin/`: lista de mutantes conferida contra as guardas do diff. PA-7 (`docs/engineering/achados-recorrentes.md`): sem itens.

## Achados

## Fechamento dos achados do parecer cadf28c
- A1 (guarda `any("executor"...)`, bin/forge-mutante:384): FECHADO. Mutantes M11 (`all(`) e M12 (`if False and`) em `lote-mutante-2.json`, ambos mortos pelo teste `test_sem_executor_e_sem_testes_unittest_sai_2_em_qualquer_spec_do_conjunto`. Repetidos à mão no head: X3 e X4 derrubam 2 e 3 testes.
- A2 (guarda `isinstance(teste, str)`, :213): FECHADO. M10 morto por dois testes; à mão, X1 (`if False:`) derruba 5 testes (a falha agora é de asserção, não AttributeError).
- A3 (`partes[0] == "tests"`, recomendado): FECHADO. M8 declarado (:216); à mão, X2 (`True`) derruba 4 testes. Extras à mão: X5 (sem NFKC) derruba 2, X6 (sem `len(partes) > 1`) derruba 1.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1 mais de uma spec, teto 8 por spec | ValidacaoDaSpec.test_varias_specs_do_pedido_passam_de_oito_sem_subir_o_teto_por_spec; Execucao.test_duas_specs_do_mesmo_pedido_rodam_juntas_com_o_hash_de_cada_uma | 8 por spec (9 recusa) | passou |
| E1 pedido diferente, id repetido, conjunto vazio | test_varias_specs_com_pedido_diferente_ou_id_repetido_sao_invalidas | vazio, repetido | passou |
| E1 spec inválida barra tudo | Execucao.test_segunda_spec_invalida_barra_tudo_antes_de_rodar | rodar sem validar | passou |
| E2 id não ASCII válido, lixo recusado | test_id_de_teste_com_identificador_python_nao_ascii_e_valido; test_id_de_teste_que_nao_e_texto_ou_nao_normalizado_e_invalido; Execucao.test_teste_com_nome_nao_ascii_roda_e_mata | não texto, fora da NFKC, hífen, espaço, `tests` sozinho | passou |
| Rota sem executor e sem tests/test_*.py | Execucao.test_sem_executor_e_sem_testes_unittest_sai_2_em_qualquer_spec_do_conjunto | qualquer spec do conjunto sem executor | passou |
| `testes` com item não texto | Execucao.test_spec_com_testes_que_nao_sao_texto_sai_2_como_spec_invalida | tipo do item | passou |
| SKILL.md:85 várias specs | texto conferido (mais de 8 divide em `-<n>.json`, mesmo `pedido`, id único) | n/a | conforme |

## Cenários e resultado real
- `python3 -m unittest tests.test_forge_mutante`: 38 testes, OK.
- `bin/forge-mutante tests/mutantes/lote-mutante.json tests/mutantes/lote-mutante-2.json`: rc=0, M1 a M12 morreram, os dois hashes `spec=` impressos (rev 0fb6a2cc0128). Conferência lista × diff: cada linha de guarda mudada (validar_specs: pedido, id repetido, vazio, rótulo; id_de_teste_valido: isinstance, partes[0], isidentifier, NFKC; executor :384) tem mutante.
- Vermelho: `forge-testes --vermelho b6eb84f --modulos test_forge_mutante`: rc=0; cabeçalho `vermelho: base=b6eb84fed86e head=0fb6a2cc0128`; contagem `não prova (passa na base)=30; prova (API ausente)=3; prova (asserção)=5`; nenhum teste cai no HEAD. Os testes de A1 e A2 passam na base porque a guarda do executor e a do tipo já existiam em forma equivalente ou eram cobertas; quem os prova é o mutante (M10 a M12), não o vermelho.
- Mutantes à mão (6) em cópia descartável, todos mortos (X1 a X6, acima). Árvore do autor intocada; sondas em `$TMPDIR/qa-engineer-lote-mutante/`.
- Suíte completa não rodada por regra do brief (roda no pre-push).
