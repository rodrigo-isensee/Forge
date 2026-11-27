---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-f4-vigia-fluxo
commit: dd25e4a821e0e284215c2916f78147edbd285e7e
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-27
---
# QA: v0481 F4 (vigia sem rede), volta 2, delta 04b508f6..dd25e4a8

- ci: dd25e4a821e0e284215c2916f78147edbd285e7e verde
  (`gh pr checks 931` no head: suíte partes 1 a 5, python 3.14, passos, verificações longas, instalação, teto de pulados e `catraca` verdes; `bateria` e `bateria (pareceres)` esperam os pareceres, fora da conta.)

## Critério → teste → resultado
Sem `CA-n`; as obrigações vêm de E34.10 (achado A1 da volta 1 e A8/S1/S2 dos outros portões), E34.6 e R-TETO.

| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| A1: toda spec confere com a fonte (`de` único em M7 e M8) | `test_forge_mutante.ConferirTodas` (5 testes) | `de` único | passou |
| Erro de escrita da lista não sobe ao `status` nem ao `proximo` | `GravacaoDaLista.test_status_e_proximo_seguem_com_a_gravacao_falha` | OSError 30 (somente leitura) | passou |
| Diretório no caminho da lista: nada sobe, pasta intacta | `test_diretorio_no_caminho_nao_sobe_nem_deixa_temporario` | destino não regular | passou |
| Disco cheio: lista anterior fica, temporário sai | `test_disco_cheio_mantem_a_lista_anterior_e_tira_o_temporario` | OSError 28 no meio da escrita | passou |
| Temporário que não sai também não sobe | `test_temporario_que_nao_sai_tambem_nao_sobe` | PermissionError no unlink | passou |

## Cenários e resultado real
- Afetados locais: `python3 -m unittest test_hook_vigia_f4 test_proximo test_forge_status_estado` (em `tests/`): 94 testes OK; `tests.test_forge_mutante.ConferirTodas`: 5 OK.
- Mutantes, `bin/forge-mutante --processos 3 --base 04b508f60417897819537305b78a9e4db5258971` (`rev=dd25e4a821e0`): `v0481-f4-vigia-fluxo-7.json` M49 a M52 `morreu` (M50 e M52 por erro do teste declarado, com o controle verde; M51 morreu limpo); `v0481-s1-status.json` M1 a M8 `morreu` (M7 e M8 com o `de` agora único). Sem sobrevivente nem sem veredito. Cada linha de guarda mudada em `bin/forge_estado.py` (`except OSError`, `unlink`, `except OSError` interno) tem o seu mutante (M50, M51, M52).
- Vermelho, `bin/forge-testes --vermelho 04b508f6 --modulos tests.test_hook_vigia_f4`: `vermelho: base=04b508f60417 head=dd25e4a821e0`; os 4 testes novos de `GravacaoDaLista` saem `H=ok · B=erro · sem veredito`, rc 2. A ferramenta classifica o erro da base (OSError sem captura subindo) como sem veredito, não como falha provada; registro o rc 2 sem tratá-lo como vermelho da ferramenta. A prova vermelha vem dos mutantes M50 a M52, que desfazem o `except` e derrubam os mesmos testes. Não bloqueia.
- Não rodei a suíte inteira (G3); o CI do head é a evidência das demais partes.
