---
tipo: review
contrato: 1
pedido: lote-cilista
branch: melhoria/lote-cilista
commit: 79fb8162cbaafc7d34f5b1eab672a2383e3c39d0
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-26
---
# Review: lote-cilista

Escopo: E1 do pedido LOTE-CILISTA (CI-LINT-LISTA-ABERTA), revalidação 2 da volta 1. Delta lido (`forge-check delta --parecer` sobre o parecer 2606e53): `009668b..79fb816`, `tests/test_ci_local.py` linhas 3, 29-36, 61-65, 68-69, 71-72, 74, 76, 86, 88-93 e 279-317, e `changelog.d/lote-cilista.md`:2. Já lido no parecer anterior (009668b), sem mudança: o resto de `tests/test_ci_local.py` (`passos_da_bateria`, a tabela `novos` e a contraprova depois do zizmor).

## Achados
- A4 (bloqueante) tests/test_ci_local.py:36 · defeito provado e segurança com gatilho: o regex ancorado e sem aspas deixa passar `env: {BASH_ENV: ...}`, a chave `"BASH_ENV":` e `"defaults":` (YAML válido, lista vazia); detalhe e sugestão em "Detalhe do A4"
- A5 (recomendado) tests/test_ci_local.py:74 · quem muda o gate ou o download de propósito recebe só o nome do passo em `fora`, sem o hash novo; sugestão: pôr o sha256 calculado no item (`"<nome> (run sha256 <x>)"`), para a atualização no mesmo diff ser mecânica.
- A6 (recomendado) tests/test_ci_local.py:288 · o comentário diz "cada uma reprova com um item", mas o subcaso afirma só `assertTrue(fora)`; sugestão: `assertEqual(len(fora), 1, fora)` como na tabela `novos`, ou ajustar o comentário.

## Detalhe do A4
Classe: defeito provado (o teste e o fragmento declaram `BASH_ENV`, `ENV` e `defaults` proibidos) e segurança com gatilho (CI-ORDEM-LINT: `BASH_ENV` no gate faz o bash ler um arquivo da branch antes do lint). Sondas, cada uma com `yaml.safe_load` ok e `passos_antes_do_lint_fora_da_lista` vazia: `env: {BASH_ENV: scripts/x.sh, GH_TOKEN: ...}` no gate; chave `"BASH_ENV": scripts/x.sh` no env do gate; `"defaults": {run: {shell: "python {0}"}}` no job. Sugestão: tirar a âncora e aceitar aspas e fluxo (`(?:^|[{,\s])["']?(BASH_ENV|ENV|defaults)["']?\s*:`) e somar os três casos à tabela `variantes`.

## Parecer
**Reprovado** por A4, numa passada só (nenhum outro bloqueante no delta).

Achados do parecer 2606e53: **A1 fechou** (o regex `CODIGO_DA_BRANCH` saiu; gate e download agora passam por hash do `run`; subcaso "gate com ponto e caminho .github"). **A2 fechou na forma de bloco** (`shell` recusado em todo passo sem `uses` e em ação, `BASH_ENV`/`ENV`/`defaults` no arquivo inteiro, `run: |-`/`>-` cai no hash porque o `ler_jobs` guarda só o indicador), **mas fica aberto nas formas de fluxo e com aspas: é o A4**. **A3 fechou** (subcasos "condição do actionlint/zizmor fora da esperada"; o `run` e o `shell` dos dois também passaram a ser conferidos, o que fecha o A3 da segurança).

Troca do regex pelo hash: legível e mantível. Conferir por conteúdo é o padrão de negar que a segurança pediu (A4 dela), e o hash é sobre o texto que o `ci-local` lê, então qualquer forma que o parser não leia (bloco `|-`, âncora, alias) vira texto diferente e reprova. O custo é o hash opaco: mudar o gate exige atualizar `SHA256_RUN_DO_GATE` no mesmo diff, o que o comentário das linhas 29-30 diz e o review vê (o diff do `ci.yml` mostra o conteúdo; o do teste, a troca do hash). A5 só barateia essa atualização.

Pontos da conferência de entrega, lidos e sondados:
1. Passo com `if` SO_SEM_LINT depois do gate com qualquer `run` (:71-72): a sonda confirma que passa (`bash scripts/x.sh; echo /tmp/falso >> "$GITHUB_PATH"` depois do gate resulta em `[]`), **mas não é defeito da trava**: depois do gate a saída `pesada` está fixa, e o passo só roda quando ela não é `'true'`, caso em que o actionlint e o zizmor (com `if` SO_COM_LINT, conferido na :90) não rodam no job. Não há lint para esconder; o binário no `GITHUB_PATH` não alcança nada que a trava proteja. Um passo posterior não muda `steps.gate.outputs`. Sem achado.
2. Env inline `env: {BASH_ENV: ...}` (:36): confirmado por sonda, é o A4 (também a chave entre aspas e o `defaults` entre aspas). O env do gate, do download, do actionlint e do zizmor não é lido passo a passo, mas o regex roda no arquivo inteiro, então a correção do A4 cobre os quatro.

Testes do lote: `python3 -m unittest tests.test_ci_local` → `Ran 53 tests in 1.519s OK` no head 79fb816 (18 variantes como subcasos do mesmo teste). Sondas em `$TMPDIR/tech-lead-lote-cilista/sonda-r3.py` e `sonda-r4.py`.

Teto M14: 164 linhas de código e teste (`tests/test_ci_local.py` 151+13; fragmento e pareceres ficam fora), abaixo de 400; não toca `hooks/` nem `PROTEGIDOS`. Fragmento em `changelog.d/` atualizado. Commit 79fb816 em Conventional Commits em português, com o motivo no corpo. `R-NEUTRO` e `R-CUSTO`: sem termo de projeto nem serviço pago. Achados recorrentes (PA-7): lista vazia, nada a conferir. O projeto não tem `docs/engineering/praticas.md`, sem regra "ferramenta" a citar.
