---
tipo: qa
contrato: 1
pedido: melhorias-de-projeto-1311
branch: melhoria/mp1311-conferencia-janela
commit: 773e7e7aa9f87a8dfa14e308a0c1b167ecd0c06d
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-13
---
# QA: janela da conferência de entrega (MP1311, item 1, E1.15)

Branch `melhoria/mp1311-conferencia-janela`, head `773e7e7a`, base `efe7c9e8`. Sem PR aberto: só os testes afetados, o vermelho, os mutantes e o caso extra rodaram locais (máquina com carga acima de 13).

## Achados
- A1 (recomendado) bin/forge-check:2180 · o `Revisar-sha:` que é commit da base já mesclada na branch (não ancestral do Base-sha antigo) vale como `--desde`; a janela fica mais larga (mostra arquivos já conferidos), nunca menor. Falha para o lado seguro.

## Critério → teste → resultado
O pedido não tem `CA-n` de UX; a obrigação é o item 1 do pedido (escopo e regra declarados no commit 7246a080).
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Item 1a: parecer de outro portão é anexo em toda etapa de código | `JanelaDaEntrega.test_parecer_de_outro_portao_na_etapa_qa_e_anexo_do_portao` | etapa `qa` (não só `codigo`) | passou |
| Item 1b: `--desde` no commit revisado pelo portão vale e anuncia `base:` | `test_desde_no_commit_revisado_pelo_portao_vale` | intervalo começa no revisado | passou |
| Item 1b: commit não revisado segue recusado | `test_desde_em_commit_nao_revisado_segue_recusado` | sha fora dos `Revisar-sha` | passou |
| Item 1b: revisado fora da história do head recusado | `test_desde_revisado_fora_da_branch_segue_recusado` | não ancestral do head | passou |
| Item 1b: revisado que é da base recusado | `test_desde_revisado_na_base_segue_recusado` | ancestral do Base-sha | passou |
| Item 1b: pedido gravado na entrega recusado | `test_desde_revisado_com_pedido_na_entrega_segue_recusado` | `docs/pedidos/` no intervalo | passou |
| Commits vindos de merge da base (caso do brief) | cenário QA, ver abaixo | merge-commit e commit da base como `--desde` | passou (com A1) |

## Cenários e resultado real
- `python3 -m unittest tests.test_selo_e_entrega.JanelaDaEntrega`: 6 testes, OK.
- Vermelho (`forge-testes --vermelho efe7c9e83ec2e17fa05971d2e80f4e55b499f836`), saída 0:
  `vermelho: base=efe7c9e83ec2 head=773e7e7aa9f8 módulos=…test_selo_e_entrega…` / `revertidos à base: bin/forge-check, changelog.d/mp1311-conferencia-janela.md` / `mantidos no HEAD: tests/mutantes/mp1311-conferencia-janela.json, tests/test_selo_e_entrega.py` / `[exited with code 0]`. Ao menos um teste prova e nenhum cai no HEAD.
- Mutantes (`bin/forge-mutante tests/mutantes/mp1311-conferencia-janela.json`), todos mortos:
  `M1 · morreu · bin/forge-check:2757`, `M2 · morreu · :2180`, `M3 · morreu · :2180`, `M4 · morreu · :2184`, `M5 · morreu · :2653`, `M6 · morreu · :2180`, `M7 · morreu · :2668`.
- Cobertura (`forge-mutante --cobertura --base efe7c9e8`): as quatro condições mudadas (2180, 2653, 2668, 2757) saem `coberta`; nenhuma linha de guarda sem mutante.
- Caso dos commits que vêm de merge da base (cenário meu, derivado de `JanelaDaEntrega`, fora do repositório, pois o brief só autoriza este parecer): entrega revisada, develop avança, a branch mescla develop (merge `M`), o portão sela `Revisar-sha: M`, o autor faz uma volta.
  - `--desde M` com o Base-sha original: rc 0, `intervalo: <M>..<head>`, `base: commit do autor revisado pelo portão`, só `volta.txt`; o `dev.txt` da base não aparece. Passou.
  - `--desde <commit da develop mesclado>` selado como revisado: rc 0, mas a janela inclui `bin/app` e `docs/notas/a.md` (trabalho do autor já conferido). Janela maior, não menor: é o A1.
  - `--desde M` com o Base-sha avançado ao topo da develop: rc 1 por `Base-sha fora da branch`; é efeito do `origin/develop` velho do harness (a guarda é anterior ao diff e não se relaciona ao item), não defeito.

## Provas
- Mutantes: 7 de 7 mortos, sem sobrevivente nem equivalente.
- Vermelho na base: rc 0.
- CI do PR: não há PR; a suíte inteira fica para o CI.
