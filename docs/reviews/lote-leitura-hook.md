---
tipo: review
contrato: 1
pedido: lote-leitura-hook
branch: melhoria/lote-leitura-hook
commit: f8e00ae6d17c6ade5fc417308ca98ede79f97971
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-21
---
# Review: lote-leitura-hook (revalidação 3)

Escopo: a entrega inteira, `git diff ad6d96ce6b19663f7695d361d61f59c7545bdca6 f8e00ae6d17c6ade5fc417308ca98ede79f97971`. Revalidei por delta desde o parecer anterior (849174b, sobre a437574). `forge-check delta --parecer docs/reviews/lote-leitura-hook.md` listou o intervalo `a437574..f8e00ae`: bec010b, 66c23b0, 56881bd e f8e00ae, em `hooks/_comum.py` (417-494, 788-911, 948-950, 1058-1085), `hooks/conformidade.py` (35, 666-689, 724-727, 757), `hooks/parecer.py` (341-376), `tests/test_hooks.py`, as 17 fixtures novas, `docs/hooks.md:94-95` e o fragmento do changelog. Li só esse delta. Os commits até a437574 ficam como "já lido", e os pareceres das rodadas anteriores continuam valendo para eles. Sou revisor independente, não o autor. A segurança (E1.3) tem parecer próprio em `docs/security/lote-leitura-hook.md`, que não refiz aqui.

## Achados

## Parecer
**Aprovado.** O A1 da rodada anterior está resolvido. O caso `git add x && git commit -m "$(cat <<'EOF'` com apóstrofo, que o HEAD anterior recusava, voltou a passar. O A1 de segurança (o dono do heredoc noutra linha física) também fecha nas sondas abaixo. Ficam recomendações, sem bloqueante.

### Sondas
As sondas rodaram em cópias por `git archive` da base (ad6d96c), do HEAD anterior (a437574) e do HEAD (f8e00ae) em `$TMPDIR`. O hook real rodou pelo `Fixture`, pelo `montar_proc` e pelo `rodar` de cada cópia, com os modelos `conformidade/shell-heredoc-no-commit-libera` e `parecer/forge-clone-pr-ready-sem-parecer-bloqueia`. Nas linhas "push", o corpo é `git push --no-verify origin x`, e nas linhas do `parecer`, `gh pr ready feature/x` sem parecer.

| Caso (hook) | base | a437574 | f8e00ae |
|---|---|---|---|
| `git add … && git commit -m "$(cat <<'EOF'` com `it's` (conformidade) | 0 | 2 | **0** |
| `cd src && cat > n.md <<'EOF'` com `it's` (conformidade) | 0 | 2 | **0** |
| `git commit -m "$(cat <<'EOF'`, `git commit -F -`, `python3 -`, `cat \| python3`, `mkdir && cat >`, `cat > a.md && git add && git commit`, todos com apóstrofo (conformidade) | 0 | 0 | 0 |
| `patch -p1`, `kubectl apply -f -`, `while read … done` com `<<'EOF'` e apóstrofo (conformidade) | 0 | 2, mensagem errada | 2, mensagem com saída por arquivo |
| `cat > notas.md <<'EOF'` com apóstrofo e `patch -p1 < notas.md` na linha seguinte (conformidade) | 0 | 0 | 0 |
| `for f in a b; do cat > $f.md <<'EOF'` e `sudo tee /etc/x <<'EOF'`, com apóstrofo (conformidade) | 0 | não medido | 2, mensagem com saída por arquivo |
| push: `cat <<'EOF' \|`⏎…⏎`EOF`⏎`bash`, `bash \`⏎`<<'EOF'`, `cat <<'EOF' \| \`⏎`bash`, `eval "$(cat <<'EOF'`, `cat >x; source x` (conformidade) | 0 a 2 | 0 a 2 | 2 |
| push: `eval "$(`⏎`cat <<'EOF'` e `bash -c "$(`⏎`cat <<'EOF'` (R7 da segurança, conformidade) | 0 | 0 | **2** |
| push: `cat \| bash`, `cat \| tee \| sh`, `{ read; bash; }`, `(cat) \| bash`, `\|&`, dois heredocs, `xargs sh`, `git -c alias` (conformidade) | 2 | 2 | 2 |
| push: `git add … ; cat <<'EOF'` (o corpo só é impresso, conformidade) | 0 | 2 | 0, correto |
| push: `cat > x.sh <<'EOF'`⏎…⏎`EOF`⏎`bash x.sh` (R6 da segurança, conformidade) | 2 | não medido | **0** |
| push: `sort --compress-program=sh <<'EOF'` (R8 da segurança, conformidade) | 2 | não medido | **0** |
| ready: `cat <<'EOF' \|`⏎…⏎`EOF`⏎`bash` (parecer) | 2 | 0 | 2 |
| ready: `eval "$(`⏎`cat <<'EOF'` (parecer) | 0 | não medido | 2 |
| ready: `cat > x.sh <<'EOF'`⏎…⏎`EOF`⏎`bash x.sh` (R6, parecer) | 2 | não medido | **0** |
| `git add a && git commit -m "$(cat <<'EOF'` com `it's` e `&& gh pr list`, e `kubectl apply -f -` com apóstrofo e `gh pr list` (parecer) | 0 | 0 | 0 |
| `gh pr create --draft --body "$(cat <<'EOF'` com `it's done` (parecer) | 0 | não medido | 0 |

O bash local confirma o R6: `cat > x.sh <<'EOF'`⏎`echo RODOU`⏎`EOF`⏎`bash x.sh` imprime `RODOU`.

### Delta lido, por commit
- **bec010b (recomendação do review anterior):** atendida. O `TETO_DE_CARACTERES` cai para 150 mil. O teste de orçamento afirma o teto e que a linha logo acima dele recusa pelo teto antes de metade do timeout. A mensagem da recusa não mudou e continua dizendo como corrigir.
- **66c23b0 (A1 de segurança e o falso positivo do `git add && git commit`):** resolvido. `tirar_heredocs` troca cada operador por uma marca (`__forge_heredoc_<n>__`), lê a linha sem os corpos pela mesma porta da ADR 0013 (`leituras(..., com_sinal=True)`) e passa a `dono_do_heredoc` o pipeline que contém a marca, mais os comandos de fora quando o heredoc está numa substituição. A marca é uma palavra comum, e por isso não muda a prova do `#` da gramática G. Com subshell, comando composto, leitura ilegível ou marca perdida, o dono é o `comando_logico` inteiro, o que fecha na dúvida. `RODA_TEXTO` no comando lógico mantém o comportamento da develop para `cat > x.sh <<'EOF' && bash x.sh`. O `com_sinal` é opcional e só acrescenta um quarto elemento, então quem já chamava `comandos` e `leituras` não muda. O teste `test_corpo_de_heredoc_so_lido_pela_lista_positiva` afirma um mínimo de 11 formas e testa as seis separadas que só leem, e as 9 fixtures `-bloqueia` cobrem as quatro formas da segurança nos dois hooks. As funções novas são pequenas e têm docstring com o porquê. A `pipeline_do_operador` é a mais densa (dois laços e o retorno pela substituição de fora), mas está legível.
- **56881bd (A1 do review anterior):** resolvido pela sugestão mínima. O corpo ilegível dado a um dono fora da lista recusa com mensagem própria nos dois hooks (`hooks/conformidade.py:724`, `hooks/parecer.py:357`), e essa mensagem manda gravar o texto num arquivo com `cat > arq <<'FIM'` sozinho e passar o arquivo ao programa. A recusa continua fechando na dúvida, sem afrouxar pela rede da ADR 0011. A fixture `…gravado-em-arquivo-e-patch-depois-libera` prova que a saída indicada funciona. Como a flag `corpo_de_heredoc` entra na chave do cache de conferências, a mesma linha lida como corpo e como linha não divide resultado.
- **f8e00ae (docs):** `docs/hooks.md:94-95` descreve o dono por pipeline, os casos do comando lógico, a saída por arquivo e o teto de 150 mil. O fragmento foi dividido em dois itens, como o review anterior recomendou.

### Recomendações (fora do bloco)
- **R6 e R8 da segurança, recuos em relação à base:** `cat > x.sh <<'EOF'`⏎…⏎`EOF`⏎`bash x.sh` (nos dois hooks) e `sort --compress-program=sh <<'EOF'` saem 0, e a base dava 2. O R6 cabe no limite que `docs/hooks.md` já registra no item [B], o script gravado e executado depois, e o teste o fixa de propósito em `separados`. O R8 não está documentado. A correção é trivial: tirar o `sort` de `LEITORES_DO_CORPO` ou tratar `--compress-program` como quem roda texto. A classificação é da segurança (E1.3), que deu os dois como recomendação. Fica ao integrador (E1.5) confirmar que eles entram na descrição do PR com o rótulo `afrouxa-regra`.
- **Falso positivo restante, agora com saída:** `for … do cat > $f <<'EOF' … done` e `sudo tee /etc/x <<'EOF'` com apóstrofo no corpo recusam. No primeiro, o laço leva ao comando lógico inteiro. No segundo, `sudo` está em `RODA_TEXTO`. A mensagem resolve os dois casos (arquivo e depois `sudo cp`). Se aparecer nos projetos, vale pôr `sudo tee` na lista com o `tambem`.
- Quando o dono fora da lista é um shell (`bash <<'EOF'` com aspa sem par), a mesma mensagem leva ao limite do R6 (`bash arq`). O bash também recusaria esse corpo por sintaxe, então o efeito prático é nulo.
- Continua aberta: o cartão HOOK-N4 entra no quadro antes do merge, para o `skipTest` do T1 ter dono.
- Os commits continuam limpos, um por achado, em Conventional Commits em português, com o porquê na mensagem.

### Invariantes e ferramentas
O delta não toca em `tests/config.json`. O rótulo `afrouxa-regra` do dono continua necessário no merge (E1.5), porque o diff toca em `hooks/conformidade.py`. Não refiz as ferramentas. O pre-push deste parecer roda a suíte sobre o mesmo patch.
