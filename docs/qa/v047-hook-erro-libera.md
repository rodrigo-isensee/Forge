---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-hook-erro-libera
commit: 4c350b2f78a2f5fc5753f74be8d5fb760c8bebbc
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-13
---
# QA: v047-hook-erro-libera

Pedido v047, etapa E3.37: QA por delta do head `4c350b2f` (base `c5aa70e1`), sobre a volta única da HOOK-ERRO-LIBERA (A1 a A4 da E3.18, parecer anterior no `9e3f57c6`, reprovado). Os critérios seguem sendo C1 a C8 e os casos E1 a E8 do modelo de ameaças da E3.6 (`/root/.forge-contrib/docs/security/v047-v2-ameacas.md`, seção 1). Domínio retestado: o que `forge-check parecer delta` listou (`bin/forge-testes`, `hooks/conformidade.py`, 14 fixtures `errointerno-*` novos, specs de mutante 2 e 5, `test_hook_erro_libera.py`, `test_testes_tocados.py`). Sem PR e sem check-run `bateria` do head: a suíte inteira fica para o CI do PR (carga ~14 em 12 núcleos).

## Achados
- A4 (recomendado) agents/tech-lead.md:21 · M14 segue acima da orientação: 445 linhas contáveis no head (eram 432) contra 150; não trava, mas o corpo do PR precisa de `teto: excedido, 445 linhas, <motivo>` (um comportamento, corpus próprio de 39 fixtures e 40 mutantes).

## Situação dos achados anteriores
Nenhum achado bloqueante aberto: A1, A2 e A3 do parecer anterior estão resolvidos (tabela abaixo).

## Critério → teste → resultado (delta)
| Achado/critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| A1 / C2 (verbos do git que gravam arquivo) | fixtures `errointerno-git-{restore,checkout,apply,am}-em-pedidos-bloqueia`, `-git-checkout-de-branch-libera`, `-prazo-git-{checkout,restore}-em-pedidos-bloqueia` | verbo fora da lista; `git checkout main` (sem caminho) segue liberando | passou; sondas próprias recusam `git restore --source=x docs/pedidos/v1.md` e `git checkout x -- pedidos/v1.md` |
| A2 / C2, C3 (troca de base) | fixtures `errointerno-cd-e-cp`, `-pushd-e-cp`, `-sh-c-cd-e-cp`, `-git-C-checkout`, `-git-work-tree-restore`, `-prazo-cd-e-cp`; legítimo `-cd-e-ls-libera` | `cd`, `pushd`, `-C`, `--work-tree`, dentro de `sh -c`; `cd` sem escrita libera | passou; sondas próprias recusam `cd docs; cp …`, `(cd docs && cp …)`, `env -C docs cp …`, `GIT_WORK_TREE=docs` com checkout e `--work-tree=docs` com checkout |
| A3 (mutante por verbo) | M34, M35 (`checkout`, `restore`), M36, M37 (`apply`, `am`), M38 (`BASE_TROCADA` na linha), M39, M40 (alternativas do regex) | cada verbo e cada alternativa de `BASE_TROCADA` | 40 de 40 morreram |
| A4 (teto M14) | medição | n/a | recomendado, ver Achados |
| C1, C3 a C8 (inalterados) | `test_hook_erro_libera` completo | ver parecer anterior | passou (11 testes) |

## Provas

**Testes do pedido** (`python3 -m unittest tests.test_hook_erro_libera tests.test_testes_tocados`): `Ran 161 tests in 128.832s`, `OK (skipped=1)`, rc 0. O `skip` vem de outro módulo; `test_hook_erro_libera` não tem skip.

**Vermelho antes do verde** (`R-QA`): `bin/forge-testes --vermelho c5aa70e1 --modulos test_hook_erro_libera`, rc 0. Abre com `vermelho: base=c5aa70e11859 head=4c350b2f78a2 módulos=test_hook_erro_libera`; os 11 testes passam no HEAD (`H=ok`) e caem na base; `contagem: prova (API ausente)=4; prova (asserção)=7`. O mínimo dos fixtures subiu para 39 e o de prazo para 7 (`minimo(...)` em `test_hook_erro_libera.py`), e o teste passa no head com esses pisos.

**Mutação:** `bin/forge-mutante --processos 2` sobre as 5 specs `tests/mutantes/v047-hook-erro-libera{,-2,-3,-4,-5}.json`: 40 mutantes, 40 `morreu`, rc 0 (M3, M4, M15, M20 e M23 morrem por erro do teste declarado sob o mutante, que passa sem ele; morte válida). Cobertura: `forge-mutante --cobertura --base c5aa70e1` só deixa `não coberto: hooks/hooks.json` (M29 e M30 o cobrem à mão); a linha de guarda `ESCRITORES` (`conformidade.py:2824`) agora tem mutante por verbo (M34 a M37) e a linha de `BASE_TROCADA` tem M38 a M40. Conferi o diff: nenhuma condição Python mudada sem mutante.

**Sondas próprias** (fixture temporário fora da árvore, `forcar: Guarda.bash/erro`, esperado rc 2 com `erro interno do hook conformidade`): recusam (rc 2) as 6 variantes de troca de base acima, `install -m 644 x docs/pedidos/v1.md`, `tee docs/pedidos/v1.md < x`, `sed -i s/a/b/ docs/pedidos/v1.md` e o verbo `merge`; liberam, como devem, `git status`, `ls ~zz`, `git checkout main`, `cp x build/y`, `git log --oneline`, `cd /tmp && ls`. Observação, sem achado: `git switch -f`, `git stash pop`, `git reset --hard`, `git cherry-pick`, `git rebase`, `git pull` e `git revert` liberam no erro forçado porque não citam caminho da política; a guarda normal também decide por caminho citado, então não é regressão nem critério C1 a C8 (não comparei o lado normal verbo a verbo).

**Suíte e CI:** sem PR, sem check-run `bateria` do head; a suíte inteira fica para o CI do PR. Acessibilidade e E2E: n/a (hooks de linha de comando).
