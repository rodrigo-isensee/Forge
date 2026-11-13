---
tipo: revisao-seguranca
contrato: 1
pedido: v047-ci-parecer-job
branch: melhoria/v047-ci-parecer-job
commit: 7ba85a056b4eb332362ce5cda7b6efb193b6b017
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-12
---
# Review de segurança: v047-ci-parecer-job

Pedido v047, etapa E1.12: parecer de segurança da E1.4 (CI-PARECER-NAO-BARRA-SUITE, job `bateria (pareceres)` no `ci.yml`) no head `7ba85a05`, contra os controles J1 a J11 do modelo de ameaças `docs/security/v047-e1-ameacas.md` (E1.5). Diff lido: `a986c292..7ba85a05` (7 arquivos). Os commits posteriores da branch (`cdfbbd0d`, `e0cc4431`, `3a1a30ff`) só trazem os pareceres de devops e de review.

## Gatilhos
`R-SEGURANCA`: mudança em `.github/workflows/` (portão de pareceres no servidor, check exigido `bateria`) e em texto de agente que ensina o pipeline aos projetos (`agents/devops-engineer.md`, `pronto.md` das stacks).

## Achados
- A1 (bloqueante) tests/test_suite_partes.py:300 · O teste da fiação do agregador ficou com os `needs` antigos (sem `pareceres`) e falha no head (S1): a suíte fica vermelha e a guarda que conta um `= success ]` por job exigido, a que mata o afrouxamento do J2 (S3), não cobre o job novo.
- A2 (bloqueante) .github/workflows/ci.yml:674 · J2/J3 e W3 a W5: a condição do agregador para `pareceres` não está presa por teste. Trocar por `skipped` aceito em qualquer evento (S2) deixa verdes os testes da branch e o de fiação já corrigido. Mesma correção do A1 do code review.
- A3 (bloqueante) agents/devops-engineer.md:12 · J11: o texto (e o do `pronto.md` das duas stacks, :55 e :30) diz que o job é obrigatório e fora do `needs` da suíte, mas não diz que pulado ou cancelado em PR reprova; o projeto copia o agregador `!contains(failure)` e o portão some.
- A4 (recomendado) tests/test_ci_local.py:301 · J3/J5/W6/W7: o teste novo não confere `--modo pareceres` em exatamente um job (só que saiu do de passos) nem as permissões do job; `pull-requests: write` a mais no job passa (S4).
- A5 (recomendado) .github/workflows/ci.yml:552 · J9 pedia `timeout-minutes` 5; ficou 10. Sem custo novo (mesmo runner, ação já fixada pelo mesmo SHA), só teto maior.

## Sondas
- S1 · `python3 -m unittest tests.test_suite_partes.FiacaoDoCI.test_agregadores_tem_o_nome_exigido_e_exigem_todas_as_partes` no head 7ba85a05 · espera: OK · obtido: FAILED, `Items in the first set but not the second: 'pareceres'`
- S2 · ci.yml:674 com `[ "$PARECERES" = skipped ]` no lugar de `{ ... && [ "$EVENTO" != pull_request ]; }`, depois `unittest tests.test_ci_local tests.test_catraca.Workflows` · espera: FAILED · obtido: OK (72 testes)
- S3 · ci.yml:674 com `[ "$PARECERES" != failure ]` no lugar da condição, os mesmos testes · espera: FAILED · obtido: OK (72 testes)
- S4 · job `pareceres` com `pull-requests: write` em `permissions`, os mesmos testes · espera: FAILED · obtido: OK (72 testes)

## Detalhe dos achados

### Controles J1 a J11 no head 7ba85a05
| Controle | Situação | Evidência |
|---|---|---|
| J1 check exigido | ok | agregador `name: bateria` com `pareceres` em `needs` (ci.yml:658); nenhuma mudança de ruleset |
| J2 pulado não é verde | ok no código, sem teste (A2) | ci.yml:674; tabela-verdade executada: success/PR rc 0; failure, skipped, cancelled e vazio em PR rc 1; skipped em push e `workflow_dispatch` rc 0; cancelled em push rc 1. Job sem `needs` e sem o gate `pesada` (:550): roda em todo commit do PR, inclusive só de parecer |
| J3 passo único, fora do caminho da suíte | ok no código; teste parcial (A1, A4) | `--modo pareceres` só em ci.yml:579; nenhum outro job tem `pareceres` em `needs` |
| J4 script da base | ok | ci.yml:572-579, mesmo padrão `HEAD^1` + worktree da base; mutante que usa o script do PR é morto pelos testes |
| J5 permissões e credenciais | ok (melhorou) | `permissions: contents: read` só (:553-554), sem `GH_TOKEN` nem `secrets`; o modo `pareceres` não chama a API (`tests/catraca.py`:1714-1716); checkout pelo mesmo SHA, `persist-credentials: false`, `fetch-depth: 0` (:556-559). Antes o passo herdava `checks: read` do job de passos |
| J6 injeção de expressão | ok | `HEAD_REF`, `PR_AUTOR`, `HEAD_REPO`, `BASE_REPO`, `BASE_REF` só por `env:`; `--ramo="$HEAD_REF"` entre aspas; nada de `${{ }}` no `run:` (:572-579) |
| J7 gatilho | ok | `on:` sem mudança (`pull_request`, `push`, `workflow_dispatch`); job condicionado a `pull_request` |
| J8 cancelamento | ok | agregador `always()` e só `success` em PR; `cancelled` reprova também fora de PR |
| J9 custo | ok, com A5 | `ubuntu-26.04`, sem setup de outra linguagem, sem CLI, sem ação nova (a de setup é a mesma, mesmo SHA); timeout 10 |
| J10 agregador 3.14 | registrado | o portão vale pelo `bateria`; nada a mudar |
| J11 regra nos projetos | falta uma das três condições (A3) | agents/devops-engineer.md:12 e `pronto.md` das duas stacks |

### A1 (bloqueante, defeito provado)
Evidência: `tests/test_suite_partes.py`:300-313 espera `needs` do agregador igual a `{bateria, verificacoes, partes-doze, pulados-doze}` e falha no head (S1). Caminho: a suíte do PR fica vermelha; e, enquanto o conjunto não tiver `pareceres`, o laço de :311 e a contagem de :313 (um `= success ]` por job exigido) não protegem o job novo. Com `pareceres` no conjunto, a contagem passa a matar S3 e a remoção da condição. Severidade: média (é a guarda do portão). Correção mínima: acrescentar `"pareceres"` ao conjunto do caso `agregador`. Esforço P. Dono: `devops-engineer`.

### A2 (bloqueante, controle J2/J3 exigido pelo modelo com teste)
Evidência: ci.yml:674; o teste novo (`tests/test_ci_local.py`:301-312) só confere que `PARECERES: ${{ needs.pareceres.result }}` existe. Caminho de ataque: uma edição futura do `ci.yml` (do agente, num PR que o próprio portão julga) troca a condição por `skipped` aceito em qualquer evento; um `if:` ou `needs` posto no job o pula em PR, e o merge sai sem parecer. Mesmo com o A1 corrigido, S2 sobrevive (a contagem de `= success ]` não muda). Severidade: média. Correção mínima: teste que extraia o `run:` do agregador e o execute (como a tabela acima) com `PARECERES` em success, failure, skipped e cancelled e `EVENTO` em `pull_request` e `push`, exigindo rc 0 só em success/PR e skipped fora de PR (casos W3, W4, W5); e que o job `pareceres` não tenha `needs` nem `if:` além de `github.event_name == 'pull_request'`. Esforço P. Dono: `devops-engineer` (com o `qa-engineer`).

### A3 (bloqueante, controle J11)
Evidência: agents/devops-engineer.md:12; `stacks/*/pronto.md` (node-react :55, python :30), na seção CI. O controle J11 pede as três condições: (1) o job entra no check exigido, direto ou pelo agregador; (2) pulado ou cancelado em PR reprova; (3) a suíte não espera por ele. O texto traz (1) e (3). Caminho de ataque: o `devops-engineer` de um projeto monta o agregador com o padrão comum `if: always()` + "nenhum `needs` em failure", que conta `skipped` e `cancelled` como verde; o job de pareceres com qualquer `if:` (filtro de caminho, gate) fica pulado e o PR mescla sem parecer. Severidade: média. Correção mínima: nos três textos, acrescentar que o agregador exige `success` desse job em PR (pulado ou cancelado reprova). Esforço P. Dono: `devops-engineer`.

### A4 (recomendado)
J3 pede "em exatamente um job" e W7 pede as permissões, o `persist-credentials: false` e o `uses:` por SHA do job conferidos por teste. Hoje `--modo pareceres` posto também em outro job que não o de passos passa, e S4 sobrevive. Sem caminho de ataque hoje (o token não chega aos passos sem `env:` explícito, e a CI varre com o linter de workflow e o auditor de ações). Dono: `devops-engineer`.

### A5 (recomendado)
ci.yml:552 `timeout-minutes: 10`; o J9 sugeria 5. Medida de custo, não de segurança: ajuste se o tempo medido do job ficar perto de 1 min. Dono: `devops-engineer`.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática do diff, tabela-verdade do `run:` do agregador executada localmente, sondas de mutação no `ci.yml` (revertidas) contra `tests.test_ci_local`, `tests.test_catraca.Workflows` e `tests.test_suite_partes`. Lacunas: o linter de workflow e o auditor de ações não estão no PATH desta máquina; rodam no job de passos do CI, que precisa passar (J6). Sem PR aberto, sem CI a citar: rodei só os testes afetados.
