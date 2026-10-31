---
tipo: review
contrato: 1
pedido: impl-catraca-2
branch: melhoria/impl-catraca-2-c1
commit: 5e8ec33b3e54a8187441c5c73c48f90fc10bf2e2
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-30
---
# Review: impl-catraca-2 (branch c1)

## Achados

## Parecer
Aprovado. A branch entrega o item E1 do pedido (FIXTURE-DATA-GIT, C1 do desenho `docs/propostas/lotes-1030/catraca-2.md`). Diff lido: `234dbe0..5e8ec33`, dois commits (`7f6feab` teste, `5e8ec33` fragmento).

M14 (`agents/tech-lead.md:19`): 55 linhas contadas (`git diff --numstat --no-renames 234dbe0 5e8ec33`: `tests/test_catraca.py` 50+5; o fragmento `changelog.d/` fica fora), abaixo de 150. Um comportamento só (ambiente de git das fixtures com datas fixas). Não toca `hooks/` nem `PROTEGIDOS`.

Conferido contra o modelo de ameaças (`docs/security/ameacas/catraca-2.md`, 3.1):
- C1-1: `ambiente_de_git` (`tests/test_catraca.py:42-50`) filtra o `GIT_*` herdado, passa por `sem_manutencao` e só depois fixa as datas.
- C1-2: as duas datas recebem o mesmo valor, data fixa mais contador do módulo (`itertools.count`, `:39`); não há variante sem contador.
- C1-3: `Repo.git`, `_g` e `_tem` usam a função; o `ls-files` do repositório real (`:2720-2721`) fica com o ambiente antigo, como o modelo prevê.
- C1-4: a espera de 1,2 s e o `import time` saem; nenhuma asserção do b8 sai (`assertNotEqual(m, self.m)` segue).
- C1-5: data base 2025-06-01, longe dos instantes simulados de 2026-01-02.
- Testes novos: T1-1 e T1-3 em `AmbienteDeGitDasFixtures` (`:64-89`), T1-2 em `test_dois_squash_do_mesmo_conteudo_sem_espera_dao_shas_diferentes`.

Regras ferramenta: rodei `python3 -m unittest tests.test_catraca tests.test_ambiente_git` no head revisado: 280 testes, OK (a leitura estática aceita a função nova como ponto único). A suíte completa fica com o CI do PR e o pre-push. Segurança: parecer próprio do `security-engineer` (E1.3), não refeito aqui.
