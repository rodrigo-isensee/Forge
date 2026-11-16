---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-changelog-versao-existente
commit: 9bf1fa1c63159c0e393ec44723d0e23c8b61ca91
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-15
---
# QA: v047-changelog-versao-existente

Item E2.77 do v047: `forge-changelog release` com versão já existente no CHANGELOG.md recusa dizendo o quê, por quê e como destravar, sem gravar nada. Sem especificação de UX nem plano antecipado (correção de mensagem).

## Achados
- A1 (recomendado) bin/forge-changelog:190 · A mensagem manda usar `release --anexar`, que ainda não existe na develop (vem de melhoria/v047-changelog-anexar, E1.256). Até essa entrar, o "como destravar" aponta para opção inexistente; entrar na ordem certa.

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
