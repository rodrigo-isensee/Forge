---
tipo: review
contrato: 1
pedido: v0474
branch: melhoria/v0475-copia-pasta
commit: d17f94a617c16226b543f5e5b79edaa6d0266120
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-17
---
# Review: v0474 (E3.158, revalidação de E3.134, item E3.44, `bin/forge-copia`)

## Achados
- A2 (recomendado) docs/propostas/copia-pasta-settings.patch:8 · o modelo de projeto só muda pelo patch, que o dono aplica (settings protegido). O PR precisa dizer isso e citar a segurança A1/A2.
- A5 (recomendado) bin/forge-copia:1 · o código e o teste passam de 150 linhas (M14). O corpo do PR leva `teto: excedido, <n> linhas, <motivo>`.
- A6 (recomendado) tests/mutantes/v0475-copia-pasta.json:105 · a spec tem 14 mutantes. Passou de 8, os de M9 em diante iriam para `v0475-copia-pasta-2.json` (qa-testing, 'Mutantes declarados'). Não é defeito: todos morrem.

## Sondas
- S1 · bin/forge-mutante --processos 1 tests/mutantes/v0475-copia-pasta.json (head 5d7ca50b) · espera: M11 a M14 morrem · obtido: M1 a M14 morreram (M11 :53, M12 :59, M13 :61, M14 :70)

## Parecer
Aprovado. Li só o delta, `forge-check parecer delta docs/reviews/v0475-copia-pasta.md`, no intervalo 5d7ca50b..d17f94a6, sem o que veio da develop. O merge 77a8d645 trouxe a develop f8e9c377 pelo `forge-fechar`. No domínio mudou só `skills/trabalho-em-paralelo/SKILL.md`, com uma frase, no commit d17f94a6.

- O commit d17f94a6 devolve a frase "Linhas do `## Histórico` e decisões do dono, por `forge-check anotar`", que `tests/test_anotar.py` exige. Contra a base f8e9c377, a linha do quadro fica igual à da develop. Nesse arquivo, a branch muda só as duas linhas já aprovadas (a da série e a da cópia).
- As linhas "Lote por arquivo" e "CI pago" que aparecem no delta vieram da develop (f8e9c377), não da branch.
- `python3 -m unittest tests.test_anotar` dá 18 testes OK, e `tests.test_metricas_texto` dá 2 testes OK.
- `python3 -I tests/catraca.py --base origin/develop` deu rc=0. O delta não tem guarda nova.

A2, A5 e A6 seguem como recomendados para o texto do PR ou para a próxima spec e não bloqueiam. A S1 vale do head 5d7ca50b: o delta não toca código nem spec. Não há PR nem CI na branch: a suíte inteira fica para o CI do PR.
