---
tipo: review
contrato: 1
pedido: v046
branch: melhoria/ci-lote-e1
commit: 00e6d4304a6612dc657b084cef669944b7dd9371
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-11
---
# Review: v046 (E1.2, lote E1 do CI), revalidação da volta 1

Delta lido: b38fe7e6..00e6d430 (um commit, 00e6d430). O `forge-check parecer delta` rodado em ~/.forge-contrib não acha o commit b38fe7e6 (`commit ... não existe`), porque esse repositório não é o clone. Por isso o delta foi lido com `git diff b38fe7e6 00e6d430` no clone. Tamanho M14 do PR inteiro (`git diff --numstat --no-renames 36d976df...00e6d430`, sem changelog.d nem tests/mutantes): 146 linhas, dentro do teto. Sem custo em dinheiro (`R-CUSTO`): é um job a mais em runner hospedado, sem serviço novo.

## Achados
- A1 (recomendado) scripts/suite-paralela.py:564 · `forge-mutante --cobertura` dá `sem mutante` em :564 (`or ()`) e :568 (filtro de crase); o teste já cobre os dois ramos, falta declarar M7 e M8 na spec.
- A2 (recomendado) .github/workflows/ci.yml:562 · O job novo reinstala Node e CLI (mais minutos de runner, sem custo em dinheiro); quando o vermelho barato for medido, conferir se compensa.

## Sondas

## Parecer
Aprovado. O A1 bloqueante da rodada anterior está resolvido. O job `bateria (passos)` (ci.yml:410) agora só tem os passos baratos: gate, lint, zizmor, degrau, CLI, validate, changelog, segredo e parecer. Provas, shellcheck e e2e passaram para o job novo `bateria (verificações longas)` (ci.yml:562), que tem `needs: [bateria]` e roda em paralelo às partes. O agregador `bateria` exige os quatro resultados em `success` (ci.yml:639), e um vermelho barato pula as partes e as verificações. O `bateria (python 3.14)` reprova pela parte pulada. Os checks exigidos não mudaram de nome. O gate passa como saída do job (`pesada`). Como o gate sempre grava `true` ou `false`, o `!= 'false'` equivale ao `== 'true'` no GitHub, e o ci-local também roda os passos. Ordem CI-ORDEM-LINT mantida no job novo: o CLI vem antes do primeiro código da branch.

Os recomendados anteriores também estão resolvidos. A2: o teste afirma o 30 literal, e o mutante M2 (30 para 31) morreu. A3: há 6 mutantes declarados, e os 6 morreram. A4: a Neutralidade saiu do job de passos e roda uma vez só, nas partes (tests.test_forge); no commit só de parecer, segue no passo leve (ci.yml:459). Também não há mais promessa de tempo: o comentário (ci.yml:14) e o changelog trocaram "30 s" por "sem medida".

Decisão sobre perder o vermelho cedo da Neutralidade: aceito. Ela continua bloqueando o merge pelas partes; só fica vermelha alguns minutos mais tarde. Tirá-la do discover das partes e manter no job barato pediria uma exceção na guarda de completude da divisão (a parte confere que cobre todo o discover). Seria um mecanismo a mais para um teste que raramente cai e que o envio local já roda quando o diff toca texto.

Ferramentas no head (worktree destacada em 00e6d430):
- `bin/forge-mutante tests/mutantes/v046-ci-lote-e1.json`: M1 a M6, todos `morreu`.
- `--cobertura`: só o A1 acima; `.github/workflows/ci.yml` aparece como `não coberto` (não é Python) e fica com os testes de fiação.
- Testes dos arquivos tocados (`tests.test_suite_paralela`, `test_suite_partes.FiacaoDoCI`, `test_ci_local.MatrizNeedsEAgregadorTest` e `LeituraDosWorkflowsTest`): 86 testes, OK.
- O actionlint e a suíte inteira ficam com o CI do PR.
