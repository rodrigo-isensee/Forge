---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-f6-ci-uma-vez
commit: 5f26b0f9c0071209726aba5e89ad04acc177eb42
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-27
---
# Review de segurança: v0481 (E32.17, F6, #929), revalidação por delta das voltas 1 a 3

Revalidação por delta (`forge-check parecer delta`) sobre `e8368a4c..ac8202d0`, sem o que veio da develop; o código de `ac8202d0` é igual ao de `5f26b0f9` (de lá para cá só pareceres de devops). A 1ª rodada (reprovada, A1) fica no git.

Gatilhos: CI e workflows, permissões do token, controle do Forge (prova da árvore da develop e da promoção).

## Delta lido (no domínio)
- `scripts/arvore-testada.py`: `prova_do_pr` e `--do-pr` saem inteiros; a prova volta a ser só a do push na develop (`provar`, C-3), sem caminho novo de leitura da API.
- `.github/workflows/ci.yml`: sai o job `arvore-envio` e todo `if: needs.arvore-envio...`; as 5 partes, o teto de pulados e o agregador `rapida` (`ci.yml:136`) voltam a rodar sempre no push na develop, com `contents: read` só. O nome do passo de fumaça 3.14 ficou entre aspas (sem efeito de segurança).
- `.github/workflows/diario.yml:101-127`: a fatia de mutantes passa a uma spec por chamada e tira por `--ids` os mutantes de `tests/fixtures/mutantes-pendentes.txt`. Entradas só de arquivos da develop revisados; `$linha` sem aspas segue sem entrada externa; permissões inalteradas (`contents: read` no topo, `issues: write` só no `cartao`, `diario.yml:140`, sem checkout).
- `tests/config.json:81-83`: exceção de neutralidade `\bnpm\b` só para `diario.yml`, no mesmo molde da do `ci.yml`, para a mesma linha de instalação (`diario.yml:82`, versão fixa e `--allow-scripts` restrito ao pacote). Não abre termo novo nem vale para outro arquivo.
- `tests/test_catraca.py:4245-4269`: tetos de tempo e contagem de `always()` ajustados à saída do job (um agregador da develop, 3 jobs com `always()`, todos sem `uses:`); a guarda continua a mesma.

## Achados anteriores
- A1 (prova do PR forjável, `scripts/arvore-testada.py:163` na 1ª rodada): resolvido pelo corte. `prova_do_pr` não existe mais (`tests/test_arvore_testada.py:195` confere a ausência) e nada em `.github/`, `scripts/` ou `bin/` cita `--do-pr` ou `arvore-envio`. A segunda barreira (suíte no push na develop, lida pela promoção) volta ao que era antes do F6; a sonda S1 deixa de se aplicar.

## O que aperta, o neutro e o que afrouxa
**Aperta:** o `diario.yml` segue como sinal diário novo (suíte 3.14, e2e 3.12, fatia de mutantes) com issue automática.
**Neutro:** o push na develop e a promoção voltam ao comportamento anterior ao F6.
**Afrouxa** (decisão do dono de 26/11 19:37, rótulo `afrouxa-regra` aplicado pelo time, ADR 0003): suíte 3.14, e2e 3.12 e mutantes saem do portão do PR para o diário; os mutantes pendentes conhecidos ficam fora da fatia diária (a catraca que só encolhe continua no PR).

## Riscos aceitos e ferramentas
Nenhum risco aceito. CI do PR no head `ac8202d0` (run 45935698348): partes 1 a 5, passos, verificações longas, instalação e `bateria (python 3.14)` verdes; `bateria`, `bateria (pareceres)` e `catraca` vermelhos só por esperarem este parecer e o rótulo, como diz o brief. Rodei `tests.test_arvore_testada` e `tests.test_catraca.Workflows` (29 testes, OK). Ferramentas ausentes nesta estação: `gitleaks`, `actionlint`, `zizmor`, `osv-scanner`, `semgrep` (lacuna; o CI roda `actionlint` e `zizmor`).
