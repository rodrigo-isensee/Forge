---
tipo: revisao-devops
contrato: 1
pedido: v046
branch: melhoria/ci-lote-e1
commit: 00e6d4304a6612dc657b084cef669944b7dd9371
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-11-11
---
# Review de devops: v046 (E1.2, lote E1 do CI), volta 1

## Achados
- A1 (recomendado) .github/workflows/ci.yml:562 · O job `verificacoes` repete checkout, setup-python, setup-node e instalação do CLI (cerca de 1 a 2 min a mais de runner por execução, dentro da franquia; R-CUSTO sem recurso pago). Aceito; o tempo de parede cai porque roda em paralelo às partes.

## Detalhes
Sem bloqueante: A1 e A2 da volta anterior resolvidos. Revalidação lendo só o delta b38fe7e6..00e6d430 (ci.yml, 3 testes, mutantes, fragmento).

A1/A2 resolvidos: o job `bateria` ficou só com passos baratos (gate, lint, degrau, CLI, validate, changelog, segredo, parecer). Provas, shellcheck e e2e foram para `verificacoes` (`needs: [bateria]`), que roda em paralelo às partes. O agregador `bateria` passou a exigir `bateria`, `verificacoes`, partes e pulados em `success`; vermelho barato deixa `verificacoes` e partes skipped e o agregador (`if: always()`) reprova. O check exigido segue com o mesmo nome; `bateria (python 3.14)` não precisa de `verificacoes` (suas partes já esperam `bateria`). `pesada` é exposta como output do job e lida com `!= 'false'` nos passos longos, correto para o ci-local. Comentário sem promessa de tempo ("sem medida do vermelho ainda"), honesto.

Neutralidade só nas partes: aceito. Perde o vermelho cedo dela, mas o teste segue no gate (roda em `tests.test_forge` nas partes) e a duplicação saiu; custo de segundos e nenhuma regra afrouxada.

Segurança do pipeline: `verificacoes` com `permissions: contents: read`, `persist-credentials: false`, ações fixadas por SHA com tag, `timeout-minutes: 20`, sem `continue-on-error`, `[skip ci]` nem teste pulado, sem escrita na `main` (R-MAIN, R-VERIFY). O CLI continua antes de qualquer código da branch (CI-ORDEM-LINT). Testes ajustados (needs do agregador, job pulado em vermelho, 30 literal) e 6 mutantes em tests/mutantes/v046-ci-lote-e1.json conferem a fiação.

Ferramentas: `shellcheck` no PATH (sem script de shell alterado); `actionlint` e `zizmor` ausentes (lacuna; o lint do CI roda os dois). Testes não rodados por mim: a prova é o CI do PR.
Aviso ao tech-lead: o token do bot não tem o escopo `workflow`; o envio do ci.yml é do dono. Arquivo protegido de `.github/` pode pedir `afrouxa-regra` (não afrouxa: reordena e agrega `needs`).

## Custo e rollback
Sem recurso pago; alguns minutos de runner a mais por PR pelo setup repetido. Rollback: `git revert` dos commits do lote; o CI volta ao paralelo anterior.
