---
tipo: qa
contrato: 1
pedido: v0457
branch: melhoria/escopo-ponto
commit: 0a0a7c808607535ddfe5e2eaf715a9340d7f8b8b
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

## Revalidação por delta c51ecb48..73e4848c (E23.51)
`forge-check parecer delta` lista no domínio: bin/forge-check, changelog.d, specs 3, 4 e 5 e tests/test_selo_e_entrega.py.
- review A4: o anexo do devops usa a etapa real `review` e o `Agente destino:` do brief é o papel do tipo; negativos `test_brief_do_review_nao_ancora_o_devops` e `test_brief_do_devops_nao_ancora_o_review` (M29, M30 morrem); a fixture `ParecerDoPortao` usa a etapa real.
- segurança A5: `veredito_trocado` olha todos os arquivos da pasta, com `branch:` igual, na base e em cada commit; rev-list ou ls-tree que falha conta como trocado. Negativos: `test_veredito_trocado_em_outro_arquivo_da_pasta_segue_fora`, `test_x_apagado_e_y_aprovado_no_mesmo_commit_segue_fora`, `test_ls_tree_que_falha_conta_como_veredito_trocado`, `test_rev_list_que_falha_conta_como_veredito_trocado`, `test_parecer_de_outra_branch_na_pasta_nao_troca_o_veredito` (M31 a M33), `test_arquivo_sem_frontmatter_na_pasta_nao_quebra_o_veredito` (M28).
- `forge-check pr` não mudou (fora do diff) e segue escolhendo por (data, nome); fica seguro só porque a entrega recusa o forjado. Registrado, não bloqueia.
- 635 linhas no teste (teto excedido): decisão do review/tech-lead, não é defeito de QA.

## Provas (delta E23.51, head 73e4848c, worktree destacada)
- `python3 -m unittest tests.test_selo_e_entrega`: 70 testes OK; `tests.test_conf_escopo`: 16 OK (um por vez).
- `forge-mutante` das 5 specs `v0457-escopo-ponto*`, uma por vez: M1 a M33 todos `morreu`, rc=0 em cada uma (M28 morre por erro do teste declarado, que passa sem o mutante).
- `forge-mutante --cobertura --base 8b5a44d5`: 26 linhas `coberta`, nenhuma sem mutante, rc=0.
- Vermelho: o delta só soma testes sobre código novo; cada um dos novos negativos é morto por mutante, sem teste que passe com o mutante vivo.

## Achados (delta)
Nenhum aberto.

## Revalidação por delta 73e4848c..0a0a7c80 (E23.55)
`forge-check parecer delta` lista no domínio: bin/forge-check, changelog.d, specs 3 e 5 e tests/test_selo_e_entrega.py.
- segurança A7 (S6): `veredito_trocado` roda `rev-list --full-history de..head -- <pasta>` (bin/forge-check:2345). Testes `test_merge_de_ramo_lateral_que_apaga_o_reprovado_segue_fora` e `test_merge_com_o_ramo_lateral_como_primeiro_pai_segue_fora` montam o S6 do parecer de segurança (x.md reprovado, y.md aprovado no ramo lateral com o mesmo `commit:`, merge --no-ff que apaga o x.md) nas duas ordens de pais e esperam `y.md` fora. M34 (tira o `--full-history`) morre nos dois.
- segurança A8 (S7): a busca é na pasta do portão do `tipo` (`PASTA_E_REGRA[tipo][0]`, :2344) com subpastas por `ls-tree -r` (:2349), parâmetro `tipo` novo. `test_parecer_em_subpasta_do_portao_com_o_reprovado_apagado_segue_fora` é o S7 (x.md apagado em commit anterior, `sub/y.md` aprovado com o mesmo `commit:`). M35 (volta a `Path(nome).parent`) morre nele.
- M28 (declarado, dá erro sob o mutante): conferido, o teste de arquivo sem frontmatter na pasta passa sem o mutante e morre com ele (spec 4 morreu=8).
- M20 e M22 mudaram só o trecho `de` (assinatura nova e `--full-history`), mesma guarda; seguem mortos.
- Fronteira nova: a busca já inclui subpasta e merge; o `forge-check pr` não mudou (cartão A9 da segurança, versão seguinte).
- 673 linhas na branch (teto excedido): decisão do review/tech-lead, vai para a versão seguinte; não é defeito de QA.

## Provas (delta E23.55, head 0a0a7c80, worktree destacada)
- `python3 -m unittest tests.test_selo_e_entrega`: 73 testes OK; `tests.test_conf_escopo`: 16 OK (um por vez).
- `forge-mutante` das 5 specs `v0457-escopo-ponto*`, uma por vez: rc=0 em cada; 8+8+8+8+3 = 35 `morreu` (M1 a M35), nenhum sobrevivente nem sem veredito.
- `forge-mutante --cobertura --base 8b5a44d5`: todas `coberta`, nenhuma sem mutante, rc=0.
- Vermelho: o delta soma testes sobre código novo; cada negativo novo é morto por mutante (M34, M35).

## Achados
Nenhum aberto.
