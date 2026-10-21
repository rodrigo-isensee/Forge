---
tipo: revisao-seguranca
contrato: 1
pedido: prepush-so-parecer
branch: melhoria/prepush-so-parecer
commit: 441ae2727f04a76299723ca79a2c2989117148de
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-21
---
# Review de segurança: prepush-so-parecer

Escopo: `git diff 10c838fa35c96229d04ca96b0897cec19cbaa631 6753dc7c6532e4d10bfa051277d69125f729dc50` (`.githooks/pre-push`, `tests/test_pre_push_parecer.py`, `changelog.d/prepush-so-parecer.md`) e o `.githooks/pre-push` inteiro. Referência: a decisão D2 do dono (2026-10-20 22:38) e a de 2026-10-21 01:33 (manter a suíte inteira no push de código).

**Veredito: aprovado.** O atalho só se abre quando todas as condições valem: uma única ref, que seja branch; local e remoto não zerados e em hexadecimal; HEAD igual ao commit enviado; árvore de trabalho limpa (inclusive arquivos não rastreados); a árvore do commit remoto anotada na prova, que é arquivo regular do próprio usuário e não link; e todo arquivo do delta (`--no-renames`, então renomeação e exclusão aparecem como caminhos) dentro de `docs/{reviews,security,qa,devops}/`. Qualquer falha, inclusive delta vazio ou ilegível, cai na suíte inteira (`.githooks/pre-push:119-147`). As checagens de fast-forward e de branch protegida continuam antes, sem mudança (`:62-88`), e a decisão é tomada depois de obtida a trava, então o estado conferido é o da hora do teste. O hook local não é o portão: o CI repete a bateria inteira. Ficam três recomendações de severidade baixa, que não bloqueiam.

## Gatilhos
Mudança em controle do Forge (`.githooks/pre-push`, portão local de R-VERIFY e R-MAIN, e a fila de R-TETO). Não há segredo, rede, dependência nova nem custo (R-CUSTO).

## Achados

## Detalhe dos achados
Sondas, todas por leitura e numa cópia por `git archive` em `$TMPDIR` (os 14 testes novos passam lá):
- Nome de arquivo com quebra de linha ou aspas: o git o devolve entre aspas mesmo com `core.quotepath=false`, a linha começa com `"`, não casa com o prefixo e vai para a suíte inteira. Não há como um caminho fora das quatro pastas parecer estar dentro delas.
- Delta vazio: `<<< ""` gera uma linha vazia, que cai em `*) return 1`. Falha fechada.
- Prova forjada: a prova fica na pasta privada da trava (XDG_RUNTIME_DIR ou `forge-<uid>` com modo 700). Quem consegue gravá-la é o próprio usuário, que já poderia editar o hook. Mesmo com prova falsa, o atalho só pula testes de um delta que só tem pareceres, sobre um código que já está no remoto. Esse envio não leva código novo, e o CI repete tudo.
- A prova é por conteúdo (hash da árvore) e não por repositório: árvores iguais testam igual. Isso é aceitável.

Recomendações (severidade baixa, esforço P, dono `tech-lead`, que mantém `.githooks/`):
1. **Prova gravada com o HEAD do fim, não com o do início** (`.githooks/pre-push:149-153`). A árvore anotada é `HEAD^{tree}` lida depois da suíte, que leva cerca de 5 min. Na worktree compartilhada por vários revisores, outro agente pode fazer commit ou `merge --ff-only` durante esse tempo, e a árvore nova, que não foi testada (ou foi testada pela metade), entra na prova se a árvore de trabalho estiver limpa no fim. O caminho de abuso é pouco realista: para valer, essa árvore ainda precisa chegar ao remoto sem passar pela suíte deste clone. O impacto fica no hook local, porque o CI repete tudo. Correção mínima: ler `HEAD^{tree}` e o estado limpo antes de rodar os testes e só anotar se os dois forem iguais depois.
2. **Arquivos das quatro pastas que não são parecer seguem pelo atalho.** `docs/security/_modelo.md` é lido por `tests/test_volta_por_delta.py:651`, e o próprio `bin/forge-testes:67` o liga a `test_volta_por_delta`, uma classe que o atalho não roda. Também seguem pelo atalho os modelos de ameaças em `docs/security/ameacas/` e, sem leitor nos testes, `docs/security/aceites/`, que é a pasta do usuário. Um erro num modelo só aparece no CI. Correção mínima: excluir do atalho `_*.md` e `docs/security/aceites/`, ou derivar as classes pelo mapa de `bin/forge-testes`.
3. **A prova se propaga pelo atalho** (`.githooks/pre-push:148`, que anota também depois do caminho curto). A árvore que só acrescentou pareceres vira prova sem ter passado pela suíte inteira. Isso é intencional (`test_cadeia_de_pareceres_continua_curta`) e se limita a deltas de docs; se a recomendação 2 for adotada, a cadeia também fica restrita a pareceres. Registro informativo.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do diff e do hook, `git archive` e `python3 -m unittest tests.test_pre_push_parecer` (14 OK) numa cópia em `$TMPDIR`. Lacuna: `shellcheck`, `gitleaks` e `zizmor` não estão no PATH deste ambiente (não instalados, R-CUSTO). O `shellcheck` roda no CI do Forge.

## Volta 1
Escopo: `git diff 926b9e6f11c4e4f6ac605c50400d9a3b0db06503 441ae2727f04a76299723ca79a2c2989117148de` (`.githooks/pre-push`, `tests/test_pre_push_parecer.py`, `changelog.d/prepush-so-parecer.md`), contra o A1 do review e as recomendações 1 e 2 acima, e o `.githooks/pre-push` inteiro relido no trecho do atalho (`:113-162`). Nenhum achado bloqueante; o bloco `## Achados` continua vazio. **Veredito: aprovado.**

- **A1 do review (NeutralidadeDoNucleo fora do atalho): resolvido.** O caminho curto passa a rodar as quatro classes de `tests/test_forge.py` que varrem `docs/` no repositório (`Referencias` e `Neutralidade` por `arquivos_texto()`, `NeutralidadeDoNucleo` e `AntiDuplicacao` pelo `rglob` das pastas) (`.githooks/pre-push:150`). Conferi que nenhuma outra classe do mapa de conteúdo de `bin/forge-testes` lê pareceres do próprio repositório. Teste novo: parecer em `docs/security/` com termo de stack falha no caminho curto e a árvore não vira prova.
- **Recomendação 2 (modelos e pastas de controle): adotada pela decisão R2 do dono.** `*/_*`, `docs/security/ameacas/*` e `docs/security/aceites/*` vão à suíte inteira antes do casamento com as quatro pastas (`.githooks/pre-push:141`). Sonda do `case` em `$TMPDIR`: `_modelo.md` em qualquer das pastas, modelo de ameaças, aceite e `_*` em subpasta vão à suíte; `docs/securityx/`, linha vazia e caminho fora também; `a_b.md` segue curto, o que é correto. A recomendação 3 (a prova se propaga pelo atalho) fica agora restrita a pareceres de fato.
- **Recomendação 1 (prova com a árvore do fim): resolvida no essencial, com resíduo baixo.** A árvore e o estado limpo são lidos depois de obtida a trava e antes da suíte (`:121-122`), e a anotação exige limpo no início e no fim (`:156`). A árvore do fim, que não foi testada, não entra mais na prova (`test_prova_grava_a_arvore_do_inicio_da_suite`). A suposição do autor vale para o caso comum. O resíduo é este: estar limpo nas duas pontas não prova que a árvore ficou parada no meio. Se outro agente na worktree compartilhada fizer commit ou `merge --ff-only` durante a suíte, as classes que rodam depois da troca leem a árvore nova, e a do início é anotada sem ter passado inteira. O impacto fica restrito ao hook local: o próximo envio só de pareceres sobre essa árvore pula a suíte, e o CI repete tudo. Recomendação (severidade baixa, esforço P, dono `tech-lead`): anotar só quando `HEAD^{tree}` no fim for igual a `arvore_inicio`. É uma linha. O teste novo, que hoje espera a anotação da árvore do início mesmo com o HEAD movido, passaria a esperar que nada fosse anotado.
- Informativo, sem efeito de segurança: o comentário de `.githooks/pre-push:114` ainda diz que as classes curtas são as mesmas do gate do CI. Hoje elas diferem (o gate pula só para `docs/(reviews|qa)/`). O ajuste do texto fica com o review.

Ferramentas da volta: leitura do delta e do hook; `git archive` de 441ae27 em `$TMPDIR` e `python3 -m unittest tests.test_pre_push_parecer` (17 testes, OK); sonda do `case` do atalho com caminhos de borda. As lacunas de ferramenta são as mesmas de antes.

