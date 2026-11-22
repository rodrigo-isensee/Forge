---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-k170-movimento
commit: 0000c1bfedc51ec787fc29791f385e85b33bf3e4
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-21
---
# QA: v0479-k170-movimento (E77.4)

K170: `forge-check movimento --de Bloqueado` só vale se a última linha do cartão no `historico.md` o pôs em Bloqueado; sem ela, recusa com rc 2 e nada gravado.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| K170: sem histórico, recusa e não cria o arquivo | `MovimentoDeBloqueado.test_sem_historico_recusa_e_nao_cria_o_arquivo` | cartão sem movimento | passou |
| K170: último movimento fora de Bloqueado, recusa | `MovimentoDeBloqueado.test_ultimo_movimento_fora_de_bloqueado_recusa` | última linha diferente de Bloqueado | passou |
| K170: entrada registrada, aceita | `MovimentoDeBloqueado.test_com_a_entrada_registrada_aceita` | entrada registrada | passou |

## Cenários e resultado real
- `python3 -I -m unittest discover -s tests -p test_sobreposicao_quadro.py` (TMPDIR criado): Ran 65 tests, OK. Sem suíte inteira (brief).
- Vermelho (`forge-testes --vermelho 5e3ca873 --modulos test_sobreposicao_quadro`): `vermelho: base=5e3ca873fb65 head=0000c1bfedc5`; revertidos à base: `bin/forge-check`, `changelog.d/v0479-k170-movimento.md`; os dois testes de recusa dão H=ok, B=falha, `prova (asserção)`; `contagem: não prova (passa na base)=63; prova (asserção)=2`; rc 0.
- Mutação (`bin/forge-mutante tests/mutantes/v0478-k170-movimento.json`): M1..M6 `morreu`, rc 0, sem sobrevivente. A lista cobre as 6 linhas de guarda mudadas em `bin/forge-check` (condição de `--de`, última linha, comparação com Bloqueado, mensagem, recusa antes de gravar, rc 2).
