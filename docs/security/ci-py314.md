---
tipo: revisao-seguranca
contrato: 1
pedido: CI-PY314
branch: melhoria/ci-py314
commit: 8f869ba25e1e1840a717edf8bc401f63f084c64e
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-23
---
# Review de segurança: CI-PY314

## Gatilhos
`R-SEGURANCA`: pipeline/CI (`.github/workflows/ci.yml`, controle do Forge). Diff revisado: `origin/develop...8f869ba` (um job novo, `bateria-python-tres-quatorze`, mais fragmento de changelog e pareceres).

## Achados

## Detalhe dos achados
Sem achado bloqueante. Verificado no job novo (`.github/workflows/ci.yml:37-70`):
- Ações fixadas por sha, os mesmos dos jobs atuais: `checkout` 11d5960a (v4.4.0), `setup-python` a26af69b (v5.6.0), `setup-node` 49933ea5 (v4.4.0). Nenhuma ação nova nem por tag.
- `persist-credentials: false` no checkout; `permissions: contents: read` herdado do topo (linha 13); sem segredo no job; gatilhos inalterados (`pull_request`, nunca `pull_request_target`); `timeout-minutes: 15`; `concurrency` herdada.
- Instalação do CLI do Claude Code com versão fixada (`@2.1.296`) e `--allow-scripts` restrito ao próprio pacote, igual ao job `bateria` (linhas 129 e 65); a repetição só em falha de rede não afrouxa a verificação.
- Nomes dos checks exigidos intactos: `bateria`, `checagem rápida (push na develop)` e `catraca` não mudaram; o check novo `bateria (python 3.14)` é aditivo (torná-lo obrigatório é ação do dono). Mesma condição `if` da `bateria`.
- Cobertura do que depende da versão do Python: roda `scripts/suite-paralela.py` e `tests/e2e-instalacao.sh` (`python3 -c` na linha 27 e `bin/forge-init`). Ficam na `bateria` os gates em Python (changelog, release, catraca), cuja lógica a suíte, rodando no 3.14, já exercita, e as ferramentas que não executam Python (shellcheck, actionlint, zizmor, `claude plugin validate`, varredura de segredos). Aceito do ponto de vista de segurança: nenhum gate de segurança deixa de rodar, e a `bateria` no 3.12 segue completa. Run 39979644068: `bateria (python 3.14)` e `bateria` success, `checagem rápida` skipped (esperado).
- Recomendação não bloqueante: o job roda inteiro também em commit só de parecer (custo de tempo, sem risco; a revisão de devops já registra).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática do diff e dos runs; `actionlint` e `zizmor` ausentes do PATH local (lacuna; rodam na `bateria` do CI sobre este arquivo); `gitleaks` não executado (diff sem credencial, só workflow e docs).
