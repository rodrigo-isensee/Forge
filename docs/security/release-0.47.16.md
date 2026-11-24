---
tipo: revisao-seguranca
contrato: 1
pedido: release-0.47.16
branch: melhoria/v0480-release-04716-anexo
commit: 51fc24a74534d3ba419d2f7f08c9ae307aa07347
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-24
---
# Review de segurança: release 0.47.16 (versão inteira), revalidada no anexo 51fc24a7

Etapa E167.9 do pedido v0478. Volta por delta: a rodada anterior (marca 2b8d11be, E167.3) fica no git (`git show 89db5b73:docs/security/release-0.47.16.md`) e vale para os 37 merges de `v0.47.15..35b05bd3`, com a classificação de cada um lá. Esta rodada lê só o que entrou depois do corte 35b05bd3: 11 merges de primeiro pai (#843, #844, #845, #848, #839, #846, que a marca #852 trouxe da develop sem os juntar; e #805, #847, #851, #853, #812, depois da marca), a squash da marca 89db5b73 e o anexo 51fc24a7 (parecer do pedido `docs/security/v0480-release-04716-anexo.md`, aprovado: só metadado de versão).

Gatilhos: hooks (`ordens` novo e registrado em `UserPromptSubmit`, `_comum.py`), controles do Forge (`docs/regras/R-REVIEW.md`, `docs/regras/R-SEGURANCA.md`, `docs/adr/0003`, `docs/adr/0009`), execução de comando (`bin/forge-check`, `bin/forge-fechar` com `rm -rf` do `--limpar`, `bin/forge-mutante`, `bin/forge-testes`, `bin/forge_dora.py`), release usada por todos os projetos.

## Delta lido
`forge-check parecer delta` não serve aqui: o `commit:` anterior (2b8d11be, cabeça do PR #852) não é ancestral de 51fc24a7, porque o merge foi por squash. Leitura feita à mão, em três partes:
- **Marca.** `git diff --name-status 0f4a7791 89db5b73`: só `plugin.json` dos dois manifestos, `CHANGELOG.md`, `docs/engineering/placar-mutacao.md`, os seis pareceres da marca e a remoção dos fragmentos. Igual ao que a rodada anterior aprovou. `git diff 2b8d11be 89db5b73` é, arquivo por arquivo, a soma de `35b05bd3..6161978d` e `6161978d..0f4a7791` (os seis itens da develop) mais os pareceres da marca: nenhuma diferença fora disso.
- **Cada item com o parecer próprio.** Para os 9 itens com código, teste ou skill, o `commit:` do parecer de segurança é ancestral da cabeça do PR (`refs/pull/<n>/head`) e `git diff <commit:> <cabeça>` nos arquivos de `bin/`, `hooks/`, `scripts/`, `.githooks/`, `.github/`, `tests/`, `agents/`, `skills/`, `docs/regras/`, `docs/retrospectivas/` e `templates/` que o merge tocou é vazio, e `git diff <cabeça> <merge>` nos mesmos arquivos também. Duas exceções, lidas: no #805 (aprovado em a6e0d101), `tests/test_hooks.py` ganhou `test_fixtures_do_repo_publico`, que veio da develop (#837 e #850) pelo merge 1c4359d8; no #851 (aprovado em da8e0173), `tests/mutantes/v0474-mp6-disco.json` e `-2.json` realinham M8 e M9 ao teste novo do `--limpar` (a5e738b1, E166.6, com review e QA por delta): o trecho guardado é a nova condição de origin normalizado, e nenhum mutante sai. Ambas neutras.
- **Anexo.** 12 linhas novas no `CHANGELOG.md` e 11 fragmentos apagados; nada mais.

Superfície do delta: nenhum arquivo em `.github/`, `.devcontainer/`, `.githooks/`, `scripts/`, `docs/security/aceites/`, `tests/config.json`, `tests/catraca.py` nem manifesto de dependência. Versão: `.claude-plugin/plugin.json:3` e `dev/.claude-plugin/plugin.json:3` em `0.47.16`, igual a `CHANGELOG.md:7`; `bin/forge-changelog conferir-release`: `ok: changelog.d/ sem fragmentos pendentes`.

Hooks medidos no head: `bin/forge-check comparar v0.47.15 51fc24a7`: `so-aperta: medido base=5a232208 head=51fc24a7 casos=239 aceites-novos=0` (famílias merge-pr, push-forcado e sem-verificar com 8 casos cada). A medida cobre só a decisão dos hooks.

Achados anteriores: nenhum (a rodada anterior saiu sem achado). Os dois pontos que ela deixou abertos fecham aqui: o anexo foi feito com `--anexar 0.47.16` e o #844 (`fix(dora)`) está lido acima e abaixo; a apuração do #810 é de processo e segue com o dono.

## Detalhe dos achados
Sem achados.

## Aceites novos
Nenhum: o delta não toca `docs/security/aceites/`, e a medida dos hooks dá `aceites-novos=0`.

## Só aperta? (para o rótulo afrouxa-regra da promoção)
Nos controles que recusam (hooks, `forge-check`, `forge-fechar`), a versão só aperta ou é neutra frente à 0.47.15: a medida dá `so-aperta`, e nenhum item do delta faz passar uma entrada que antes era recusada. Mas a versão **não é só aperta na norma**: dois itens do delta afrouxam regra escrita e entram pela autorização do dono, não por esta confirmação:
- **#805, hook `ordens`:** afrouxa o item 1 da ADR 0003 (`docs/adr/0003-hooks-deterministicos-e-silenciosos.md:65`): um hook passa a injetar contexto no `SessionStart` e a cada mensagem do dono. Não decide nada e sai sempre com 0; a fonte é só do Jarvis (`docs/security/v0480-ordens-hook.md`, commit a6e0d101). Autorização: DECISÃO DO DONO de 2026-11-23 15:25, Decisão 2, opção 2a, que cita o hook de ordens.
- **#812, revalidação só no delta (G1.2):** afrouxa R-REVIEW e R-SEGURANCA (`docs/regras/R-REVIEW.md:17`, `docs/regras/R-SEGURANCA.md:17`; `bin/forge-check:4176`): bloqueante novo fora do delta, sem `explorável: S<n>`, vira recomendado e cartão. Classificação do item em `docs/security/v0480-g1-2-delta.md` (commit 14c7e31e). Autorização: ORDEM DO DONO de 21/11 22:13 (o comportamento) e DECISÃO DO DONO de 2026-11-23 15:25, opção 2a (o rótulo do G1.2/G1.3). Entrada na 0.47.16: DECISÃO DO DONO de 2026-11-24 07:49 e ORDEM DO DONO de 11:45 (mesclado pelo dono, "siga direto para a promoção da 0.47.16").

Os outros 9 itens, conforme o parecer de segurança de cada um:
- **Só aperta:** #853 (`v0480-vigia-trava-critica`: prazo vencido numa trava recusa com ou sem marcador, pela DECISÃO DO DONO de 2026-11-24 07:43), #851 (`v0480-limpar-url-git`: só aperta ou neutro para a perda de trabalho; o `rm -rf` segue preso às travas que não dependem da URL).
- **Neutros:** #844 (`v0480-dora-zero-falso`), #845 (`v0480-testes-sem-i`), #846 (`v0480-mutante-varias-trocas`), #847 (`v0480-dir28-sandbox`), #848 (`v0480-bp14-definicao`).
- **Só documento, sem gatilho e sem parecer de segurança:** #839 e #843 (propostas BP9 e BP15).

A promoção toca arquivos protegidos e pede o rótulo afrouxa-regra. Para os itens que só apertam ou são neutros, a autorização é a da rodada anterior (DECISÃO DO DONO de 2026-11-23 15:25, regra até 27/11 com esta confirmação escrita; DECISÃO DO DONO de 2026-11-23 21:11, que vale também para a main nas condições de 21/11 20:15; DECISÃO DO DONO de 2026-11-24 09:05). Para o #805 e o #812, a autorização é a opção 2a. Os dois vão no aviso de marco como itens que afrouxam. O merge homolog → main segue do usuário (`R-MAIN`).

## Riscos aceitos e ferramentas
Nenhum risco aceito nem pendente de aceite. A suíte inteira vale pelo CI do PR de promoção. Localmente rodei só `comparar`, `conferir-release` e `tests.test_changelog` (91 testes, OK). Para a correspondência entre parecer e merge, usei `git fetch` das cabeças `refs/pull/<n>/head` para `FETCH_HEAD`, sem ref nova. Lacuna: gitleaks, osv-scanner, semgrep, zizmor e actionlint estão fora do PATH; o delta não toca workflow nem dependência.
