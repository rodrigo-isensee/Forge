---
id: R-MAIN
titulo: A main é do usuário
verificada_por: hook pre-push do Forge e do modelo de projeto (teste HookPrePush); permissions do modelo de projeto; invariantes em tests/config.json
---
# R-MAIN: A main é do usuário

Propósito: texto único desta regra; os outros arquivos citam o ID. Público: todo o time. Revisão: 2026-10-12.

- A **`main` é do usuário**: nenhum agente faz commit, merge, rebase, reset, cherry-pick ou push nela, nem com `--force` (`R-VERIFY`). Vale no Forge e em cada projeto.
- Toda mudança chega à `main` por pull request: a `main` do Forge e a de cada projeto só mudam com o PR validado e mesclado pelo usuário. Agentes podem abrir o PR (`gh pr create`); mesclar na `main` (`gh pr merge`) é do usuário.
- O hook `.githooks/pre-push` recusa envio para a `main` (ative com `git config core.hooksPath .githooks`). Não o contorne.
- Para atualizar a sua branch com a `main`: `git fetch` e `git merge origin/main` **na sua branch**, nunca o contrário.
- Se a branch atual for a `main`, crie uma branch de trabalho antes de mudar qualquer arquivo.
- Só o usuário move um cartão para "Pronto", ao fazer o merge.
