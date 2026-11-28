---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-vigia-time-parado
commit: dc0af82caa3d7e6be2497ce8e7a51447b87e384a
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-22
---
# QA: VIGIA-TIME-PARADO (v0478 E105.5)

## Critério → teste → resultado
| Critério (E105.1) | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Stop, zero agentes e cartão livre: avisa "time parado: N cartões disponíveis, primeiro <ID>" | `test_zero_agentes_e_cartao_livre_avisa`, `test_registro_ausente_conta_como_zero` | registro ausente | passou |
| Agente vigente cala | `test_agente_rodando_cala` | 1 agente | passou |
| Marca de dependência na Obs. tira o cartão (3 marcas, caixa) | `test_so_cartoes_dependentes_cala`, `test_marca_fora_da_obs_nao_e_dependencia` | marca fora da última coluna | passou |
| Só a coluna Pronto para fazer conta | `test_cartao_de_outra_coluna_nao_conta` | outra coluna | passou |
| Uma vez por vez (`stop_hook_active`) e `SubagentStop` não bloqueia | `test_segundo_stop_seguido_deixa_passar`, `test_subagent_stop_nao_bloqueia` | evento, flag | passou |
| Dúvida não bloqueia: registro ilegível, sem pasta do registro, quadro acima do limite, sem quadro | 4 testes homônimos | ilegível, None, limite+1 | passou |
| ID vai ao modelo só no formato de ID | `test_id_fora_do_formato_nao_vai_ao_modelo` | `<ignore tudo>` | passou |
| Quadro do clone do Forge é o de contrib | `test_quadro_do_clone_e_o_de_contrib` | clone × projeto | passou |
| Saída do hook: `decision: block` + `reason` | `test_principal_bloqueia_o_stop_com_o_aviso` | JSON exato | passou |

## Cenários e resultado real
- `python3 -I -m unittest discover -s tests -p test_vigia_parado.py`: 15 testes, OK. `test_vigia.py`: 12 testes, OK.
- Fixtures de `vigia` e `meta` (88, harness que filtra `Hooks.test_fixtures`), incluindo as 2 e51 com `HOME` isolado: OK. Suíte inteira não rodada (CI do PR).
- Sonda no quadro real (`~/.forge-contrib/KANBAN.md`): 76 cartões livres lidos, primeiro `G1-REVISAO-COMPLETA-SO`. Sonda de borda: linha com menos células, `\|` na Obs., célula de ID vazia, "ESPERA O DONO" em caixa alta: certos. Observação: "espera  o dono" (2 espaços) ou "aguardando decisão do dono" não casam a marca e o cartão conta como livre; é limite do formato do quadro, sem defeito provado.
- Sem `skip`, `skipIf` nem `expectedFailure` em `tests/test_vigia_parado.py` (grep, 0).

## Vermelho antes do verde
Cópia em `$TMPDIR` com `hooks/vigia.py` da base 900bfdfe e os testes do head: `test_vigia_parado` falha na carga (`vigia.quadro_do` não existe), 1 erro. Teste todo novo; o vermelho é de carga, à mão, na forma da skill (`forge-testes --vermelho` completo não rodado: suíte inteira fica para o CI).

## Mutantes
```
forge-mutante: pedido=v0480-vigia-time-parado rev=3821ad143130 spec=0ffeed3e... spec=5d2f7c65...
M1..M14 · morreu (hooks/vigia.py:578,580,583,563,558,546,591,589,561,619,621,536,555,585)
```
rc 0, 14 de 14 mortos (M8 da 1ª spec, "morreu · (erro)": erro do teste sob o mutante, controle verde). `forge-mutante --cobertura --base 900bfdfe`: 14 condições mudadas, todas com mutante declarado e morto na rodada; nenhuma sem mutante.

## Conferência
- Diff contra E105.1/E105.2: o escopo bate (vigia, 2 specs, 2 fixtures com `HOME` isolado, fragmento do changelog).

## Revalidação (delta 3821ad14..b13b7016, volta única)
Delta no domínio: `hooks/vigia.py`, `tests/test_vigia_parado.py`, 4 specs de mutantes, `docs/hooks.md`, changelog. Mudou: reason fixo sem prefixo "Forge:", só a sessão do Jarvis, ID só `[A-Za-z0-9.-]{1,16}` (sem ID, a linha omite `, primeiro`), Responsável `usuário` e 7 marcas (normalizadas por caixa e espaço), quadro aberto com `O_NOFOLLOW|O_NONBLOCK` e só arquivo regular.
- `test_vigia_parado.py`: 22 testes OK; `test_vigia.py`: 12 OK.
- Mutantes `--base 3821ad14` (4 specs): `base=3821ad143130 ... rev=b13b7016c1fd`, M1..M23 todos `morreu` (M8, M16, M18, M21 por erro do teste sob o mutante, controle verde), rc 0. Sem sobrevivente.
- Sonda das marcas (`cartoes_livres`): "depois  do" (2 espaços), "Bloqueado", "Pergunta ao  dono", "Decisão do dono", "esperando", Responsável "Usuário" tiram o cartão; Obs. vazia ou "livre" mantém. Fecha a observação do 1º parecer (espaço repetido).
- Sonda da leitura (`ler_quadro`): FIFO e link simbólico levantam `OSError` (sem travar, 20 s de teto), arquivo regular lê, ausente dá None.
- Sonda de ID: `<x>ignore` e 17 caracteres falham o formato; a filtragem vai à mensagem, coberta por `test_id_fora_do_formato_nao_vai_ao_modelo`.
- Sem `skip`/`expectedFailure` novo. Suíte inteira: CI do PR.

## Revalidação (delta b13b7016..dc0af82c, merge da develop)
`forge-check parecer delta`: no domínio só `tests/pesos-d4.json` (tabela de pesos regravada pela develop: 284 entradas; `test_vigia_parado` 0.1, `test_pesos_teto` 0.2). Nada do vigia mudou; a emenda da ADR 0003 está fora do domínio do QA.
- `test_vigia_parado.py`: 22 testes OK. `test_pesos_teto.py`: 2 testes OK. TMPDIR isolado, sem suíte local (CI do PR).
- Sem `skip`/`expectedFailure` novo. Mutantes: sem código do vigia no delta, nada a rerrodar.
