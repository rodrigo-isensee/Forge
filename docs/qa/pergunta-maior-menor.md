---
tipo: qa
contrato: 1
pedido: versao-033
branch: melhoria/pergunta-maior-menor
commit: 88c82dd4d4c97f004e0d273ef70c142f443e5c18
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-04
---
# QA: versao-033 (PERGUNTA-MAIOR-MENOR)

Links: não há `docs/ux` neste repositório; o critério vem do cartão (`docs/propostas/backlog/versao-0.34-triagem.md`) e do pedido de QA. Código testado: 88c82dd4d4c97f004e0d273ef70c142f443e5c18 (um commit sobre b45e40a). Entrega só de texto: escopo incremental, suíte completa não rodada. Review lido só pelo número do parecer; segurança não é deste parecer.

## Achados
- Nenhum.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| CA-1: a decisão do dono diz, em palavras, se o custo de cada opção fica maior ou menor que o das outras (cartão; dono 2026-10-22) | tests.test_pergunta_maior_menor.PerguntaMaiorMenor.test_regra_e_skill_pedem_dizer_se_o_custo_fica_maior_ou_menor | frase na regra `R-DECISAO`, no passo 4 da skill e nas três opções do exemplo (mais barata, mais cara, não dá para dizer) | passou; cai na base |
| CA-2: a regra vira invariante cobrado (`tests/config.json`) | tests.test_comportamento (lê o invariante novo de `R-DECISAO.md`) | invariante some se a frase sair | passou |

## Execução
- `python3 -I -m unittest discover -s tests -p test_pergunta_maior_menor.py`: 1 OK.
- `python3 -I -m unittest discover -s tests -p test_comportamento.py`: 6 OK, rc 0.
- Leitura do texto: R-DECISAO e passo 4 da skill pedem o dito em palavras ("a mais barata", "a mais cara", "igual"); o exemplo neutro traz as três situações e a conta confere (A, 3 milhões de tokens, é mais barata que B, 7 milhões; C não medido não é comparado). Entrega o cartão.
- `python3 -I tests/neutralidade.py` no head: rc 0, sem saída.
- Vermelho antes do verde: arquivos de texto trazidos a b45e40a na worktree qa-pergunta-maior-menor (`git checkout b45e40a -- <arquivos>`), teste rodado, árvore restaurada ao head e limpa. Falha observada na base, abaixo; no head, o teste passa.
- Base (R-DECISAO.md, modo-iniciante/SKILL.md e tests/config.json em b45e40a): `FAILED (failures=1)`, AssertionError: 'se esse custo fica maior ou menor que o das outras opções' not found in R-DECISAO.
- Bugs abertos: nenhum.
