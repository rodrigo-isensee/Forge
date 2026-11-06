---
tipo: revisao-seguranca
contrato: 1
pedido: versao-033
branch: melhoria/ci-ubuntu-26
commit: c481b780e7d368f426043e49451ae7297f5281f3
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-04
---
# Review de segurança: ci-ubuntu-26 (migração para ubuntu-26.04)

Aprovado, sem bloqueante. Revisão estática de `b45e40a..c481b78` (código em `fd3a3e1`). Nos três workflows mudam só as 5 linhas `runs-on: ubuntu-24.04` para `ubuntu-26.04` (`ci.yml` 3, `catraca.yml` 1, `release.yml` 1). Nenhuma linha de `on:`, `if:`, `permissions:`, `env:`, `uses:` ou `run:` mudou. Também entram um teste novo em `tests/test_ci_local.py` (todo job em `ubuntu-26.04`) e um fragmento de changelog. Este parecer substitui o da rodada anterior, que fixou o `ubuntu-24.04` (commit `bbc658f`).

## Gatilhos
`R-SEGURANCA`: mudança em `.github/workflows/` (CI e o job da catraca, que é controle do Forge). Não toca segredo, dado pessoal nem dependência de pacote.

## Verificações
- **SHAs das ações:** as 11 ocorrências de `uses:` (`ci.yml` 8, `catraca.yml` 1, `release.yml` 2) seguem fixadas por SHA de 40 caracteres com comentário de versão. Nenhuma linha `uses:` está no diff. actionlint e zizmor continuam baixados em versão fixa e conferidos por `sha256sum -c` (`ci.yml:141-142`).
- **permissions:** intactas. Topo `contents: read` em `ci.yml:16-17` e `catraca.yml:10-11`. Escopo extra declarado no job: `ci.yml:79-81` (`checks: read`) e `catraca.yml:22-25` (`pull-requests: read`, `actions: read`). `release.yml:9-10` mantém `contents: write` no topo, só em push na main. Isso é anterior ao diff e já foi registrado no parecer anterior. Nenhum `pull_request_target` nem `secrets.` nos workflows. `persist-credentials: false` em todos os checkouts. A imagem do runner não muda o escopo do token.
- **Controles que deixaram de rodar:** nenhum. Os `if:` dos jobs `rapida`, `bateria`, `bateria-python-tres-quatorze`, `catraca` e `release` e os de cada passo da bateria (gate, changelog, release, degrau, segredos, pareceres, provas, suíte, shellcheck, e2e) não mudaram. Os `name:` dos jobs, que são os checks exigidos na proteção de branch, também não mudaram. Rótulo de runner indisponível deixa o check pendente, e ferramenta ausente na imagem (por exemplo o `shellcheck`) dá exit 127. Nos dois casos a falha é fechada: o check não fica verde.
- **catraca.yml com o python3 do sistema:** `catraca.yml:45` e `:50` rodam `tests/catraca.py` sem `setup-python`, e no 26.04 o interpretador passa de 3.12 para 3.14. Li `tests/catraca.py` atrás de falha aberta por versão. As comparações por AST (`contar_testes` :349, `forca_dos_testes` :381, `acrescimo_inerte` :525) analisam base e head com o mesmo interpretador, então a comparação continua simétrica. O 3.14 não cria `SyntaxError` novo para código válido no 3.12 (a PEP 765 dá só `SyntaxWarning`). Exceção não tratada sai com código diferente de zero e deixa a catraca vermelha (`main`, :1176-1180). Risco baixo, mas o controle passa a depender da imagem (A3).
- **Passo `env -a` (branch `melhoria/ci-env-argv0-v2`, `ea2227f`, sem merge):** `git merge-tree` com `4135cde` sai limpo, sem conflito de texto. A união junta dois passos com `sudo apt-get install rust-coreutils` (`ci.yml:56` e `:256` da árvore unida) ao runner 26.04, e nenhum parecer revisou essa combinação. O passo falha fechado (`set -euo pipefail`, confere o caminho e `env -a x true`). Não achei caminho de ataque novo. Dois pontos mudam no 26.04, porém (A1). O comentário "o GNU env 9.4 do runner recusa -a" (`:58` e `:259` da árvore unida) provavelmente fica falso: no 26.04 o coreutils padrão do Ubuntu é o uutils, o que não foi medido na imagem do GitHub. Com isso, o PATH do job inteiro já usa o uutils, não só o `env`, inclusive no `sha256sum -c` que protege o download das ferramentas de lint (A2).

## Achados
- A1 (recomendado) .github/workflows/ci.yml:46 · a união com melhoria/ci-env-argv0-v2 sai sem conflito e põe o passo env -a no 26.04 sem revisão; no 26.04 o comentário do GNU env 9.4 fica falso; revisar aquela branch rebaseada sobre esta
- A2 (recomendado) .github/workflows/ci.yml:141 · no 26.04 o sha256sum -c que confere actionlint e zizmor pode ser o do uutils; um autoteste negativo (checksum errado precisa falhar) prova a falha fechada
- A3 (recomendado) .github/workflows/catraca.yml:45 · a catraca e os passos da bateria sem setup-python rodam no python3 da imagem (3.14 no 26.04); fixar o interpretador desacopla o controle da imagem

## Detalhe dos achados
**A1.** Evidência: `ci.yml:46` e `:77` (runners dos jobs que recebem o passo). Na árvore unida, `ci.yml:56-73` e `:255-274`. O parecer `docs/security/ci-env-argv0-v2.md` daquela branch analisou o runner 24.04.
- Caminho de ataque: nenhum direto. O risco é de processo. Uma branch que toca o CI entra sobre uma base que ela não viu, e o comentário passa a afirmar algo falso sobre o controle. O próximo revisor parte de premissa errada.
- Severidade: baixa.
- Correção mínima: rebasear `melhoria/ci-env-argv0-v2` sobre `melhoria/ci-ubuntu-26`. No primeiro run em 26.04, registrar o `env --version` que o passo já imprime. Se o `env` do sistema já aceitar `-a`, retirar a instalação ou ao menos corrigir o comentário nas duas cópias. Revisão de segurança curta sobre o delta.
- Esforço: P. Dono: `devops-engineer`.

**A2.** Evidência: `ci.yml:141-142`.
- Caminho de ataque: improvável. Exigiria um asset de release do actionlint ou do zizmor adulterado e, ao mesmo tempo, um `sha256sum -c` que devolvesse 0 diante de divergência. O binário adulterado rodaria no job `bateria`, que tem `contents: read` e `checks: read`, sem segredo.
- Severidade: baixa. Não há defeito provado do uutils aqui. É troca de implementação embaixo de um controle de integridade.
- Correção mínima: antes da conferência, `echo "0000…  $ferramentas/actionlint.tgz" | sha256sum -c - && exit 1 || true`, ou seja, o passo reprova se um checksum errado passar. Outra opção é conferir com `python3 -c` e `hashlib`, com o código inline no workflow e não da branch, como pede o CI-ORDEM-LINT.
- Esforço: P. Dono: `devops-engineer`.

**A3.** Evidência: lista completa dos passos que rodam `python3` sem `setup-python` antes:
- `catraca.yml:45` (catraca).
- `catraca.yml:50` (texto do PR).
- Em `ci.yml`, quando o gate dá `pesada != 'true'`, porque `setup-python` em `:122-125` só roda com `pesada == 'true'`:
  - `:121` (testes que leem pareceres);
  - `:165` (changelog);
  - `:173` e `:175` (conferir-release);
  - `:214` (catraca `--modo pareceres`);
  - `:236` (reexecutar-provas).

Caminho de ataque: nenhum hoje (análise acima). O risco é de deriva. Uma mudança de comportamento do Python da imagem, que o GitHub atualiza sem PR, alteraria um controle do Forge sem passar por review. A suíte cobre a catraca no 3.14 do `setup-python` (`ci.yml:53-55`), não no 3.14 da imagem.
- Severidade: baixa.
- Correção mínima: em `catraca.yml`, um passo `actions/setup-python@6d4fd22b20465ccc0f7354476588e8df7c9ca0e0 # v7.1.0` com `python-version: "3.12"` antes de `:31`. Em `ci.yml`, tirar o `if:` do `setup-python` em `:123`, que custa segundos.
- Esforço: P. Dono: `devops-engineer`.

## Riscos aceitos e ferramentas
Nenhum risco aceito.
- Rodado: `python3 -I -m unittest discover -s tests -p test_ci_local.py` em `4135cde`, que contém `c481b78`: 54 testes, OK.
- Feito à mão: grep dos `uses:` sem SHA (nenhum), de `pull_request_target`/`secrets.` (nenhum) e das linhas executáveis no diff (nenhuma); leitura de `tests/catraca.py`; `git merge-tree` com `melhoria/ci-env-argv0-v2`.
- Lacunas: `actionlint` e `zizmor` não estão no PATH desta máquina. Não foram rodados aqui, e o job `bateria` do PR roda os dois. Também faltam `gitleaks` e um runner 26.04 para medir o `env`, o `sha256sum` e o `python3` da imagem. O primeiro run do PR é a prova.
