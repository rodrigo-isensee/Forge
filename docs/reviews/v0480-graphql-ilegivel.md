---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-graphql-ilegivel
commit: 933539c5d2b6083c6112425624040e63a9bdcedd
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0478 E168.10 (PR #854, 2ª volta E168.9, por delta)

Terceira rodada, por delta. `forge-check parecer delta` lido: intervalo 7afc147a..933539c5, sem o que veio da `develop` (merge 933539c5 de c752c227); no domínio `hooks/conformidade.py`, `hooks/parecer.py`, 11 fixtures novas e 4 ajustadas, `tests/test_hooks.py`, os mutantes `-6`, `-7` e `-8` (GQ28 a GQ48) e os ajustes em `-2`, `-4`, `-5`, `gh-merge-admin*` e `v0480-repo-publico-fix-6`, o índice das fixtures e o fragmento do changelog. As rodadas anteriores (433c3782 e 7afc147a) ficam como estavam.

## O que a volta faz
- A1 e A2: `parecer.gh_incerto` marca a palavra com expansão, ou `api`/`pr`, entre o `gh` e o subcomando (achado pela regra do cobra, agora em `subcomando_do_gh` e `leva_valor`). Quem chama recusa com R-CONFORMIDADE, sem escolher leitura: `Guarda.gh`, `analise_do_comando` no `parecer` e, na sessão do Forge, o rótulo exige o dono. `ordem_do_gh` não tem mais o ramo da dúvida.
- `analisar` pula a opção com valor entre `pr` e o subcomando como o gh pula (`gh -b x pr merge 1` vira `gh pr -b x merge 1`), com o `-R` dali valendo e o `--` parando.
- A3: as duas fixtures de entrada padrão na sessão do Forge usam um `gh` falso no `PATH` com a conta do dono; o R-MAIN não depende mais da credencial da máquina.
- A4: os `de` de GQ21, GQ24, RP41 e RP42 voltaram a casar com a fonte.
- A5 da segurança: a chave com `,` ou `..` fora de aspas sobe a palavra ao nível 2, e o GraphQL sem campo à vista também passa pela consulta ilegível. O mérito é da segurança; aqui conferi só a leitura.

## Regras de leitura
- Tamanho: delta de 72 linhas mudadas nos hooks pelo `diff --stat` (20 no `conformidade`, 52 no `parecer`, parte é a extração de `subcomando_do_gh` e `leva_valor`), dentro do H1; um comportamento (a dúvida recusa).
- Mutantes: GQ28 a GQ48, um por guarda nova ou mudada, apontados para testes de comportamento (fixtures e testes de função; nenhum lê a fonte). Conferi que cada `de` casa uma vez só na fonte. A cobertura é do autor e não foi refeita.
- Falsos: o `bin/gh` das fixtures só imprime a conta; a regra que ele alimenta (conta do dono) é a mesma do script.
- Commits: o 6042b096 segue Conventional Commits em português, e o fragmento do changelog descreve o comportamento novo ("na dúvida … recusa, sem escolher uma leitura").

## Verificação
- Testes dos arquivos tocados, no head 933539c5: `python3 -m unittest` de `test_gh_incerto`, `test_analisar_pula_a_opcao_entre_pr_e_o_subcomando`, `test_expansao_por_palavra_chaves`, `test_alias_do_gh_com_opcao_antes_do_nome`, `test_ordem_do_gh` e `test_fixtures_do_repo_publico`: OK (6 testes, 21,8 s).
- Sondas pelos hooks reais (`executar_fixture` de `tests/test_hooks.py`, projeto descartável na `feature/x`), nos papéis `forge:tech-lead`, um dev de stack e a sessão principal, nos dois hooks. As formas S1 e S4 da rodada anterior saem 2 R-CONFORMIDADE no `conformidade` e no `parecer` (S1 sem a opção de forçar o merge, que a recusa da dúvida dispensa); as fixtures novas cobrem as formas com ela.
- `gh -- api …` e `gh -R o/r api …` saem 0, mas o próprio gh 2.105.0 recusa as duas (`unknown command "api"` e `unknown shorthand flag: 'R'`, conferido com `gh … api rate_limit`): não há o que soltar.
- CI do head 933539c5 (run 45412307624): suíte 3.12 e 3.14 verde nas partes 1, 2, 4 e 5, então A3 e A4 fecham no CI. A parte 3 falha só pela neutralidade em `docs/security/v0480-graphql-ilegivel.md` (termo de stack no parecer da segurança, não no código): fica com o `security-engineer`. O `bateria (pareceres)` falha pelos pareceres reprovados da rodada anterior, e a `catraca` pede o rótulo `afrouxa-regra` do dono (hooks de controle e pulos em `tests/test_hooks.py`): ambos são do fechamento, não do código.

## Sondas
- S1 · `gh -b api pr merge 1` (tech-lead, dev de stack, sessão principal) · espera: 2 · obtido: 2 R-CONFORMIDADE no conformidade e no parecer
- S2 · `gh -X $M graphql -f query='{viewer{login}}'` (os três papéis) · espera: 2 · obtido: 2 R-CONFORMIDADE no conformidade; 0 no parecer, que só olha o comando crítico
- S3 · `gh --repo=$R api -X PUT repos/o/r/pulls/1/merge` e `gh -R$R …` (os três papéis) · espera: 2 · obtido: 2 R-CONFORMIDADE nos dois hooks
- S4 · `gh pr view 1 -R o/r` (os três papéis) · espera: 0 · obtido: 0 nos dois hooks

## Parecer
Aprovado. A1 e A2 fecham: na dúvida sobre o subcomando, os dois hooks recusam, sem escolher leitura, e o merge que a base barrava volta a ser barrado. A3 e A4 fecham no CI. O que falta no CI (neutralidade do parecer da segurança, os pareceres, o rótulo da catraca) não é do código.
