---
name: contribuir-com-o-forge
description: Use quando você, em qualquer projeto, perceber uma melhoria de fábrica (agente, skill, processo, modelo, hook, CI ou teste do Forge) e precisar levá-la ao repositório do Forge por pull request na develop. Cobre classificação, clone próprio, acesso por branch ou fork, checagens e texto do PR.
---

# Contribuir com o Forge a partir de qualquer projeto

Decisão: `docs/adr/0006-contribuicao-de-qualquer-projeto.md`. Qualquer agente de qualquer projeto contribui, como colaborador do GitHub. **Uma melhoria por PR.** `R-CONTRIB`: o projeto abre o PR e nunca o mescla.

## 1. Classifique: fábrica ou projeto
- **Fábrica (vai ao Forge):** o que melhora como o time trabalha em qualquer projeto: agentes, skills, fluxo, práticas gerais, hooks, modelos, testes e CI do Forge.
- **Projeto (fica no projeto):** o que é do sistema (`R-NEUTRO` neutralidade da fábrica).
- Misturou os dois: são dois PRs, um em cada repositório. Na dúvida, pergunte ao usuário com a sua recomendação.
- No projeto atual nada muda por causa da melhoria de fábrica. Avise o usuário, sem parar a entrega.

## 2. Prepare um clone próprio
- Use `~/.forge-contrib/<projeto>` (um clone por projeto, fora do projeto).
- **Nunca** use worktree de outro clone do Forge (o estado git compartilhado já corrompeu um repositório); `R-COPIA` não copiar agentes e skills para o projeto (nem editar o cache do plugin).
- Não existe? `git clone git@github.com:rodrigo-isensee/Forge.git ~/.forge-contrib/<projeto>`. Depois, `git fetch origin`.
- Ao criar o clone, ative o hook: `git config core.hooksPath .githooks` (`R-CONTRIB`).

## 3. Cheque o acesso
`gh repo view rodrigo-isensee/Forge --json viewerPermission`
- **`WRITE`, `MAINTAIN` ou `ADMIN`:** `git switch -c melhoria/<assunto> origin/develop`; envie a branch ao próprio repositório.
- **`READ` (sem escrita):** `gh repo fork rodrigo-isensee/Forge --clone=false`, adicione o fork como remoto, crie a branch a partir de `origin/develop` e envie ao fork; o PR vai para a `develop` do Forge.
- **Sem `gh` autenticado:** registre a proposta em `docs/kanban/melhorias.md` do projeto (situação, mudança, como medir) e avise o usuário.
- Nunca envie para `develop`, `homolog` ou `main` (`R-FLUXO` branches e promoção; `R-MAIN` a main é do usuário).

## 4. Faça a mudança
- Siga o `.claude/CLAUDE.md` do Forge e as regras em `docs/regras/`: `R-NEUTRO` neutralidade da fábrica, `R-CUSTO` nada que custe dinheiro sem autorização; regras invioláveis preservadas.
- Acrescente uma linha em `## [Não publicado]` do `CHANGELOG.md`. **Não** suba a versão em `.claude-plugin/plugin.json`: a versão é decidida na release pelo `tech-lead`.

## 5. Antes do PR, no clone de contribuição
```bash
python3 -m unittest discover -s tests -v
scripts/validar-plugin.sh                  # cópia limpa em $TMPDIR (o sandbox suja a raiz; o CI usa claude plugin validate . --strict)
scripts/verificar-contribuicao.sh        # segredos e caminhos pessoais no diff
```
Falhou? Corrija e rode de novo; o PR só sai com as três verdes.

## 6. Abra o PR para a `develop`
Use `.github/pull_request_template.md` e preencha:
- **Projeto de origem** e **situação observada**, sem dados do projeto (se o repositório for público, o PR é público);
- **O que muda**;
- **Como medir** o efeito (`docs/melhoria-continua.md`);
- checklist: testes, validate, `verificar-contribuicao`, CHANGELOG, neutralidade.

Comando: `gh pr create --base develop --title "<tipo>: <resumo>" --body-file <texto>` (de um fork: `--repo rodrigo-isensee/Forge`).

## 7. Depois
Acompanhe o CI e responda ao review do `tech-lead`; a promoção até a `main` segue `R-FLUXO`. O projeto recebe a melhoria com `claude plugin update forge@forge` depois da release.
