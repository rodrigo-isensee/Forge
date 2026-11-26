---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-ci-parecer-nao-cancela
commit: 7bf55772445e422b84ac551433ddf1f60e86a9bc
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-26
---
# Review de segurança: v0481 (E22.12, PR #913, volta 2 por delta)

Delta lido: `forge-check parecer delta` de 8e9f5704..7bf55772, sem o que veio da develop. No domínio só `.github/workflows/obsoletas.yml`. Fora do domínio, lidos só como prova: `tests/test_ci_nao_cancela_parecer.py` e `tests/mutantes/v0481-ci-parecer-nao-cancela.json`. A rodada anterior está no git (parecer em 8e9f5704).

Gatilhos: workflow de CI (`actions: write` em workflow disparado por `pull_request`), entradas do evento, checks exigidos.

## Achados
- A1 (bloqueante) tests/test_falhas_no_resumo.py:241 · resolvido na volta 1, segue intacto
- A2 (bloqueante) tests/test_catraca.py:4238 · resolvido na volta 1, segue intacto
- A3 (bloqueante) scripts/ci-local:274 · resolvido na volta 1, segue intacto
- A4 (bloqueante) .github/workflows/obsoletas.yml:53 · resolvido: só cai run com head_sha diferente de HEAD_SHA, origem igual a REPO e id menor que RUN_ID; no run real o CI do head (45861169646) não foi cancelado

## Detalhe
**A4.** O `--jq` emite `.head_sha` (`obsoletas.yml:50`) e a condição pede as três coisas (`obsoletas.yml:53`), que é a correção mínima pedida. Prova no run real: o Obsoletas 45861169690 (RUN_ID maior que o do CI) rodou com HEAD_SHA 7bf55772 e não cancelou nada. O CI 45861169646 do mesmo head terminou com as dez partes da suíte verdes. O teste novo (`test_nunca_cancela_o_ci_do_proprio_head_mesmo_com_id_menor_que_o_run_id`) põe no gh falso os runs 4 e 8 com o head atual e id menor que o RUN_ID, e nenhum dos dois cai. O mutante M15 inverte a condição do sha e morreu. Os casos limite falham fechados: `head_sha` nulo vira `null` e passa a ser candidato, mas só se a origem for o próprio repositório e o id for menor. O HEAD_SHA chega só por `env:` e entre aspas, sem interpolar no script.

**CI do head.** O vermelho que sobra não vem do delta. `bateria (pareceres)` falha porque espera os pareceres aprovados da classe (R-REVIEW, R-QA), e este é um deles. `catraca` falha porque a mudança em `ci.yml` e em `obsoletas.yml` pede o rótulo `afrouxa-regra`, que é decisão do usuário (R-CONFORMIDADE, R-DECISAO).

### Aperta, neutro, afrouxa
- **Aperta:** o cancelamento fica estritamente menor. Só cai run de outro commit, então o CI do head que acabou de chegar nunca é cancelado pelo próprio envio. A disponibilidade da suíte volta a valer, o que era o objetivo do E22.
- **Neutro:** permissões (`actions: write` só no job do Obsoletas e `contents: read` no topo), o filtro de origem, a condição de id (o Obsoletas atrasado de um envio antigo não derruba o CI de um envio novo), a saída cedo em envio só de parecer, as entradas do evento por `env:`, os checks exigidos e os agregadores.
- **Afrouxa:** nada neste delta. Segue o que a volta 1 registrou: existe um segundo workflow disparado por `pull_request` com escrita em `actions`, restrito a PR do próprio repositório e sem checkout. O efeito residual é só de disponibilidade: se o mesmo sha voltar ao ramo depois de outro envio, o run antigo desse sha não é cancelado e roda até o fim, sem contornar portão. O rótulo `afrouxa-regra` é do usuário.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Usados: o diff do delta; `python3 -m unittest tests.test_ci_nao_cancela_parecer tests.test_falhas_no_resumo.Fiacao tests.test_catraca.Workflows` (16 testes, OK); `bin/forge-mutante tests/mutantes/v0481-ci-parecer-nao-cancela.json` (M1 a M15 morreram); a API de runs do head 7bf55772 e os logs dos runs 45861169690 e 45861169646. Não estavam no ambiente: `zizmor`, `actionlint` e `gitleaks`. É lacuna; o diff foi lido à mão e não tem segredo.
