---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-conferencia-patch-dono
commit: c793d6eae3908b56c6df2756c3e8dcdaf308d9c9
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-13
---
# QA: v047 · conferência aceita o patch do dono (E1.2, parecer E1.17)

Pedido de correção sem especificação de UX: as obrigações são a E1.2 do pedido e as ameaças P1-P12 / casos C1-C15 citados no código e no teste.

## Achados
- A1 (recomendado) tests/mutantes/v047-conferencia-patch-dono-2.json:2 · as três specs trazem `pedido` diferente (`...-2`, `...-3`); `forge-mutante` das três juntas sai "specs de pedidos diferentes" e nada roda. Use o mesmo `pedido` com id único; rodei uma a uma.
- A2 (recomendado) bin/forge-check:1690 · o comentário remete a docs/security/v047-e1-ameacas.md, que não existe na branch nem na develop; a rastreabilidade P1-P12 fica sem alvo no repositório.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1.2: arquivo do dono declarado (Histórico + DECISÃO + sha40 + caminho) não reprova | PatchDoDono.test_c_leg_nome_commit_e_decisao_cumprem | sem declaração reprova antes, ok depois | passou |
| Declaração incompleta ou fora da forma não isenta (C1, C2, C3, C5, C10) | test_declaracao_que_nao_isenta (14 subcasos) | sha curto, maiúsculo, HEAD~1, blob, inexistente; pasta, curinga, `./`, `//`; caminho mais longo | passou |
| Conteúdo, modo ou symlink/submódulo mudado depois do commit do dono (C6, C7) | test_c6_c7_... | blob e modo iguais ao do commit | passou |
| Commit solto ou de merge (C9, C14) | test_c9_c14_... | fora da branch, 2 pais | passou |
| Commit já na base (C8) | test_c8_commit_ja_na_base | ancestral do Base-sha | passou |
| Só o arquivo que o commit altera (C11) | test_c11_... | commit sem o arquivo | passou |
| Parecer, aceite, oráculo e pedido nunca isentam (C4, C13) | test_c4_c13_... | lista de caminhos proibidos | passou |
| Git que falha reprova (C15) | test_c15_git_que_falha_reprova | ls-tree e rev-list com rc 1 | passou |

## Cenários e resultado real
- `python3 -m unittest tests.test_conf_escopo`: 19 testes, OK (carga ~18 em 12 CPUs; a suíte inteira fica para o CI do PR, que ainda não existe).
- Vermelho antes do verde (`forge-testes --vermelho origin/develop --modulos test_conf_escopo`; a 1ª tentativa, sem `--modulos`, estourou o prazo de 550 s sob carga, sem veredito, e foi repetida restrita ao módulo alterado), rc 0:
  - os 8 testes de `PatchDoDono` provam: 6 por asserção, 2 por API ausente (`isencao_do_dono`); H=ok em todos.
  - 11 testes herdados "não prova (passa na base)", sem relação com o diff.
- Mutação (`forge-mutante`, uma spec por vez, rc 0 nas três): spec 1 M1-M8 morreram; spec 2 M1-M8 morreram; spec 3 M1-M7 morreram. 23 de 23 mortos, nenhum sobrevivente, nenhum equivalente.
- `forge-mutante --cobertura --base a986c292`: 21 condições mudadas, todas "coberta" por ao menos um mutante (1700-1765 e 2572), nenhuma `não coberta`. Linha de guarda mudada sem mutante: nenhuma.
- Bugs abertos: nenhum. Acessibilidade e E2E: n/a (ferramenta de linha de comando).

## Revalidação por delta 69bd4863..c793d6ea (E1.32, junção com a develop #517 e #522)
- `forge-check parecer delta`: domínio `bin/forge-check` e `tests/test_conf_escopo.py` (o resto veio da base).
- Ordem dos ramos em `linhas_de_entrega` conferida: parecer com autoria, merge-integracao, anexo implícito, anexo do portão (`etapa == "codigo"`), e por último o `else` com `isencao_do_dono`; a isenção do dono só vale quando nenhum ramo anterior resolve, e o anexo do portão continua antes dela. P1-P12 seguem guardados: `caminho_isentavel`, `decisao_do_patch`, `pedido_na_entrega`, blob e modo no head, git que falha reprova.
- `python3 -m unittest tests.test_conf_escopo tests.test_pr_hook_prazo`: 42 testes, OK (carga ~10-12).
- `forge-mutante` das três specs, uma a uma: todos morreram após o deslocamento de linhas (ex.: M5 em 2747, M8 em 1848), nenhum sobrevivente.
- A1 e A2 seguem abertos como recomendados (o documento de ameaças fica fora do repositório). Sem bugs; a suíte inteira fica para o CI do PR.
