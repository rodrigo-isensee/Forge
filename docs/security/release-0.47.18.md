---
tipo: revisao-seguranca
contrato: 1
pedido: release-0.47.18
branch: melhoria/marca-0.47.18
commit: 217e73ed2e9bc41ac0ba09550b76721fbd36359d
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-25
---
# Review de segurança: release 0.47.18 (versão inteira), para a promoção

Etapa E12.16 do pedido v0481. Conteúdo: `git diff 5fb8e328..217e73ed`, 49 arquivos, da marca da 0.47.17 até a marca da 0.47.18. São quatro squashes, #887, #889, #891 e #893, cada um com os próprios pareceres, mais a marca, coberta por `docs/security/marca-0.47.18.md` no mesmo commit. Aqui confiro a junção, a marca, o CHANGELOG e a versão.

Gatilhos: controles do Forge (`bin/forge-check`, `tests/catraca.py`), execução de comando e fluxo de release (`bin/forge-fechar --corte`, `bin/forge-copia`), skills de portão (`engineering-practices`, `qa-testing`) e release usada por todos os projetos.

## Junção: cada item com o parecer próprio
Para cada PR, busquei `refs/pull/<n>/head` para `FETCH_HEAD`, sem criar ref, e conferi três pontos:
- **Pareceres:** os de segurança, review e QA estão `aprovado`, e o `commit:` de cada um é ancestral da cabeça. Os commits são: #887 `8e814a73`, #889 `7bdd25d5`, #891 `e05f8faa` e #893 `55f87ffd`.
- **Diff da cabeça contra o squash na develop:** vazio nos quatro, nos caminhos de código (`bin`, `hooks`, `scripts`, `.githooks`, `.github`, `tests`, `agents`, `skills`, `docs/regras`, `templates`, `patches`, `stacks`).
- **O que veio depois do parecer:** só pareceres em `docs/`. A única exceção é o #893, que recebeu o merge da develop `9b9ae143` com o #891 já mesclado. O `--remerge-diff` desse merge é vazio, sem resolução à mão.

## Marca e versão
- A marca (`eeb81062..217e73ed`) toca só os dois `plugin.json`, o `CHANGELOG.md` e os 4 fragmentos apagados. Ela é idêntica à saída de `forge-changelog release 0.47.18 2026-11-25` rodado sobre `eeb81062`.
- CHANGELOG: a seção `## [0.47.18] - 2026-11-25` (`CHANGELOG.md:7`) traz os 4 itens. Adicionado 1: G3, #893. Alterado 1: `--corte`, #887. Corrigido 2: catraca, #891, e `forge-copia`, #889. Cada linha é idêntica à do fragmento. `conferir-release` dá `ok` e `tests.test_changelog` roda 91 testes, OK.
- Versão: `0.47.18` em `.claude-plugin/plugin.json:3` e em `dev/.claude-plugin/plugin.json:3`. A `origin/main` está em `0.47.16` (`ad55cd9c`), e a 0.47.17 espera o merge do dono (#884).
- Segredos: busquei nas linhas acrescentadas do diff inteiro os padrões de token do GitHub, chave da Anthropic, chave da AWS, chave privada e token do Slack. Nada encontrado.

Superfície protegida em `5fb8e328..217e73ed`: nenhum arquivo em `.github/`, `.devcontainer/`, `.githooks/`, `scripts/`, `hooks/`, `docs/regras/`, `docs/security/aceites/`, `agents/`, `templates/` ou `stacks/`. Também não há `tests/config.json` nem manifesto de dependência no diff, então nenhuma invariante sai. Medida dos hooks: `bin/forge-check comparar 5fb8e328 217e73ed` dá `so-aperta: ... casos=239 aceites-novos=0`. Essa medida cobre só a decisão dos hooks, que a versão não toca.

## Só aperta ou neutro, por escrito (para o rótulo afrouxa-regra da promoção)
Os quatro PRs levaram o rótulo `afrouxa-regra`. Rodei a catraca do pai de cada squash contra ele, como o CI (`--base <pai>`). Dois PRs precisaram do rótulo por tocarem arquivo de controle protegido (ADR 0008), não por afrouxarem regra:
- #891 por `tests/catraca.py`;
- #893 por `bin/forge-check`, com o aviso "valor esperado trocado" em `tests/test_pre_envio_brief.py::Gerar.test_parecer_sem_pr_diz_que_a_suite_fica_para_o_ci`, conferido no review do item: o caso sem PR passou para a segurança, que fica fora do G3, e o texto novo do review e do QA está coberto por `LeOCiNoBrief`.

O #887 e o #889 passam na catraca da base sem violação. Neles o rótulo não era exigido. O PR da promoção vai pedir ao dono o rótulo `afrouxa-regra` pelos dois arquivos protegidos do #891 e do #893.

Frente à 0.47.17, a versão só aperta ou é neutra nos controles que recusam:
- **Só aperta:**
  - #891: a catraca conta a asserção feita no ajudante do teste. Tirar `self.fica()` ou renomear teste sem asserção passa a pedir o rótulo. O teto de expansões falha fechado, contando só as diretas, que é o piso da base.
  - #889: o `forge-copia` tenta menos refs (nunca `origin/origin/<base>`). O `--revisao` é opcional, cai fora (saída 1) se a branch não está no remoto e mantém todas as recusas de destino.
  - #893: o `forge-check pr` passa a recusar o review ou o QA aprovado sem `- ci: <sha40> verde` (PARECER-LE-O-CI). A PARECER-SO-COM-CI-VERDE e os checks do head seguem iguais.
- **Neutros:**
  - #893: `CHECKS_FORA_DA_LINHA_DO_CI` é só texto, não filtra checks, e o merge exige todos. A isenção de transição deixa o parecer de `commit:` anterior à regra exatamente na regra da develop e fecha por padrão. Nas skills, a frase "a suíte inteira só no CI" já valia, e o enxugamento da `qa-testing` mantém as invariantes. O G3.3, que afrouxaria `R-QA`, não foi entregue e ficou com o dono.
  - #887: o `--corte` mede a marca e escreve o corpo do PR com a linha de teto e os pareceres `release-<versão>`. O anexo do fragmento tardio só avança o ramo da marca, sem `--force`, e pede revalidação dos pareceres. No V3, o pedido de rótulo é só um texto impresso (`gh pr view --web`): o script não aplica rótulo (`test_script_nunca_usa_force_no_verify_nem_rotulo`). A contagem em `tests/test_reval_delta.py:124` (2 para 3) reflete a citação sintética revisada.
  - Os realinhamentos de mutantes antigos (`mp1311`, `v0479-forge-check-ci-verde-2/-3`, `v0480-d3-*`, `v0480-d4-corte-contador-4` e `v0481-copia-base`) acompanham as linhas novas da fonte com a mesma troca. O peso de `test_fechar_corte` em `tests/pesos-d4.json` (16.8 para 46.0) só reparte a suíte.

Nenhum item afrouxa na norma. Nenhum teste foi apagado e nenhuma invariante saiu.

## Riscos aceitos e ferramentas
Nenhum risco aceito novo nem pendente de aceite: o delta não toca `docs/security/aceites/`, e a medida dá `aceites-novos=0`.

A suíte inteira vale pelo CI. No PR #894, na cabeça `217e73ed`, a leitura mostrou 14 checks em `pass` (catraca, as baterias, instalação e "árvore já provada") e duas partes da suíte em andamento. Os jobs só de push na develop saíram pulados. O CI de push da develop em `eeb81062` está verde (run 45579103080). O CI do PR de promoção continua sendo o portão. Localmente rodei só `comparar`, `conferir-release`, `tests.test_changelog`, a catraca por squash e a medida do teto.

Lacuna: `gitleaks`, `osv-scanner`, `semgrep`, `zizmor`, `actionlint`, `shellcheck` e `trivy` estão fora do PATH. O delta não toca workflow nem dependência, e a busca de segredos foi feita por padrões.
