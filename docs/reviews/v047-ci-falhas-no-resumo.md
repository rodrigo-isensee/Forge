---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-ci-falhas-no-resumo
commit: 0de0d3ee37dcf9c3f893beee32f79efbd36958f8
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-17
---
# Review: v047-ci-falhas-no-resumo (E2.503, revalidação por delta no head a00638db)

Revalidação por delta do parecer aprovado no head 82623453 (E2.287). Li só `forge-check parecer delta docs/reviews/v047-ci-falhas-no-resumo.md` (intervalo `82623453..a00638db`, sem o que veio da base `develop` 86ac0fcb). No domínio entraram 29 arquivos: o resumo de falhas readaptado (3a9a8181) e a volta do CI-RAPIDO do #576 com os consertos (a00638db). O delta é quase todo o #576, já aprovado no head 0237a1bc (`docs/reviews/v047-ci-rapido.md` no 22f1eaa8). Por isso li o interdiff dele contra o 22f1eaa8, e não as 3,4 mil linhas de novo.
- `scripts/pesos-do-ci.py`, `scripts/suite-partes.py`, `tests/test_pesos_do_ci.py`, `tests/test_suite_partes.py`, `tests/test_ci_rapido_guardas.py`, `tests/test_ci_local.py`, `tests/test_forge.py`, `docs/propostas/ci-rapido.md`, os `stacks/*/pronto.md`, o README, a economia de tokens e as specs `v047-ci-rapido-{1,2,4..7}` estão iguais ao #576.
- **ci.yml:** só muda pelo resumo de falhas nas 4 matrizes de 5 partes (`rapida-partes-doze`, `rapida-partes-quatorze`, `partes-doze` e `partes-quatorze`). Cada matriz ganha `set -o pipefail` e `| tee` no passo da parte, e o leitor `python3 -I` com `!cancelled()`. No PR o leitor vem com `provada != 'true'`.
- **Catraca** (`tests/test_catraca.py:3492-3515`): conta os 18 tetos de tempo e o `always()` dos dois agregadores de prova da develop. Os 4 jobs com `always()` não podem ter `uses:`, precisam de `needs: [` e não rodam código da branch.
- **Métricas do ci-cd:** os 2 bullets que o #576 punha em `skills/ci-cd/SKILL.md` saíram de lá.
- **Orçamento de devops:** foi para `templates/projeto/docs/engineering/protecao-de-branch.md:15`.
- **Specs:** a `v047-ci-rapido-3` e a `v046-ci-lote-e1` foram realinhadas ao YAML novo. I96 e I97 foram retiradas, porque a função `pesos_por_modulo` saiu. O F14 aponta para a rápida do 3.14.

## Achados
- A1 (recomendado) stacks/node-react/pronto.md:65 · remete o T à skill `ci-cd`, "Tempo e dependências", mas a definição de T e o orçamento não estão mais na skill: o conserto das métricas os pôs em `templates/projeto/docs/engineering/protecao-de-branch.md:15`. Aponte para lá (R-REVIEW).
- A2 (recomendado) scripts/suite-partes.py:227 · a parte vermelha passa a anotar a falha duas vezes: a linha `::error title=forge-suite` daqui e um `::error` por falha do leitor (`.github/workflows/ci.yml:92`). São dois mecanismos para a mesma saída: fique com um ou justifique (R-DECISAO; segue o A1 anterior).
- A3 (recomendado) .github/workflows/ci.yml:1 · são 2051 linhas de código e teste contra a develop (`git diff --numstat`, M14). Quando o PR existir, o corpo dele leva `teto: excedido, 2051 linhas, <motivo>`; substitui o A5 anterior (R-REVIEW).
- A4 (recomendado) tests/test_prepush_so_docs.py:356 · o teste novo não chama `exigir(self, "proc")` e checa o filho por `vivos()` (lê `/proc`): em /proc de outro namespace passa vazio e o G1 "sobrevive". Peça o `exigir`, como nos irmãos.

## Sondas

## Verificações citadas
- Delta: `forge-check parecer delta docs/reviews/v047-ci-falhas-no-resumo.md`, intervalo `8262345394250e8b2f2130950da47af33fac4621..a00638dbc0e5f8dbd150b631c4399b096f501e73`, 29 arquivos no domínio.
- Testes dos arquivos tocados, na raiz do clone e sem `-I`:
  - `python3 -m unittest tests.test_falhas_no_resumo tests.test_suite_partes tests.test_ci_local tests.test_ci_rapido_guardas tests.test_pesos_do_ci`: `Ran 180 tests`, `OK`.
  - `tests.test_catraca.Workflows`: `Ran 6 tests`, `OK`.
  - `tests.test_forge.PrePushSoOsAfetados`: `OK`.
- `bin/forge-mutante --conferir --base 86ac0fcb`: "conferidas: o trecho de cada spec do diff está no lugar".
- `bin/forge-mutante --processos 1 tests/mutantes/v047-ci-falhas-no-resumo.json`: F1 a F14 `morreu`; o F14 está em `.github/workflows/ci.yml:203`.
- Suíte inteira: não rodei, por ordem do dono (16/11). Fica no CI do PR, que ainda não existe (brief sem PR).
- Pareceres de devops e de segurança do workflow: cabem a esses papéis (`R-SEGURANCA`), e não os refiz.

## Parecer
**Aprovado.** O consertado está certo:
- O `pipefail` antes do `tee` mantém o código da parte vermelha.
- O leitor não roda em execução cancelada nem na promoção com árvore provada.
- Os agregadores de prova da develop só leem `needs.*.result`, e a catraca agora prova isso, job a job.
- Tirar as linhas da skill `ci-cd` resolve as métricas sem perder a regra, que fica no modelo do projeto.

Os três achados são recomendados, sem defeito provado. O A1 é texto órfão de referência e o A2 é duplicação de anotação. Os A1 a A4 do parecer anterior seguem abertos como recomendados, porque o delta não os toca.

## Revalidação por delta no head 21fa3b17 (E2.583)
Li só `forge-check parecer delta docs/reviews/v047-ci-falhas-no-resumo.md` (intervalo `a00638db..21fa3b17`, sem o que veio da base `develop`). No domínio entraram 3 arquivos, todos só de comentário: `.github/workflows/ci.yml` (2 linhas) e `tests/test_catraca.py` (1) trocam o caminho `docs/propostas/ci-rapido.md` por "a proposta ci-rapido"; `tests/mutantes/v047-ci-rapido-3.json` (M25 e M26) foi sincronizada com o texto do ci.yml. Nenhuma guarda mudou.
- `bin/forge-mutante --conferir --base a00638db`: "conferidas: o trecho de cada spec do diff está no lugar".
- `bin/forge-mutante --processos 1 tests/mutantes/v047-ci-rapido-3.json`: M25 a M34 `morreu`; M25 e M26 matam a mesma mutação (matriz de 5 partes trocada por 4).
- Testes tocados, na raiz do clone e sem `-I`: `python3 -m unittest tests.test_suite_partes tests.test_catraca.Workflows`: `Ran 55 tests`, `OK`.
- Suíte inteira: não rodei, por ordem do dono (16/11); fica no CI do PR.
- Achados A1 a A3 seguem recomendados, intocados pelo delta. Parecer segue **aprovado**.

## Revalidação por delta no head 0de0d3ee (E2.605)
Li só `forge-check parecer delta docs/reviews/v047-ci-falhas-no-resumo.md` (intervalo `21fa3b17..0de0d3ee`, sem o que veio da base). No domínio: `templates/projeto/.githooks/pre-push` (2 linhas), `tests/test_prepush_so_docs.py` (teste novo), `tests/mutantes/v047-ci-falhas-no-resumo-2.json` (G1, G2) e `tests/test_forge.py`.
- Lógica do kill: sem pgid legível, `kill -0 -- -$etapa` prova que o grupo de PGID da etapa ainda tem membro; só então `pg=$etapa` e `alvo=-$etapa`. O PID da etapa não se repete enquanto o grupo vive, então o grupo é o dela. Sem grupo (sem `set -m`), `kill -0` falha, `pg` fica vazio e o alvo segue só a etapa. Correto.
- `python3 -m unittest tests.test_prepush_so_docs`, sem `-I`: `Ran 63 tests`, `OK (skipped=9)`; os 9 pulos são do /proc e do chown do sandbox. O teste do ps falso roda e passa.
- Sonda com `kill -0` no lugar de `vivos()`: hook real, `OK`; guarda G1 trocada por `:`, `FAILED (failures=1)`. A guarda é provada por comportamento.
- `bin/forge-mutante --conferir --base 21fa3b17`: "conferidas: o trecho de cada spec do diff está no lugar". `bin/forge-mutante --processos 1 tests/mutantes/v047-ci-falhas-no-resumo-2.json`: G1 `sobreviveu`, G2 `controle vermelho`, ambos pelo A4 (/proc do sandbox), não por defeito do hook.
- Suíte inteira: não rodei, por ordem do dono; fica no CI. Parecer segue **aprovado**.
