---
tipo: revisao-devops
contrato: 1
pedido: release-0.32.0
branch: melhoria/release-0.32.0
commit: cb9f7c1ee1a5ba99b8ddc80dae7c4c9535b20ff9
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-11-03
---
# Review de devops: release-0.32.0

Escopo: `git diff 5b6d13a...cb9f7c1` (rodada 2: delta 5e7f003..cb9f7c1, só `changelog.d/README.md`) (PRs #427 a #430 e o commit de release), na parte de pipeline, scripts e pre-push. Pareceres dos PRs individuais lidos como insumo, sem refazê-los.

## Parecer
Aprovado na rodada 2. O A1 da rodada 1 (teste da L34 vermelho sem `changelog.d`) está resolvido: o cb9f7c1 versiona `changelog.d/README.md`, a pasta existe e `test_todo_caminho_citado_em_agentes_skills_e_regras_existe` passa (rodado). O que é de pipeline (ci.yml, scripts, pre-push) está sem defeito.

Detalhe do A1 (fora de `## Achados`): na rodada 1, `changelog.d` estava em `PASTAS_CITADAS` (tests/test_forge.py:339), mas a release apaga os fragmentos; no 5e7f003 a pasta não existia, `test_todo_caminho_citado_em_agentes_skills_e_regras_existe` falhava (citações em agents/tech-lead.md e skills/contribuir-com-o-forge/SKILL.md) e o pre-push recusava o envio. A recomendação da rodada 1 (pôr `changelog.d` em `CRIADOS_NO_PROJETO`) não foi a adotada: o cb9f7c1 versiona `changelog.d/README.md` e não muda o teste.

- `.github/workflows/ci.yml` (#429): `timeout-minutes` 10→20 (checagem rápida) e 15→25 (bateria e bateria python 3.14). Só o teto sobe; `permissions:`, `concurrency`, SHAs das ações e nenhum `uses:` foram tocados (0 linhas `uses:` mudadas). Sem `continue-on-error`, `[skip ci]` nem `pull_request_target` (grep). O YAML carrega sem erro.
- `ci.yml` (#430, L01): o gate do commit só de parecer agora cobre `docs/{reviews,qa,security,devops,ux}/`, recusa modelo `_*` e `docs/security/{ameacas,aceites}/`, e continua exigindo `bateria` verde do app `github-actions` no commit anterior, só em PR com base `develop` e ação `synchronize`. `$ANTES` e `$HEAD_SHA` seguem por variável de ambiente, sem interpolação de entrada não confiável em `run:`. Entrou `NeutralidadeDoNucleo` nos testes leves do gate, coerente com o núcleo do Jarvis ter movido invariantes.
- `scripts/suite-paralela.py` (L32): `registrar_vermelha` roda só fora do CI (`GITHUB_ACTIONS`), só após o veredito, nunca muda o código de saída, abre com `O_NOFOLLOW` e modo 0600, não cria a pasta e a recusa se não for do usuário ou tiver escrita de outros; grava só ids e números. Sem rede, sem serviço.
- `.githooks/pre-push` e `bin/forge-testes`: o pre-push não mudou na leva; `bin/forge-testes` só registra módulos novos e o mapa de `tests/comportamento/`.
- Custo (`R-CUSTO`): zero. Nenhum runner, serviço, cache ou artefato novo. O teto maior só pesa se o job realmente demorar (cobrança é por minuto usado). `R-MAIN`: nenhum workflow tocado escreve na `main`.
- Dependabot e `release.yml`: não alterados.

Ferramentas: `shellcheck` disponível (o pre-push e `forge-testes` são Python/hook com shebang não-shell nos arquivos testados; sem achado nos que ele aceita); `actionlint` ausente no PATH, lacuna registrada (o CI o roda). Lista PA-7 (`docs/engineering/achados-recorrentes.md`) conferida na rodada 3: AR-9 não se aplica (os textos de 10 min citam o job da catraca, que não mudou); AR-6 não se aplica (o `|| true` de `ci.yml:230` já existia em `main`, fora da leva); A2 e A3 têm a forma da AR-3 (lista negativa divergente entre CI e pre-push), recomendados e sem bloqueio.

Versão minor: nada na leva quebra os projetos. O que muda é aditivo (novos subcomandos do `forge-check`, avisos sem recusa, registro local, `forge-mutante --processos` com padrão 1) ou reorganiza texto do Jarvis para skills sem remover regra. A mudança de papel (só o `qa-engineer` roda a suíte inteira, D-5) é decisão do dono e não exige ação dos projetos. Minor adequado.

## Achados
- A1 (recomendado) tests/test_forge.py:339 · RESOLVIDO no cb9f7c1 (changelog.d/README.md versionado; teste da L34 passa); defeito original e recomendação descartada no corpo do parecer.
- A2 (recomendado) .github/workflows/ci.yml:108 · a exclusão de modelo no CI testa `/_[^/]*$` (só o nome do arquivo), enquanto o pre-push usa `*/_*` (qualquer componente); caminho como docs/devops/_x/y.md passa no CI e roda tudo no pre-push.
- A3 (recomendado) .github/workflows/ci.yml:107 · o gate do CI isenta docs/ux/ e o pre-push (.githooks/pre-push:225) não; o comentário diz "como no pre-push". Alinhar o comentário ou o pre-push (hoje o CI é o mais permissivo, sem efeito, pois docs/ux/ não existe).

## Custo e rollback
Custo: 0 minutos novos garantidos; limites de tempo maiores apenas evitam queda por teto. Rollback: reverter o PR que sobe a versão e os tetos (`git revert` na branch `melhoria/*`, pelo fluxo); sem migração, estado ou recurso externo. O registro `suite-vermelha.jsonl` é local e pode ser apagado sem efeito.
