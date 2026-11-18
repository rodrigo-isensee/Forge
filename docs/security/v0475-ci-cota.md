---
tipo: revisao-seguranca
contrato: 1
pedido: v0474
branch: melhoria/v0475-ci-cota
commit: 322798df5b7bd991ddf6a955c00a92363e13e1b3
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-18
---
# Review de segurança: v0475-ci-cota (E3.171, revalidação por delta)

Gatilhos: credencial de integração externa (token do `gh`), custo (R-CUSTO), comando sugerido ao dono.

## Resumo
Revalidação por delta 19e7b93f..322798df (`forge-check parecer delta`: nenhum arquivo do domínio mudou; fora do domínio só tests/test_cota_ci.py). A ferramenta segue só leitura (bin/forge-cota-ci:36), sem mudança desde o parecer anterior. A4 corrigido. Aprovado.

## Achados

## Sondas

## Revalidação
Delta lido: tests/test_cota_ci.py (+`from ambiente_git import sem_manutencao`, :11; `env=sem_manutencao()` em `git init` e `git remote add`, :39 e :41). Já lido antes: o resto do diff 2fa505d7..19e7b93f.

- A1, A2, A3 (recomendados): corrigidos na rodada anterior; nada no delta os toca.
- A4 (recomendado) corrigido: o teste roda git pelo ponto único (tests/test_cota_ci.py:39, :41); `tests.test_ambiente_git` passa.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Rodado: `python3 -I tests/catraca.py --base origin/develop`, `python3 -m unittest tests.test_cota_ci tests.test_ambiente_git`. Suíte inteira: fica para o CI do PR (R-REVIEW). Ferramentas ausentes do PATH: gitleaks, zizmor, actionlint, semgrep (lacuna; nenhum workflow mudou).
