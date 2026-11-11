---
tipo: revisao-seguranca
contrato: 1
pedido: v046
branch: melhoria/ci-lote-e1
commit: 00e6d4304a6612dc657b084cef669944b7dd9371
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-11
---
# Review de segurança: v046 (E1.2, lote E1 do CI), revalidação

Revalidação por delta: `b38fe7e6..00e6d430` (1 commit, `00e6d430`), em `.github/workflows/ci.yml`, `changelog.d/ci-lote-e1.md`, `tests/mutantes/v046-ci-lote-e1.json`, `tests/test_ci_local.py`, `tests/test_suite_paralela.py` e `tests/test_suite_partes.py`. O parecer anterior (commit `b38fe7e6`, aprovado) vale para o resto do diff `36d976df..b38fe7e6`, que o delta não toca.

## Gatilhos
`R-SEGURANCA`: job novo no workflow do CI (`verificacoes`) que executa código da branch, saída nova entre jobs (`outputs.pesada`) e mudança no grafo `needs` do check exigido `bateria`.

## Achados
- A2 (recomendado) .github/workflows/ci.yml:586 · no job verificacoes a ordem CLI antes de código da branch (Provas, e2e) só está no comentário; nenhum teste nem mutante a guarda, ao contrário do bateria (test_ci_local.py:326)

## Sondas

## Detalhe dos achados
A1 do parecer anterior: resolvido. O job `bateria` ficou só com os passos baratos; Provas, shellcheck e e2e foram para `verificacoes` (`ci.yml:562`, `needs: [bateria]`), e o changelog não promete mais tempo.

Verificado sem achado de segurança:
- **CI-ORDEM-LINT no job `bateria`.** A remoção do passo Neutralidade não muda a ordem: o download conferido por checksum, o actionlint, o zizmor, o CLI e o validate seguem antes de todo código da branch. O teste `tests/test_ci_local.py:326` continua verde.
- **CI-ORDEM-LINT no job `verificacoes`.** O job é novo e tem `GITHUB_PATH` limpo. Ele não roda lint; o lint do mesmo commit já passou no `bateria`, que ele exige (`needs`), e nenhum julgamento do lint fica para um job que a branch envenenaria antes. O CLI vem antes das Provas e do e2e (`ci.yml:587-591`). A ordem Provas, shellcheck, e2e é a mesma que estava no `bateria` (pré-existente, fora do delta).
- **Permissões.** `verificacoes` tem só `contents: read`: o `checks: read` do gate não foi herdado. `persist-credentials: false`, ações nas mesmas SHAs, nenhum segredo, nenhum `pull_request_target`.
- **Saída entre jobs.** `outputs.pesada` (`ci.yml:420`) é escrito pelo gate, que roda antes de todo código da branch e só grava o literal `true` ou `false`. Ele só aparece em expressões `if:`, nunca interpolado num `run:`, então não há injeção. A troca de `== 'true'` para `!= 'false'` falha para o lado seguro: saída vazia roda os passos pesados em vez de pulá-los.
- **Agregador falha fechado.** `agregador` (`ci.yml:634-652`) exige `success` explícito de `bateria`, `verificacoes`, `partes-doze` e `pulados-doze`, com `always()`. Um `verificacoes` pulado ou vermelho reprova o check exigido. Os mutantes M5 e M6 (`tests/mutantes/v046-ci-lote-e1.json`) cobrem o `needs` e o agregador. O `bateria (python 3.14)` não exige `verificacoes`, e isso está certo: as partes dele já exigem o `bateria`, e as verificações longas rodam uma vez só.
- **Neutralidade só nas partes (aceito).** Perde-se o vermelho cedo, mas a guarda do `R-NEUTRO` continua no check exigido: as partes rodam `tests.test_forge` inteiro e conferem que a divisão cobre todo o discover. No caminho do commit só de parecer, o `bateria` ainda roda `tests.test_forge.Neutralidade` (`ci.yml:459`). Nada sai do portão, só a latência muda.
- **Custo (`R-CUSTO`).** Um job a mais por PR, nos runners gratuitos do repositório público. O vermelho barato pula esse job e as seis partes. Nada pago entra.

A2: evidência `ci.yml:586` (comentário "O CLI antes de qualquer código da branch") sem asserção correspondente; `test_bateria_lint_e_ferramentas_antes_de_qualquer_codigo_da_branch` (`tests/test_ci_local.py:326`) só lê os passos do `bateria`. Caminho de ataque: nenhum hoje. Quem controla a branch já controla o `tests/e2e-instalacao.sh`, que é o único passo que usa o `claude` depois. O risco é uma edição futura pôr um passo de código da branch antes do CLI ou de um verificador neste job sem que nada reprove. Severidade: baixa. Correção mínima: estender o teste de ordem ao job `verificacoes` (instalação do CLI antes de "Provas cmd...", "shellcheck (scripts e hooks)" e "Instala o Forge num projeto vazio e inicializa") e um mutante que inverta a ordem. Esforço P. Dono: devops-engineer (teste com o qa-engineer).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do delta e testes dos arquivos tocados (`tests.test_suite_paralela`, `tests.test_suite_partes`, `tests.test_ci_local`: 151 testes, OK) num worktree destacado do `00e6d430`. Lacuna: actionlint, zizmor e gitleaks não estão no PATH local; o actionlint e o zizmor rodam no job `bateria` do CI deste head.
