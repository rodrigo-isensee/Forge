---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-conformidade-trilha
commit: a247ae11fac6c9ce96b3d56abe8b4f18763173a6
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: v0478 (E63.20, revalidação da trilha do conformidade)

Volta por delta. As rodadas anteriores (até o head `7a739fca`, A1 a A18 e S1 a S22) ficam no git e não são recopiadas aqui.

Gatilhos: hook de conformidade (analisador de comando), R-VERIFY, R-FLUXO, pastas de controle do Jarvis (VV-2), catraca do CI (afrouxa-regra).

## Achados
- A18 (recomendado) docs/hooks.md:56 · Segue aberto, sem mudança: o texto diz que o link criado na mesma linha recusa, o que vale só para `ln`, `link`, `mv`, `install`, `rename` e `cp -s/-l`; o link copiado ou extraído (`cp -a`, `rsync`, `tar -x`, `os.symlink`) passa. Correção e dono como na rodada `7a739fca`.

## Delta lido
`forge-check parecer delta` (`7a739fca..a247ae11`, sem o que veio da develop):
- no domínio: `docs/hooks.md` e `tests/test_hooks.py`. As duas linhas são da develop `c8e8a08d` (PESADO-VERSOES-FORA-DA-FILA, `--dirigida` → `--afetados`), sem diferença frente a ela;
- fora do domínio: `docs/hooks-fixtures.md` (índice regerado) e `tests/mutantes/v0435-review.json` (R6).

Conferências feitas:
- `hooks/conformidade.py` e `hooks/conformidade.json` não mudaram de `7a739fca` a `a247ae11`.
- A develop não tocou o `conformidade.py` entre `d4f0b10a` e `c8e8a08d`. O diff da trilha frente à develop nova é linha a linha o mesmo da rodada anterior.
- Os outros códigos que mudaram no merge (`hooks/pesado.py`, `bin/forge-check`, `bin/forge-testes`, `bin/forge_autorizacao.py`) são iguais aos da develop `c8e8a08d`.
- Fixtures frente à develop nova: 169 novas, 1 renomeada (`oraculo-limite-python-c-libera` → `oraculo-python-c-tech-lead-bloqueia`, de 0 para 2) e 1 alterada (`rverify-fp-heredoc-pedido-contrib-libera`, papel trocado para `forge:jarvis`). As duas já estavam na rodada `7a739fca`. As 3 fixtures novas da develop são do hook `pesado`.
- Mutante R6: a âncora `de` existe uma vez (`hooks/conformidade.py:2801`). O `para` muda só o ramo `alias.` e mantém o `help.autocorrect`. Rodei `bin/forge-mutante tests/mutantes/v0435-review.json --rev a247ae11 --ids R6`: `R6 · morreu · hooks/conformidade.py:2801`.

Sem suíte local, como pede o brief. Ainda não há PR, então não há CI para citar.

## Confirmações (head a247ae11)
Confirmação: só aperta. O código do hook é o mesmo do `7a739fca`, onde as 58 sondas, as 3196 fixtures da develop e as 48 `libera` novas mostraram que a trilha não abre nem reabre porta. A develop `c8e8a08d` não mexeu no `conformidade.py`, então o diff frente à base é o mesmo. O merge não mudou o código esperado de nenhuma fixture frente à develop nova. O mutante R6 só se alinhou à tupla já aprovada.

Custo do corpus: segue em +5478 passos, 0,093% (abaixo de 0,1%). Não mudaram o hook, as entradas do corpus nem `test_corpus_nos_dois_hooks`: a develop mudou só uma linha de `tests/test_hooks.py`, fora do corpus. O número da rodada `7a739fca` vale.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas locais: `forge-check parecer delta`, `git diff` e `bin/forge-mutante --ids R6`. Lacunas: gitleaks, semgrep, zizmor e actionlint estão fora do PATH. O delta não toca workflow, dependência nem segredo.
