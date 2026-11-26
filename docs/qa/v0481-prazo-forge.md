---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-prazo-forge
commit: ecb13af6dac68a1f57c173c7000e03bbb5a71054
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-25
---
# QA: v0481 prazo-forge (#888, classe C), delta 4ab16b74..ecb13af6 (E7.51)

- ci: ecb13af6dac68a1f57c173c7000e03bbb5a71054 verde

Escopo: `git diff 4ab16b74..ecb13af6` e `forge-check parecer delta` (sem o que veio da develop). O código de produção do PR não mudou neste delta: a volta traz a develop (#885, que mexeu em `hooks/conformidade.py` e `tests/test_hooks.py`, revisados no PR de origem), regenera `docs/hooks-fixtures.md` (3590 fixtures, único conflito do merge) e acrescenta a isenção em `tests/mutantes/v0481-prazo-forge.json`. Parecer anterior (4ab16b74, aprovado) lido; os critérios dele seguem valendo, sem teste novo ou mudado do PR neste delta.

## Critério → teste → resultado
| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Guarda do `prazo_vencido` (só o PreToolUse recusa sem marcador; PostToolUse nunca) | M1 a M5 da spec `v0481-prazo-forge.json` | evento PostToolUse, critico None | morreram |
| Isenção da guarda reescrita tem motivo verdadeiro | leitura de `hooks/_comum.py:2924` e `--cobertura` | n/a | confere |
| Prazo da sessão e do registro (M14 a M22) | já provados em 4ab16b74; código inalterado | resta <= 0 | herdado, sem mudança no delta |

## Resultado real
- **Isenção verdadeira.** A guarda `critico is None and evento != "PreToolUse"` não foi apagada: virou `recusa = evento != "PostToolUse" and (critico is not None or evento == "PreToolUse")` (`hooks/_comum.py:2924`, em `prazo_vencido`), que o M2 cobre e que morre. A razão da isenção (De Morgan, a guarda reescrita) está certa.
- `bin/forge-mutante --cobertura --base 34ab6714`: a linha `isenta · hooks/_comum.py:2875(base)` sai com o motivo; as demais condições saem `coberta`, e nenhuma `descoberta` nem `isenta velha`.
- `bin/forge-mutante tests/mutantes/v0481-prazo-forge.json --processos 2` no head: `pedido=v0481-prazo-forge rev=ecb13af6dac6`, M1 a M8 `morreu` (M4 por erro do teste declarado, que passa sem o mutante), rc 0, nenhum sobrevivente.
- Afrouxa na margem (só as travas de recurso desistem mais cedo sob carga; as de segurança continuam bloqueando): aceito pelo dono em 25/11 21:15; o rótulo `afrouxa-regra` está no PR.
- Local, só o que o delta toca: os mutantes acima. Os módulos de teste rodam inteiros no CI.

## CI do PR (PARECER-LE-O-CI)
`gh pr checks 888`, head `ecb13af6` (`headRefOid` igual): as 10 partes da suíte (3.12 e 3.14, 5 de 5), `bateria (passos)`, `bateria (python 3.14)`, `bateria (verificações longas)`, `instalação (python 3.14)`, `teto de pulados` (3.12 e 3.14) e `árvore já provada na develop` estão `pass`. Falham só os que esperam o parecer ou o rótulo: `bateria (pareceres)`, `bateria` e `catraca`. O log da `catraca` pede o rótulo `afrouxa-regra` depois do último push para `hooks/_comum.py` e `hooks/conformidade.py` (decisão do dono, tratada no portão), com o aviso "valor esperado trocado" em `test_carga_explica_a_recusa_so_pelo_vigia_do_prazo_longo_com_disputa_provada`, que não barra.
