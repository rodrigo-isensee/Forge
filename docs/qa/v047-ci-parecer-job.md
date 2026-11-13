---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-ci-parecer-job
commit: bd28180e9129015578029dee765abd206960bac1
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-12
---
# QA: v047 E1.4 (job de pareceres separado no CI)

## Revalidação por delta (E1.20): head bd28180e, volta E1.18 (de 7ba85a05)
Veredito: APROVADO. A1 fechado, A2 fechado. Sem PR aberto: sem check-run `bateria` para citar; rodei os testes afetados e a mutação.
- Delta (`forge-check parecer delta`): ci.yml (timeout do job de pareceres 10 para 5, J9), devops-engineer.md, pronto.md de node-react e python, changelog, tests/mutantes/v047-ci-parecer-job.json, test_catraca, test_ci_local, test_suite_partes.
- Testes afetados: `unittest tests.test_ci_local tests.test_catraca.Workflows tests.test_suite_partes.FiacaoDoCI`: 82 testes, OK.
- Vermelho antes do verde (à mão; `forge-testes --vermelho` passou de 3 min e foi interrompido por carga, sem veredito): com o `ci.yml` da base a986c292 no lugar, os 3 testes novos do agregador e do `if:` caem (8 falhas e 1 erro, `KeyError` do job novo); com o do head, passam.
- Mutação: `bin/forge-mutante tests/mutantes/v047-ci-parecer-job.json`: M1, M2, M3, M4 (ci.yml:674, agregador), M5 (:550, `if:`) e M6 (:552, timeout) todos `morreu`, saída 0. Linhas de guarda mudadas no ci.yml do delta: :552 (M6); as de :550 e :674 já eram do head anterior e agora têm mutante (eram M4, M5, M7 sobreviventes).
- Agregador testado por execução real do `run:` em bash (sucesso e falha, PR e fora de PR): o comportamento deixou de ser só afirmado.
- Texto de doc (devops-engineer.md, pronto.md): conferido no diff, coerente com o ci.yml.
- Não executável aqui: o job em PR real (permissões, `fetch-depth: 0`); a prova é o CI do PR.


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
