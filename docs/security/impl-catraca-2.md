---
tipo: revisao-seguranca
contrato: 1
pedido: impl-catraca-2
branch: melhoria/impl-catraca-2-c1
commit: c91d05568756b9fb3db8a6f32f79742ed353f339
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-31
---
# Review de segurança: impl-catraca-2 (branch c1)

## Gatilhos
R-SEGURANCA, gatilho de controles do Forge: a mudança está nos testes da catraca (`tests/test_catraca.py`), que guardam um controle protegido. O controle em si (`tests/catraca.py`) não muda.

Item entregue: E1 do pedido (FIXTURE-DATA-GIT, C1 do desenho e seção 3.1 do modelo de ameaças `docs/security/ameacas/catraca-2.md`). Diff lido: `234dbe0..c91d055`, commits `7f6feab` (teste), `5e8ec33` (fragmento) e `c91d055` (parecer do review).

M14 (`agents/tech-lead.md:19`): cumpre. `git diff --numstat --no-renames 234dbe0 c91d055` conta 55 linhas de teste (`tests/test_catraca.py`, 50+5); o fragmento de `changelog.d/` e o parecer `.md` ficam fora. Abaixo de 150, um comportamento só (ambiente de git das fixtures com datas fixas e crescentes), sem arquivo de `hooks/`, `.githooks/`, `bin/`, `.github/` nem de `PROTEGIDOS`.

## Achados

## Detalhe dos achados
Sem achado. Conferido contra o modelo de ameaças, 3.1:
- C1-1: `ambiente_de_git` (`tests/test_catraca.py:42-50`) filtra o `GIT_*` herdado, passa por `sem_manutencao` e só depois fixa as datas. Nenhum `GIT_*` herdado volta ao ambiente; o risco que o filtro cobre (um `GIT_DIR` exportado por hook levar o commit da fixture ao repositório real) segue fechado.
- C1-2: as duas datas recebem o mesmo valor, data fixa mais contador do módulo que só cresce.
- C1-3: `Repo.git`, `_g` e `_tem` usam a função; o `ls-files` do repositório real (`:2720-2721`) mantém o ambiente antigo e não cria commit.
- C1-4: a espera e o `import time` saem; nenhuma asserção do b8 sai.
- C1-5: data base 2025-06-01, longe dos instantes simulados de 2026-01-02.

Provas de vermelho, refeitas por mim numa cópia em `$TMPDIR` (o código da branch não mudou):
- mutação sem filtro de `GIT_*`: cai `test_nao_devolve_o_git_herdado_do_processo` (T1-3);
- mutação sem contador (data fixa só): caem `test_traz_as_duas_datas_iguais_e_crescentes`, `test_dois_squash_do_mesmo_conteudo_sem_espera_dao_shas_diferentes`, o b8 e mais dois que dependem dele (5 falhas).

Sem caminho de ataque novo: a mudança é só de teste, roda em repositório temporário e não afrouxa nenhuma asserção (a contagem de testes sobe).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Rodei `python3 -m unittest tests.test_catraca` no head revisado (265 testes, OK) e `tests.test_ambiente_git` (15, OK). `gitleaks` e `semgrep` não estão no PATH: lacuna registrada; o diff é só de teste e não traz credencial nem configuração.
