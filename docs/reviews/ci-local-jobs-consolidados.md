---
tipo: review
contrato: 1
pedido: develop-vermelha-ci-local
branch: melhoria/ci-local-jobs-consolidados
commit: 5d623443be6f7acab6a401fbfecaa988b428341c
parecer: aprovado
revisor: forge:tech-lead (independente)
data: 2026-10-15
---
# Parecer: ci-local acompanha os jobs consolidados (`rapida` e `bateria`)

Escopo: `git diff origin/develop..5d62344` (`scripts/ci-local`, `tests/test_ci_local.py`, `changelog.d/ci-local-jobs-consolidados.md`). Parecer: **aprovado**, sem item que bloqueie. Pareceres de devops e QA são de outros papéis e seguem em delegações próprias.

## Não afrouxa o ci-local
- `NAO_OBRIGATORIOS` fica vazio: todo job é obrigatório. Só um passo cujas ferramentas ausentes estejam todas em `FERRAMENTAS_OPCIONAIS` (`actionlint`, `zizmor`) é pulado, com AVISO em stderr.
- Passo misto (ex.: `shellcheck` e `actionlint` ausentes juntos) não é pulado: `ausentes <= FERRAMENTAS_OPCIONAIS` falha, e o job vira `ausente` (reprova). O teste `test_ferramenta_obrigatoria_ausente_continua_reprovando_com_actionlint_ausente` cobre isso.
- O passo de download (curl) já era tratado como preparo pelo `PASSO_DE_PREPARO`; não muda.
- O teste `test_bateria_consolidada_mantem_os_passos_que_eram_jobs` confere que a `bateria` ainda traz unittest, shellcheck, actionlint, zizmor, `claude plugin validate`, e2e-instalacao, `[Não publicado]`, "Nada pula degrau" e verificar-contribuicao.
- O ci-local não vira check exigido: nenhum arquivo de `.github/` foi tocado.

## Qualidade (D-QUALIDADE)
Função nova pequena, com um propósito e nome claro; constante nomeada com comentário do motivo. Os dois testes novos de `RodarJobTest` restauram `shutil.which` em `finally`. O teste de ids atualizado deixa de listar jobs que não existem.

## Achados
- Recomendado (não bloqueia): a docstring do módulo ficou com uma linha mais longa que as vizinhas (`Jobs obrigatórios: todos; só os passos...`); quebrar na próxima mexida.
- Recomendado (não bloqueia): o teste de trechos compara com `comandos + "\n".join(nomes)`; correto, mas a precedência é pouco óbvia. Um `texto = ...` nomeado ajudaria.

## Provas
- Suíte (`env -u FORGE_ABERTURA_FEITA python3 -m unittest discover -s tests`, load 0,62 antes): "Ran 653 tests in 178.552s / OK".
- `scripts/validar-plugin.sh`: "Validation passed".
- Fragmento de changelog presente em `changelog.d/` (R-FLUXO do #139); a versão sobe só na release.
