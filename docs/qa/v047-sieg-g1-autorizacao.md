---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-sieg-g1-autorizacao
commit: 580b6c34c8cc46ae8270cc42017427d82f64b784
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-17
---
# QA: v047 G1.0-G1.1, `forge-check autorizacao ler` e ADR 0018 (head 580b6c34)

Escopo: `bin/forge_autorizacao.py`, a ligação em `bin/forge-check`, `tests/test_autorizacao.py`, os 7 mutantes e a ADR 0018 (itens 1, 2, 5 a 7 e 12; etapa G1.1 do corte). Sem PR aberto, então não há check-run `bateria` do sha; a suíte inteira não foi rodada (brief). Rodei só os testes dos arquivos tocados.

## Achados
- A1 (bloqueante) tests/test_autorizacao.py:18 · R-QA: `forge-testes --vermelho 86ac0fcb --modulos test_autorizacao` sai 2 (sem veredito) duas vezes; o módulo carrega `bin/forge_autorizacao.py` no import e quebra na base. Sem rc 0 não há vermelho. Carregue em setUpModule/setUpClass.
- A2 (recomendado) bin/forge_autorizacao.py:46 · única linha de guarda mudada sem mutante (`--cobertura`): `e.strerror or e` na mensagem de erro de leitura. Quase equivalente; declare-o em `equivalente` com justificativa ou mate-o com `assertIn` do texto do erro.

## Critério → teste → resultado
Obrigações da ADR 0018 (itens 5 a 7, 12 e etapa G1.1); sem `CA-n`, a UX não se aplica.
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| G1.1 integridade e leitura: mensagem inteira, validade no fuso e em UTC | `Ler.test_integra_mostra_a_mensagem_inteira_validade_no_fuso_e_em_utc` | 11:00 UTC exato = vencida; 10:59 = ativa | passou |
| evento adulterado (corpo, gravador, ato, alvos, inicial, autoriza, campo ausente, pedido) | `test_evento_adulterado_ou_fora_da_forma` | cada campo fora da forma | passou |
| link, pasta, UTF-8 inválido, campo repetido, sem linha vazia: erro, nunca íntegro (item 7, falha fechada) | `test_evento_ilegivel_e_erro_e_nada_e_integro_por_ele` | arquivo não comum | passou |
| pasta que é link, nome fora da forma | `test_pasta_que_e_link_e_nome_fora_da_forma_sao_erro` | `A-1.bak` | passou |
| pasta ausente, só concessão listada | `test_pasta_ausente_nada_e_so_concessao_e_listada` | pasta vazia ou ausente | passou |
| só vale o gravado pelo `forge-check` carregado | `test_forge_check_autorizacao_ler_aceita_so_o_gravado_por_ele` | hash do gravador | passou |
| item 6, A6 e D1: fala 21:00 local = dia seguinte em UTC; 48 h; 7 dias; uso único | `test_validade_em_utc_a6_e_teto_d1_...` | 10:59/11:00, 23:59/00:00, fuso inválido, hora sem Z | passou |
| itens 7 e 9: retirada, uso, fechamento do pedido, confirmação (E2.662) | `test_retirada_uso_fechamento_do_pedido_e_confirmacao` | confirmação antes da fala, hash errado, outro Id, texto com palavra a mais | passou |

## Cenários e resultado real
- `python3 -m unittest tests.test_autorizacao` (TMPDIR, sem `-I`): 8 testes, OK.
- ADR 0018 contra o código: G1.1 diz só leitura, nada barra; `ler` sai 1 só com adulterada ou erro e não grava nada. Confere. Sem teste de rótulo no hook (é G1.3).
- Mutantes: `bin/forge-mutante tests/mutantes/v047-sieg-g1-autorizacao{,-2..-7}.json`, rc 0, 55 morreram, nenhum sobrevivente, nenhum equivalente, rev=580b6c34c8cc.
- `forge-mutante --cobertura --base 86ac0fcb9495d11343049b8cdecb25419aed1cf9`: tudo coberto, exceto `sem mutante · bin/forge_autorizacao.py:46` (A2).
- Vermelho (saída colada):
```
vermelho: base=86ac0fcb9495 head=580b6c34c8cc módulos=test_autorizacao (restrito por --modulos)
revertidos à base: bin/forge-check, bin/forge_autorizacao.py, changelog.d/v047-sieg-g1-autorizacao.md, docs/adr/0018-autorizacao-do-dono-gravada.md, docs/adr/README.md, docs/security/v047-sieg-g1-autorizacao.md
test_autorizacao · sem veredito (prazo, sinal ou executor sem registro em B)
sem veredito: volta ao autor; não vale como vermelho nem como já falhava.   (rc=2)
```
  Prova manual (não substitui a ferramenta): na base, `python3 -m unittest tests.test_autorizacao` cai em `FileNotFoundError: .../bin/forge_autorizacao.py` na linha 18 do teste, então a base falha; o que falta é a ferramenta registrar isso por teste (A1).
- Suíte inteira: não rodada aqui; o CI do PR a roda.
