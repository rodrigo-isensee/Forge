---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-entrega-anexos
commit: df0aef74d183d9b89d108ac9dadc0352bf2b870e
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-20
---
# QA: v0478 E62.1 (registro de bug do QA como anexo do portão na volta), head `df0aef74`

Diff lido contra `d4f0b10a`: `bin/forge-check` (`BUGS_DO_QA`, `bug_do_qa_na_volta`, ramo `elif` em `linhas_de_entrega`), `tests/test_selo_e_entrega.py` (classe `BugDoQaNaVolta`, 10 testes), spec `tests/mutantes/v0479-entrega-anexos.json` (M1 a M5), 4 fixtures `pp-sessao-forge-wt-*-qa-bugs-*`, `docs/hooks.md`, `docs/hooks-fixtures.md`, fragmento do changelog. Sem suíte local: a suíte inteira fica com o CI do PR.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Bug em `docs/qa/bugs/` mesclado antes da volta é anexo (caso real) | `test_caso_real_bug_mesclado_antes_da_volta_e_anexo` | merge sem resolução à mão | prova (asserção) na base |
| Bug commitado na branch depois da volta é anexo | `test_bug_commitado_na_branch_depois_da_volta_e_anexo` | commit só de `docs/qa/` | prova (asserção) |
| Só vale na volta (com conferida) | `test_sem_conferida_a_regra_nao_vale` | 1ª entrega | M1 morreu |
| Só a pasta `docs/qa/bugs/` | `test_arquivo_de_docs_qa_fora_de_bugs_sem_frontmatter_segue_fora` | vizinho `docs/qa/nota.md` | M1 morreu |
| Autor que grava o bug no commit do código segue fora | `test_autor_que_grava_o_bug_no_commit_do_codigo_segue_fora` | commit misto | ok |
| Commit com outro arquivo segue fora | `test_commit_do_bug_com_arquivo_fora_de_docs_qa_segue_fora` | arquivo fora de `docs/qa/` | M5 morreu |
| Merge com o bug resolvido à mão segue fora | `test_merge_com_o_bug_resolvido_a_mao_segue_fora` | merge não limpo | ok |
| qa-engineer autor da volta só com o `parecer conferido` (E50.6) | `test_qa_autor_da_volta_sem_linha_do_jarvis_segue_fora`, `test_autores_e_linha_do_jarvis` | sem autor lido; autor qa; blob certo/errado | M2 e M3 morreram |
| `rev-list` que falha ou vem vazio recusa | `test_rev_list_que_falha_ou_vazio_recusa` | rc 128; saída vazia | M4 morreu |
| Hook: só o `qa` grava em `docs/qa/bugs/` | `test_hooks.test_fixtures_do_parecer_pelo_papel` (4 fixtures) | dev, tech-lead, segurança bloqueiam; qa libera | passou |

## Execução
Todos os comandos em primeiro plano, saída em arquivo (`/root/.forge-contrib/wt/qa624-*.txt`).

Vermelho (`bin/forge-testes --vermelho d4f0b10a --modulos test_selo_e_entrega`, rc 0, 821 s):
```
vermelho: base=d4f0b10aead7 head=df0aef74d183 módulos=test_selo_e_entrega (restrito por --modulos)
revertidos à base: bin/forge-check, changelog.d/v0479-entrega-anexos.md, docs/hooks-fixtures.md, docs/hooks.md
BugDoQaNaVolta.test_autores_e_linha_do_jarvis · H=ok · B=erro · prova (API ausente)
BugDoQaNaVolta.test_bug_commitado_na_branch_depois_da_volta_e_anexo · H=ok · B=falha · prova (asserção)
BugDoQaNaVolta.test_caso_real_bug_mesclado_antes_da_volta_e_anexo · H=ok · B=falha · prova (asserção)
BugDoQaNaVolta.test_rev_list_que_falha_ou_vazio_recusa · H=ok · B=erro · prova (API ausente)
contagem: não prova (passa na base)=145; prova (API ausente)=2; prova (asserção)=2
```
Os 6 testes "passa na base" da classe são de recusa (o bug segue fora): passam na base por construção e quem os prova são os mutantes M1, M2, M3 e M5.

Cobertura (`forge-mutante --cobertura --base d4f0b10a`, rc 0): `bin/forge-check:3114` M3; `:3117` M4 e M5; `:3337` M1 e M2, todas `coberta · declarado, não provado`; nenhuma condição mudada sem mutante.

Mutantes (`forge-mutante tests/mutantes/v0479-entrega-anexos.json`, rc 0):
```
M1 · morreu · bin/forge-check:3337
M2 · morreu · bin/forge-check:3338
M3 · morreu · bin/forge-check:3114
M4 · morreu · bin/forge-check:3117
M5 · morreu · bin/forge-check:3117
```
Hook: `python3 -I -m unittest discover -s tests -p test_hooks.py -k fixtures_do_parecer_pelo_papel` → `Ran 1 test ... OK`.

Remoto avançou com os pareceres de review e de segurança (`371406b8`, só `docs/reviews/` e `docs/security/`); trazido por merge, sem tocar o código revisado.
