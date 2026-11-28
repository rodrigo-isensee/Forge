---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-espera-amarela
commit: 054d4103ddb0c0364136575a4b36bbd3a2708164
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-27
---
# Review: v0481 (E47.7, #948, espera amarela, revalidação da volta 1)

Delta lido `5d293a8b..054d4103` (1 commit do E47.6, 17 arquivos), no clone de revisão `/root/.forge-contrib/wt/v0481-espera-amarela-tech-lead-3`, head `054d4103`. Delta lido pela ferramenta: `forge-check parecer delta docs/reviews/v0481-espera-amarela.md` · `revalida: sim (desatualizado: .github/workflows/catraca.yml mudou depois do parecer)`; o diff do domínio é o do E47.6. A rodada anterior (E47.2, head `517557ab`, aprovado) fica no histórico do git.

## CI e ferramentas (citadas, não refeitas)
- ci: 054d4103ddb0c0364136575a4b36bbd3a2708164 verde
- `gh pr checks 948`, runs `46083587844` (ci.yml) e `46083666333` (catraca.yml), head `054d4103`: suíte 3.12 (5/5), `bateria (passos)`, `bateria (python 3.14)`, `bateria (verificações longas)`, `instalação (python 3.14)`, `teto de pulados (python 3.12)` e `árvore já provada na develop` verdes. Vermelhos que esperam: `bateria (pareceres)` e `bateria` (R-REVIEW: pareceres de review e devops `commit: desatualizado`, log do job) e `catraca (conferência)` com `catraca` (R-CONFORMIDADE sem o rótulo, script da base, sem o rc 3).
- Testes do diff, à mão: `test_catraca.{EsperaNaoEVermelho,EsperaDoRotuloSoComAApiRespondendo,Workflows}`, `test_ci_local`, `test_forge_pronto.ProvaDoCi`, `test_modelos_projeto.TestPassoAPassoDaProtecao`, `test_pre_envio_brief.ChecksForaDaLinhaDoCi`, `test_suite_partes.FiacaoDoCI` · 138 testes, OK.
- Mutantes: `bin/forge-mutante --processos 1` nas 4 specs do item · M1 a M25 morreram (M18 por erro do teste declarado, que a ferramenta aceita); `IL-M79` realinhado de `v047-integracao-em-lote-10.json` morreu. `--cobertura --base 517557ab`: as guardas novas e mudadas de `tests/catraca.py` (1927, 2103, 2104, 2161, 2163, 2172, 2291, 2293, 2302, 2304, 2313) cobertas; os workflows a ferramenta não mede, e as guardas mudadas deles (ci.yml 620 e 681, catraca.yml 60 e 70) têm M7, M11, M21 e M22.
- Teto (H1): acumulado da branch `319a968d..054d4103` em código, 123 linhas (+123 -21 em `.github/workflows/`, `scripts/ci-local` e `tests/catraca.py`, comentários inclusos), abaixo de 150; um comportamento só.

## Leitura do delta
1. A1 da rodada anterior (igual ao A1 da segurança) fechado: o sufixo do agregador do ci.yml exige os 5 `needs` em `success` e o da catraca.yml, a conferência em `success`; suíte ou T1 vermelho com a espera dá o vermelho no nome exato. O teste avalia a condição com cada `need` reprovado de cada vez (falha, cancelado, pulado), o que obriga a condição a citar todos. `docs/protecao-de-branch.md:29` corrigido.
2. A2 da segurança: a espera dos pareceres vira o booleano de `pareceres_e_espera`, e a linha só é espera se o padrão ancorado casa e o caminho separado é o mais longo dos caminhos conhecidos (pastas e pareceres do head) que abre a linha; nome de arquivo com a marca ou com `: commit: desatualizado` cai no vermelho, e parecer não exigido que reprova (`outros`) também. Caminho com espaço ou desconhecido cai no vermelho (falha fechada).
3. A3 da segurança: execuções `None`, PR sem resposta (`fonte` ou `pr_atual()` em `None`) e git que estoura o prazo entram em `falhas` e tiram a espera do rótulo (rc 1, com a mensagem). `fonte` só é lida quando o bloco anterior a definiu (mesma condição `not custo and not liberado`).
4. A4 da segurança: o último check do head só vale como espera numa lista fechada (`nenhum`, `failure`, `cancelled`, `timed_out`, `action_required`, `stale`); verde, pulado, neutro, `null` e em andamento ficam vermelhos, nos dois workflows, com teste em subprocesso de cada estado.
5. Os testes realinhados tiram só o sufixo condicional (`ESPERA`, `pernas` do ci-local) e ainda afirmam o fim exato da expressão; o `pernas` sem matriz agora apaga qualquer `${{ }}` do nome, o que só alcança o sufixo da espera nos jobs de hoje. Commit em Conventional Commits em português, com pedido e etapa; fragmento em `changelog.d/` atualizado.

## Parecer
Aprovado no head `054d4103`. O A1 da rodada anterior fechou, os quatro recomendados da segurança estão fechados com teste de comportamento do ramo de falha, os workflows e o script seguem falhando fechados, o teto acumulado é de 123 linhas e os 25 mutantes do item mais o `IL-M79` realinhado morrem. O A2 da rodada anterior (título corrigido deixa o `catraca` vermelho velho até o rótulo) fica fora do delta e segue como cartão depois do merge.
