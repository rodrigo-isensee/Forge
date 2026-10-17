---
tipo: review
contrato: 1
pedido: pa-4
branch: melhoria/pa-4-parecer-commitado
commit: 54bfcf9d56fb9f7f1f18c4ca9edca84947f9703f
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-16
---
# Review independente: quem emite o parecer o commita (PA-4)

Escopo: `b38cd283...4a28e23c` (base b38cd283fcb5; o autor não é este revisor). 8 arquivos, 3 commits (`bb4b4b6` feat, `0925835` docs, `4a28e23` changelog), 55 linhas acrescentadas e nenhuma removida.

## Ferramenta
- `python3 -m unittest tests.test_forge -q`: `Ran 236 tests in 23.751s` / `OK` (HEAD 4a28e23, árvore limpa). Só essa suíte, como pede o brief; `test_hooks` e a bateria completa ficam para o QA e o CI.

## Checklist (leitura)
1. **A lacuna é real e foi fechada.** Conferido em `hooks/parecer.py:189-198`: o `gh pr create` da branch atual chama `verificar` com `ref=None`, e `cmd_pr` lia o parecer do disco (`bin/forge-check:170-172`); parecer não commitado passava. `gh pr ready`, `gh pr merge` e `git merge`/`git pull` já passam `ref` (`hooks/parecer.py:218`, `:306`, `:235`) e leem do git. O novo `parecer_commitado` (`bin/forge-check:477-485`) recusa o parecer novo, só no índice ou editado depois do commit; fora de repositório ou sem HEAD, não confere (o `commit_vale` cobre esse caso). Com `--ref` nada muda (`bin/forge-check:506`, condição `ref is None`), e o teste `test_pr_com_ref_nao_olha_a_arvore_de_trabalho` prova. Mensagem clara, com o arquivo, o que fazer e o R-ID do tipo de parecer.
2. **Fluxo e regras.** As quatro instruções (`agents/tech-lead.md:17`, `agents/qa-engineer.md:21`, `agents/devops-engineer.md:18`, `agents/security-engineer.md:15`) dizem o mesmo: só o arquivo do parecer, `git add` explícito, mesmo push. Nada contradiz `R-REVIEW`, `R-QA` nem `R-SEGURANCA`; a do security-engineer preserva `docs/security/aceites/` como do usuário (`R-SEGURANCA`, `R-DECISAO`) e não lhe dá escrita fora de `docs/security/` (fora do escopo do pedido, respeitado). O endurecimento só fecha: nada afrouxa.
3. **Legibilidade.** Função curta, docstring diz o contrato; sem duplicação.
4. **Erros.** Falha do `git status` vira `True` (libera); só ocorre com repositório quebrado depois de `cat-file` ter achado o arquivo no HEAD, e o `commit_vale` continua valendo. Aceitável.
5. **Segurança.** Mexe em controle do Forge; o parecer de segurança é do security-engineer, em paralelo (`docs/security/pa-4.md`), e não é refeito aqui.
7. **Testes.** Os 6 testes ajustados (`test_pr_aprovado_no_head`, `test_pr_com_autoria_do_papel_certo_vale`, `test_pr_sem_arquivo_de_autoria_nao_exige`, o de devops e segurança juntos, `test_pr_sem_gatilho_nao_exige_devops_nem_seguranca` e o auxiliar dos `riscos-aceitos`) só ganharam `self.commitar("pareceres")`; nenhuma asserção mudou ou saiu. O caso novo cobre os três estados (só no disco, só no índice, editado depois do commit) e confirma que só o arquivo editado é apontado.
9. **Commits.** Pequenos, Conventional Commits em português, trailers presentes.
11. **Invariantes** (`tests/config.json`): só acréscimos (5 linhas), cada um com texto que existe no agente.
- **Neutralidade** (`R-NEUTRO`): nada de projeto, nome ou stack. Fragmento `changelog.d/pa-4-parecer-commitado.md` com o nome da branch, tipo `Alterado`.

## Achados
| Arquivo:linha | Problema | Sugestão | Severidade |
|---|---|---|---|
| `bin/forge-check:32` e `:2056` | A ajuda de `pr` e do `--ref` ("padrão: disco e HEAD") não diz que, sem `--ref`, o parecer do disco precisa ser igual ao do HEAD. | Uma frase na docstring do módulo e no `help` do `--ref`. | recomendado |
| `agents/tech-lead.md:17`, `agents/qa-engineer.md:21`, `agents/devops-engineer.md:18`, `agents/security-engineer.md:15` | O rótulo "(PA-4)" é um cartão interno da fábrica; vai para os projetos sem significado ali (nenhuma outra instrução de agente cita cartão). Não fere `R-NEUTRO`. | Tirar o rótulo do texto dos agentes; ele já está no commit e no changelog. | recomendado |
| `agents/security-engineer.md:15` | "Commit só em `docs/security/`" é regra de texto: o hook `conformidade` restringe a escrita do papel, não os caminhos de `git add`/`git commit`. O pedido pede "a regra", e o texto a dá; a garantia por hook fica com o security-engineer avaliar no parecer dele. | Nenhuma neste pedido; se o security-engineer pedir a garantia, cartão próprio. | informativo |
| commit `bb4b4b6` (mensagem) | Diz que `gh pr create`, `ready` e `merge` liam do disco; só o `gh pr create` da branch atual lia (os outros passam `ref`). O código está certo. | Nada (histórico não se reescreve, `R-VERIFY`); vale para a descrição do PR. | informativo |

## Riscos residuais
- "No mesmo push" não é verificado: o `forge-check pr` confere o commit local, não o remoto. Fora do escopo do PA-4.
- `test_hooks` (fixtures de `tests/hooks/parecer/` com `gh pr create`) não foi rodado aqui; o QA e o CI o rodam.

Parecer: **aprovado**, com dois recomendados que não bloqueiam.

## Revalidação após a volta do autor
Escopo: `4a28e23c..7424d5c2` em `bin/`, `tests/`, `agents/` e `changelog.d/` (commits `da2f537` fix e `7424d5c` docs; o `docs/security/pa-4.md` no mesmo intervalo é de outra delegação e não entra aqui).
- **Recomendados tratados.** Ajuda do `pr` (`bin/forge-check:33`) e do `--ref` (`bin/forge-check:2056`) citam que, sem `--ref`, o parecer do disco precisa ser igual ao do HEAD. O rótulo "(PA-4)" saiu dos quatro agentes; o texto da regra ficou igual. `tests/config.json` não continha o rótulo nos invariantes e não mudou; o fragmento `changelog.d/` continua fiel e não mudou.
- **Comparação de bytes em `parecer_commitado`** (`bin/forge-check:478-485`): `git show HEAD:<rel>` (`bruto=True`) contra `read_bytes()` do disco. O resto do comportamento se mantém: fora de repositório ou sem HEAD continua `True`; parecer ausente no HEAD, só no índice ou editado continua recusado; o único chamador (`:506`) só roda com `ref is None` e com `rel` vindo do disco. Única mudança de efeito: falha do git com HEAD legível agora recusa (antes liberava), como pediu a segurança (B-PA4-1); isso fecha, não afrouxa.
- **Teste** `test_pr_parecer_editado_nao_escapa_por_skip_worktree_nem_assume_unchanged`: cobre as duas marcas do índice e a volta ao verde depois de desfeitas. Vermelho antes do verde conferido: com o `bin/forge-check` de `4a28e23` numa cópia em `$TMPDIR`, o teste falha (`FAILED (failures=1)`).
- **Ferramenta:** `python3 -m unittest tests.test_forge -q` no HEAD `7424d5c`, árvore limpa: `Ran 237 tests in 24.688s` / `OK`.
- **Informativo:** com filtros de checkout (`core.autocrlf`, `smudge`) o disco pode diferir do blob sem edição e o parecer seria recusado; falha fechada e rara nos pareceres em Markdown; cartão só se aparecer.

Parecer da revalidação: **aprovado**.

## Revalidação após a segunda volta do autor
Escopo: `7424d5c..54bfcf9` em `bin/`, `tests/`, `agents/` e `changelog.d/` (`54bfcf9`, BUG-1 do QA): a mudança é só o `help=` do subparser `pr` (`bin/forge-check:2054`) e o teste `test_ajuda_geral_cita_parecer_commitado_no_pr`, sem efeito colateral; `agents/` e `changelog.d/` intactos. `python3 -m unittest tests.test_forge -q` no HEAD `54bfcf9`: `Ran 238 tests` / `OK`.

Parecer da revalidação: **aprovado**.
