---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-entrega-merges
commit: 590d1954d4d31881a434ef926530a0bc52e2c711
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: v0478 (E62.17), melhoria/v0479-entrega-merges

Gatilhos: controle do Forge (`bin/forge-check entrega`), afrouxa o escopo do autor (ENTREGA-MERGE-DA-DEVELOP, ENTREGA-MERGE-DE-PARECER-ANINHADO).

Diff lido: `8ee73d15..590d1954` (bin/forge-check, testes, mutantes, fragmento). Tentativas pedidas: ref local reescrita (resiste: o gate pela ref local só decide se consulta o remoto; os testes da branch cobrem), merge de fora da develop (resiste, teste da branch), arquivo devolvido à develop do que a branch mudou até a conferida (resiste, `desfeitos`), aceite do usuário (resiste, `ACEITES_DO_USUARIO`), conferido fora da história do outro pai (resiste, `rev-list` do outro pai). Há brecha em duas outras formas (A1, A2): o remoto lido pelo `git ls-remote` não é só a develop, e o merge-base aceito não é só um estado da develop.

## Achados
- A1 (bloqueante) bin/forge-check:7376 · `remoto_da_branch` pega a 1.a linha do `git ls-remote origin refs/heads/develop`, que casa por cauda: a branch `a/refs/heads/develop` (o pre-push aceita) vem antes e vira a develop; com a ref local reescrita, o arquivo fora do brief sai do escopo e a entrega cumpre (S1)
- A2 (bloqueante) bin/forge-check:2865 · o merge-base com a develop remota pode ser commit intermediário de PR lateral já mesclado (fora da 1.a linha de pais da develop): o autor mescla esse commit, traz versão que a develop nunca teve na ponta (ou apaga arquivo) e ela sai do escopo (S2, S3)
- A3 (recomendado) bin/forge-check:2868 · arquivo ausente no head e no merge-base compara "" com "" e sai do escopo (falha aberta da `blob_de`); exigir presença nos dois ou tratar a remoção só com o merge-base na 1.a linha de pais (A2)
- A4 (recomendado) bin/forge-check:2528 · `conferidos_ancestrais` aceita o blob de qualquer conferido ancestral, não o do outro pai: merge resolvido à mão rebaixa o parecer a uma versão superada (sonda local); exigir também blob(merge)=blob(outro pai); hoje só a M2 (linha 3324, fora de docs/qa) segura
- A5 (recomendado) bin/forge-check:3258 · com A1/A2 corrigidos, a linha "merge da develop sem âncora: o que ela trouxe segue no escopo" sai junto de "integração da base pelo remoto" que tira o arquivo (S2): mensagem contraditória para quem confere

## Sondas
- S1 · push de <c> (só agents/fora.md, fora do brief) a refs/heads/a/refs/heads/develop; update-ref refs/remotes/origin/develop <c>; entrega com bin/app por cima · espera: agents/fora.md fora do declarado, rc 1 · obtido: integração da base pelo remoto (1 arquivo), cumpriu, rc 0
- S2 · develop com PR lateral X (agents/guarda.md "fraco") e Y ("forte") mesclado --no-ff; autor faz `git merge --no-ff X` · espera: agents/guarda.md fora do declarado, rc 1 · obtido: merge-base = X, head com "fraco", integração da base pelo remoto, resultado: cumpriu, rc 0
- S3 · como S2, com X apagando KANBAN.md e Y o devolvendo; autor mescla X · espera: KANBAN.md no escopo, rc 1 · obtido: KANBAN.md some do escopo, resultado: cumpriu, rc 0

## Detalhe dos achados
**A1.** Evidência: `bin/forge-check:7376` (`saida.split("\t")[0]`), consumido em `vindos_da_base` (`bin/forge-check:2862`). O padrão do `git ls-remote` casa a cauda do nome (o `git` lista `refs/heads/a/refs/heads/develop` para o padrão `refs/heads/develop`, em protocolo 1 e 2, verificado com remoto local), e a saída vem em ordem de nome: qualquer `<x>/refs/heads/develop` com `<x>` antes de `develop` na ordem vem primeiro. O `.githooks/pre-push:164,171` só barra `refs/heads/develop` exato. Caminho: o autor (agente com envio de branch) publica a ref homônima apontando para o próprio commit com o arquivo fora do brief e reescreve a `origin/develop` local (o gate da linha 2860); o `entrega` toma a ref forjada como develop e tira o arquivo. Não enviei ref forjada ao GitHub (postura defensiva): se ele aceita o nome não foi provado; a sonda usa remoto local, como os testes. A falha também atinge os outros usos de `remoto_da_branch` (linhas 7419 e 8434), anteriores a esta branch. Severidade: alta (anula o escopo do autor em controle do Forge). Correção mínima: em `remoto_da_branch`, aceitar só a linha cujo 2.o campo é exatamente `refs/heads/<branch>` (nenhuma, ou mais de uma: None e `conferido` False); teste com a ref `a/refs/heads/develop` no remoto. Esforço P. Dono: autor da branch (quem escreveu ENTREGA-MERGE-DA-DEVELOP).

**A2.** Evidência: `bin/forge-check:2865-2868`. O `merge-base` do head com a develop remota é sempre ancestral da develop, mas não necessariamente um estado da develop: commit de PR lateral mesclado com `--no-ff` é ancestral dela sem nunca ter sido a ponta. O autor mescla esse commit (o `merges_nao_conferidos` já o trata como merge da base, por ser ancestral da `origin/develop`), o merge-base passa a ser ele, e a versão intermediária (a anterior à correção pedida no review daquele PR, ou o arquivo apagado) sai do escopo. Severidade: média (precisa de commit lateral útil já na develop; o diff do PR contra a develop ainda mostra a regressão, mas a conferência diz `cumpriu`). Correção mínima: só aceitar `ponto` que esteja na 1.a linha de pais da develop remota (`git rev-list --first-parent <remoto>` contém `ponto`) e com um só merge-base (`git merge-base --all` com uma linha); fora disso, nada sai. Testes: S2 e S3 como casos de abuso. Esforço P. Dono: autor da branch.

**A3.** Falha aberta: `blob_de` devolve "" para ausente e para falha, e a comparação igual tira o arquivo; o `igual_na_base` da mesma família exige código 0 nos dois lados. Com A2 corrigido, a remoção que a develop fez na 1.a linha de pais segue legítima; a recomendação é ler a ausência explicitamente. Severidade: baixa. Esforço P. Dono: autor da branch.

**A4.** Sonda local (unidade, `merges_nao_conferidos`): parecer de review conferido P1 (`aprovado`) e P2 (`reprovado`) no mesmo ramo; o merge de P2 resolvido à mão com o blob de P1 sai sem recusa (antes desta branch recusava, porque só o blob do outro pai valia). Na entrega completa, a M2 (`bin/forge-check:3324`) recusa o blob superado nas pastas de review, segurança e devops, mas exclui `docs/qa`. Severidade: baixa (defesa em profundidade). Correção mínima: guardar, para cada P aceito, o outro pai `q` de que ele é ancestral e exigir `blob(merge, n) == blob(q, n)`; o caso real (o parecer aninhado) já cumpre isso. Esforço P. Dono: autor da branch.

**A5.** Texto contraditório na saída de S2: o aviso da linha 3258 diz que o trazido segue no escopo e a linha nova o tira. Ajustar o texto quando `vindos_da_base` tirar algo. Esforço P. Dono: autor da branch.

Sobre o rótulo afrouxa-regra: a mudança afrouxa o escopo do autor (aceita mais do que hoje) nas duas frentes; a avaliação acima é para a lista do dono, que decide o rótulo.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Suíte: não rodei a suíte inteira (fica no CI); CI do head não consultado (sem PR e sem credencial do `gh` no sandbox). Rodei a classe `MergeDaBaseDepoisDoBrief` (herdada pelas sondas, 15 testes verdes) e as sondas S1 a S3 e a de A4 por subclasses fora da árvore. Ferramentas ausentes no PATH: gitleaks, semgrep, zizmor, actionlint (lacuna; o diff não toca workflow nem traz segredo à leitura).
