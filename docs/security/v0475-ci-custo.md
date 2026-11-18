---
tipo: revisao-seguranca
contrato: 1
pedido: v0475-ci-custo
branch: melhoria/v0475-ci-custo
commit: f59f7766bfcecbb1887cce0b6c0aff6ab31880cd
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-17
---
# Review de segurança: v0475-ci-custo

Escopo: os workflows-modelo de projeto `templates/projeto/.github/workflows/ci.yml` e `ci-docs.yml`, a substituição de `{{COMANDO_PRONTO}}` pelo `bin/forge-init` (`bin/forge-init:56`, `:67-68`, `:163`), `skills/ci-cd/SKILL.md` e `tests/test_modelo_ci.py` (pedido v0474, E3.65). Revisão estática, com o teste novo rodado localmente.

## Gatilhos
Gatilhos: CI/CD (workflow-modelo copiado para todo projeto novo).

## Achados
- A1 (recomendado) templates/projeto/.github/workflows/ci-docs.yml:72 · PR misto (código e .md) dispara os dois workflows: o "ci" leve fica verde em segundos com o mesmo nome do check exigido; se a proteção o aceitar antes do agregador do ci.yml existir, há janela de merge (ou auto-merge) sem a suíte. Não provado aqui.
- A2 (recomendado) templates/projeto/.github/workflows/ci.yml:21 · O grupo usa o nome da branch de cabeça: PR de fork com branch homônima (develop, main ou a de outro PR) entra no mesmo grupo e, com cancel-in-progress, cancela a rodada alheia. Indisponibilidade do CI, sem ganho de escrita.

## Sondas

## Detalhe dos achados
Conferido e sem achado:
- **Permissões:** `contents: read` no topo e no job `suite` (`ci.yml:17-18`, `:29-30`); `permissions: {}` no agregador (`ci.yml:47`) e no `ci-docs.yml:65`. Nenhum segredo referenciado.
- **Ações fixadas:** a única ação, `actions/checkout`, está fixada por SHA (`ci.yml:32`); conferido por `git ls-remote` que `11d5960a…7262` é a tag `v4.4.0`, o mesmo SHA dos workflows do Forge. `persist-credentials: false` (`ci.yml:34`). O Dependabot do modelo cobre `github-actions` (`templates/projeto/.github/dependabot.yml:15`).
- **Gatilhos:** só `pull_request` e `push` nas branches do fluxo; sem `pull_request_target`, `workflow_run` nem `issue_comment` (o teste `Higiene` barra o primeiro). PR de fork roda com token só de leitura e sem segredo.
- **Injeção por `${{ }}`:** nenhum `${{ }}` em `run:`. `github.head_ref` só aparece em `concurrency.group` (não é shell); `needs.suite.result` entra por `env:` e é lido como `"$RESULTADO"` (`ci.yml:50-52`).
- **`{{COMANDO_PRONTO}}`:** o valor vem da stack (`Comando sugerido:` em `stacks/<stack>/pronto.md`) ou do `--pronto` de quem roda o `forge-init`, ambos do operador; nenhum dado de evento do GitHub entra nele. O `escapar` (`bin/forge-init:67`) trata `/`, `&` e `|` do `sed`. Sem comando na stack, o valor é `a definir` e a suíte falha (fecha). Um `${{ }}` digitado pelo próprio operador no `--pronto` seria avaliado pelo Actions, mas sem caminho de ataque externo: informativo.
- **Agregador:** `if: always()` com `needs: [suite]` e `test "$RESULTADO" = "success"` falha em `failure`, `cancelled` e `skipped`; sem `continue-on-error`.

**A1** (média se confirmado; recomendado por não ter prova). Evidência: `ci-docs.yml:60` usa `paths:`, que dispara se *algum* arquivo casar; `ci.yml:12` usa `paths-ignore:`, que só pula se *todos* casarem. Num PR que muda código e um `.md`, os dois rodam e há dois check runs `ci` no mesmo commit; o leve termina em segundos (`ci-docs.yml:72-78`). Caminho: um autor (ou agente) junta um `.md` à mudança de código; se a proteção de branch avaliar o `ci` verde do leve antes de o agregador do `ci.yml` ser criado (ele espera a suíte, `ci.yml:44`), o botão de merge ou o auto-merge libera a suíte ainda não concluída. Não verifiquei o comportamento da proteção com check runs homônimos de workflows diferentes (exige repositório no GitHub). Correção mínima (dono: `devops-engineer`, esforço P): um workflow só, sem filtro de caminho no gatilho; um job inicial detecta se a mudança é só de documento (diff contra a base, sem ação de terceiro), a `suite` roda com `if:` quando não for, e o agregador aceita `skipped` só quando o detector disse "só documento". Alternativa: provar num repositório de teste que a proteção bloqueia o PR misto com a suíte vermelha e com a suíte em andamento, e registrar a prova na skill.

**A2** (baixa). Evidência: `ci.yml:21` e `ci-docs.yml:68`, `group: ...-${{ github.head_ref || github.ref_name }}` com `cancel-in-progress: true`. Caminho: em repositório público (ou privado com fork liberado), alguém abre PR de um fork com branch `develop`, `main` ou de mesmo nome que a de um PR aberto e faz push repetido: cada push cancela a rodada da vítima, cujo agregador fica vermelho por `cancelled`. Sem ganho de escrita; o PR da vítima só não fica verde até o atacante parar. Também, sem ataque, o push na `develop` e o PR `develop`→`homolog` caem no mesmo grupo e um cancela o outro. Correção mínima (dono: `devops-engineer`, esforço P): para PR, chavear pelo número (`github.event.pull_request.number`), e para push, por `github.ref`; o push só roda nas branches do fluxo, então o ganho de juntar push e PR da mesma branch de trabalho não existe neste modelo. Ajustar `tests/test_modelo_ci.py` (classe `Concorrencia`) e o item da skill (`skills/ci-cd/SKILL.md`, seção "CI de projeto privado: minutos").

## Riscos aceitos e ferramentas
Nenhum risco aceito. Teste rodado: `python3 -m unittest tests.test_modelo_ci`, 13 testes, OK. A suíte inteira fica com o CI do PR. Ferramentas ausentes no PATH (lacuna, nada instalado): `zizmor`, `actionlint`, `gitleaks`.
