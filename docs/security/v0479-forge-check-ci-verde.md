---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-forge-check-ci-verde
commit: cb1d5ed7d506a409e05807f30b664ae1ee84f1da
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: v0479-forge-check-ci-verde (E47.3, revalidação)

Revalidação por delta: `forge-check parecer delta` de `0b2e8d6f..cb1d5ed7` (base origin/develop 8a50379). No domínio: `bin/forge-check` (+6 −4) e `tests/test_forge_check_pr.py` (classe `SuiteNoBriefSemPr`). Fora do domínio: fragmento do changelog e `tests/mutantes/v0479-forge-check-ci-verde-5.json`. A rodada anterior (head 0b2e8d6f, aprovada, sem achado) fica no git e não é recopiada; a confirmação de que ela só apertava segue valendo para o que o delta não tocou.

Gatilhos: controle do Forge (`bin/forge-check`, `brief gerar` das etapas `pr` e de merge, portão `pr`).

## Só aperta: confirmação por escrito
**Confirmo: somada, a mudança em `bin/forge-check` continua só apertando em relação à develop; nada afrouxa portão, catraca nem hook.** Motivo:
- A develop (origin/develop 8a50379) não tem PARECER-SO-COM-CI-VERDE nem `suite_do_parecer` (`git grep` sem ocorrência). O `brief gerar` de `pr` e de merge na develop nunca recusava pela falta da linha da suíte.
- O delta só põe `adiar_suite=True` na chamada de `pareceres_da_etapa` (`bin/forge-check:8788`); em `pr_da_cli` (`:1592`) ele só entra na variável `suite`, isto é, no `adiar` do `suite_do_parecer` (`:2137`): sem a prova, aviso no stderr. Não toca `checks_do_head`, `veredito_do_parecer`, as demais linhas de falta nem o `sem_checks`. No `brief gerar` (`:9064`) e no `avisos_da_etapa` (`:8338`), o resultado fica igual ao da develop, mais um aviso.
- Seguem exigindo o CI verde no head (sem `adiar_suite`): `forge-check pr` direto (`:10563`), as chamadas de `pr_da_cli` em `:8916` e `:9015`, e os passos 4 e 6 do `forge-fechar`. O teste `test_o_pr_direto_sem_pr_segue_reprovando` prova o `pr` direto reprovando sem PR.
- `adiar_suite` não é alcançável pela linha de comando: só `pareceres_da_etapa` o passa.

## Detalhe dos achados
Sem achado. `tests.test_forge_check_pr` rodado localmente no head cb1d5ed7: 47 testes, OK (inclui a classe nova). A suíte inteira é do CI do PR.

## Riscos aceitos e ferramentas
Nenhum risco aceito nem pendente de aceite. Lacuna: gitleaks, osv-scanner, semgrep, zizmor e actionlint fora do PATH; o delta não toca workflow nem dependência.
