---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-espera-amarela
commit: d38537ee5176cd9cc587a6158fc6662e99dd6bb5
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-27
---
# Review de segurança: v0481 (espera amarela, #948, volta 2, E47.15)

- ci: d38537ee5176cd9cc587a6158fc6662e99dd6bb5 verde nas 5 partes da suíte, verificações longas, passos, teto de pulados, instalação, `bateria (python 3.14)` e árvore já provada; vermelhos por construção `bateria (pareceres)` (pareceres desatualizados pelo próprio delta e o QA reprovado da rodada que este delta responde), `bateria`, `catraca` e `catraca (conferência)` (log: só `R-CONFORMIDADE: mudança em` `.github/workflows/catraca.yml`, `.github/workflows/ci.yml` e `tests/catraca.py`, liberável pelo rótulo do dono)

Gatilhos: workflow de CI (nome do check exigido, guarda do verde velho), controle de conformidade (`tests/catraca.py`, rc da catraca), regra afrouxada com `[afrouxa-regra` no título.

Aprovado. Revalidação por delta (`forge-check parecer delta`, 054d4103..d38537ee; no domínio só `tests/test_catraca.py`; fora: `tests/test_ci_local.py`, `tests/mutantes/v0481-espera-amarela-5.json` e pareceres). Nenhuma linha de produção mudou: `git diff --name-only 054d4103..d38537ee` fora de `docs/` e `tests/` é vazio, então `tests/catraca.py`, `scripts/ci-local` e os workflows seguem os aprovados na volta 1. O delta só acrescenta testes que fecham o ramo de falha:
- `tests/test_catraca.py:4677-4710`: parecer reprovado sem arquivo sensível e QA reprovado com review e segurança aprovados (o ramo do `cmd_pr` sem achado, M27) saem 1, sem a marca `catraca: espera`; só parecer de outra branch sai `ESPERA` (ausência, não defeito); `LINHA_DE_ESPERA` não casa os vizinhos `branchx`, espaço duplo e `conferido`. Reforça o A2 da rodada 1: a espera não se forja por texto parecido.
- `tests/test_ci_local.py:1174-1176` (lido por pedido do brief, fora do domínio): rc 1 do script com a API respondendo `nenhum` ou `failure` segue rc 1 e sem `espera=` no `GITHUB_OUTPUT`: defeito não vira espera mesmo quando o estado do check permitiria o amarelo. Os auxiliares `job` e `agregador` trocam o desempacotamento por asserção explícita, sem afrouxar o que é conferido.

## Estado dos achados anteriores
- A1 a A4 da rodada 1 seguem fechados (o código não mudou). O cartão `sha_rotulado_do_mesclado` (`tests/catraca.py:1836-1857`, `tech-lead`, baixa) segue aberto, fora do delta.

## Sondas no d38537ee
- Rodados: `test_catraca.EsperaNaoEVermelho` e `test_ci_local.EsperaAmarelaNosWorkflows`, 19 testes OK. A suíte inteira vale pelo CI acima.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do delta, os testes novos, `gh` de leitura dos check runs e do log. Ausentes na estação, sem instalar (lacuna, `R-CUSTO`): `gitleaks`, `actionlint`, `zizmor`, `semgrep`.
