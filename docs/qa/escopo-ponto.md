---
tipo: qa
contrato: 1
pedido: v0457
branch: melhoria/escopo-ponto
commit: c51ecb4847bcac295a72bf42f0dec8ab44f1538e
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-12
---
# QA: escopo-ponto (E23.35)

Diff 8b5a44d5..ba359573: bin/forge-check (cinco defeitos da conferência de entrega, E23.17 a-c e E23.36 d-e), 2 módulos de teste e 3 specs de mutantes. Sem especificação de UX nem contrato de API: as obrigações são os cinco defeitos do pedido.

## Obrigação, teste, resultado
| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| (a) ponto inicial do caminho fica | PontoInicial.test_caminho_com_ponto_inicial_e_pontuacao_final | `.github/` com pontuação final | verde; vermelho na base |
| (b) volta herda o escopo dos briefs anteriores | VoltaNaMesmaBranch (5 testes) | outra branch, outro pedido, outra etapa não entram | verde; 2 provam na base, 3 negativos passam na base de propósito |
| (c) pareceres pelo pedido do brief | PareceresPeloPedido (3) | id diferente do nome do arquivo; outro pedido segue reprovando | verde; 2 provam na base |
| (d) parecer de portão da branch é anexo | ParecerDoPortao (5) | outra branch, outro pedido, sem frontmatter, sem commit revisado | verde; 1 prova na base; ver A1 |
| (e) intervalo parte do merge-base | MergeDaBaseDepoisDoBrief (4) | head já na develop, base fora da branch, arquivo da develop mudado | verde; 1 prova na base |

## Provas
- Classes rodadas uma por vez: PontoInicial 1 OK, VoltaNaMesmaBranch 5 OK, PareceresPeloPedido 3 OK, ParecerDoPortao 5 OK, MergeDaBaseDepoisDoBrief 4 OK.
- Vermelho: `forge-testes --vermelho 8b5a44d5 --modulos tests.test_selo_e_entrega,tests.test_conf_escopo --prazo 500` abre com `vermelho: base=8b5a44d5ffd5 head=ba3595736842`, bin/forge-check revertido à base; contagem: `não prova (passa na base)=59; prova (asserção)=7`; nenhum teste cai no HEAD. Os 7 que provam cobrem os 5 defeitos; os negativos passam na base por serem proteção do que não muda.
- Mutantes: `forge-mutante` das 3 specs, 17 mutantes (M1 a M17), todos `morreu`, rc=0. `--cobertura --base 8b5a44d5` lista as 11 linhas de condição mudadas como cobertas.
- Falha de ambiente: a primeira rodada de `--vermelho` sem `--modulos` estourou o prazo de 590 s sob load 14 a 22 (sem veredito, não vale como vermelho); repetida restrita aos dois módulos.

## Revalidação por delta ba359573..c51ecb48 (E23.43)
- A1 resolvido: M18 a M20 (tipo, parecer, veredito) e M21 a M23 morrem; testes novos `test_tipo_de_outra_pasta_segue_fora`, `test_parecer_sem_veredito_valido_segue_fora`.
- Âncoras novas, caso negativo de cada uma: brief selado do portão (`test_commit_sem_brief_selado_do_portao_segue_fora`, `test_brief_do_portao_de_outra_etapa_ou_pedido_nao_ancora`), troca de veredito no mesmo commit (`test_veredito_trocado_no_mesmo_commit_segue_fora`, `test_git_que_falha_conta_como_veredito_trocado`), merge-base (`test_brief_selado_sem_base_sha_nao_conta_como_ancora`, `test_merge_base_sem_ancora_fica_o_base_sha`, `test_brief_selado_antes_do_da_entrega_nao_ancora`, `test_origin_develop_reescrita_nao_move_o_intervalo`), pedido por branch (`test_parecer_de_outra_branch_com_o_id_nao_troca_o_slug`), VV-3 (`test_vv3_confere_o_caminho_com_o_ponto_inicial`).
- Fora do escopo, vira cartão (sem bloquear): os filtros L08/G2 também confiam na `origin/develop` local.

## Provas
- `python3 -m unittest tests.test_selo_e_entrega`: 62 testes OK; `tests.test_conf_escopo`: 16 OK (um por vez, worktree destacada no head c51ecb48).
- `forge-mutante` das 4 specs `v0457-escopo-ponto*`: M1 a M28, todos `morreu`, rc=0.
- `forge-mutante --cobertura --base 8b5a44d5`: 24 linhas de condição mudadas, todas `coberta`, nenhuma sem mutante.
- Vermelho: o do delta anterior (59 passam na base de propósito, 7 provam) segue; o delta só soma testes sobre código novo, sem teste que passe sem ele nos mutantes.

## Achados
Nenhum aberto. A1 (antigo) resolvido no c51ecb48.
