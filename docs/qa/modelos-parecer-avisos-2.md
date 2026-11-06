---
tipo: qa
contrato: 1
pedido: versao-033
branch: melhoria/modelos-parecer-avisos-2
commit: 98eb919fd70863a829ce8323c9b98ae0317c5894
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-04
---
# QA: versao-033 (MODELOS-PARECER-AVISOS-2)

Links: não há `docs/ux` neste repositório; o critério vem do cartão (`docs/propostas/backlog/versao-0.34-triagem.md`) e do pedido de QA. Código testado: 98eb919fd70863a829ce8323c9b98ae0317c5894 (um commit sobre b45e40a). Entrega só de texto: escopo incremental, suíte completa não rodada. Review lido só pelo número do parecer; segurança não é deste parecer.

## Achados
- Nenhum.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| CA-1: os quatro modelos de parecer dizem se o teto de 300 conta o prefixo (não conta) | tests.test_modelos_parecer_avisos_2.ModelosDeParecer.test_teto_de_300_diz_que_o_prefixo_nao_conta | os quatro caminhos (reviews, qa, security do projeto e security do Forge); `assertEqual(len, 4)` guarda a lista | passou; cai na base |
| CA-2: o modelo de segurança do Forge avisa da neutralidade, e o do projeto não | tests.test_modelos_parecer_avisos_2.ModelosDeParecer.test_modelo_de_seguranca_do_forge_avisa_da_neutralidade | aviso só em `docs/security/_modelo.md`; `assertNotIn` no modelo de projeto | passou; cai na base |

## Execução
- `python3 -I -m unittest discover -s tests -p test_modelos_parecer_avisos_2.py`: 2 OK.
- `python3 -I -m unittest discover -s tests -p test_modelos_projeto.py`: 6 OK; `python3 -I bin/forge-check docs`: rc 0.
- A afirmação "o prefixo não conta" confere com `bin/forge-check:1471`: o teto de 300 mede só o grupo 5 da regex `ACHADO` (o texto depois do ` · `).
- `python3 -I tests/neutralidade.py` no head: rc 0, sem saída.
- Vermelho antes do verde: arquivos de texto trazidos a b45e40a na worktree qa-modelos-parecer-avisos-2 (`git checkout b45e40a -- <arquivos>`), teste rodado, árvore restaurada ao head e limpa. Falha observada na base, abaixo; no head, o teste passa.
- Base (os quatro modelos em b45e40a): `FAILED (failures=2)`; AssertionError: 'o prefixo `A<n> (...) <arquivo>:<linha>` não conta' not found (modelo de review) e 'o parecer não cita nome de linguagem' not found (modelo de segurança do Forge).
- Bugs abertos: nenhum.
