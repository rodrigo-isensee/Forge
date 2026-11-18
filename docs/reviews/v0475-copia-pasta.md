---
tipo: review
contrato: 1
pedido: v0474
branch: melhoria/v0475-copia-pasta
commit: 5d7ca50b2d8e9cabd196b8a1d5dd928536fd88fb
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-17
---
# Review: v0474 (E3.134, revalidação de E3.112, item E3.44, `bin/forge-copia`)

## Achados
- A2 (recomendado) docs/propostas/copia-pasta-settings.patch:8 · o modelo de projeto só muda pelo patch, que o dono aplica (settings protegido). O PR precisa dizer isso e citar a segurança A1/A2.
- A5 (recomendado) bin/forge-copia:1 · o código e o teste passam de 150 linhas (M14). O corpo do PR leva `teto: excedido, <n> linhas, <motivo>`.
- A6 (recomendado) tests/mutantes/v0475-copia-pasta.json:105 · a spec tem 14 mutantes. Passou de 8, os de M9 em diante iriam para `v0475-copia-pasta-2.json` (qa-testing, 'Mutantes declarados'). Não é defeito: todos morrem.

## Sondas
- S1 · bin/forge-mutante --processos 1 tests/mutantes/v0475-copia-pasta.json (head 5d7ca50b) · espera: M11 a M14 morrem · obtido: M1 a M14 morreram (M11 :53, M12 :59, M13 :61, M14 :70)

## Parecer
Aprovado. Li só o delta, `forge-check parecer delta docs/reviews/v0475-copia-pasta.md` (rc=0), no intervalo a108ef53..5d7ca50b, sem o que veio da develop. No domínio mudaram `tests/mutantes/v0475-copia-pasta.json` (M11 a M14) e `tests/test_forge_copia.py` (um teste novo).

- Cada mutante novo cobre uma guarda de `bin/forge-copia`: a origem com `-` (:53), o destino recusado (:59), o ramo da worktree (:61) e o `__main__` (:70). Os trechos `de` batem com a fonte, e todos morreram (S1).
- `Recusa.test_origem_com_cara_de_opcao` testa o comportamento do ramo de falha: chama o script com `--origem=--upload-pack=x` e espera a saída 2. Não lê o texto da fonte. Ele mata o M11.
- `python3 -I tests/test_forge_copia.py` sob `env -i` dá 14 testes OK.
- `forge-mutante --cobertura --base 5fb2c856`: as 13 condições do diff têm mutante declarado. Fica de fora só o `.patch`, que não é código.
- `python3 -I tests/catraca.py --base origin/develop` deu rc=0.

A2, A5 e A6 ficam para o texto do PR ou para a próxima spec e não bloqueiam. Não há PR nem CI na branch: a suíte inteira fica para o CI do PR.
