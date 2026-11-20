---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0478-promocao-pr
commit: 6ab1228acf7d1560b1d43541c59438a9e01ffcac
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-18
---
# Review: v0478 (E31.3 e E31.8, promoção por marca)

Head revisado d836c435 sobre o Base-sha 73842444. Diff: `promocao()` passa a aceitar o head que está na cadeia de primeiros pais de `origin/develop` (base `homolog`) ou de `origin/develop`/`origin/homolog` (base `main`), por `foi_ponta_da_integracao`; teste novo `tests/test_promocao_por_marca.py`, spec `tests/mutantes/v0478-promocao-pr.json`, M52 do lote L08 ajustado ao texto novo.

## Ferramentas (citadas, sem refazer)
- Teste novo: `python3 -m unittest tests.test_promocao_por_marca` · 4 testes, OK.
- `bin/forge-mutante --processos 1 tests/mutantes/v0478-promocao-pr.json` · M1, M2, M3, M4 morreram (M2 por erro do teste declarado, que passa sem o mutante).
- `bin/forge-mutante --cobertura --base 73842444` · linhas de guarda 1582, 1589 e 1592 cobertas; só `tests/pesos-d4.json` (dado) fora.
- Tamanho (H1): 14 linhas de código em `bin/forge-check` e 1 em `bin/forge-testes`, um comportamento.
- Suíte: no CI do PR (R-CUSTO, decisão M8); não rerrodada aqui.

## A pergunta do brief: um item escapa de E7/H1?
Não, pelas razões abaixo, conferidas no repositório:
1. **Branch de trabalho mesclada.** A develop recebe item por squash (novo sha, um pai) ou por merge commit (o head do item é o segundo pai). Em nenhum dos dois o head da branch entra na cadeia de primeiros pais; o teste `test_branch_mesclada_na_develop_nao_vira_promocao` e o mutante M4 (sem `--first-parent`) provam o merge commit.
2. **Commit na develop sem PR.** Um envio direto à develop (barrado pelo `.githooks/pre-push` e pela proteção do GitHub, R-VERIFY e R-FLUXO) já era tratado como promoção antes da mudança, enquanto fosse a ponta. A mudança estende no tempo o que já valia; não cria classe nova de head aceito. O lugar de E7/H1 é a entrada na develop, não a promoção.
3. **Ponta antiga da homolog (base `main`).** A cadeia de primeiros pais da homolog só tem merges de promoção, cujo conteúdo já passou pela develop; levar à main um estado anterior da homolog não traz linha que não tenha passado pelos portões. A base `homolog` segue aceitando só a cadeia da develop.
4. **Branch velha apontada para um commit da develop.** Existe hoje: `origin/melhoria/entrega-push-proxy` aponta para 217a09e9, primeiro pai da develop. Com a mudança, o `forge-check pr --base main` a chamaria de promoção; o conteúdo, porém, é só da develop, e o passo "Nada pula degrau" do CI (`.github/workflows/ci.yml:685`, tabela PROMOCOES) recusa `melhoria/*` para `main`. Defesa em camadas intacta; o `forge-check` é até mais estrito que o CI (primeiro pai contra ancestral).
5. **Falha fechada.** Sem a ponta ou com o `git rev-list` falhando, não é promoção (M2, M3).

## Revalidação E31.8 (head 1e0c50a7, A1 da segurança)
Delta lido: `forge-check parecer delta docs/reviews/v0478-promocao-pr.md`, intervalo d836c435..1e0c50a7; no domínio `bin/forge-check`, `changelog.d/v0478-promocao-pr.md`, `tests/mutantes/lote-l08-e7b.json`, `tests/mutantes/v0478-promocao-pr.json`, `tests/test_promocao_por_marca.py`. Fora do domínio nada relido.
- `ponta_da_integracao`: com `origin/<base>`, a cadeia de primeiros pais (merge pelo PR, envio direto barrado, R-FLUXO); sem a remota, igualdade estrita com a ponta local, e o ff na develop local não torna promoção o commit intermediário do item. Resolve a sonda S1 da segurança.
- Teste novo `test_avanco_rapido_na_develop_local_sem_remoto_nao_vira_promocao`: `python3 -m unittest tests.test_promocao_por_marca` · 5 testes, OK.
- `bin/forge-mutante --processos 1 tests/mutantes/v0478-promocao-pr.json` · M1, M5, M6, M2, M3, M4 morreram.
- `bin/forge-mutante --cobertura --base d836c435` · linhas 1582, 1590 e 1592 cobertas (M1/M52, M5, M6).
- Suíte: no CI do PR (R-CUSTO, M8); não rerrodada.

## Revalidação E31.12 (head 6ab1228a, A1 deste review)
Delta lido: `forge-check parecer delta docs/reviews/v0478-promocao-pr.md`, intervalo 1e0c50a7..6ab1228a; no domínio `bin/forge-check`, `changelog.d/v0478-promocao-pr.md`, `docs/fechamento-integrador.md`, `tests/mutantes/v0478-promocao-pr.json`, `tests/test_promocao_por_marca.py`. Fora do domínio nada relido.
- A1 resolvido: a docstring de `ponta_da_integracao` e o `docs/fechamento-integrador.md` declaram a premissa (squash ou merge commit, rebase-merge desligado), e `avisar_rebase_merge` avisa na promoção quando `allow_rebase_merge` é `true` (`gh api`, só leitura, R-CUSTO), sem mudar o veredito; sem `gh`, sem rede ou resposta que não é dict, nada.
- Teste novo `test_promocao_avisa_quando_o_repositorio_permite_rebase_merge` (true, false, vazio, None, lista): `python3 -m unittest test_promocao_por_marca` · 6 testes, OK.
- `bin/forge-mutante --processos 1 tests/mutantes/v0478-promocao-pr.json` · M1, M5, M6, M2, M3, M4, M7 morreram.
- `bin/forge-mutante --cobertura --base 1e0c50a7` · linha 1591 coberta (M7).
- Suíte: no CI do PR (R-CUSTO, M8); não rerrodada.

## Parecer
Aprovado (revalidado no head 6ab1228a; A1 resolvido). A mudança é mínima, resolve o caso real da 0.47.8 (marca b407f8f7 com o #682 depois) e não abre caminho para item escapar de E7/H1: o critério é o sha do head, que só está na cadeia de primeiros pais se entrou na develop pelo caminho integrado. R-REVIEW, R-FLUXO.
