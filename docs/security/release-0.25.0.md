---
tipo: revisao-seguranca
contrato: 1
pedido: release-0.25.0
branch: melhoria/release-0.25.0
commit: 630d200aff68570aa1a184be41b645ecb8d60ab8
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-20
---
# Review de segurança: release-0.25.0

## Gatilhos
Controles do Forge (`R-SEGURANCA`): `.github/workflows/ci.yml` e `scripts/conferir-release.py` (DV-4, 37212eb, mesclada no #229 sem pareceres, decisão do dono "B"); na leva, `.githooks/pre-push` (SUITE-CONCORRENTE), `hooks/conformidade.json` (FC-AQ-HOOK), `bin/forge-fechar` (FECHAR-ROTULO) e `bin/forge-check` (FC-PEDIDO-FORA, DV-5). O commit 630d200 só muda versão e changelog.

## Achados

## Detalhe dos achados
Veredito: aprovado. Nenhum bloqueante na DV-4 nem aberto na leva.

**DV-4: nada do PR roda com permissão elevada.** O workflow dispara só em `pull_request`, `push` e `workflow_dispatch`, sem `pull_request_target` (.github/workflows/ci.yml:7-11). O job `bateria` tem `contents: read` e `checks: read` (.github/workflows/ci.yml:42-44), e o checkout usa `persist-credentials: false` (.github/workflows/ci.yml:51-54). O passo de release (.github/workflows/ci.yml:132-142) não recebe segredo nem token: o `GH_TOKEN` só existe no `env` do passo do gate. O script vem do checkout do PR, como antes vinha o código inline do mesmo passo, então o nível de confiança é o mesmo. O passo também não depende do gate, que pula os passos pesados, e por isso roda em todo PR para a main ou a homolog.

**DV-4: sem injeção por título, branch ou versão.** `github.event.pull_request.base.sha` e `github.base_ref` entram por `env` e são usados entre aspas (.github/workflows/ci.yml:134-141); nenhuma expressão `${{ }}` é interpolada no `run`, e título e `head_ref` não entram no passo. No script, os dois `subprocess.run` recebem lista, sem shell (scripts/conferir-release.py:19, :42). A versão só vai ao `re.escape` e às mensagens (scripts/conferir-release.py:37). Versão fora de `X.Y.Z` levanta exceção e sai com rc diferente de 0, ou seja, falha fechada (sonda abaixo). O `--base` vem do SHA do evento e nunca começa com `-`; um valor forjado à mão só leva a base para 0.0.0, que é o lado restritivo.

**DV-4: a checagem da main não ficou mais fraca.** O ramo `else` chama o script sem `--so-se-versao-mudou` (.github/workflows/ci.yml:140-141), e a lógica é a mesma do código inline removido: base ilegível vale 0.0.0, `a <= b` reprova (scripts/conferir-release.py:34), a entrada `## [versão]` é exigida, `[Não publicado]` tem de estar vazia, e o `bin/forge-changelog conferir-release` roda com o rc propagado (scripts/conferir-release.py:42-44). Sondas num repositório descartável em `$TMPDIR` com o script copiado (main, depois homolog): versão igual dá rc 1 e 0 (promoção sem release, como pretendido); versão menor dá 1 e 1; `0.26.0-rc` dá 1 e 1; versão nova com changelog dá 0 e 0. A afrouxada na homolog (só confere quando a versão muda, scripts/conferir-release.py:30) é o próprio escopo da DV-4 e nada tira da main. `python3 -m unittest tests.test_conferir_release`: 10 testes OK. Entre 37212eb e 630d200, o passo, o script e o teste não mudaram.

**R1 (recomendado, baixa) tests/catraca.py:37 · a regra da release saiu de um caminho protegido.** Antes, a comparação de versão e de changelog ficava inline em `.github/workflows/ci.yml`, que está em `PROTEGIDOS`, e mudar esse arquivo exige o rótulo do dono (`R-CONFORMIDADE`). Agora ela mora em `scripts/conferir-release.py`, que está só em `SENSIVEIS` (tests/catraca.py:39) e pede parecer de review, não o rótulo. Caminho: um PR futuro na develop (um agente enganado, ou uma injeção vinda de um projeto) afrouxa o script, passa pelo review e chega à main sem o rótulo do dono. O impacto se limita à disciplina de versão, e o dono continua mesclando a main à mão. A fábrica já aceita esse padrão: `bin/forge-changelog conferir-release` e `scripts/verificar-contribuicao.sh` também são chamados pelo CI e estão fora de `PROTEGIDOS`. Por isso fica como recomendação. Correção mínima: incluir `scripts/conferir-release.py` em `PROTEGIDOS`, com teste. Essa mudança aperta um controle, mas mexe na catraca, que pede o rótulo. Esforço P. Dono: tech-lead. Ainda não há cartão: cabe ao Jarvis registrar um, por exemplo CONFERIR-RELEASE-PROTEGIDO.

**R2 (informativa) .github/workflows/ci.yml:134 · base do evento, não a ponta atual.** O passo usa `pull_request.base.sha`, enquanto os passos seguintes usam `HEAD^1`. O código inline anterior fazia o mesmo, então isso não piorou. Se a base andar com a versão já subida, a homolog ainda confere (versões diferentes), o que fica do lado restritivo. Nada a fazer agora.

**Leva: nenhum bloqueante aberto.** Os pareceres docs/security/fc-aq-hook.md, docs/security/fechar-rotulo.md, docs/security/suite-concorrente.md, docs/security/fc-pedido-fora.md e docs/security/dv-5.md estão `aprovado`, com o bloco `## Achados` vazio. As recomendações pendentes e os cartões:
- SUITE-CONCORRENTE R1 (modo da subpasta `forge-<uid>`, .githooks/pre-push:30): o cartão TRAVA-MODO-SUBPASTA aparece no Histórico do pedido e no QA, mas **não está no KANBAN.md**. R2 e R3 são informativas.
- FC-PEDIDO-FORA R1 (linha `origem:` sem `sem_controle`): cartão FC-SAIDA-SANITIZADA, que está no KANBAN.
- DV-5 R1 (ref `origin/develop` lida pelo nome curto): cartão REF-REMOTA-EXPLICITA, no KANBAN. A R2 (`git fetch` antes, na frase de `R-FLUXO`) **não tem cartão**. R3 e R4 são informativas.
- FECHAR-ROTULO R2 (item marcado dentro de citação): cabe no MODELO-PR-ROTULO, no KANBAN. A R1 (referência errada a `R-CONFORMIDADE` em docs/fechamento-integrador.md:17) **não tem cartão**.
- FC-AQ-HOOK, recomendação informativa (pôr no teste maiúsculas, o clone como link e `.git/` aninhado): **sem cartão**.

Nenhuma dessas recomendações tem caminho de ataque que justifique bloquear. As que faltam no KANBAN (TRAVA-MODO-SUBPASTA, DV5-R2-FETCH, FECHAR-R1-DOC, FC-AQ-HOOK-TESTES e a R1 desta revisão) são lacuna de registro, e o Jarvis as registra.

**Sem rede paga (`R-CUSTO`).** O diff da DV-4 não traz rede nem segredo novo (`grep` por `urllib`, `requests`, `curl`, `socket`, `http` e `secrets.` no script e no passo: nada). O diff de `origin/homolog` (50b1353) até 630d200 em `bin/`, `hooks/`, `scripts/`, `.githooks/` e `.github/` também não acrescenta chamada de rede.

## Riscos aceitos e ferramentas
Nenhum risco aceito. A entrada da DV-4 sem pareceres é decisão do dono "B", e este parecer é a revisão a posteriori. Ferramentas: leitura estática, `git diff` e `git show`, a suíte `tests.test_conferir_release` e sondas num repositório descartável em `$TMPDIR`, sem trocar o HEAD da worktree. Lacunas: `actionlint`, `zizmor`, `gitleaks` e `shellcheck` não estão no PATH local. `actionlint` e `zizmor` rodam no CI (.github/workflows/ci.yml, passos da bateria).
