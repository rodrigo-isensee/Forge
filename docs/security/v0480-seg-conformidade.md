---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-seg-conformidade
commit: a4266c77896643b544328310ae6deee34665d6c1
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-22
---
# Review de segurança: v0478 (E113.2, cartões S22, A20 e RESTO-SOBE do hooks/conformidade.py)

Revisão completa única do diff `b0895f6c..a4266c77` (hooks/conformidade.py, 23 fixtures, tests/test_conformidade_seg_v0480.py, mutantes). Cada sonda rodou na cabeça e na base (`git archive b0895f6c`), com o mesmo montador das fixtures (`tests/test_hooks.py`: `Fixture.montar` e `rodar`), repositório na `main` e um papel de implementação da stack, salvo onde se indica.

## Gatilhos
Gatilhos: guarda de controle (hook conformidade), R-MAIN, escrita no diretório do git.

## A mudança só aperta?
Sim. Nenhuma das 55 sondas que passaram pela base e pela cabeça foi recusada na base e liberada na cabeça. Pelo código: o S22 só acrescenta candidatas a `ramos` e o `ramo_em` (hooks/conformidade.py:2613) troca a mais nova pela de integração quando há uma, nunca o contrário (com uma candidata só, o resultado é o de antes); o A20 só acrescenta `barrar` (hooks/conformidade.py:1772) e o posicional só soma a linha aos textos largos, lidos com `any` para recusar (hooks/conformidade.py:1737, 1757, 1900); o RESTO-SOBE só normaliza o resto quando a 1ª parte não é nome do git, caso que antes devolvia `None`, e o resultado só entra como alvo a mais (hooks/conformidade.py:1848, 1831). O corpus de legítimos das sondas segue livre: `git switch -c x && git push origin`, com quebra e com `git add -A` no meio, `d=docs; cp … "$d/c"`, `"$(mktemp -d)/c"`, `"$(pwd)/docs/c"`, `"$(mktemp -d)/../x"`, `"$X/a/../docs/x"`.

## Sondas refeitas dos cartões
- S22: as 10 formas incertas (`false && git switch -c x; git push origin`, `true || … &&`, `| cat &&`, `&& git status;`, `&`, `|&`, `{ …; } &&`, `( … ) &&`, `if false; then …; fi;`, `git checkout -b`) recusam com R-MAIN na cabeça; na base, 9 delas passavam. As 3 formas certas liberam. Fechado para o push; aberto para o merge (A1).
- A20: `"$(echo .git)/."`, `set -- .git; … "$@"/c`, `d=.git; … "$d/."`, `"${d}/x/y"`, `"$(printf %s .git)/."` recusam na cabeça e passavam na base. Fechado.
- RESTO-SOBE: `"$X/a/../config"`, `"$X/a/../../config"`, `"$X/../hooks/pre-push"`, `TMPDIR=.git` e `export TMPDIR=.git` com `"$(mktemp -u)"/../config` e `"$(mktemp -d)"/../config` recusam na cabeça e passavam na base. Aberto quando o `..` é o fim do resto (A2).

## Achados
- A1 (bloqueante) hooks/conformidade.py:2613 · S22 incompleto no merge: com duas candidatas de integração o ramo_em devolve a mais nova, não a mais dura; na main, `false && git switch develop; git merge develop` passa (develop sobre develop) e o bash mescla a develop na main
- A2 (bloqueante) hooks/conformidade.py:1848 · RESTO-SOBE e A20 incompletos: o resto que se anula (`/..`, `/.`, `/a/..`) depois de opaco que o hook não sabe passa; `TMPDIR=.git; cp ev/config "$(mktemp -d)"/..` grava .git/config, e `"$X/.."`, `"$X/."` passam onde `"$X"` e `"$X/"` recusam

## Sondas
- S1 · na main, papel de implementação da stack: `false && git switch develop; git merge develop` · espera: código 2, R-MAIN (merge na main é do usuário) · obtido: código 0 (cabeça e base)
- S2 · na main, papel forge:tech-lead: `false && git switch homolog; git merge homolog` · espera: código 2, R-MAIN · obtido: código 0 (cabeça e base)
- S3 · na main: `git merge develop` (controle) · espera: código 2, R-MAIN · obtido: código 2, R-MAIN
- S4 · `TMPDIR=.git; cp ev/config "$(mktemp -d)"/..` · espera: código 2, R-CONFORMIDADE (.git/config) · obtido: código 0 (cabeça e base); num repositório descartável, o mesmo comando grava ev/config em .git/config
- S5 · `cp ev/config "$X/.."` e `cp ev/config "$X/a/.."` · espera: código 2, como `cp ev/config "$X"` · obtido: código 0 (cabeça e base); com X apontando para .git/hooks, grava .git/config
- S6 · `cp ev/config "$X/."`, `cp -rT ev "$X/."`, `cp ev/config "$X/./"`, `cp ev/config "$(cat f)/."` · espera: código 2, como `"$X"` e `"$X/"` · obtido: código 0 (cabeça e base)

## Detalhe dos achados
**A1.** Evidência: hooks/conformidade.py:2613 (`next((n for n in nomes if n in INTEGRACAO), nomes[0])`) e o merge em hooks/conformidade.py:2678 (`atual in INTEGRACAO and not all(b == atual …)`). Caminho de ataque: o agente na main (ou na homolog) escreve uma troca de branch que não roda (`false &&`, `true ||`, `| cat;`) para outra branch de integração e mescla essa mesma branch; o hook lê "develop sobre develop" e libera, o bash mescla a develop na main por qualquer papel (R-MAIN) e, na homolog, o tech-lead mescla sem passar pela regra da homolog. É a própria brecha do cartão S22, que o diff fecha para o push (lá qualquer candidata de integração já recusa) e deixa aberta para o merge; a docstring do `ramo_em` promete "a da regra mais dura", e entre main e develop a mais dura é a main. Severidade: alta (contorna R-MAIN, ação crítica, sem ninguém ver). Correção mínima: com a troca incerta, o hook confere a regra com cada candidata e recusa se alguma recusar, nos quatro chamadores do `ramo_em`: o merge (hooks/conformidade.py:2677), o `git_integracao` (hooks/conformidade.py:2871), o rebase (hooks/conformidade.py:2927) e o push (hooks/conformidade.py:3077); alternativa mais curta: o `ramo_em` ordena as candidatas por dureza (main e master, depois homolog, depois develop, depois as outras) e o merge recusa também quando há mais de uma candidata e alguma difere da branch mesclada. Fixtures: S1, S2 e a forma com `true ||` e `| cat;`. Esforço: P. Dono: quem implementou E113.1.

**A2.** Evidência: hooks/conformidade.py:1848 (o resto normalizado que fica vazio devolve `None`), hooks/conformidade.py:1769 e 1780 (o `resto_com_barra` sai sem recusar quando o hook não sabe o valor) e hooks/conformidade.py:1718 (o `opaco_sem_resto` só tira `/`, não `.` nem `..`). Caminho de ataque: o agente escreve o destino com um resto que se anula ou sobe um nível (`/.`, `/..`, `/a/..`); o hook trata como resto livre, quando o valor é o do opaco (ou o pai dele) que ele não sabe. Com `TMPDIR=.git` e `mktemp -d` a linha sozinha grava .git/config (S4, conferido num repositório descartável); com uma variável exportada numa chamada anterior (`X=.git/hooks`), `cp ev/config "$X/.."` faz o mesmo. É a dimensão do cartão RESTO-SOBE (o `..` depois do opaco) com o `..` no fim, e do A20 (o resto `/.`) com valor que o hook não sabe. Severidade: alta (escrita no .git: config e hooks, execução de código no próximo comando do git). Correção mínima: depois de normalizar o resto, o que fica vazio (`/.`, `/./`, `/..`, `/a/..`, `/a/../.`) é o opaco sem resto e vai ao `destino_opaco` (recusa o valor que o hook não calcula, como `"$X"`), e o `..` que sobe acima do opaco (`/..` no fim) recusa como o opaco sem resto, porque o pai do valor que o hook não sabe também é desconhecido; vale também para o `opaco_sem_resto` (hooks/conformidade.py:1718) e para o `origem_do_git_no_opaco`. Fixtures: S4, S5, S6, e as legítimas `"$(mktemp -d)/c"` e `"$(mktemp -d)/../x"` seguem livres. Esforço: P. Dono: quem implementou E113.1.

## Riscos aceitos e ferramentas
Nenhum risco aceito. A1 e A2 já existiam na base (não são regressão), mas são as mesmas brechas dos cartões S22 e RESTO-SOBE/A20 e por isso bloqueiam a entrega deles. Suíte: não rodei a suíte (só no CI); rodei as sondas acima e conferi as fixtures novas pelas próprias entradas. Ferramentas: só leitura do diff e o montador das fixtures; nenhuma varredura externa.
