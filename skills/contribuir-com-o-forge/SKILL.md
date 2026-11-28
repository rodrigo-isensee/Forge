---
name: contribuir-com-o-forge
description: Use quando você, em qualquer projeto, perceber uma melhoria de fábrica (agente, skill, processo, modelo, hook, CI ou teste do Forge). No projeto, ela vira só sugestão (`forge sugerir --guardar`); a sessão do Forge a tria e implementa. Cobre classificação, sugestão, triagem e entrega.
---

# Contribuir com o Forge a partir de qualquer projeto

`R-CONTRIB` (diretriz 36 do dono): **projeto nunca mexe no Forge, só sugere.** Na sessão de um projeto, nada de clone, branch, commit, envio, PR, comentário ou rótulo no repositório do Forge. O hook `conformidade` recusa e diz a forma aceita. A ADR 0006 (contribuição por PR vinda do projeto) fica substituída nesse ponto pela diretriz 36.

## 0. No projeto: sugira (`forge sugerir`)
Gatilhos: o Forge recusou algo que a pessoa pediu (recusa de hook, F4), o doutor ou um comando do Forge falhou, ou você notou uma melhoria de fábrica. Neles, **ofereça**: "Quer que eu sugira essa melhoria ao Forge?". Com "sim", escreva problema observado, proposta e como medir. Nada de nome do projeto, caminho nem dados pessoais (`R-NEUTRO`). Rode a linha sozinha `forge sugerir --guardar "<texto>"`. Ele tira o que sobrou e guarda na fila local (`~/.local/state/forge/sugestoes/`). A issue só nasce depois que o dono confirma. **A pessoa** a envia no terminal dela, fora do Claude, com `forge sugerir --fila`, depois de ver o texto final. Nunca envie por conta própria. Avise a pessoa e siga a entrega do projeto.

## 1. Classifique: fábrica ou projeto
- **Fábrica (vira sugestão ao Forge):** o que melhora como o time trabalha em qualquer projeto. São agentes, skills, fluxo, práticas gerais, hooks, modelos, testes e CI do Forge.
- **Projeto (fica no projeto):** o que é do sistema (`R-NEUTRO` neutralidade da fábrica).
- Misturou os dois: a parte do projeto segue no projeto e a de fábrica vira sugestão. Na dúvida, pergunte ao usuário com a sua recomendação.
- No projeto atual nada muda por causa da melhoria de fábrica. `R-COPIA` não copiar agentes e skills para o projeto (nem editar o cache do plugin).

## 2. O que a sessão de projeto não faz
Não clona o Forge e não cria branch, commit, envio, PR, issue, comentário nem rótulo no repositório dele. Não escreve em `~/.forge-contrib/`, que é da sessão do Forge (`R-CONTRIB`). Formas recusadas pelo hook: `formas-recusadas.md`, nesta pasta. Recusa do hook nesses atos não se contorna (`R-CONFORMIDADE`). Guarde a sugestão e avise a pessoa.

## 3. Na sessão do Forge: triagem
A sessão do Forge lê as sugestões confirmadas (issues). Confere cada uma contra a `develop`: já existe? Duplica cartão? Depois as tria para o quadro, com o projeto de origem anonimizado. Só daí nasce o cartão e o pedido (`fluxo-do-pedido`).

## 4. Na sessão do Forge: faça a mudança
- Branch `melhoria/<tema>` a partir da `develop`, numa worktree em `~/.forge-contrib/wt/` (`R-FLUXO`). Nunca envie para `develop`, `homolog` ou `main` (`R-MAIN` a main é do usuário).
- Siga o `.claude/CLAUDE.md` do Forge e as regras em `docs/regras/`. Valem `R-NEUTRO` neutralidade da fábrica e `R-CUSTO` nada que custe dinheiro sem autorização. As regras invioláveis ficam preservadas.
- Registre a mudança num fragmento em `changelog.d/`: `bin/forge-changelog novo <Adicionado|Alterado|Corrigido> "<texto>"`. O arquivo é `changelog.d/<branch-sem-prefixo>.md`; não edite o `CHANGELOG.md`. **Não** suba a versão em `.claude-plugin/plugin.json`. A versão é decidida na release pelo `tech-lead`.

## 5. Antes do PR
Quem implementa **não roda a suíte inteira do Forge** (`python3 -m unittest discover -s tests`). Quem a roda é o CI do PR, que não custa nada no repositório público (`R-CUSTO`). Rode só os testes dos arquivos que você tocou e os dois comandos abaixo. Teste do Forge roda em `nice` e um arquivo por vez: `nice -n 19` antes da forma de `skills/qa-testing/comandos.md` ('Um módulo de teste').
```bash
scripts/validar-plugin.sh                # cópia limpa em $TMPDIR
scripts/verificar-contribuicao.sh        # segredos e caminhos pessoais no diff
```
Falhou? Corrija e rode de novo. O PR só sai com as duas verdes e os testes dos arquivos tocados.

## 6. Abra o PR para a `develop`
Use `.github/pull_request_template.md`. Preencha a sugestão de origem (link da issue, sem dados do projeto). Preencha **o que muda**: mecanismo novo diz o que já existe e por que não basta, com evidência de execução. Preencha **como medir** (`docs/melhoria-continua.md`). Marque o checklist: testes, validate, `verificar-contribuicao`, changelog, neutralidade. Quem abre e mescla o PR é o `tech-lead` da sessão do Forge. O Jarvis não abre nem mescla PR (FILA-22). A forma: `gh pr create --base develop --title "<tipo>: <resumo>" --body-file <texto>`.

## 7. Depois
A promoção até a `main` segue `R-FLUXO`. O projeto recebe a melhoria com `claude plugin update forge@forge` depois da release. Depois do merge, apague a branch remota, a local e a worktree (`R-FLUXO`, "Depois do merge").
