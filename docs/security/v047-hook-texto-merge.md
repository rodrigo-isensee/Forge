---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-hook-texto-merge
commit: 9d9a069d997fffe261c4563b8e1c6137b8382773
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-16
---
# Review de segurança: v047-hook-texto-merge (E2.271, HOOK-TEXTO-COM-MERGE)

Parecer completo (não havia parecer anterior) sobre o head 9d9a069d, base develop 5e74c70e. Escopo: `hooks/parecer.py` (`VARIAVEL`, `ALVO_DO_CAT` e a chamada da rede D na linha 960), as 11 fixtures novas `tests/hooks/parecer/texto-*`, `tests/mutantes/v047-hook-texto-merge.json`, `docs/hooks-fixtures.md` e o fragmento do changelog.

## Gatilhos
Hook de guarda do `R-REVIEW` (controle que analisa entrada: classificador de comando Bash). A mudança afrouxa uma rede de recusa; a pergunta do portão é se afrouxa algo além da classe pedida.

## Achados

## Sondas

## Detalhe dos achados
Sem achado bloqueante nem recomendado.

**O que muda.** Só a rede D (`fora_da_gramatica_com_heredoc`, `hooks/parecer.py:960`) recebe o texto com o alvo do `cat > arq <<` trocado por `_` quando esse alvo é `"…"` ou `'…'` com caracteres de caminho, ou `$NOME`/`${NOME}` com sufixo de caminho, seguido de espaço e `<<`. As demais redes (leitura principal, M3, reavaliação, `$(` interno, teto) continuam lendo o `original`. Portanto a mudança só pode tirar recusas da rede D, nunca das outras.

**Por que não abre caminho novo.** O trecho removido contém só aspas pareadas, `[\w./:@,+%~^ -]` e `$NOME` sem operador; `$(`, crase, `${X:-…}`, `\`, `|`, `<`, `(` e quebra de linha ficam fora (`hooks/parecer.py:72-74`). Uma expansão de variável num alvo de redirecionamento não executa nada (no máximo dá "ambiguous redirect"). A forma do heredoc continua exigindo delimitador entre aspas (`HEREDOC_MODELADO`, `hooks/_comum.py:669`), então o corpo não expande.

**Sondas executadas (head contra base 5e74c70e, pelo `Fixture`/`rodar` de `tests/test_hooks.py`, branch sem parecer):**
- Passam no head e eram recusadas na base: `cat > "$TMPDIR/x.md" <<'EOF'` com `gh pr merge` no corpo; o mesmo com `<<"EOF"`; dois K1 seguidos; `cat > $A`, `cat > ${A}/x`; `cat >> "$A" <<'EOF' && echo ok`; `cat > "$GIT_DIR/hooks/post-merge"`. Cada um tem o análogo literal (`cat > /tmp/x.md`, `cat > a … cat > b`, `cat > .git/hooks/post-merge`) que já passava na base: nenhuma classe nova.
- Seguem recusados no head e na base: `<<EOF` sem aspas com `$(gh pr merge …)`; `"${A:-x}"`; `"$(…)"` no alvo; `>|`; `2>&1` antes do `<<`; subshell `( … )`; `"$A""$B"`; ação crítica fora do corpo (`&&`, `&`, `;`, linha seguinte); `bash -c`; `eval`; arquivo gravado e rodado na mesma chamada por `sh`, `bash`, `.`, `source`, `"$A"`, `$A`, `| sh`, e `$(sh a)` em outro heredoc; gravar `.git/hooks/pre-commit` e `git commit` na mesma chamada.
- Tentativas de usar a troca textual para enganar a leitura de aspas (o `"` casado pela regex sendo o fechamento de uma string anterior: `echo "a cat > "b" <<'EOF'"`, a variante com `'`, `x="…"`, `printf … | sh`): todas recusadas no head pela leitura principal, que lê o `original` e vê o `gh pr merge` como comando.

**Achados recorrentes (PA-7).** AR-10 (texto isento executado por outro caminho): coberto pelas sondas de M3 acima. AR-1/AR-12: os três mutantes (HTM1-HTM3) ancoram uma vez cada no head. AR-7/AR-8/AR-11: a mudança não toca pasta, `cd` nem leitura do `gh api`.

**Observação informativa (sem caminho de ataque).** A troca é textual e alcança também corpos de heredoc e strings; como só a rede D a vê e as outras redes leem o original, não há efeito de segurança.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Teste do item rodado na raiz do clone: `python3 -m unittest tests.test_hooks_parecer_pasta.PastaDoGit.test_corpus_texto_passa_e_barra` (OK, 23,9 s). A suíte inteira fica com o CI do PR (`R-REVIEW`). Varreduras de segredo e de workflow não se aplicam (sem segredo, workflow ou dependência no diff).
