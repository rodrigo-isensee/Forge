---
tipo: review
contrato: 1
pedido: versao-033
branch: melhoria/hook-parecer-034
commit: ef5e341a146734ca2e74aa05f458fddaf01243a6
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-04
---
# Review: hook-parecer-034 (PARECER-HOOK-DICA-EDIT e PARECER-BARRA-FETCH)

Base b45e40a, HEAD ef5e341. Dois commits: 6a7a85a (mensagens de recusa do `hooks/parecer.py`, frase em `docs/hooks.md`, 4 fixtures `texto-barra-heredoc-*`) e ef5e341 (só testes: corpus `atualiza-*` com 5 casos e o método `test_corpus_atualiza_passa_e_barra`).

## Achados
- A1 (bloqueante) hooks/parecer.py:669 · o ramo novo vale também quando o dono roda o corpo (sh, bash: corpo_de_heredoc é True) e a causa é um heredoc aninhado sem aspas; a dica troca o <<'FIM' pelo script fora do hook. Use isinstance(corpo_de_heredoc, str) e uma fixture com sh
- A2 (recomendado) hooks/parecer.py:86 · com o programa do texto sh ou ./x.sh, "grave pelo Write ou Edit e rode o programa noutra chamada" aponta a lacuna [B] (script fora do hook); a classe já existia na base (M3). Cartão à segurança para a dica não nomear rodar o arquivo gravado

## O que foi lido e rodado
- Diff inteiro de código e teste: `hooks/parecer.py` (+10/-6), `tests/test_hooks_parecer_pasta.py` (+9), a frase de `docs/hooks.md`, o fragmento `changelog.d/hook-parecer-034.md`, as 9 fixtures novas e a spec de mutantes.
- `python3 -I -m unittest discover -s tests -p test_hooks_parecer_pasta.py`: 3 testes, OK (24,9 s). É o módulo das fixtures `pasta-*`, `texto-*` e `atualiza-*` do hook; o `test_hooks` inteiro não rodou (D-5).
- `bin/forge-mutante tests/mutantes/hook-parecer-034.json` (rev ef5e341a1467): M1 a M5 morreram.
- Comparação de comportamento: o hook da base (b45e40a) e o da branch sobre as mesmas 7 entradas, no mesmo repositório temporário. Código de saída igual em todas (6 recusas com 2, o `fetch` mais `merge --ff-only` da própria branch com 0); só o texto da recusa muda.

## Nenhuma recusa passou a liberar
Confirmado por leitura e por execução. O único fluxo novo é o `if corpo_de_heredoc:` dentro do `except ValueError`, que chama `bloquear` (saída 2) antes do `bloquear` que já existia: o ramo continua recusando sempre. As outras três mudanças trocam só a frase do `Corrigir:`. O cartão PARECER-BARRA-FETCH não mexe no hook: o corpus `atualiza-*` prova que `fetch`, `merge --ff-only` e `pull --ff-only` do autor da volta na branch reprovada passam e que, na develop, o `merge --ff-only` e o `pull --ff-only` da mesma branch seguem barrados pelo parecer reprovado (stderr `R-REVIEW: docs/reviews/p1-1.md`). O teste afirma o mínimo de 5 e os dois lados, e o nome da fixture diz o esperado (item 11 do checklist).

## As mensagens ensinam contorno? (A1 e A2)
A1, defeito provado: a premissa do ramo novo, "`<<'FIM'` já está na linha", vale no caso do cartão (corpo de `.md` gravado e `git` na mesma chamada; a sonda mostra `corpo_de_heredoc='git'`), mas não quando o dono roda o corpo. Entrada `sh <<'EOF'` com o corpo `cat <<Y`⏎`$(date)`⏎`Y`⏎`git merge origin/develop`: a sonda mostra `corpo_de_heredoc=True` e o `ValueError` vem do heredoc aninhado sem aspas. Na base, a recusa mandava "use <<'FIM'", que corrige a causa e deixa o corpo lido e conferido. Na branch, manda "grave pelo Write ou Edit e rode o programa noutra chamada", ou seja, gravar o `git merge origin/develop` num script e rodá-lo noutra chamada, que o `parecer` não lê (`docs/hooks.md`, [B]). Nenhuma recusa libera, mas a dica nova leva ao caminho que o hook não vê, e a causa que ela diz está errada nesse caso. Correção: no `except`, a mensagem nova só com `isinstance(corpo_de_heredoc, str)` (o arquivo gravado que um programa do texto roda, o alvo do cartão), e a antiga com `True`. Fixture `texto-barra-*` com `sh <<'EOF'` e um heredoc aninhado sem aspas, que afirme o `<<'FIM'` no stderr, e o M1 da spec trocado para matar essa troca.

A2: as recusas M2 e M3 já mandavam, na base, "rode o programa noutra" quando o programa é `sh f` ou `./publica.sh`. A branch só troca "numa chamada do Bash" por "Write ou Edit" e não cria a classe. Fica como recomendação e cartão à segurança, fora deste PR.

## M14 e o lote dos dois cartões
- Teto: `hooks/parecer.py` 16 linhas mais `tests/test_hooks_parecer_pasta.py` 9 linhas, 25 linhas. As fixtures de `tests/hooks/`, a spec de `tests/mutantes/`, o fragmento e o `.md` ficam fora. Abaixo de 150, sem linha de exceção (que não valeria aqui, porque mexe em `hooks/` e em um PROTEGIDO).
- Um PR ou dois: cabem num PR. A regra da 0.34 (`versao-0.34.md`, linha 3) permite "PR próprio ou lote por arquivo", e os dois cartões são do mesmo arquivo, `hooks/parecer.py`. A M14 pede uma classe de comportamento por PR em `hooks/`, com corpus próprio. Só o PARECER-HOOK-DICA-EDIT muda o hook (texto da recusa, com o corpus `texto-barra-heredoc-*-dica-*`). O PARECER-BARRA-FETCH não muda nenhuma linha de `hooks/`: ele prova o que já existe, com o corpus próprio `atualiza-*`. Há uma classe em `hooks/` e dois corpus separados, então não há achado M14.
- `hooks/parecer.py` está em `PROTEGIDOS` (`tests/catraca.py:44`), e a catraca do PR pede o rótulo do dono depois do último push.

## Regras de ferramenta
Na revisão rodei só o módulo dos testes tocados e a mutação (acima). `shellcheck` não se aplica (nenhum shell tocado). A suíte inteira fica com o QA e o CI (D-5).

## Fora do código (ao Jarvis)
Nenhum dos dois cartões está na lista dos 20 da 0.34 (`docs/propostas/backlog/versao-0.34.md` do forge-contrib), e a lista diz que nenhum trabalho novo da 0.34 abre antes do "sim" do dono. O review não decide isso: fica a conferir com o dono antes do merge.

## Parecer
Reprovado por A1 (bloqueante): o comportamento de bloqueio está preservado e testado, e o teto e o lote estão dentro da M14. A volta é pequena: uma condição em `hooks/parecer.py:669`, uma fixture e o M1 da spec. A2 é recomendação e não devolve.
