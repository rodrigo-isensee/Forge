---
tipo: review
contrato: 1
pedido: pa-4
branch: melhoria/pa-4-parecer-commitado
commit: 4a28e23c1c4f05ba7e0270d5acf6364b18b21f3c
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
