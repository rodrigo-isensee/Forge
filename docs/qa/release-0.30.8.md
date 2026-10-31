---
tipo: qa
contrato: 1
pedido: release-0.30.8
branch: melhoria/release-0.30.8-fecha
commit: 9f4cc095249ec158b49e520d9a13a42b336bc60f
parecer: aprovado
revisor: forge:qa-engineer
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-31
---
# QA: release-0.30.8

Código testado: 57baeb6 (HEAD da branch, da71897, difere só pelo parecer de review: `git diff 57baeb6 HEAD --stat` toca só `docs/reviews/release-0.30.8.md`). Escopo: a leva contra a main, `git diff 6c17ca7...57baeb6` (22 commits, PRs #373 a #398, 148 arquivos). Sem especificação de UX: vale o critério de integração (`R-QA`); cada PR da leva já tem QA próprio. Aqui: suíte inteira sobre o conjunto, validação do plugin, e a rodada de todos os mutantes declarados pela leva, conferidos contra o diff.

## Achados
- A1 (recomendado) bin/forge-check:612 · `(base or "")` em `base_do_delta` sem mutante; equivalente de fato (o hook só chama com base truthy, `pr_da_cli` só com string), mas nenhuma spec o declara como `equivalente`. Declarar no próximo PR de processo.
- A2 (recomendado) .githooks/pre-push:42 · a guarda C-14 (200 bytes, só imprimíveis) é shell e a checagem de cobertura a lista `não coberto`; sem spec no #397. Provei à mão (P1 a P3, abaixo) e todas morreram; falta a spec em tests/mutantes.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Suíte inteira verde (`R-VERIFY`) | `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -q` na worktree: 2330 testes, 1194 s | n/a | passou (OK, 27 skipped herdados, rc 0) |
| Plugin válido | `scripts/validar-plugin.sh` | n/a | `Validation passed` |
| Mutantes declarados pela leva | `bin/forge-mutante tests/mutantes/<spec>.json`, uma rodada por spec (14 specs: cobertura-equivalente, k164-intervalo, k164-mesma-base, mutante-casa-espaco, pn1 a pn7, promover-auto, vermelho-filtro, worktree-orfas) | uma guarda por mutante | 101 mutantes, 101 `morreu`, nenhum sobrevivente, nenhum equivalente, 14 de 14 com rc 0 |
| Cobertura contra o diff | `bin/forge-mutante --cobertura --base 6c17ca7`: toda condição Python mudada em `bin/` e `hooks/` aparece `coberta`, `apagada` (condição só da base) ou `sem mutante` | condição mudada | 2 `sem mutante`: bin/forge-check:612 (equivalente, A1) e :639 (`if aviso:`, mutante meu Q1 morreu pelo teste `PrAposMergeDaBase.test_head_ja_contido_na_base_vale_so_pelo_diff_literal`) |
| Guarda shell do pre-push (#397) | spec minha fora do repositório: P1 (limite 200 B), P2 (só imprimíveis), P3 (aviso de espera usa o texto limpo) contra `tests.test_pre_push_trava` | tamanho máximo, caractere de controle | 3 `morreu` |
| Versão e CHANGELOG da release | conferidos no review (`scripts/conferir-release.py`, 21 entradas); não refeito | n/a | aceito do review |

## Cenários e resultado real
- Vermelho antes do verde: não refeito para a leva inteira (22 PRs); cada PR trouxe o seu `forge-testes --vermelho` no QA próprio. Aqui a prova de força dos testes é a mutação acima (101 + 4 mutantes mortos).
- Linhas de guarda sem mutante: `bin/forge-fechar` (shell, `não coberto` na checagem) tem a spec `worktree-orfas` (6 mutantes mortos) para a mudança do passo 7; `.githooks/pre-push` coberto por P1 a P3 (A2). `hooks/parecer.py` e `scripts/promover-homolog.py`: todas as condições mudadas estão `coberta` ou `apagada`.
- Estabilidade: a suíte passou na primeira rodada, sem falha de tempo; as duas quedas de teste de tempo vistas no pre-push do review (A2 dele) não se repetiram aqui.
- Sem rede útil: o sandbox nega as sondas externas do validador, sem efeito no resultado. Nada de `gh` consultado; os testes de CI ficam para o PR.
- Bugs novos: nenhum; `docs/qa/bugs/` não ganha arquivo.

## Revalidação pelo delta (head 9f4cc09, branch melhoria/release-0.30.8-fecha)
Parecer anterior sobre 57baeb6. Entre ele e 9f4cc09 entraram o fragmento `changelog.d/release-0.30.8.md` (1f76c6e, PR #399) e o fechamento (9f4cc09: fragmento apagado e a linha dele na seção [0.30.8] do CHANGELOG). Nenhum arquivo de `bin/`, `hooks/`, `.githooks/`, `scripts/` ou `tests/` mudou, então a conclusão do parecer anterior se mantém.
- `forge-check delta --parecer docs/qa/release-0.30.8.md` (rc 0): intervalo 57baeb6..7e6ff4d, única linha listada `CHANGELOG.md:24` (+1). Lido: a linha acrescentada em [0.30.8], texto igual ao do fragmento apagado (`git diff 19407f6 HEAD -- CHANGELOG.md changelog.d`). Já lido, sem releitura: o restante da leva, aceito do parecer anterior.
- Suíte inteira sobre o head (`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -q`): 2330 testes, 948 s, `OK (skipped=27)`, rc 0.
- `scripts/validar-plugin.sh`: `Validation passed`.
- Mutantes (101) e cobertura: não refeitos; o delta não toca código, e a rodada anterior vale (mesmo código de 57baeb6).
- Teto por PR (M14): contra origin/develop, o diff da branch tem 0 linhas de código ou teste (só CHANGELOG, fragmento e pareceres, todos fora da contagem). A branch cumpre a M14.
- Achados A1 e A2 seguem recomendados, sem mudança; nenhum bug novo.
