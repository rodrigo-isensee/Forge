---
tipo: revisao-seguranca
contrato: 1
pedido: impl-pre-push
branch: melhoria/impl-pre-push-c5
commit: 01ae5742b90c69cd0f674b1d0951d05e0d75aae3
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-31
---
# Review de segurança: impl-pre-push, branch c5 (namespace no texto da trava)

Diff lido: `234dbe0..01ae574` (`8c7d7e9` C5; `81f0400` C-14 e `7404c26` revert dele; `31d4cf6` e `7cb63e2` fragmento; `1972519`, `887f563` e `01ae574` pareceres do code review, só `docs/reviews/`).

## O que entrega
O E4 do pedido: controles C-16 e C-17 do modelo `docs/security/ameacas/pre-push.md` (seção C5). Em `.githooks/pre-push:243-244` o hook lê o inode do pid namespace por `readlink /proc/self/ns/pid`, mantém só dígitos e grava `pid N ns I desde HH:MM:SS` na trava; leitura que falha grava `ns ?`. O revert `7404c26` deixa o hook e o teste iguais ao `8c7d7e9` (`git diff 8c7d7e9 7404c26` só toca `changelog.d/` e `docs/reviews/`): o C-14 não está nesta branch, está na c6.

## M14 (agents/tech-lead.md:19)
`git diff --numstat --no-renames 234dbe0 01ae574`: `.githooks/pre-push` 4+1, `tests/test_pre_push_trava.py` 11; total 16, abaixo de 150 (fragmento e parecer fora da conta). Um comportamento só (o conteúdo gravado na trava). Mexe em `.githooks/`, protegido, sem precisar da exceção. Cumpre.

## Gatilhos
R-SEGURANCA: controles do Forge (o pre-push e a trava da suíte).

## Conferência dos controles
- **C-16 (formato):** os dois primeiros campos continuam `pid <N>`. `scripts/suite-paralela.py:510-511` pega `split()[:2]`; conferido à mão com `conferir_trava` sobre uma trava presa com `pid <pid> ns 4026531836 desde 00:00:00`: retorno vazio (aceita). Caso de abuso 13 cumprido.
- **C-17 (falha):** `2>/dev/null || true` e `${ns:-?}`; a falha não barra o push nem pula etapa. O filtro `${ns//[!0-9]/}` deixa só dígitos: o campo novo não abre caminho para caractere de controle na trava (não amplia a A5 do modelo, que a c6 trata).
- **Escrita:** continua no descritor 9 já conferido (`trava_confere`, `:43`), depois de truncar por `/proc/self/fd/9` (`:240`); nenhuma escrita nova pelo caminho.
- **Exposição:** o inode do pid namespace é informação local, visível ao mesmo usuário em `/proc`; sem ganho para quem lê.

## Achados
- A1 (recomendado) .githooks/pre-push:244 · O formato novo da trava não tem teste em tests/test_suite_paralela.py (as travas de :307 e :316 seguem no formato antigo); um caso com "pid N ns I desde" fixa o C-16 contra mudança futura do leitor.

## Detalhe dos achados
- **A1.** Evidência: `tests/test_suite_paralela.py:307`, `:316`; leitor em `scripts/suite-paralela.py:510-511`. Caminho de ataque: nenhum; é regressão possível (o leitor muda e passa a recusar a própria trava, falha fechada e vermelha). Severidade: informativa. Correção mínima: um teste que grava a trava no formato do C5 e espera `conferir_trava` vazio. Esforço P. Dono: `qa-engineer`, em pedido futuro ou no QA desta branch.

## Verificação
- `python3 -m unittest tests.test_pre_push_trava -k namespace` na worktree: 1 teste, OK.
- Chamada direta de `conferir_trava` (`scripts/suite-paralela.py`) com o formato novo: aceita.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática do diff, o teste acima e a chamada direta. Faltaram no PATH: `shellcheck`, `gitleaks`, `zizmor`, `actionlint` (lacuna; o CI roda o shellcheck do hook). Sem segredo no diff (leitura manual).

## Parecer
Aprovado.
