---
tipo: revisao-seguranca
contrato: 1
pedido: v0474
branch: melhoria/v0475-ci-cota
commit: 19e7b93fe4b59d2883128e17482ce3e1829955f4
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-17
---
# Review de segurança: v0475-ci-cota (E3.156, revalidação por delta)

Gatilhos: credencial de integração externa (token do `gh`), custo (R-CUSTO), comando sugerido ao dono.

## Resumo
Revalidação por delta e0ac8508..19e7b93f (`forge-check parecer delta`). A ferramenta continua só leitura: `gh api <endpoint>` em lista de argumentos, sem método nem campo (bin/forge-cota-ci:36). Os três achados recomendados da rodada anterior foram corrigidos. Um achado novo fora do domínio de segurança (A4, teste), levado ao tech-lead e ao QA. Aprovado.

## Achados
- A4 (recomendado) tests/test_cota_ci.py:38 · `git init` e `git remote add` sem `env=ambiente_git.sem_manutencao()`: `tests.test_ambiente_git` falha (linhas 38 e 40) e o CI do PR fica vermelho; passar o env do ponto único. Fora do domínio de segurança, dono qa-engineer.

## Sondas

## Revalidação
Delta lido: bin/forge-cota-ci (validação do login, motivos juntos, nova mensagem ao dono), skills/ci-cd/SKILL.md e skills/esperar-estado/SKILL.md (texto encurtado, sem mudança de controle); fora do domínio, conferidos só para A3: tests/test_cota_ci.py e tests/mutantes/v0475-ci-cota-2.json. Já lido antes: o resto do diff 2fa505d7..e0ac8508.

- A1 (recomendado) corrigido: a dica `gh auth refresh -s user` saiu; a mensagem aponta Settings > Billing no navegador e o `gh api` de leitura (bin/forge-cota-ci:101-103). A skill ci-cd mantém "não peça escopo".
- A2 (recomendado) corrigido: `LOGIN.fullmatch` (bin/forge-cota-ci:19, :28-30) antes de consultar ou imprimir (:89). Sonda com `gh` falso: `--dono '$(id)'` imprime "não tem formato de login" e o `gh` não é chamado; `--dono a-b` consulta normalmente. Com `FORGE_COTA_CI_ENDPOINT` a validação é pulada, mas o dono não entra na mensagem (:103), e a variável é do próprio usuário.
- A3 (recomendado) corrigido: o `gh` falso registra os argumentos e os testes conferem a lista exata de chamadas (tests/test_cota_ci.py:30-43, :151, :158) e a ausência de chamada com dono inválido (:166-178).

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Rodado: `python3 -m unittest tests.test_cota_ci` (26 testes, OK), `tests/catraca.py --base origin/develop`, `tests.test_ambiente_git` (FAILED, 1 falha: test_nenhum_modulo_roda_git_sem_o_ponto_unico em test_cota_ci.py, ver A4) e a sonda de A2 com `gh` falso, sem rede. Suíte inteira: fica para o CI do PR (R-REVIEW). Ferramentas ausentes do PATH: gitleaks, zizmor, actionlint, semgrep (lacuna; nenhum workflow mudou).
