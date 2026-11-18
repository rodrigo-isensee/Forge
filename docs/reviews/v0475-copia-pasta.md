---
tipo: review
contrato: 1
pedido: v0474
branch: melhoria/v0475-copia-pasta
commit: 7884b151194706a0e9fcf2a1f216fe37525bac06
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-18
---
# Review: v0474 (E3.197, revalidação de E3.158, item E3.44, `bin/forge-copia`)

## Achados
- A2 (recomendado) docs/propostas/copia-pasta-settings.patch:8 · o modelo de projeto só muda pelo patch, que o dono aplica (settings protegido). O PR precisa dizer isso e citar a segurança A1/A2.
- A5 (recomendado) bin/forge-copia:1 · o código e o teste passam de 150 linhas (M14). O corpo do PR leva `teto: excedido, <n> linhas, <motivo>`.
- A6 (recomendado) tests/mutantes/v0475-copia-pasta.json:105 · a spec tem 14 mutantes. Passou de 8, os de M9 em diante iriam para `v0475-copia-pasta-2.json` (qa-testing, 'Mutantes declarados'). Não é defeito: todos morrem.

## Sondas
- S1 · bin/forge-mutante --processos 1 tests/mutantes/v0475-copia-pasta.json (head 5d7ca50b) · espera: M11 a M14 morrem · obtido: M1 a M14 morreram (M11 :53, M12 :59, M13 :61, M14 :70)

## Parecer
Aprovado. Li só o delta, `forge-check parecer delta docs/reviews/v0475-copia-pasta.md`, no intervalo d17f94a6..7884b151. No domínio mudou só `skills/trabalho-em-paralelo/SKILL.md`, uma palavra, no commit 7884b151.

- O commit 7884b151 troca "serializam" por "não andam em paralelo" na linha da série. Volta a frase "Itens com arquivo em comum não andam em paralelo", que `tests/test_jarvis_nucleo.py:200` exige. O sentido da regra não muda.
- `python3 -m unittest tests.test_jarvis_nucleo` dá 43 testes OK, e `tests.test_metricas_texto` dá 2 testes OK.
- `python3 -I tests/catraca.py --base origin/develop` deu rc=0. O delta não tem guarda nova.

Revalidação anterior (d17f94a6, E3.158): a frase de `tests/test_anotar.py` segue no arquivo. A2, A5 e A6 seguem como recomendados para o texto do PR ou para a próxima spec e não bloqueiam. A S1 vale do head 5d7ca50b: o delta não toca código nem spec. Não há PR nem CI na branch: a suíte inteira fica para o CI do PR.
