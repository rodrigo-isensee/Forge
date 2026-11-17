---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-hook-texto-merge
commit: 9d9a069d997fffe261c4563b8e1c6137b8382773
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-16
---
# Review: v047-hook-texto-merge (E2.335, cartão HOOK-TEXTO-COM-MERGE)

Parecer completo (primeira passada; não havia parecer anterior), no head 9d9a069d, base develop 5e74c70e. Revisor: instância que não fez a entrega.

## Achados
- A1 (recomendado) hooks/conformidade.py:1322 · A rede D da conformidade segue lendo o texto cru: num projeto Forge, `cat > "$TMPDIR/p.txt" <<'FIM'` com git merge no corpo ainda recusa (R-CONFORMIDADE, sonda abaixo). Fora do cartão (o hook R-REVIEW); vale cartão próprio se o falso positivo aparecer em projeto.

## Sondas

## Parecer
**Aprovado.** O diff faz o que o cartão pede e nada além: antes da rede D (`fora_da_gramatica_com_heredoc`), o alvo do `cat > arq <<` entre aspas ou com `$NOME`/`${NOME}` vira `_`, o mesmo caminho literal que já passava. A troca só alcança a rede D; M3, reavaliação e as regras da linha seguem lendo o texto original.

Leitura (R-REVIEW, R-CONFORMIDADE):
- `ALVO_DO_CAT` (hooks/parecer.py:73) não cruza linha (`[ \t]` e classes sem `\n`), não aceita `\`, aspa interna, `$(`, `${X:-…}`, crase nem curinga (`*?[`), e exige `<<` em seguida: a palavra trocada é uma só para o bash e não roda nada. `$1` e `$?` ficam de fora (só nome que começa por letra ou `_`).
- O corpo do heredoc não é tocado: com delimitador sem aspas, `$( )` e crase no corpo seguem na rede D.
- Tamanho: 7+1 linhas em hooks/parecer.py; um comportamento só, corpus próprio (11 fixtures `texto-*`, 3 libera e 8 recusa), índice `docs/hooks-fixtures.md` atualizado.
- PA-7 conferido: AR-1 (3 guardas mudadas, 3 mutantes, `--cobertura` limpo), AR-10 (sondas abaixo), AR-12 (spec bate com o head: os 3 morreram), AR-13 (sem curinga no alvo aceito).

Ferramenta (citada, não refeita):
- `python3 -m unittest tests.test_hooks_parecer_pasta.PastaDoGit.test_corpus_texto_passa_e_barra` no head: `Ran 1 test in 28.194s OK`.
- `bin/forge-mutante --processos 1 tests/mutantes/v047-hook-texto-merge.json`: HTM1 morreu (parecer.py:960), HTM2 morreu (:72), HTM3 morreu (:73).
- `bin/forge-mutante --cobertura --base 5e74c70e`: nenhuma condição mudada sem mutante.
- Suíte completa: fica no CI do PR (ainda sem PR nesta etapa).

Sondas executadas (fixtures temporárias no corpus `texto-*` do parecer, apagadas depois; nenhuma prova bloqueante, por isso fora do bloco `## Sondas`), todas com espera código 2 e obtido código 2:
`F=x.sh; cat > "$F" <<'EOF'` + git merge + `sh x.sh`; `. "$TMPDIR/x"` depois do gravado; corpo com `$(gh pr merge …)` e com crase sob `<<EOF`; `<<'EOF' && gh pr merge …` na linha do cat; `${X:-$(git merge …)}` no corpo com alvo `$TMPDIR/x` sem aspas.

Sonda do A1 (hook conformidade, fixture `heredoc-parecer-qa-cat-e-echo-libera` com o alvo trocado por `"$TMPDIR/p.txt"`): espera 0, obtido 2, ``R-CONFORMIDADE: `$TMPDIR` com ação crítica: o hook não modela``. Não bloqueia: o cartão e as fixtures (`forge: false`) são do hook R-REVIEW em outro repositório.
