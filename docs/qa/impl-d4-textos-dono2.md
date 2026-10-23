---
tipo: qa
contrato: 1
pedido: impl-d4-textos-dono2
branch: melhoria/impl-d4-textos-dono2
commit: 872351ed09b9586c1585abad57b9cef3acfdc663
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-23
---
# QA: impl-d4-textos-dono2 (RET-TEXTOS-DONO2, E1.3)

Testado: `83c817f25f9dcc01da3404cde689b8587a6eab20` (código idêntico ao de `4df5e74`, que só traz o parecer de segurança `d1b4576`, em `docs/security/`). Base `af79bef`. O pedido de origem se perdeu; as obrigações são as dos commits e do fragmento `changelog.d/impl-d4-textos-dono2.md` (suposição do pedido RET-TEXTOS-DONO2): F7 (revisão de UX só com interface), F10 (pedido, lista ou decisão do dono gravados; vigia avisa lista não gravada).

## Achados
- A1 (recomendado) hooks/vigia.py:234 · Mensagem em blocos cujo primeiro bloco começa com "<" (lembrete) descarta a lista do dono nos blocos seguintes (falso negativo, reproduzido; é o A4 do review).
- A2 (recomendado) hooks/vigia.py:247 · O destino do registro casa por substring: gravar em `/x/notdocs/pedidos/a.md` conta como registro e cala o aviso (reproduzido; falso negativo do aviso, nunca bloqueio).
- A3 (recomendado) hooks/vigia.py:224 · Lista que só começa depois dos primeiros 64 KB da mensagem não é contada (limite declarado no código; registrar em docs/hooks.md).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| F7: passo 7 do Jarvis e regra 1 de economia-de-tokens com a condição de interface | `tests/test_textos_dono_f7.py` (2 testes) | texto exato nos dois arquivos | passou; vermelho na base (2 falhas) |
| F10: R-DECISAO e Jarvis dizem "pedido, lista ou decisão do dono" e vedam scratchpad; sem citação de diário | `tests/test_textos_dono_f10.py` (2 testes) | ausência de "diário de retomada" | passou; vermelho na base (5 falhas) |
| F10: vigia declara `entrada-sem-registro` e o texto fixo | `tests/test_textos_dono_f10.py::test_vigia_declara...` | texto fixo sem texto do dono | passou |
| F10: aviso com 3+ itens sem gravação, sem texto do dono na saída nem no log | fixtures `vigia/entrada-sem-registro-avisa`, `-texto-fixo-sem-trecho`, `entrada-em-blocos-de-texto-avisa` | mínimo 3 itens; `ausente` confere o texto | passou (suíte) e CT-01 manual |
| F10: 2 itens, lembrete de sistema, resultado de ferramenta, sidechain: silêncio | fixtures `entrada-com-2-itens-silencio`, `-lembrete-de-sistema-nao-conta`, `-tool-result-nao-conta` | 2 itens (logo abaixo do limite) | passou |
| F10: gravação em `docs/pedidos/`, `docs/kanban/`, `KANBAN.md` (Write, Bash) silencia | fixtures `entrada-com-write-em-pedidos`, `-write-no-quadro`, `-bash-em-kanban-silencio` | os 3 destinos | passou |
| F10: não reavisar; só `Stop` principal | fixtures `entrada-nao-reavisa`, `entrada-subagentstop-ignora`, `-antes-do-stop-avisa` | dedupe por id; deslocamento próprio | passou |

## Cenários e resultado real
Ambiente: Linux/WSL2, Python 3.14, worktree `~/.forge-contrib/wt/qa-impl-d4-textos-dono2` (HEAD `4df5e74`, merge do parecer de segurança).
- **Suíte completa** `python3 -m unittest discover -s tests`: `Ran 1599 tests ... FAILED (failures=4, skipped=1)`, duas execuções (377 s e 359 s) com as mesmas 4 falhas, todas as conhecidas do ambiente que o PR #288 corrige: `test_shellcheck_no_hook` (SC2329 em `.githooks/pre-push:243`), `test_erro_interno_com_lista_de_permissao_falha_fechado [forge-dev:aq]` e as fixtures `conformidade/contrib-falha-fechada-pela-raiz-cwd-home-bloqueia` e `-cwd-wt-bloqueia`. Nenhuma falha é do vigia nem dos textos da branch. O `skipped=1` não vem do diff (a branch não adiciona skip; a catraca de skip passou).
- **Vermelho antes do verde:** cópia com `hooks/vigia.py`, `agents/jarvis.md`, `docs/regras/R-DECISAO.md` e `docs/economia-de-tokens.md` de `af79bef` e os testes da branch: `Ran 5 tests ... FAILED (failures=7)`; na branch: `Ran 5 tests ... OK`.
- **Exploratório no hook real** (projeto git temporário, `.forge/versao`, transcrição montada; `Stop` após `SessionStart`):
  - CT-01 lista de 4 itens: aviso fixo, sem texto do dono; segundo `Stop` silencioso: ok.
  - CT-02 2 itens, transcrição vazia, linha com JSON quebrado/nula, `isSidechain`, `SubagentStop`, gravação depois da lista: silêncio (JSON quebrado com lista válida ainda avisa): ok.
  - CT-03 gravação antes da lista: avisa: ok. Mensagem de 5 MB: avisa, rc 0, sem demora perceptível. `uuid` com `../`, `;` e `$()`: saneado, rc 0, sem stderr.
  - CT-04 blocos mistos com lembrete primeiro: sem aviso (A1). CT-05 `notdocs/pedidos`: sem aviso (A2). CT-06 lista depois de 64 KB: sem aviso (A3).
  - Em todos: rc 0 (o vigia nunca bloqueia).
- Mutação: sem ferramenta gratuita declarada para hooks Python; não executada. Acessibilidade e E2E: não se aplicam (sem interface).
- Bugs abertos: nenhum. Os três achados são falsos negativos de um aviso heurístico (sem perda de dado, sem bloqueio indevido), recomendados e na linha dos achados do review (A1 a A4), que seguem como cartão ou volta futura.

## Parecer
Aprovado sobre `83c817f`. Revalidar só o que mudar quando a branch trouxer a `develop` com o PR #288 (as 4 falhas conhecidas somem).

## Revalidação por delta (REVAL-288, E2.3)
Depois do review e da segurança por delta aprovados, pela decisão "C" do dono (2026-10-23). Delta desde `83c817f` (commit do parecer anterior) até `872351e`: a entrada da `develop` (`7423c44`, PR #288, FIX-SUITE-LOCAL: `.githooks/pre-push`, `tests/test_hooks.py`, `tests/apoio_pathlib_312/`, duas fixtures `contrib-falha-fechada-pela-raiz-cwd-*`, documentos `suite-local-verde`) e pareceres em `docs/`. Nenhum código da entrega mudou. Comando: `bin/forge-testes`, que escolheu a suíte completa (`tests/hooks/vigia/entrada-com-2-itens-silencio.json` sem mapa): 1599 testes, 1106 s, `OK`, rc 0. As 4 falhas conhecidas somem, como previsto. Comportamento já aprovado (CT-01 a CT-06 do vigia e os achados A1 a A3, que seguem recomendados): igual, sem regressão. Veredito: aprovado, sem achado novo.
