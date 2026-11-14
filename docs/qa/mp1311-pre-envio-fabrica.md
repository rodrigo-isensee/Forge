---
tipo: qa
contrato: 1
pedido: melhorias-de-projeto-1311
branch: melhoria/mp1311-pre-envio-fabrica
commit: f30ac8d2f3edb92ef9b6b0bd81299c1b6b746ce0
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-13
---
# QA: melhorias-de-projeto-1311 (pré-envio da fábrica, E1.41)

Head f30ac8d2. Sem PR para a branch (`gh pr list --head` vazio): a suíte inteira fica para o CI do PR; aqui rodaram só os módulos afetados, os mutantes e o `--vermelho`.

## Achados
- A1 (bloqueante) tests/test_pre_envio_brief.py:122 · `forge-testes --vermelho befd4cca --modulos test_pre_envio_brief` sai rc=2 (sem veredito): Texto.test_roda_os_testes_de_texto... morre na base com erro, não por asserção. rc 2 não vale como vermelho (R-QA); faça o teste falhar por asserção na base.
- A2 (recomendado) tests/test_pre_envio_brief.py:88 · três testes negativos passam na base (fora do Forge, parecer sem pré-envio, `--texto` com outra opção): guardam fronteira, mas não provam vermelho; aceitável se o autor justificar no PQ.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Caso código: catraca, texto e afetados no brief | Gerar.test_codigo_traz_descricao_texto_e_testes_afetados | Entregar com bin/ e tests/ | passou (vermelho na base) |
| Caso só texto: sem afetados | Gerar.test_so_texto_fica_sem_os_testes_afetados | Entregar só com docs/ | passou (vermelho na base) |
| Caso junção (`pr`): sem afetados | Gerar.test_juncao_fica_sem_os_testes_afetados | etapa pr com caminho de código | passou (vermelho na base) |
| Fora do Forge não cobra | Gerar.test_fora_do_forge_nao_cobra_o_pre_envio_da_fabrica | projeto não-Forge | passou (passa na base, só guarda) |
| Parecer não leva pré-envio do autor | Gerar.test_parecer_nao_leva_o_pre_envio_do_autor | etapa review | passou (só guarda) |
| Parecer com PR: `gh pr checks <n>` | Gerar.test_parecer_com_pr_... | PR aberto | passou (vermelho na base) |
| Parecer sem PR: suíte fica ao CI | Gerar.test_parecer_sem_pr_... | `pr == {}` | passou (vermelho na base) |
| Parecer sem gh/rede: regra mantida | Gerar.test_parecer_sem_gh_mantem_a_regra | `pr is None` | passou (vermelho na base) |
| Lista do brief = lista do `--texto` | Texto.test_a_lista_do_brief_e_a_do_modo_de_texto | duas listas | passou (vermelho na base) |
| `--texto`: um comando, rc e resumo | Texto.test_roda_os_testes_de_texto_num_comando... | rc propagado, 1 linha | passou; vermelho sem veredito (A1) |
| `--texto` não combina | Texto.test_texto_nao_combina_com_outra_opcao | 5 opções | passou (só guarda) |

## Cenários e resultado real
- `python3 -m unittest -q tests.test_pre_envio_brief tests.test_testes_tocados`: 161 testes, OK (1 pulado pelo sandbox, /proc de outro namespace, já existente), rc=0.
- `bin/forge-testes --texto`: rc=0 em 93 s, uma linha de resumo; `--texto --completa` sai 2 com "não combina com outras opções".
- Mutantes M1 a M10 (`bin/forge-mutante` das duas specs): todos morreram, rc=0. Conferência da lista contra o diff: linhas de guarda 8292, 8297, 8306, 8310, 8405/8406 (forge-check) e 792, 824 (forge-testes) têm mutante.
- `--vermelho`: 6 provam por asserção, 1 por API ausente, 3 passam na base (guardas), 1 sem veredito; rc=2.
- Nota de ambiente: primeira tentativa em segundo plano perdeu os jobs (subshell encerrado); repetida com run_in_background, sem falha de produto.
