---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-forge-check-ci-verde
commit: 5c998a57f1f7126a1c0f4427865136ede7829f4f
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-20
---
# QA: v0478 (E47.4, PARECER-SO-COM-CI-VERDE e META85-FC-RESTOS)

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Aprovado só conta com CI verde no head (PR no mesmo head, todo check em pass/skipping, exigidos presentes) | `test_forge_check_pr.CiVerdeNoHead` | pendente, vermelho, ausente, outro head, sem rede, nenhum check: falha fechada | passa (M1-M3, M21 mortos) |
| Ou com a linha `- suíte: <sha40> rc=0 módulos=...` cobrindo os módulos de teste do diff | `test_forge_check_pr` (prova da suíte) | sha curto/outro, rc≠0, módulo faltando, base ilegível | passa (M4-M17 mortos) |
| `--previo` e passo 1 do fechar só avisam; fora do Forge nada | `test_forge_check_pr` (adiar) | previo; não-Forge | passa (M18-M20 mortos) |
| `parecer novo` traz a linha da prova e o caminho `<pasta>/<slug>.md` | `test_aq5_parecer_novo`, `test_forge_check_pr` | slug inseguro cai em `<pedido>.md` | passa (M22-M24 mortos) |
| Brief de merge-integracao manda juntar só `origin/<base>` | `test_forge.LerDirigidoDoBrief` | base remota, não a local | passa |
| Teto de arquivos com `python3 -I` e ambiente limpo; Jarvis passo 5 só com `revalida: sim` | `test_meta85_item_arquivos`, `test_jarvis_nucleo` | n/a | passa |

## Cenários e resultado real
Máquina com carga e sem suíte local, por ordem do brief. Rodados só os módulos tocados, com TMPDIR:
- `test_forge_check_pr` 45 OK; `test_aq5_parecer_novo` 8 OK; `test_meta85_item_arquivos` 6 OK; `test_jarvis_nucleo` 43 OK; `test_forge -k LerDirigidoDoBrief` 2 OK. O `test_forge.py` inteiro não foi rodado aqui (fica para o CI do PR, ainda sem PR no head; por isso não gravei a linha `- suíte:`).
- Vermelho antes do verde: `bin/forge-check` da base 004ce869 sobre a árvore do head: `test_forge_check_pr` Ran 45, FAILED (failures=2, errors=16); `test_aq5_parecer_novo` Ran 8, FAILED (failures=1). `forge-testes --vermelho` estourou o prazo de 400 s (rc=143, sem veredito; carga), então a prova foi por substituição manual em cópia em `$TMPDIR`.
- Mutação: `bin/forge-mutante` nas 4 specs (`--processos 2`): rc=0, M1 a M24 todos `morreu`, nenhum sobrevivente, nenhum equivalente.
- `forge-mutante --cobertura --base 004ce869`: toda condição mudada de `bin/forge-check` sai `coberta` por mutante declarado; nenhuma `não coberto`.
- Revisão do diff: `ci_verde_no_head` falha fechada (sem branch, head, PR, checks); `checks_ruins` é a mesma fonte do `checks_do_head`, sem divergência.

## Revalidação no head cb1d5ed7 (E47.4, volta do review)
`forge-check parecer delta` (0b2e8d6f..b8d940bb, só o domínio de código e testes): `bin/forge-check` (`adiar_suite` em `pr_da_cli` e `pareceres_da_etapa`), `tests/test_forge_check_pr.py` (`SuiteNoBriefSemPr`), `tests/mutantes/v0479-forge-check-ci-verde-5.json`, o changelog. O resto do intervalo é review e segurança, fora do meu domínio.
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| `brief gerar` de `pr` e de merge roda antes de o PR existir: a suíte sem CI só avisa | `SuiteNoBriefSemPr.test_etapas_que_recusam_nao_travam_sem_pr` | sem PR, nas 3 etapas de `ETAPAS_QUE_RECUSAM` | passa (M25, M26 mortos) |
| O `pr` direto sem PR segue reprovando (catraca não afrouxa) | `SuiteNoBriefSemPr.test_o_pr_direto_sem_pr_segue_reprovando` | `adiar_suite` só entra pelo `pareceres_da_etapa` | passa |
- `tests.test_forge_check_pr` (`-I`, discover): Ran 47, OK (eram 45).
- `forge-mutante tests/mutantes/v0479-forge-check-ci-verde-5.json`: `rev=b8d940bb8951`; M25 `morreu · bin/forge-check:1592`; M26 `morreu · bin/forge-check:8788`; rc=0. Os M1-M24 não têm linha mudada no delta.
- Vermelho: `bin/forge-check` de `cb1d5ed7~1` com os testes do head, em cópia em `$TMPDIR`: Ran 47, FAILED (failures=3, as 3 etapas do subTest de `test_etapas_que_recusam_nao_travam_sem_pr`); o teste do `pr` direto passa nos dois lados, como deve (guarda de não afrouxamento). `forge-testes --vermelho cb1d5ed7~1` estourou o prazo da carga da máquina (sem veredito), então a prova foi por substituição manual.
- Mudanças de texto (spec -5, changelog) conferidas contra o código: dizem que o `brief gerar` só avisa, a catraca não muda.
- Suíte inteira: fica para o CI do PR (sem PR no head ainda); sem linha `- suíte:`.

## Revalidação no head 5c998a57 (E47.4, alinhamento das specs)
`forge-check parecer delta` (cb1d5ed7..5c998a57, sem o que veio da develop): no domínio só `tests/mutantes/lote-l08-escopo.json` (M61) e `tests/mutantes/v0479-forge-check-ci-verde-3.json` (M19, M20). Mudança só no trecho `de`/`para`, que passa a casar com a assinatura e a linha atuais do `bin/forge-check` (`adiar_suite`); nenhuma guarda de código mudou.
- `forge-mutante --ids M61 tests/mutantes/lote-l08-escopo.json`: `rev=5c998a57f1f7`; `M61 · morreu · bin/forge-check:1578`; rc=0.
- `forge-mutante --ids M19,M20 tests/mutantes/v0479-forge-check-ci-verde-3.json`: `rev=5c998a57f1f7`; `M19 · morreu · bin/forge-check:1592`; `M20 · morreu · bin/forge-check:1592`; rc=0. (As duas specs são de pedidos diferentes: uma chamada por pedido.)
- `python3 -I -m unittest discover -s tests -p test_forge_mutante.py -k ConferirTodas`: Ran 4, OK (13,6 s). A forma `-m unittest tests.test_forge_mutante.ConferirTodas` não importa sob `-I` (ModuleNotFoundError), como a skill já avisa.
- Suíte inteira: fica para o CI do PR; sem linha `- suíte:`.
