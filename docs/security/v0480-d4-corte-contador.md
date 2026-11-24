---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-d4-corte-contador
commit: c9b5d269018c90f24d6414aa5e523adb88fbd41e
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-24
---
# Review de segurança: v0478 (E174.29, PR #869, D4 corte pelo contador), volta por delta

## Gatilhos
Gatilhos: controle do Forge (bin/forge-fechar, fluxo de branches e promoção), automação que abre PR para a main e promove para a homolog.

## Resumo
Volta por delta. A rodada anterior (E174.21, commit bf598d2f, aprovado com A1 a A3 recomendados) está no git e não é recopiada aqui.

Delta lido (`forge-check parecer delta`, bf598d2f..c9b5d269): no domínio, bin/forge-fechar (+5/-1), docs/fechamento-integrador.md (1 linha) e tests/test_fechar_corte.py (+16). Fora do domínio e lidos mesmo assim: tests/test_reval_delta.py (entrada `tests/test_fechar_corte.py: 2` na lista de citações do README.md sintético, sem afrouxar a guarda das outras entradas) e os mutantes -2 e -5. Já lido antes e sem mudança: V2 a V5, `--promover`, `mesclar_direto`.

**Veredito sobre o controle: só aperta.** Nada no delta afrouxa portão:
- bin/forge-fechar:1484: `A && B || die` virou `if [ -z ] || ...; then die; fi`. Equivalente (morre se qualquer versão estiver vazia), continua fail-closed; é a correção de estilo do A1 do tech-lead. Neutro.
- bin/forge-fechar:1490-1492: novo portão no V1. Com a main à frente da homolog (sort -V), o corte para antes do V2 e do V3: não promove nem abre PR de versão mais velha para a main. Aperta (fecha o A2 da rodada anterior).
- Nas linhas acrescentadas de bin/forge-fechar não há `pr merge`, `--auto`, `--force`, `--no-verify` nem `gh api` (contagem 0).
- tests/test_fechar_corte.py:83 `sem_merge` afirma que o registro do gh falso não tem `pr merge` nem `--auto`, chamado na promoção e no PR da main aberto; tests/test_fechar_corte.py:209 cobre a main à frente da homolog (código 1, sem `item` nem `pr create`). Fecha o A3.

Verificação no head c9b5d269 (ambiente limpo, com TMPDIR): test_fechar_corte, test_fechar_laco, `test_fechar.Fechar.test_fechar_sem_a_e_b_ou_c_solto` e `test_reval_delta.Guarda.test_caminho_de_texto_so_e_citado_como_a_lista_conhece`: 31 testes, OK. CI do PR #869 no head (execução 45489524527): suíte em andamento na hora deste parecer; `bateria (pareceres)` vermelha pela falta dos pareceres desta volta. A suíte inteira é do CI e decide o merge.

Estado dos achados anteriores: A2 corrigido (bin/forge-fechar:1490); A3 corrigido (tests/test_fechar_corte.py:83); A1 segue aberto, abaixo.

## Achados
- A1 (recomendado) bin/forge-fechar:1496 · Sem mudança desde a rodada anterior: V2 acha a marca com `git log -1 -G` sem `--first-parent`; com merge commit na develop, o --promover receberia um sha fora da cadeia. Use `--first-parent` e confira o assunto `chore(release): marca da <v_dev>`.

## Detalhe dos achados
- **A1** · severidade baixa · o tech-lead (E174.19) o considerou correto porque a develop mescla por squash; o caminho só existe com merge commit (o #795 mostra que já ocorreu) e P1/E31.10 tendem a recusar (fail-closed). Mantenho recomendado, sem promoção. Esforço P. Dono: autor do D4.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: `forge-check parecer delta`, leitura estática, grep nas linhas acrescentadas, testes rodados localmente, `gh pr checks` (só leitura). gitleaks, zizmor, actionlint e semgrep não estão no PATH (lacuna; o delta não toca workflow nem traz credencial).
