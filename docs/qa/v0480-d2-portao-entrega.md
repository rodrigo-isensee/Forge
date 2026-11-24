---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-d2-portao-entrega
commit: 5cac29190646ed60b36cfe8f704b948bc920ee69
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-24
---
# QA: v0478 E173.23 (PR #864, delta da volta E173.16, head 5cac2919)

Escopo: delta do head reprovado d64a506b para 5cac2919: `patches/d2-portao-entrega.patch` (`d2_so_avisa`), `tests/test_pre_push_d2.py` (de 15 para 22 testes), specs `tests/mutantes/v0480-d2-portao-entrega.json` e `-2.json` (16 mutantes). Sem UX (pedido de controle do Forge).

## Reteste dos achados anteriores
| Achado | O que mudou | Resultado |
|---|---|---|
| A1 (hooks/ e scripts/ sozinhos no índice) | M1 e M2 | morreram |
| A2 (guarda da ponta != HEAD) | M3, teste `Ponta.test_branch_cuja_ponta_nao_e_o_head_nao_e_conferida` | morreu |
| A3 (filtro refs/heads/) | M4, teste `Ponta.test_ref_fora_de_refs_heads_nao_e_conferida` | morreu |
| A4 (spec de mutantes do autor) | duas specs, um mutante por guarda | atendido |

Guardas novas da volta (envio só de parecer só avisa): M5 (fora de docs/{reviews,qa,security,devops}/ ou delta vazio barra), M6 (índice só avisa), M7 (teto e texto do PR só avisam). Todas mortas. Ref nova ou sha remoto desconhecido barra (`SoParecer.test_ref_nova_ou_sha_remoto_desconhecido_barra`): fronteira correta, o delta vazio cai fora da fronteira.

## Critério → teste → resultado (só o que mudou)
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Índice confere com hooks/ ou scripts/ sozinhos | Indice (subTest por pasta) | pasta tocada | passou, M1 e M2 mortos |
| Ref com ponta fora do HEAD não é conferida | Ponta.test_branch_cuja_ponta_nao_e_o_head_nao_e_conferida | ponta ≠ HEAD | passou, M3 morto |
| Tag ou ref fora de refs/heads/ não é conferida | Ponta.test_ref_fora_de_refs_heads_nao_e_conferida | ref não-branch | passou, M4 morto |
| Envio só de parecer só avisa (índice, teto, texto do PR) | SoParecer.* | fronteira docs/{reviews,qa,security,devops}/ | passou, M5 a M7 mortos |
| Arquivo fora dos pareceres, ref nova ou sha desconhecido barra | SoParecer.test_delta_com_arquivo_fora_dos_pareceres_barra, test_ref_nova_ou_sha_remoto_desconhecido_barra | delta vazio, arquivo fora | passou |

Os 13 critérios do parecer anterior seguem cobertos e verdes (mesmo módulo).

## Cenários e resultado real
- `python3 -I -m unittest discover -s tests -p test_pre_push_d2.py`: 22 testes, OK (18,4 s).
- `bin/forge-mutante tests/mutantes/v0480-d2-portao-entrega.json tests/mutantes/v0480-d2-portao-entrega-2.json --processos 3`: M1 a M16 todos `morreu`, rc 0 (`rev=5cac29190646`).
- `--cobertura` não se aplica: o arquivo mudado é um `.patch`, não Python; conferi à mão que cada linha de guarda do diff (`d2_so_avisa`, duas chamadas, ponta, ref, índice) tem mutante.
- Vermelho antes do verde: o módulo não existe na base, então `forge-testes --vermelho` não dá veredito (igual à rodada anterior); a prova é o mutante morto por teste, com o controle verde.
- CI: ao conferir, o run do sha ainda estava em andamento (check-run `bateria` sem conclusão); não o cito como prova. Suíte completa não rodada local (brief).
