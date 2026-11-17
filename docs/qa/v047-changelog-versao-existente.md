---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-changelog-versao-existente
commit: 665ddd3279ad383032f47b2ff706c59e7bb54d9a
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-16
---
# QA: v047-changelog-versao-existente

Item E2.77 do v047: `forge-changelog release` com versão já existente no CHANGELOG.md recusa dizendo o quê, por quê e como destravar, sem gravar nada. Sem especificação de UX nem plano antecipado (correção de mensagem).

## Achados
## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Versão existente é recusada (rc 1) e nada é gravado (CHANGELOG, fragmento, plugin.json intactos) | Release.test_versao_ja_existente_diz_o_que_por_que_e_como_destravar_sem_gravar_nada | versão repetida | passou |
| Mensagem traz o quê, "Por quê:" e o comando de destravar | mesmo teste | texto da recusa | passou |
| Versão vizinha (0.1.1 com 0.1.0 existente) não é recusada | Release.test_versao_vizinha_de_uma_existente_nao_e_recusada_como_repetida | vizinhança | passou |

## Cenários e resultado real
- Classe `tests.test_changelog.Release`: 24 testes, OK (local, head 9bf1fa1c).
- Vermelho antes do verde (manual, em cópia em `$TMPDIR`, com `bin/forge-changelog` da base bf475209 e testes do head): `FAIL: test_versao_ja_existente_diz_o_que_por_que_e_como_destravar_sem_gravar_nada`, `FAILED (failures=1)`. O `forge-testes --vermelho` estourou o prazo com a máquina carregada (sem veredito), por isso o vermelho manual.
- Mutação: `forge-mutante: pedido=v047 rev=9bf1fa1c6315 ...`; `CV-M1 · morreu · bin/forge-changelog:186`; `CV-M2 · morreu · bin/forge-changelog:187`. Uma linha de guarda mudada, dois mutantes declarados, nenhum sobrevivente.
- Suíte inteira: no CI do PR (check-run `bateria`), não rodada aqui.


## Revalidação por delta (head 02dd674a, E2.536)
- `forge-check parecer delta`: intervalo 9bf1fa1c..02dd674a, sem o que veio da base; no domínio, `bin/forge-changelog` e `tests/test_changelog.py`, o diff é a entrada da `--anexar` vinda da develop (o review aprovou).
- `python3 -m unittest tests.test_changelog`: Ran 89 tests, OK.
- Mutação (`forge-mutante tests/mutantes/v047-changelog-versao-existente.json --base 9bf1fa1c...`): `base=9bf1fa1c63159c0e393ec44723d0e23c8b61ca91 mb=9bf1fa1c63159c0e393ec44723d0e23c8b61ca91 rev=02dd674a6df8e003012fba1d14325f07ba2a1a29`; `CV-M1 · morreu · bin/forge-changelog:195`; `CV-M2 · morreu · bin/forge-changelog:196`.
- Suíte inteira: no CI do PR (check-run `bateria`), não rodada aqui.
- O A1 anterior (`release --anexar` ausente) está resolvido: a opção existe no head, em bin/forge-changelog.
