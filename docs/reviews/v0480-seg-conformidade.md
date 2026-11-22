---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-seg-conformidade
commit: bf57b17e42a1c6019ac7f4c721f9f4900c51cc4e
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-22
---
# Review: v0478 (E113.12, melhoria/v0480-seg-conformidade)

Revalidação da 2ª volta (H2/H3, R-REVIEW), que responde aos achados A3, A4 e A5 da segurança E113.8. Delta lido: `forge-check parecer delta` deste parecer, intervalo `14696864..bf57b17e` sem o que veio da `develop`: `hooks/conformidade.py` (`alcance_da_troca`, a pilha de pastas do subshell, `origem_do_git_no_opaco` com `prog` e `valor_de_fora`), 26 fixtures novas e uma invertida, `tests/mutantes/v0480-seg-conformidade-6.json`, `tests/test_conformidade_seg_v0480.py`, `docs/hooks-fixtures.md` e o fragmento do changelog. `tests/pesos-d4.json` mudou só com nomes de testes vindos da `develop`.

## Sondas
- S1 · main, `(git switch -c x || exit 0) && git push origin` · espera: código 2 · obtido: código 2
- S2 · main, `( (git switch -c x) ) && git push origin` · espera: código 0 · obtido: código 0 (a troca é o primeiro comando nos dois níveis)
- S3 · main, `(true && git switch -c x) && git push origin` · espera: código 2 · obtido: código 2
- S4 · main, `(cd /tmp) ; (cd /) ; git merge develop` · espera: código 2 · obtido: código 2 (a pilha de pastas segue em par com a de subshells)
- S5 · feature/x, `(cd src; ls) ; git push origin feature/x` · espera: código 0 · obtido: código 0
- S6 · main, `( (cd /tmp) ; git switch -c x) && git push origin` · espera: código 2 · obtido: código 2
- S7 · feature/x, `cp -av ev "$X"` e `cp -t "$X" -R ev` · espera: código 2 · obtido: código 2
- S8 · feature/x, `cp -r ev "$(mktemp -d)"` e `cp -v ev/a "$X"` · espera: código 0 · obtido: código 0

## Parecer
Aprovado. A3: `alcance_da_troca` só deixa a troca sair de um nível quando o sinal antes do que abre o nível é `(`, de nível em nível (`primeiros`), então `exit`, `exec`, `cd` ou função antes dela prendem a troca no subshell. A4: o `(` empilha a pasta de fora e o `)` que fecha um subshell aberto a devolve, com a pilha em par com a de subshells (só empilha no `(`, só desempilha com `fecha`); a branch continua valendo fora, como antes. A5: a cópia recursiva (`-r`, `-R`, `-a`, `--recursive`, `--archive`, também combinadas) só recusa com valor de fora da linha (`valor_de_fora`), e `d=docs; cp -rT ev "$d"` segue livre.

Nenhum teste afrouxado. No delta nenhuma fixture antiga mudou, salvo a invertida `s22-subshell-cd-e-switch-e-e-push` (libera → bloqueia), que agora recusa mais: o A3 aplicado, com falha fechada. `test_conformidade_seg_v0480.py` só ganhou três testes, sem baixar mínimo, e o S22-SUB segue com `recusam=9, liberam=5`. Dentro da volta, o `liberam` do A5-COPIA subiu de 2 para 4. O teto do corpus (`test_hooks_volta_corpus`) não está no delta.

Verificadores: `python3 -I tests/test_conformidade_seg_v0480.py` no head bf57b17e, com o ambiente limpo: 11 testes OK (47 s). `bin/forge-mutante tests/mutantes/v0480-seg-conformidade-6.json`: S22p, S22c, A5c, A5r e A5v morreram (um por linha de guarda mudada: hooks/conformidade.py:873, 2297, 1861, 1871). `--cobertura --base 14696864`: as linhas de guarda de hooks/conformidade.py estão cobertas. A suíte inteira fica com o CI do PR (V2), sem rerrodar aqui.
