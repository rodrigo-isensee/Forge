---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-prepush-testes
commit: 9add4d15d59a0ff569d50107464582e896a28917
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-23
---
# QA: v0478 (E137.27, testes do envio local, PR #824)

Base 0e59c446, head 9add4d15 (código testado em 94c0e13e; o head só soma o parecer do review). Mudança só em `tests/test_pre_push_afetados.py`, `tests/test_pre_push_leve.py` e o fragmento do changelog; `.githooks/pre-push` e `scripts/suite-paralela.py` intocados. Sem especificação de UX nem contrato de API: as obrigações são as duas guardas que os testes dizem provar (E137.4).

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Checagem barata reprova sem esperar a trava (`R-QA`, ENVIO-LEVE) | `ChecagensBaratasAntesDaTrava.reprova_sem_esperar` (via `test_sintaxe_python_reprova_antes_da_trava` e os demais), herdado por `NeutralidadeECaminhoCedo` | trava presa por `flock` de fora; registro do `flock` falso vazio; sem "entrou" nem "esperando a vez" | passou; mutante M4 morreu |
| Suíte com processo morto por sinal não grava prova de árvore verde nem carimbo K6 | `EnvioLeve.test_suite_inteira_com_processo_morto_nao_anota_prova_nem_carimbo` | opt-in `1`, SIGKILL no teste; rc 1, "morto pelo sinal 9", nenhuma prova de árvore verde, sem o carimbo K6 | passou; mutantes M1, M2, M3 morreram |

## Cenários e resultado real
- `test_pre_push_afetados.py` (`ChecagensBaratasAntesDaTrava`, `NeutralidadeECaminhoCedo`): 11 testes, OK, 1 pulado (shellcheck fora do PATH; pulo do próprio teste, anterior ao PR), 10,6 s.
- `test_pre_push_leve.py`: 9 testes, OK, 4,7 s.
- O teste do `flock` falso troca o relógio por prova de estado: o registro de chamadas do `flock` é afirmado vazio, a trava segue com o segurador (`poll()` None, `flock -n` falha). Não há espera fixa nem limite de tempo.
- Sem suíte local; a inteira roda no CI do PR (`R-QA`).

## Vermelho antes do verde
`forge-testes --vermelho 0e59c446… --modulos test_pre_push_afetados,test_pre_push_leve`: `contagem: não prova (passa na base)=44; pulado=1`, `nenhum teste prova a mudança`, rc 0 na ferramenta. Esperado: o PR não muda código de produção, então a base passa os mesmos testes; a ferramenta não distingue teste que enfraquece a guarda. A prova de que os testes falham sem a guarda vem da mutação do hook e da suíte paralela, abaixo.

## Mutação (guarda mudada na cópia; spec minha, 4 mutantes)
Saída de `bin/forge-mutante` (spec fora da árvore, no scratchpad):
```
forge-mutante: pedido=v0478 rev=9add4d15d59a spec=e7743fa328b9dedbe80ef8860e0d2482655f0bb519d377a32fc7b8cef49cdcec
M1 · morreu · .githooks/pre-push:648
M2 · morreu · scripts/suite-paralela.py:614
M3 · morreu · scripts/suite-paralela.py:794
M4 · morreu · .githooks/pre-push:396
```
- M1: `rc != 0` do hook vira `rc == 255` (suíte falha sem barrar e grava prova). M2: `returncode != 0` vira `> 0` (sinal não vira causa). M3: `erros or falhas or erros_t` perde `erros` (guarda não reprova). M4: `flock -w 1` na trava antes das checagens baratas.
- Na 1ª rodada, M1 foi escrito errado por mim (`-ne 255`, ainda verdadeiro com rc 1) e sobreviveu; era mutante equivalente por erro meu, corrigido para `-eq 255` e morreu. Registrado para a evidência não parecer ajustada.

## Observações
- O review (94c0e13e) fez a sonda S1 equivalente a M4; as duas coincidem.
- O campo `commit:` segue o head pedido no brief (9add4d15); o código testado é o 94c0e13e (`Revisar-sha:`).
