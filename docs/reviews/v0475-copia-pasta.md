---
tipo: review
contrato: 1
pedido: v0474
branch: melhoria/v0475-copia-pasta
commit: 0b4b146a252b183e4a83e1065587daed889e8e40
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-18
---
# Review: v0474 (E3.220, revalidação de E3.197, item E3.44, `bin/forge-copia`)

## Achados
- A2 (recomendado) docs/propostas/copia-pasta-settings.patch:8 · o modelo de projeto só muda pelo patch, que o dono aplica (settings protegido). O PR precisa dizer isso e citar a segurança A1/A2.
- A5 (recomendado) bin/forge-copia:1 · o código e o teste passam de 150 linhas (M14). O corpo do PR leva `teto: excedido, <n> linhas, <motivo>`.
- A6 (recomendado) tests/mutantes/v0475-copia-pasta.json:105 · a spec tem 14 mutantes. Passou de 8, os de M9 em diante iriam para `v0475-copia-pasta-2.json` (qa-testing, 'Mutantes declarados'). Não é defeito: todos morrem.

## Sondas
- S1 · bin/forge-mutante --processos 1 tests/mutantes/v0475-copia-pasta.json (head 5d7ca50b) · espera: M11 a M14 morrem · obtido: M1 a M14 morreram (M11 :53, M12 :59, M13 :61, M14 :70)

## Parecer
Aprovado. Li só o delta, `forge-check parecer delta docs/reviews/v0475-copia-pasta.md`, no intervalo 7884b151..0b4b146a. No domínio mudou só `skills/trabalho-em-paralelo/SKILL.md`, no commit 0b4b146a.

- A skill volta ao texto da `develop` e fica só com a frase da cópia: `git diff origin/develop...HEAD` no arquivo mostra uma linha, o acréscimo "Cópia: `forge-copia clone` (padrão)." A frase "Itens com arquivo em comum não andam em paralelo", que `tests/test_jarvis_nucleo.py` exige, segue igual à da `develop`.
- `python3 -m unittest tests.test_sobreposicao_quadro tests.test_jarvis_nucleo tests.test_metricas_texto` dá 106 testes OK.
- `python3 -I tests/catraca.py --base origin/develop` deu rc=0. O delta não tem guarda nova.

Revalidação anterior (7884b151, E3.197): A2, A5 e A6 seguem como recomendados para o texto do PR ou para a próxima spec e não bloqueiam. A S1 vale do head 5d7ca50b: o delta não toca código nem spec. A suíte inteira fica para o CI do PR.
