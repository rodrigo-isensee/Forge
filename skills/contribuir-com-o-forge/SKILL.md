---
name: contribuir-com-o-forge
description: Use quando você, em qualquer projeto, perceber uma melhoria de fábrica (agente, skill, processo, modelo, hook, CI ou teste do Forge). No projeto, a melhoria vira só sugestão anonimizada (`forge sugerir --guardar`); quem a implementa é a sessão do Forge, que a tria para o quadro. Cobre classificação, o texto da sugestão, a triagem e a entrega na sessão do Forge.
---

# Contribuir com o Forge a partir de qualquer projeto

`R-CONTRIB` (diretriz 36 do dono): **projeto nunca mexe no Forge, só sugere.** Na sessão de um projeto, nada de clone, branch, commit, envio, PR, comentário ou rótulo no repositório do Forge; o hook `conformidade` recusa e diz a forma aceita. A ADR 0006 (contribuição por PR vinda do projeto) fica substituída nesse ponto pela diretriz 36.

## 0. No projeto: sugira (`forge sugerir`)
Quando o Forge recusar algo que a pessoa pediu (recusa de hook, F4), o doutor ou um comando do Forge falhar, ou você notar uma melhoria de fábrica, **ofereça**: "Quer que eu sugira essa melhoria ao Forge?". Com "sim", escreva problema observado, proposta e como medir, sem nome do projeto, caminho nem dados pessoais (`R-NEUTRO`), e rode a linha sozinha `forge sugerir --guardar "<texto>"`: ele tira o que sobrou e guarda na fila local (`~/.local/state/forge/sugestoes/`). A issue só nasce depois que o dono confirma: **a pessoa** a envia no terminal dela, fora do Claude, com `forge sugerir --fila`, depois de ver o texto final. Nunca envie por conta própria; avise a pessoa e siga a entrega do projeto.

## 1. Classifique: fábrica ou projeto
- **Fábrica (vira sugestão ao Forge):** o que melhora como o time trabalha em qualquer projeto: agentes, skills, fluxo, práticas gerais, hooks, modelos, testes e CI do Forge.
- **Projeto (fica no projeto):** o que é do sistema (`R-NEUTRO` neutralidade da fábrica).
- Misturou os dois: a parte do projeto segue no projeto e a de fábrica vira sugestão. Na dúvida, pergunte ao usuário com a sua recomendação.
- No projeto atual nada muda por causa da melhoria de fábrica; `R-COPIA` não copiar agentes e skills para o projeto (nem editar o cache do plugin).

## 2. O que a sessão de projeto não faz
Não clona o Forge, não cria branch, não commita, não envia, não abre, comenta, edita nem rotula PR ou issue no repositório do Forge e não escreve em `~/.forge-contrib/`, que é da sessão do Forge (`R-CONTRIB`). Recusa do hook nesses atos não se contorna (`R-CONFORMIDADE`): guarde a sugestão e avise a pessoa.

## 3. Na sessão do Forge: triagem
A sessão do Forge lê as sugestões confirmadas (issues), confere cada uma contra a `develop` (já existe? duplica cartão?) e as tria para o quadro, com o projeto de origem anonimizado. Só daí nasce o cartão e o pedido (`fluxo-do-pedido`).

## 4. Na sessão do Forge: faça a mudança
- Branch `melhoria/<tema>` a partir da `develop`, numa worktree em `~/.forge-contrib/wt/` (`R-FLUXO`); nunca envie para `develop`, `homolog` ou `main` (`R-MAIN` a main é do usuário).
- Siga o `.claude/CLAUDE.md` do Forge e as regras em `docs/regras/`: `R-NEUTRO` neutralidade da fábrica, `R-CUSTO` nada que custe dinheiro sem autorização; regras invioláveis preservadas.
- Registre a mudança num fragmento em `changelog.d/`: `bin/forge-changelog novo <Adicionado|Alterado|Corrigido> "<texto>"` (arquivo `changelog.d/<branch-sem-prefixo>.md`; não edite o `CHANGELOG.md`). **Não** suba a versão em `.claude-plugin/plugin.json`: a versão é decidida na release pelo `tech-lead`.

## 5. Antes do PR
Quem implementa **não roda a suíte inteira do Forge** (`python3 -m unittest discover -s tests`): quem a roda é o CI do PR, que não custa nada no repositório público (`R-CUSTO`). Rode só os testes dos arquivos que você tocou e os dois comandos abaixo. Teste do Forge roda em `nice` e um arquivo por vez: `nice -n 19 python3 -I -m unittest discover -s tests -p test_x.py`.
```bash
scripts/validar-plugin.sh                # cópia limpa em $TMPDIR
scripts/verificar-contribuicao.sh        # segredos e caminhos pessoais no diff
```
Falhou? Corrija e rode de novo; o PR só sai com as duas verdes e os testes dos arquivos tocados.

## 6. Abra o PR para a `develop`
Use `.github/pull_request_template.md` e preencha a sugestão de origem (link da issue, sem dados do projeto), **o que muda** (mecanismo novo diz o que já existe e por que não basta, com evidência de execução), **como medir** (`docs/melhoria-continua.md`) e o checklist: testes, validate, `verificar-contribuicao`, changelog, neutralidade. Quem abre e mescla o PR é o `tech-lead` da sessão do Forge (FILA-22: o Jarvis não abre nem mescla PR): `gh pr create --base develop --title "<tipo>: <resumo>" --body-file <texto>`.

## 7. Depois
A promoção até a `main` segue `R-FLUXO`; o projeto recebe a melhoria com `claude plugin update forge@forge` depois da release. Depois do merge, apague a branch remota, a local e a worktree (`R-FLUXO`, "Depois do merge").
