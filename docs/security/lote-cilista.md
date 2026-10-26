---
tipo: revisao-seguranca
contrato: 1
pedido: lote-cilista
branch: melhoria/lote-cilista
commit: 009668b935cc2ed2692d199ef56807f657019af2
parecer: reprovado
revisor: forge:security-engineer
data: 2026-10-26
---
# Review de segurança: lote-cilista

Escopo: `tests/test_ci_local.py` e `changelog.d/lote-cilista.md` no diff `b6eb84f...009668b` (CI-LINT-LISTA-ABERTA). O `.github/workflows/ci.yml` não muda; foi lido para conferir a lista positiva contra a bateria real.

## Gatilhos
Controle do Forge (`R-SEGURANCA`): o teste é a trava de CI-ORDEM-LINT, que impede código da branch de rodar antes do actionlint e do zizmor (ele poderia pôr um binário falso no `GITHUB_PATH` e esconder o lint).

## Achados
- A1 (bloqueante) tests/test_ci_local.py:57 · passo condicional: um passo com `if` igual a SO_SEM_LINT é aceito em qualquer posição; antes do gate, steps.gate.outputs.pesada é vazio, a condição é verdadeira e o passo roda código da branch antes do lint, que roda depois (sonda S1, lista vazia)
- A2 (bloqueante) tests/test_ci_local.py:59 · run disfarçado: o gate e o download só passam pelo regex sobre o `run` lido pelo ler_jobs, que não lê `run: |-`/`>-` nem confere `shell:`; o gate real com `run: |-` e `python3 scripts/x.py`, ou com `shell: python {0}`, é aceito (sondas S2b, S3b)
- A3 (recomendado) tests/test_ci_local.py:76 · o `run` do actionlint e do zizmor não é conferido; `bash scripts/x.sh; actionlint -color` no próprio passo do actionlint passa (sonda S4)
- A4 (recomendado) tests/test_ci_local.py:28 · o regex de código da branch é lista negativa: caminho fora de scripts/bin/tests/hooks/.github (ex.: `docs/x`) no gate passa (sonda S6b); preferir conferir o `run` do gate por conteúdo esperado

## Detalhe dos achados
Caminho de ataque comum: quem edita `ci.yml` num PR (agente ou contribuidor) e, por engano ou refatoração, põe código da branch antes do lint; o teste existe para pegar exatamente isso. Quem quer burlar de propósito também edita o teste, e isso fica com o review; o que se cobra aqui é que a trava não tenha furo nos casos que ela mesma diz cobrir (nome parecido, `uses` sem SHA, run disfarçado de setup, passo condicional). As sondas estão em `$TMPDIR/security-engineer-lote-cilista/sonda.py` e `sonda2.py` (fora do repo) e chamam `passos_antes_do_lint_fora_da_lista` sobre o `ci.yml` real com uma alteração cada.

- **A1** · evidência `tests/test_ci_local.py:57-58` (`if passo["se"] == SO_SEM_LINT: return True`, antes de qualquer conferência de posição ou de `run`). Sonda S1: passo `Prepara` com `if: ${{ !cancelled() && steps.gate.outputs.pesada != 'true' }}` e `run: bash scripts/prepara.sh` posto antes do gate resulta em `[]`. No Actions, `steps.gate.outputs.pesada` de um passo que ainda não rodou vale nulo, `!= 'true'` é verdadeiro, o passo roda, e o gate em seguida grava `pesada=true` e o lint também roda: código da branch antes do lint, no mesmo job. A exclusão mútua com o lint só vale depois do gate. O caso de teste "passo exclusivo do gate com outra condição" põe o passo logo antes do actionlint e não cobre a posição. Severidade: média (fura a trava de CI-ORDEM-LINT). Correção mínima: aceitar SO_SEM_LINT só com índice maior que o do passo `id: gate` (e exigir que o gate exista antes) e acrescentar o caso "SO_SEM_LINT antes do gate" à tabela `novos`, inserido antes do gate. Esforço P. Dono: `devops-engineer`.
- **A2** · evidência `tests/test_ci_local.py:59-66` com `scripts/ci-local:153-157`: o `ler_jobs` só trata `run: |` e `run: >`; com `|-`, `>-`, `|+` ou indicador de indentação ele guarda só o indicador (`"|-\n"`) e o corpo some, e com `run: *ancora` guarda o alias. O regex roda sobre esse texto vazio e o gate (nome e `id` iguais) é aceito. O campo `shell` é lido mas não conferido: `shell: python {0}` com `exec(open('agents/x').read())` passa. Sondas S2b (gate real, `run: |-` com `python3 scripts/x.py`) e S3b resultam em `[]`; o próprio teste declara o caso "nome do gate copiado com código da branch" como reprovado, e a variante com `|-` não reprova. Severidade: média. Correção mínima, por padrão de negar: em `_pode_antes_do_lint`, recusar passo sem `uses` cujo `shell` não seja vazio ou cujo `run` comece por `|`, `>`, `*`, `&` ou `!` (sinal de que o corpo não foi lido), e somar à tabela `novos` os casos `|-` e `shell:`. Esforço P. Dono: `devops-engineer`.
- **A3** · evidência `tests/test_ci_local.py:76` (`n != lint` tira o actionlint da conferência; o zizmor fica fora do recorte) e só a condição deles é conferida (`:77`). Sonda S4: `run: bash scripts/x.sh; actionlint -color` resulta em `[]`. Não é passo novo antes do lint, por isso fica recomendado. Correção: exigir `run` igual ao esperado (`actionlint -color` e o comando do zizmor). Esforço P. Dono: `devops-engineer`.
- **A4** · evidência `tests/test_ci_local.py:28`. O regex pega `python3`, `bash`, `sh`, `./` e os diretórios de código, mas não `perl`, `ruby`, `env`, caminho em `docs/`, `agents/`, `skills/` ou `templates/` sem extensão `.sh`; sonda S6b (`docs/x` no gate real) resulta em `[]`. Só afeta passos com o nome exato do gate ou do download, por isso fica recomendado. Correção: conferir o `run` do gate e do download contra o conteúdo esperado (ou o hash dele), o que também fecha o A2 e o A4 de uma vez. Esforço P. Dono: `devops-engineer`.

Lista positiva larga demais: não. `uses` só de `actions/checkout`, `actions/setup-python` e `actions/setup-node`, com nome exato (dono em maiúscula ou ação parecida reprovam), SHA de 40 hex e sem `run`; ação local (`./`), `docker://`, terceiros e chave `uses` não lida (aspas, bloco) caem no `return False` final. Os furos são os dois acima, não a largura da lista.

PA-7 (`docs/engineering/achados-recorrentes.md`): lista vazia, nada a conferir. `changelog.d/lote-cilista.md`: sem segredo nem caminho pessoal. `python3 -m unittest tests.test_ci_local`: 53 OK no `009668b`.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática e as sondas em Python acima. Não estão no PATH: `gitleaks`, `actionlint`, `zizmor`, `semgrep`, `osv-scanner` (lacuna; o CI roda actionlint e zizmor, e o `ci.yml` não muda neste diff).
