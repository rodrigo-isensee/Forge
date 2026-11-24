---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-clone-nome-unico
commit: d33eb54d678d9032d6901f733797534c6f625ab4
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-24
---
# QA: v0480-clone-nome-unico (E172.18, PR #860)

Escopo: `forge-check brief gerar` sugere a cópia só do agente destino (`copia_sugerida`, reusa `nome_unico` do `forge-copia`) e põe PREENCHER no lugar do id do pedido fora da forma (BRIEF-PEDIDO-ID-CRU). Diff conferido contra a base 5f1c6e97: `bin/forge-check`, `bin/forge-copia` (só docstring), `tests/test_forge_copia.py`, spec de mutantes e fragmento de changelog. Sem suíte local; a suíte inteira fica para o CI do PR.

## Critério → teste → resultado
| Critério (obrigação) | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| CLONE-NOME-UNICO: nome <branch-sem-prefixo>-<papel> na pasta das cópias | test_no_forge_o_nome_leva_branch_e_papel_na_pasta_das_copias | n/a | passou |
| nome tomado leva sufixo -2 | test_nome_tomado_sugere_o_seguinte_livre | destino ocupado | passou |
| papéis diferentes, cópias diferentes | test_papeis_diferentes_na_mesma_branch_tem_copias_diferentes | n/a | passou |
| projeto: pasta <projeto>/.forge/wt, também de dentro de uma cópia | test_no_projeto_a_pasta_e_a_do_projeto_tambem_de_dentro_de_uma_copia | raiz dentro de cópia | passou |
| branch ou papel fora da forma não sugere | test_branch_ou_papel_fora_da_forma_nao_sugere | branch com -, .., papel com crase, None | passou |
| forge-copia ausente não derruba o brief | test_sem_o_forge_copia_ao_lado_nao_sugere | arquivo ausente | passou |
| brief traz a linha da cópia | test_brief_gerado_traz_a_copia_sugerida | n/a | passou |
| caminho fora da forma de shell não entra no brief | test_brief_sem_a_linha_com_caminho_fora_da_forma | HOME com espaço | passou |
| sem --branch não sugere | test_brief_sem_branch_nao_sugere_copia | branch vazia | passou |
| BRIEF-PEDIDO-ID-CRU: id com crase vira PREENCHER | test_id_do_pedido_com_crase_nao_vai_cru_ao_brief | id fora da forma | passou |

## Cenários e resultado real
- `python3 -I -m unittest discover -s tests -p test_forge_copia.py`: 76 testes, OK. `test_pre_envio_brief.py` (consumidor do `fc`): 21 testes, OK.
- Vermelho (`bin/forge-testes --vermelho 5f1c6e977230b0f52655cf64c96eef7075d09603 --modulos test_forge_copia`):
  `vermelho: base=5f1c6e977230 head=d33eb54d678d módulos=test_forge_copia (restrito por --modulos)`
  contagem: não prova (passa na base)=68; prova (API ausente)=6; prova (asserção)=2. Os 10 testes novos: 8 provam; test_brief_sem_a_linha_com_caminho_fora_da_forma e test_brief_sem_branch_nao_sugere_copia passam na base (testes negativos, sem cópia sugerida na base) e são provados pelos mutantes M6 e M7, abaixo.
- Mutantes (`bin/forge-mutante tests/mutantes/v0478-clone-nome-unico.json`): `rev=d33eb54d678d`; M1..M7 morreram (M4 e M7 por erro do teste sob o mutante, com controle verde).
- Cobertura (`--cobertura --base 5f1c6e97`): `base=5f1c6e977230 mb=5f1c6e977230 rev=d33eb54d678d`; as 5 linhas de guarda mudadas (9527, 9537, 9567, 9627, 9628) estão cobertas (M1..M7); nenhuma sem mutante.
- Limite visto: a linha de `merge-integracao` (`forge-fechar {id_impresso}`) e o `except` de `copia_sugerida` por `SyntaxError`/`ImportError` não têm teste próprio; não é guarda de decisão, sem achado.
