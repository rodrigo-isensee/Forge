---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-seg-conformidade
commit: a4266c77896643b544328310ae6deee34665d6c1
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-22
---
# Review: v0478 (E113.3, melhoria/v0480-seg-conformidade)

Diff `b0895f6cc..a4266c77`: S22, A20 e RESTO-SOBE em `hooks/conformidade.py` (55 linhas de código, dentro do H1), 21 fixtures, 13 mutantes em duas specs, `tests/test_conformidade_seg_v0480.py`, fragmento em `changelog.d/`.

## Achados
- A1 (bloqueante) hooks/conformidade.py:2613 · S22 incompleto contra R-MAIN: com candidatas develop e main, `ramo_em` pega a primeira de integração, não a da regra mais dura (docstring). Na main, o tech-lead roda `git switch develop; git merge feat` e o merge passa. Sugestão: main/master antes das outras.
- A2 (recomendado) hooks/conformidade.py:2230 · S22 com falso positivo novo: `(git switch -c x) && git push origin` na main era livre na base e agora recusa (R-MAIN); o sinal `)` depois do switch desfaz a cadeia, mas o subshell só segue com `&&` se o switch rodou. Idem `{ git switch -c x; } && git push`.

## Sondas
- S1 · fixture branch main, forge:tech-lead, `git switch develop; git merge feat` · espera: código 2, R-MAIN · obtido: código 0 (base b0895f6 também 0; controle `git merge feat` na main: 2)
- S2 · fixture branch main, forge:tech-lead, `git checkout develop || true; git merge feat` · espera: código 2, R-MAIN · obtido: código 0

## Parecer
Reprovado por A1. O cartão S22 diz que, com a troca incerta, a branch de antes segue candidata e a de integração decide; quando as duas candidatas são de integração, a função devolve a primeira da tupla (a nova), e a regra da main (R-MAIN no merge, linha 2678) deixa de valer. Não é regressão (a base também libera), mas é o mesmo gatilho que o item fecha para o push, provado pelas sondas S1 e S2. Correção pequena em `ramo_em`: escolher `main`/`master` antes de `develop`/`homolog`, com fixture e mutante da linha.

A2 é recomendado: falha fechada, fora do gatilho de segurança; vira cartão depois do merge (tratar `)` e `}` que fecham um grupo cujo último comando é a troca como parte da cadeia).

Conferido e sem achado: A20 (`resto_com_barra`, posicional no texto largo) e RESTO-SOBE (`resto_normalizado` só quando o resto não começa por nome do git). Sondas extras verdes no head: `"$X/hooks/../../config"`, `"$X/a/../../config"`, `d=.git; cp -rT ev "${d}/."`, `set -- .git; cp ev "${1}/config"` recusam; `"$(mktemp -d)/a/b"`, `d=docs; cp x "$d/a.md"` e `git switch -c x && git add . && git commit -m a && git push origin` (em feature) seguem livres. Os valores de `ramos` viraram tupla; os consumidores (`ramo_em` só) foram conferidos.

Verificadores: `bin/forge-mutante --processos 1` nas duas specs no rev a4266c778966: 13 de 13 morreram (S22a-f, A20a-d, RS1-3), uma guarda por linha mudada. `python3 -m unittest tests.test_conformidade_seg_v0480`: 3 testes OK. Suíte inteira: sem run de CI na branch (sem PR, E113.3); fica para o CI do PR.
