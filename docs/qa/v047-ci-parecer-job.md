---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-ci-parecer-job
commit: 7ba85a056b4eb332362ce5cda7b6efb193b6b017
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-12
---
# QA: v047 E1.4 (job de pareceres separado no CI)

Head testado: 7ba85a05 (diff contra a base a986c292: ci.yml, devops-engineer.md, pronto.md de node-react e python, test_ci_local.py, test_catraca.py, fragmento de changelog). Sem PR aberto: sem check-run `bateria` para citar; rodei só os testes afetados e a mutação à mão.

## Achados
- A1 (bloqueante) .github/workflows/ci.yml:674 · A guarda do agregador (pareceres success; skipped só fora de PR) e o `if:` do job (:550) não têm teste de comportamento. Mutante M7 (tirar a checagem de PARECERES do agregador) e M5 (tirar o `if:`) sobrevivem com 17 testes verdes: o requisito "parecer faltando reprova o merge" não está guardado.
- A2 (recomendado) .github/workflows/ci.yml:674 · M4 (aceitar skipped também em PR) sobrevive. Hoje o job não tem `needs`, então não pula em PR; é defesa em profundidade, e um teste da tabela-verdade da linha fecharia M4, M5 e M7 de uma vez.

## Critério → teste → resultado
Sem `docs/ux`: a obrigação vem de E1.4 (CI-PARECER-NAO-BARRA-SUITE) em docs/pedidos/v047.md.

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1.4: job próprio `bateria (pareceres)` fora do job de passos | test_ci_local `test_pareceres_e_job_proprio_obrigatorio_e_fora_do_caminho_da_suite` | passo `--modo pareceres` só no job novo | passou; M3 morreu |
| E1.4: obrigatório para o merge (no agregador) | mesmo teste e `MatrizNeedsEAgregadorTest` | `needs` do agregador | passou; M1 morreu; a condição da linha 674 não é guardada (M7 sobreviveu) |
| E1.4: não barra a suíte (fora de `needs` das partes e das verificações) | mesmo teste, laço sobre os jobs | `needs` dos demais jobs | passou; M2 e M6 morreram |
| Teto de tempo do job (10 min) | `test_catraca.Workflows` (lista de timeouts) | timeout | passou |
| Regra para os projetos (devops-engineer.md, pronto.md) | sem teste novo (texto de doc) | n/a | conferido no diff |

## Cenários e resultado real
- `python3 -m unittest tests.test_ci_local` : 66 testes, OK. `tests.test_catraca.Workflows`: 6, OK.
- Vermelho antes do verde (à mão; o `forge-testes --vermelho a986c292` não devolveu saída em tempo útil, então não vale como prova): o teste novo contra o `ci.yml` da base cai com `KeyError: 'pareceres'`.
- Tabela-verdade da linha do agregador, extraída do `ci.yml` do head (demais jobs success): PR+success rc=0; PR+failure 1; PR+skipped 1; PR+cancelled 1; push+skipped 0; push+failure 1; push+cancelled 1; pareceres ok com verificações failure 1. O comportamento está correto; só falta teste que o prenda.
- Mutação à mão em cópia (testes: o novo, `MatrizNeedsEAgregadorTest`, `Workflows`): M1 agregador sem pareceres, morto (3 falhas); M2 verificações com needs pareceres, morto; M3 passo sem `--modo pareceres`, morto; M6 partes com needs pareceres, morto; M4, M5 e M7 sobreviveram (A1, A2).
- Workflow real (job `pareceres` em PR, permissões, `fetch-depth: 0`, script da base): não executável aqui; a prova é o CI do PR, ainda inexistente.
- Para fechar A1: teste que avalie a linha do agregador nos casos acima (agente de CI/dev da stack, `devops-engineer`) e uma afirmação do `if:` do job.
