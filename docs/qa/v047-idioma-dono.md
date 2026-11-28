---
tipo: qa
contrato: 1
pedido: v0474
branch: melhoria/v047-idioma-dono
commit: 8321ae381950e89c93d72fc8f2c906bb42f7c406
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-17
---
# QA: v0474 (idioma do dono e rodada que encerra)

## Achados
- A1 (recomendado) tests/evals/test_erros_por_papel.py:240 · o eval da fila falha hoje por `invalid choice: 'fila'` (rc 2) do argparse; ao nascer o subcomando, confira que o `expectedFailure` vira teste normal (o `unexpected success` avisa).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Mensagem em português não é acusada (controle) | MensagemEmOutroIdioma.test_controle_mensagem_em_portugues_passa | texto no idioma do dono, sem config | passou |
| Mensagem final em inglês é acusada (`outro_idioma` true, `en` vs `pt`) | MensagemEmOutroIdioma.test_mensagem_final_ao_dono_em_ingles_e_acusada | idioma diferente do dono | passou |
| Nota entre ferramentas (backlog) | MensagemEmOutroIdioma.test_nota_entre_ferramentas_em_ingles_e_acusada | nota antes de tool_use | expectedFailure, falha pela asserção |
| Fila do dono acima de 10 min (backlog) | RodadaQueNaoEncerra.test_mensagem_do_dono_presa_mais_de_10_min_e_acusada | 12 min acusa, 1 min não | expectedFailure, falha pela asserção |
| Texto da regra em skills/falar-com-o-dono | leitura do diff | n/a | presente (SKILL.md aponta; toda-mensagem.md traz as duas regras e a medida) |

## Cenários e resultado real
- `python3 -I -m unittest discover -s tests/evals -p test_erros_por_papel.py -v` (TMPDIR do sandbox): `Ran 18 tests ... OK (expected failures=4)`; os 4 são os 2 anteriores do arquivo e os 2 novos.
- Sem o decorador, em execução isolada: o da nota dá `AssertionError: False is not true` (o hook mede só a mensagem final); o da fila dá `AssertionError: 2 != 0`, saída do argparse `invalid choice: 'fila'`. Nenhum cai por exceção do teste.
- Controle verde existe onde cabe: idioma tem o controle em português; o eval da fila não tem controle verde (decisão do pedido: todo expectedFailure, a ferramenta não existe).
- O texto é só em português, sem termo de projeto. Suíte completa: fica ao check-run `bateria` do PR; não rodada aqui.
