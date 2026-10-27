---
tipo: review
contrato: 1
pedido: metade-k6
branch: melhoria/metade-k6
commit: 053f4162e17079a796ee77ef71e5d0b80bf3b261
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-27
---
# Review: metade-k6

Lote revisado: `ce1a341..053f416` (pedido METADE-MINUTOS-REV, E1.1; decisão do dono K6 de 2026-10-27).

## Achados
- A1 (bloqueante) tests/test_suite_paralela.py:181 · defeito provado: no GitHub Actions (CI=true por padrão) o reuso é desligado de propósito (scripts/suite-paralela.py:270) e o env do Brinquedo herda CI; com CI=true o teste falha, logo o CI do PR fica vermelho. Tirar CI do self.env no setUp, como test_suite_reuso.py faz.
- A2 (recomendado) tests/test_suite_paralela.py:184 · a terceira chamada, com FORGE_SUITE_SEM_REUSO=1, não confere o código de saída (deveria ser 0); só a contagem de módulos.
- A3 (recomendado) scripts/suite-paralela.py:234 · o hash cobre só o que o git versiona; arquivo ignorado pelo .gitignore que algum teste leia não entra. Registrar o limite na docstring ou cobrir com --ignored se algum teste depender disso.

## Parecer
**Reprovado**, por um bloqueante (A1); o resto do lote está correto e dentro do pedido.

Evidência do A1 (worktree no `053f416`, logs em `$TMPDIR/tech-lead-metade-k6/`):
- `CI=true python3 -m unittest tests.test_suite_paralela.Brinquedo.test_verde_grava_carimbo_e_a_segunda_chamada_reusa_sem_rodar` → `FAIL ... line 181 ... AssertionError: False is not true` (a segunda chamada roda a suíte de brinquedo em vez de reusar).
- `env -u CI python3 -m unittest tests.test_suite_paralela.Brinquedo tests.test_suite_reuso` → `Ran 29 tests ... OK`.
- `.github/workflows/ci.yml:35,57,235` roda `python3 scripts/suite-paralela.py` no Actions, onde `CI=true`; o `AMBIENTE` de `tests/test_suite_paralela.py:29` tira `GIT_*` e `FORGE_SUITE_*`, mas não `CI`. `tests/test_suite_reuso.py:15` já tira `CI`; o Brinquedo precisa do mesmo (por exemplo `self.env.pop("CI", None)` ao lado do `GITHUB_ACTIONS`).

Conferido sem achado:
- `hash_da_arvore`: `git status --porcelain --untracked-files=all` vazio é exigido (suja ou com arquivo novo devolve `None`); `ls-tree -r -z HEAD` com modo, tipo, objeto e caminho, então bit de execução entra; os 5 prefixos saem por `startswith` com a barra final (`docs/reviewsx/` conta, coberto no teste); erro do git ou árvore vazia devolve `None`. Ambiente `GIT_*` limpo em `_git`.
- `gravar_carimbo`: só no fim do caminho verde de `orquestrar`, depois da guarda de completude e da `conferir_arvore`; hash tirado no início, então árvore que muda durante a execução já falha antes; escrita atômica por `os.replace`; carimbo no `git-common-dir`, comum às worktrees (é o que permite ao QA reusar a execução de outro agente, como decidido).
- `reuso`: antes da trava e da fila, só sem `FORGE_SUITE_TRAVA` (o pre-push nunca reusa); `CI` e `FORGE_SUITE_SEM_REUSO=1` desligam; Python por `sys.version`; JSON ilegível, não-dict, hash ou Python diferentes devolvem `None` (falha fechada). Não há execução parcial que grave carimbo (o `main` recusa argumento além de `--processo`).
- `docs/regras/R-QA.md:11`: a frase cita a linha `suite: reusa <hash>`, que é o prefixo impresso, e mantém o CI do PR rodando tudo, como na decisão K6.
- Testes: `tests/test_suite_reuso.py` cobre mesmo hash, sem carimbo, hash diferente, árvore suja, arquivo não versionado, Python diferente, carimbo corrompido (4 formas), `FORGE_SUITE_SEM_REUSO`, `CI`, prefixos fora e dentro do hash, e a chamada à mão de ponta a ponta; `test_vermelho_nao_grava_carimbo` cobre o vermelho.
- Teto M14: 240 linhas de código e teste (`scripts/` 77, `tests/*.py` 163); mutantes, changelog e `.md` fora. Sem `hooks/` nem caminho de `PROTEGIDOS`.
- `R-NEUTRO`, `R-CUSTO`: nada específico de projeto nem pago. Fragmento `changelog.d/metade-k6.md` presente.
- Risco aceito pela decisão do dono: teste que lê pareceres ou `changelog.d/` (neutralidade, `forge-check docs`) pode passar no reuso local e falhar no CI; o CI do PR roda tudo e o pre-push de commit só de parecer passa pelo `forge-check docs`.

Segurança: parecer próprio do `security-engineer` (E2.1), não refeito aqui. QA: E3.1.
