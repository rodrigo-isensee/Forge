---
tipo: revisao-seguranca
contrato: 1
pedido: lote-cilista
branch: melhoria/lote-cilista
commit: 79fb8162cbaafc7d34f5b1eab672a2383e3c39d0
parecer: reprovado
revisor: forge:security-engineer
data: 2026-10-26
---
# Review de segurança: lote-cilista

Escopo: `tests/test_ci_local.py` e `changelog.d/lote-cilista.md` no diff `b6eb84f...79fb816` (CI-LINT-LISTA-ABERTA, volta 1), com revalidação por delta (`forge-check delta`, `009668b..79fb816`) dos achados A1 a A4 do parecer `bd91b51`. O `.github/workflows/ci.yml` não muda; foi lido para conferir a trava contra a bateria real.

## Gatilhos
Controle do Forge (`R-SEGURANCA`): o teste é a trava de CI-ORDEM-LINT, que impede código da branch de rodar antes do actionlint e do zizmor (ele poderia pôr um binário falso no `GITHUB_PATH` e esconder o lint).

## Achados
- A5 (bloqueante) tests/test_ci_local.py:36 · env que executa por lista negativa: env inline (env: {BASH_ENV: scripts/x.sh}) no gate, no download, no actionlint, no zizmor ou no topo do workflow passa, e PATH, LD_PRELOAD e "BASH_ENV" entre aspas em bloco também (sonda P2a a P2h, P2j, lista vazia)
- A6 (recomendado) tests/test_ci_local.py:90 · o actionlint e o zizmor têm condição, run e shell conferidos, mas não continue-on-error nem working-directory; continue-on-error: true no actionlint passa (sonda P2l) e o lint deixa de reprovar o job

## Detalhe dos achados
Caminho de ataque comum (o mesmo do parecer `bd91b51`): quem edita o `ci.yml` num PR (agente ou contribuidor), por engano ou refatoração, põe código da branch antes do lint; a trava existe para pegar isso, e o próprio teste e o changelog declaram `BASH_ENV`, `ENV` e `defaults` proibidos. Sondas em `$TMPDIR/security-engineer-lote-cilista/sonda3.py` (log `sonda3.log`), fora do repo, chamam `passos_antes_do_lint_fora_da_lista` sobre o `ci.yml` real com uma alteração cada.

- **A5** · classe: env que executa conferido por lista negativa. Evidência `tests/test_ci_local.py:36` (regex `^\s*(BASH_ENV|ENV|defaults)\s*:` só casa chave no começo da linha, sem aspas, e só esses três nomes) e `:92`; `scripts/ci-local:158-162` lê só `env:` em bloco e ignora o valor inline, e o env do passo não entra no hash (`:61-62` confere só o `run`). Sondas, todas com resultado `[]`: P2a gate com o env trocado por `env: {GH_TOKEN: ..., BASE_REF: ..., BASH_ENV: scripts/x.sh}`; P2b download, P2c actionlint e P2d zizmor com `env: {BASH_ENV: scripts/x.sh}`; P2j `env: {BASH_ENV: scripts/x.sh}` no topo do workflow; P2e `"BASH_ENV": scripts/x.sh` em bloco no gate; P2f `PATH: ./scripts:/usr/bin:/bin` no gate; P2g `LD_PRELOAD: ./bin/x.so` no gate; P2h `BASH_FUNC_git%%` no gate. O controle P2m (`BASH_ENV` em bloco, sem aspas) reprova, e P2i (env inline no job) quebra a leitura e reprova por erro. Efeito provado localmente: `bash --noprofile --norc -eo pipefail` (o shell padrão do `run`) com `BASH_ENV=scripts/x.sh` executa `scripts/x.sh` antes do corpo, e com `PATH=./scripts:...` o `git` do gate resolve para `scripts/git` da branch. Nos dois casos o código da branch roda no passo do gate, antes do download e do lint, e pode escrever no `GITHUB_PATH` um `actionlint` falso. Severidade: média (fura a trava de CI-ORDEM-LINT nos casos que ela diz cobrir). Correção mínima, por lista positiva como o `run`: o env do gate igual ao conjunto esperado de chaves e valores (GH_TOKEN, EVENTO, ACAO, ANTES, HEAD_SHA, REPO, BASE_REF), o do job igual às quatro chaves de versão e checksum, nenhum env no download, no actionlint, no zizmor nem no topo do workflow, e qualquer `env:` com valor na mesma linha (inline ou alias) reprova; somar à tabela `variantes` os casos P2a a P2h e P2j. Esforço P. Dono: `devops-engineer`.
- **A6** · evidência `tests/test_ci_local.py:89-91`. Sonda P2l: `continue-on-error: true` no passo do actionlint resulta em `[]`; o passo falha e o job segue verde, o que esconde o lint sem código da branch. Não é código antes do lint, por isso fica recomendado. Correção: os passos do actionlint e do zizmor sem chaves além de `name`, `if` e `run` (o mesmo vale para `working-directory`). Esforço P. Dono: `devops-engineer`.

### Revalidação dos achados do parecer bd91b51 (por delta, com as mesmas sondas)
- **A1 fechado** · `:71-72` aceita SO_SEM_LINT só depois do gate; sonda S1 (passo com SO_SEM_LINT antes do gate) agora resulta em `['Prepara']`, e o subcaso "SO_SEM_LINT antes do gate roda antes do lint" está na tabela.
- **A2 fechado** · `:68-69` recusa `shell`, e o gate e o download passam só com o hash do `run` (`:61-62`, `:74`, `:76`); sondas S2, S2b (`run: |-`), S3, S3b (`shell: python {0}`) e S5 (`>-`) reprovam.
- **A3 fechado** · `:89-91` confere o `run` e o `shell` do actionlint e do zizmor; sonda S4 reprova.
- **A4 fechado** · o regex de código da branch saiu e o hash do `run` o substitui; sondas S6 e S6b (`docs/x` no gate) reprovam.

### Os dois pontos da conferência de entrega
- **(1) passo com if SO_SEM_LINT depois do gate e qualquer run (`:71-72`) roda código da branch antes do lint? Descartado.** Depois do gate, `steps.gate.outputs.pesada` já vale `true` ou `false` (ou vazio, se o gate falhou e o job reprova). Tabela das três saídas: SO_SEM_LINT e SO_COM_LINT nunca valem juntos, então o passo leve roda só quando o download, o actionlint e o zizmor não rodam no job, e não tem lint para esconder. E `pesada=false` só sai quando o diff desde o commit anterior é só `docs/reviews/` ou `docs/qa/` (sonda do `grep` do gate com GNU grep: `ci.yml` ou `tests/` no diff dá `pesada=true`), ou seja, o `ci.yml` com esse passo é o mesmo que já passou pelo actionlint e pelo zizmor no commit anterior, verde. O passo real `Testes que leem pareceres` é esse caso por desenho.
- **(2) env inline `env: {BASH_ENV: scripts/x.sh}` no gate, no download, no actionlint ou no zizmor passa (`:36`)? Confirmado:** é o A5 (sondas P2a a P2d).

PA-7 (`docs/engineering/achados-recorrentes.md`): lista vazia, nada a conferir. `changelog.d/lote-cilista.md`: sem segredo nem caminho pessoal. `python3 -m unittest tests.test_ci_local`: 53 OK no `79fb816`.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática, `forge-check delta` e as sondas em Python e bash acima (locais e passivas). Não estão no PATH: `gitleaks`, `actionlint`, `zizmor`, `semgrep`, `osv-scanner` (lacuna; o CI roda actionlint e zizmor, e o `ci.yml` não muda neste diff).
