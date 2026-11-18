---
tipo: review
contrato: 1
pedido: v0474
branch: melhoria/v0475-copia-pasta
commit: a108ef531a7b40d2bcc05082f23a73ef3888aa37
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-17
---
# Review: v0474 (E3.112, revalidação de E3.55, item E3.44, `bin/forge-copia`)

## Achados
- A2 (recomendado) docs/propostas/copia-pasta-settings.patch:8 · o modelo de projeto só muda pelo patch, que o dono aplica (settings protegido). O PR precisa dizer isso e citar a segurança A1/A2.
- A5 (recomendado) bin/forge-copia:1 · ainda há 187 linhas de código e teste, acima de 150 (M14). O corpo do PR leva `teto: excedido, 187 linhas, <motivo>`.

## Sondas
- S1 · env -i PATH HOME python3 -m unittest tests.test_ambiente_git (head a108ef53) · espera: OK · obtido: OK (20 testes)

## Parecer
Aprovado. Li só o delta, `forge-check parecer delta docs/reviews/v0475-copia-pasta.md` (rc=0), no intervalo efe73e17..a108ef53. No domínio mudaram `docs/propostas/copia-pasta-settings.patch`, `skills/contribuir-com-o-forge/SKILL.md`, `skills/trabalho-em-paralelo/SKILL.md` e `tests/test_forge_copia.py`.

- A1 resolvido: `tests/test_forge_copia.py:24` monta `self.env` com `sem_manutencao`, importado de `tests/` como nos outros módulos. O guarda `tests.test_ambiente_git` passou de FAILED a OK (S1), e `python3 -I tests/test_forge_copia.py` dá 13 testes OK.
- A3 resolvido: `contribuir-com-o-forge/SKILL.md:22-23` usa `forge-copia` (no PATH) nas duas linhas e não traz mais `git clone` solto.
- A4 resolvido: `trabalho-em-paralelo/SKILL.md:11` põe `forge-copia clone` como padrão e `worktree` como alternativa.
- Segurança A1 atendida: o patch tirou `/workspaces/.forge-contrib` do `allowWrite`.
- O enxugamento das skills não tira regra nem ID: `R-CONTRIB`, `R-TETO`, `R-WIP` e `R-DECISAO` continuam lá.
- `bin/forge-copia` e os mutantes não mudaram, então a medida de E3.55 segue valendo.

A2 e A5 ficam para o texto do PR e não bloqueiam. Não há PR nem CI na branch: a suíte inteira fica para o CI do PR. Aqui rodaram só o teste do item e o guarda que ele toca.
