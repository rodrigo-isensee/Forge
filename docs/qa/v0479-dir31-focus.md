---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-dir31-focus
commit: 0b933f1d9d842824a4ec05d9457e1df645a17d15
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-21
---
# QA: v0478 (E67.4, visão de foco, diretriz 31)

Escopo: `scripts/jarvis` (função `visao_de_foco`), modelo de projeto, README, regra de linguagem fácil em `agents/jarvis.md`. Sem suíte local (a bateria é o check-run `bateria` do PR); rodados só os testes dos arquivos tocados, com TMPDIR.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Sem arquivo: liga foco e tela cheia, sem `--verbose` | `test_sem_nenhum_arquivo_liga_a_visao_e_a_tela_cheia` | nenhum settings | passou |
| `viewMode` em qualquer arquivo do dono não é sobrescrito | `test_viewmode_em_qualquer_arquivo_do_dono_nao_e_passado`, `test_arquivo_local_vence_o_projeto` | usuário, projeto, local | passou |
| `focus` gravado só acrescenta `tui` | `test_viewmode_focus_ja_gravado_so_acrescenta_a_tela_cheia` | foco já gravado | passou |
| `tui` decidido por arquivo ou variável não é passado | `test_tui_decidido_por_arquivo_ou_variavel_nao_e_passado` | 4 origens | passou |
| Arquivo ilegível não decide pelo dono | `test_arquivo_ilegivel_nao_decide_pelo_dono` | JSON inválido nos 3 arquivos | passou |
| Python que falha não impede a abertura | `test_python_que_falha_nao_impede_a_abertura` | falha do interpretador | passou |
| Modelo liga a visão sem `tui` | `test_modelo_de_projeto_liga_a_visao_sem_trocar_o_renderizador` | n/a | passou |
| Regra de linguagem fácil uma vez | `test_jarvis_tem_a_regra_de_linguagem_facil_uma_vez` | exatamente 1 linha | passou |
| README: como desligar e extensão VS Code | `ReadmeVisaoDeFoco` | n/a | passou |

## Cenários e resultado real
- `python3 -I -m unittest discover -s tests -p test_sessao_automatica.py`: 22 testes, OK. `test_forge.py -k ReadmeVisaoDeFoco`: 1 teste, OK.
- Vermelho antes do verde (manual, cópia da base `bead3e53` em `$TMPDIR` com os dois arquivos de teste do head, porque `forge-testes --vermelho` ficou na fila da trava R-TETO): `FAILED (failures=8)` de 22 em `test_sessao_automatica.py` (os 8 são testes novos de foco, linguagem e modelo; os 14 anteriores seguem verdes) e `FAILED (failures=1)` em `ReadmeVisaoDeFoco`.
- Mutação: `bin/forge-mutante tests/mutantes/v0478-dir31-focus.json tests/mutantes/v0478-dir31-focus-2.json`: F1 a F11 todos `morreu` (scripts/jarvis:72,80,84,85,86,87,89,93,94 e settings.json:3); nenhum sobrevivente. Conferi a lista contra o diff: cada ramo de guarda de `visao_de_foco` (arquivo ilegível, `viewMode` presente, `tui` por arquivo e por duas variáveis, `modo in (None, "focus")`, `--settings` condicional) tem mutante.
- `forge-mutante --cobertura --base bead3e53`: `não coberto: scripts/jarvis` e `settings.json` (shell e JSON saem assim por desenho; a cobertura é a lista declarada, conferida à mão acima).

## Revalidação (head 0b933f1d, E67.9)
`forge-check parecer delta` (base 0d5826f9): no domínio só `tests/test_reval_delta.py`, uma linha: contagem de `tests/test_forge.py` citando `README.md` de 15 para 16 (a guarda C-2 passa a contar o teste `ReadmeVisaoDeFoco` já aprovado). O merge da develop fica fora do domínio. Rodados só `test_reval_delta.py` (10 testes, OK) e `test_sessao_automatica.py` (22 testes, OK). Sem suíte local nem vermelho (linha de contagem de teste existente; carga da máquina, pedido do brief). Parecer segue aprovado.
