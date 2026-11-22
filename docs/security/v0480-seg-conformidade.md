---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-seg-conformidade
commit: 14696864b679da061fc87f6dda8ad0b7227adb4f
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-22
---
# Review de segurança: v0478 (E113.8, revalidação da volta única E113.6 do hooks/conformidade.py)

Revalidação por delta (`forge-check parecer delta`, intervalo `a4266c77..14696864`): no domínio, `hooks/conformidade.py` (S22 com `por_dureza`, `alcance_da_troca`, a pilha de subshells no `conferir_partes`, `ramos_em` e `merge_na_integracao`; `resto_se_anula` no `opaco_sem_resto`; `+=` no `textos_do_valor`; corpos sós no `valor_calculado`), 66 fixtures novas e `tests/test_conformidade_seg_v0480.py`; fora do domínio, changelog, `docs/hooks-fixtures.md`, specs de mutante e `tests/pesos-d4.json`, não relidos. A rodada anterior está no git (commit do parecer sobre a4266c77).

Método: 107 sondas da matriz (as minhas S1 a S6, as 29 do QA, o corpus de legítimos e as formas novas de subshell) mais 34 de apoio, cada uma na cabeça e na base a4266c77, com o montador das fixtures (`tests/test_hooks.py`, `Fixture.montar` e `rodar`), repositório na `main` (S22) ou em `feature/x` (escrita), papel de implementação da stack salvo indicação.

## Gatilhos
Gatilhos: guarda de controle (hook conformidade), R-MAIN, escrita no diretório do git.

## O afrouxamento do subshell é seguro? O resto só aperta?
Comparando a cabeça com a base nas 107 sondas, só o subshell libera o que a base recusava (15 sondas). Oito dessas liberações estão certas: `(git switch -c x) && git push origin`, com quebra depois do `&&`, `( (…) )`, `(… && true)`, `(cd . ; …)`, `&& (git push origin)`, `2>/dev/null` e `(shopt …; …)`. A troca de branch muda o HEAD em disco e o `&&` depois do `)` garante o código 0 do subshell. As outras sete são brecha nova (A3). Dentro do subshell, `exit` e `exec` antes da troca encerram o subshell com 0 sem rodar a troca, e o push sai na `main`. A base recusava essas sete. Por isso o afrouxamento **não é seguro como está**. Na mesma família, `(exit 0; git switch -c x) && git reset --hard HEAD~1` recusava na base (R-REVIEW) e na cabeça passa.

O resto só aperta. Nenhuma outra sonda que a base recusava passa na cabeça, e o código confirma isso:
- `por_dureza` só reordena as candidatas, com a mais dura primeiro.
- O merge confere cada candidata.
- `resto_se_anula` manda mais formas ao `destino_opaco`, que é o caminho que recusa.
- O `+=` só acrescenta textos precisos.
- O `valores is None` só alimenta o `valor_no_git`, que serve para recusar.

O corpus de legítimos segue livre: `"$(mktemp -d)/c"`, `"$(mktemp -d)/."`, `"$(mktemp -d)/../x"`, `"$X/a/../docs/x"`, `"$(pwd)/docs/c"`, `d=docs`, `d=do; d+=cs`, `d=docs; d+=/x`, `git switch -c x && git push origin`, com quebra e com `git add -A`, e, na feature, `git switch -c x && git merge develop`.

## Achados anteriores
- A1 (merge com duas candidatas): fechado. `false && git switch develop; git merge develop` e as formas com `homolog`, `true ||`, `| cat;`, `!` e `( … );` recusam com R-MAIN e passavam na base. A forma com `exit` no subshell segue aberta e foi para o A3.
- A2 (resto que se anula): fechado na dimensão do resto. As 17 formas recusam: `/..`, `/.`, `/a/..`, `/./`, `/.//`, `"$X"/.`, `"$X"/..`, `"$X"/./..`, `"${X}/.."`, `/../..`, `/a/../.`, `$(cat f)/.`, `mv`, `TMPDIR=.git` e `export TMPDIR=.git` com `mktemp`. A forma `cp -rT ev "$X/."` da minha S6 segue livre, mas não por causa do resto: `cp -rT ev "$X"`, sem resto, também passa (na base e na cabeça). Foi para o A5.
- QA A1 (a negação) e QA A2 (o `+=`): fechados. Recusam `! git switch|checkout … && push`, `(! …) &&` e as 9 formas de `+=` (`d+="t"`, `d+=$e`, `d+=$'t'`, `declare`, `export`, três vezes, `d+=/../.git`).

## Achados
- A3 (bloqueante) hooks/conformidade.py:2279 · S22-SUB afrouxa: `exit` ou `exec` antes da troca no subshell sai com 0 sem trocar; `(exit 0; git switch -c x) && git push origin` na main passa (a base recusava), e o mesmo com `git reset --hard` e com `git merge develop`
- A4 (bloqueante) hooks/conformidade.py:2249 · O `cd` dentro de `( … )` vaza para fora no hook (o contexto só separa substituições): `(cd /tmp); git push origin`, `(cd /) ; git merge develop` e `(cd /tmp; true); git reset --hard HEAD~1` na main passam; o bash roda os três na main
- A5 (recomendado) hooks/conformidade.py:1780 · Cópia de pasta para opaco sem resto passa onde a de arquivo recusa: `cp -rT ev "$X"`, `cp -r -T ev "$X"`, `cp -r ev/. "$X"` com X de fora da linha (`cp ev/config "$X"` recusa); igual na base

## Sondas
- S1 · na main: `(exit 0; git switch -c x) && git push origin` · espera: código 2, R-MAIN (como na base) · obtido: código 0 na cabeça, 2 na base
- S2 · na main: `(exec true; git switch -c x) && git push origin` · espera: código 2, R-MAIN · obtido: código 0 na cabeça, 2 na base
- S3 · na main: `(true || exit 0; git switch -c x) && git push origin` · espera: código 2, R-MAIN · obtido: código 0 na cabeça, 2 na base
- S4 · na main: `(exit 0 && git switch -c x) && git push origin` · espera: código 2, R-MAIN · obtido: código 0 na cabeça, 2 na base
- S5 · na main: `(exit 0; git switch -c x) && git reset --hard HEAD~1` · espera: código 2, R-REVIEW (como na base) · obtido: código 0 na cabeça
- S6 · na main, papel forge:tech-lead: `(exit 0; git switch homolog) && git merge homolog` · espera: código 2, R-MAIN · obtido: código 0 (cabeça e base)
- S7 · repositório descartável na main: `(exit 0; git switch -c x) && git branch --show-current` · espera: o bash segue o `&&` sem trocar · obtido: imprime main
- S8 · na main: `(cd /tmp); git push origin` e `(cd /tmp) && git push origin` · espera: código 2, R-MAIN · obtido: código 0 (cabeça e base)
- S9 · na main: `(cd /) ; git merge develop` · espera: código 2, R-MAIN · obtido: código 0 (cabeça e base)
- S10 · na main: `(cd /tmp; true); git reset --hard HEAD~1` · espera: código 2, R-REVIEW · obtido: código 0 (cabeça e base)

## Detalhe dos achados
**A3.** Evidência: hooks/conformidade.py:2279. A troca pendente só cai quando o sinal depois dela não é `&&`, `(` ou `)`. O `alcance_da_troca` (hooks/conformidade.py:860) olha só o sinal logo antes da troca e o começo de cada subshell; ninguém olha os comandos anteriores dentro do mesmo subshell.

Caminho de ataque: o agente na `main` (ou na `homolog`) escreve `(exit 0; git switch -c x) && <ação crítica>`. O hook lê a troca como certa e libera. O bash encerra o subshell com 0 antes da troca e roda o push, o `reset --hard` ou o merge na `main` (R-MAIN, R-REVIEW). As formas provadas são `exit`, `exit 0`, `builtin exit 0`, `exec true`, `true || exit 0;`, `exit 0 &&`, `: ; exit 0 ;` e `exit 0` seguido de quebra de linha. Todas recusavam na base: é regressão do afrouxamento.

Severidade: alta (contorna R-MAIN numa ação crítica, sem ninguém ver).

Correção mínima: a troca dentro de um subshell só vale certa quando é o primeiro comando dele (sinal antes `(`, de nível em nível) e os comandos depois dela, até o `)`, vêm por `&&`. Qualquer outro comando antes da troca no mesmo subshell devolve a branch de antes como candidata. É uma lista positiva: cobre `exit`, `exec`, `return`, função, `trap` e `kill` sem listar cada um. `(cd . ; git switch -c x) && git push` passa a recusar, falso positivo aceitável; inverta a fixture `s22-subshell-cd-e-switch-e-e-push-libera`. Fixtures: S1 a S6. Esforço: P. Dono: quem implementou E113.6.

**A4.** Evidência: hooks/conformidade.py:2249. O `contexto(sub)` cria uma pasta e branches separadas só por substituição (`sub`). O `( … )` não ganha contexto próprio, e o `cd` lá dentro muda a pasta dos comandos de fora. O `segmento` devolve `/tmp`, fora de qualquer repositório, e o push, o merge e o reset seguintes não acham branch nem regra.

Caminho de ataque: na `main`, `(cd /tmp); git push origin`. O hook confere o push em `/tmp` e libera, e o bash o roda no projeto, na `main`. O mesmo vale para `git merge develop` (R-MAIN) e `git reset --hard` (R-REVIEW). Não é regressão (a base faz igual), mas é a dimensão "escopo do subshell" do cartão S22-SUB, na mesma função que a volta mexeu. Severidade: alta. Pela matriz, vira dimensão nova.

Correção mínima: o `(` abre um contexto (pasta e branches) como a substituição, e o `)` o descarta, voltando à pasta de antes. Só o HEAD em disco atravessa o `)`, pela regra do A3. Fixtures: S8 a S10 recusam; `(cd docs && ls) && git status` segue livre. Esforço: P. Dono: quem implementou E113.6.

**A5.** Evidência: hooks/conformidade.py:1780 (`destino_opaco`). `cp ev/config "$X"` recusa, mas `cp -rT ev "$X"`, `cp -r -T ev "$X"` e `cp -r ev/. "$X"` passam, na base e na cabeça. Com valor da linha (`X=.git;`, `$(cat f)`, `$(printf %s .gi)t`) o hook recusa.

Caminho de ataque: X vem de fora da linha (o ambiente da sessão) apontando para `.git`, e a cópia da pasta grava `.git/config`. É menos realista que o A3 e o A4, porque o estado do shell não persiste entre chamadas. Severidade: média.

Correção mínima: a cópia recursiva (`-r`, `-R`, `-a`) com destino opaco sem resto segue a mesma regra da cópia de arquivo. Esforço: P. Dono: quem implementou E113.6.

## Riscos aceitos e ferramentas
Nenhum risco aceito. A suíte não rodou aqui; ela roda inteira só no CI. Rodei as 141 sondas com o montador das fixtures, na cabeça e na base, e o S7 num repositório descartável. As tabelas das sondas ficaram só na área de rascunho desta sessão. Ferramentas: leitura do delta e o montador das fixtures; nenhuma varredura externa.
