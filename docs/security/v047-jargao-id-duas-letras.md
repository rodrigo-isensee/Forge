---
tipo: revisao-seguranca
contrato: 1
pedido: v048
branch: melhoria/v047-jargao-id-duas-letras
commit: ff6bff0690d9046d570c5d2b5c04824382bcf9b8
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-28
---
# Review de segurança: v047-jargao-id-duas-letras (volta por delta, E13.13)

Volta por delta sobre o head ff6bff06, base develop a1971853. A rodada anterior (parecer `aprovado` em cf59506c, pedido v047) fica no git. O delta cf59506c..ff6bff06 traz os três pareceres da v047 (só docs) e o merge ff6bff06 da develop a1971853, que não teve conflito (`git show --cc ff6bff06` sai vazio).

Gatilhos: `R-SEGURANCA` (hook `hooks/meta.py`, a medida de fim de resposta, que só conta e nunca bloqueia).

## Delta lido
- Merge sem perda: `git diff a1971853 ff6bff06` mostra só os arquivos da branch, isto é, `hooks/meta.py` (1 linha), `tests/test_meta.py` (+5), `tests/mutantes/v047-jargao-id-duas-letras.json`, `changelog.d/v047-jargao-id-duas-letras.md` e os três pareceres. Nada da develop se perdeu nem mudou.
- Mesmo comportamento: as linhas mudadas de `1b88640e..cf59506c` e de `a1971853..ff6bff06` nos quatro arquivos de código, teste, mutante e changelog são as mesmas (comparei os dois diffs, idênticos). A correção é só `hooks/meta.py:174`, `R-[A-Z]{3,}` passa a `R-[A-Z]{2,}` (estava na linha 144 antes do merge).
- Nenhum controle novo veio no merge: no domínio (`hooks/`, `bin/`, `scripts/`, `.githooks/`, `.github/`, `migrations/`), o diff contra a develop é só essa linha.
- O teto continua valendo depois do merge: a conta das classes roda sobre `texto[:TETO_DA_MEDIDA]` (`hooks/meta.py:347`, `TETO_DA_MEDIDA = 20000` em `:43`).
- Custo da regex: um quantificador só entre lookarounds fixos de um caractere, sem aninhamento nem alternância. Cada `R-` percorre só a sequência de maiúsculas que vem depois dele, então o custo total é linear. Sondas no head, todas lineares e acima do teto: `R-` + 200.000 `A` + `-`, 0,006 s; `R-` repetido 100.000 vezes, 0,005 s; ` R-AA-` 50.000 vezes, 0,06 s; ` R-` + 200.000 `R` + `x`, 0,008 s.
- `forge-check parecer delta` lista 156 linhas da develop em `hooks/meta.py`. Ele avisa que o merge a457d15 (a branch mesclada nela mesma) não está na develop e por isso conta inteiro o que veio dela. Conferi direto contra a develop, como descrito acima: no domínio, o delta real é a linha 174.
- Mutantes: as specs M1 e M2 citam o texto do head (`R-[A-Z]{2,}(?![\w-])`), que aparece uma vez em `hooks/meta.py:174`.

Achados anteriores: nenhum (a rodada em cf59506c não teve achados).

## Riscos aceitos e ferramentas
Sem riscos aceitos. Ferramentas: git (diff, `show --cc`), `forge-check parecer delta`, sondas locais da regex e `python3 -m unittest tests.test_meta` no clone (56 testes, OK). A suíte inteira roda no CI do PR #966 sobre o Revisar-sha. Varredura de segredos, de dependências e de workflow não se aplica: o delta não toca segredo, dependência nem workflow.
