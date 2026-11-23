---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-sieg-g1-gravar
commit: d7c1a53b259e6f2ce980cbe05a2986eeed958be6
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-23
---
# QA: v0479-sieg-g1-gravar (E90.9)

Refeito no head d7c1a53b (Decisão 1 do dono, sem exceção), delta desde 2a0e4620; substitui os pareceres de QA anteriores (63965b38, b18f7ec4). Escopo: `forge-check autorizacao gravar` (G1.2a, ADR 0018) com a correção do A1 (resumo de compactação), transcrição só da sessão em curso (`CLAUDE_CODE_SESSION_ID`, `~/.claude/projects`), `origin` humano positivo, Hora-da-fala no futuro ou além de 48 h, prazo local sem fuso nasce pendente. Sem suíte local; a suíte inteira é o check-run `bateria` do PR.

## Achados
- A1 (recomendado) tests/test_autorizacao_gravar.py:1 · `forge-testes --vermelho 2a0e4620` dá "sem veredito" (a base erra com TypeError: `cmd_gravar` sem o parâmetro `agora`, nos testes que o usam); a prova de vermelho vale pelos 54 mutantes mortos, não pela ferramenta

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Corpo = mensagem inteira do dono | `MensagemInteira.test_corpo_e_a_mensagem_inteira_...` | mensagem única | passou |
| Só a fala digitada na sessão em curso (A1 corrigido) | `test_so_a_mensagem_digitada_pelo_dono_na_sessao_principal`, `TranscricaoDaSessaoEmCurso.*` | origens inválidas, resumo de compactação, origin ausente, outra sessão, fora de `~/.claude/projects`, pasta que desvia | passou |
| Uma concessão por mensagem | `test_a_mesma_mensagem_so_gera_uma_concessao` | repetição | passou |
| Escopo e pendência pelo texto todo | `EscopoPeloTextoTodo.*` | negação, recorte, ato diferente | passou |
| Validade e conflito | `Validade.*` (fala no futuro e > 48 h; prazo local pendente) | mapa fechado, 48 h, futuro | passou |
| PV-A2: solta nunca nasce ativa | `ConcessaoSolta.*` | commit fora do head, sem ramo | passou |
| Leitor lê o que o gravar grava | `test_forge_check_autorizacao_gravar_grava_o_que_o_ler_aceita` | ativa, pendente, recusada | passou |

## Provas
- Testes: `python3 -m unittest tests.test_autorizacao_gravar tests.test_autorizacao` no head: 43 testes, OK. `grep -nE "skip|expectedFailure"` no arquivo do gravar: vazio.
- Vermelho: `forge-testes --vermelho 2a0e46204eb6e731fec268e2d01fa32d142479eb --modulos test_autorizacao_gravar` saiu `vermelho: base=2a0e46204eb6 head=d7c1a53b259e`, `contagem: não prova (passa na base)=2; sem veredito=24` (A1). Conferido à mão numa cópia com o head e o `bin/forge_autorizacao.py` de 2a0e4620: `TypeError: cmd_gravar() takes 3 positional arguments but 4 were given`, todos os testes que gravam erram na base.
- Mutantes (`bin/forge-mutante <spec> --processos 3`, rc 0): `-7.json` M47-M54 e `v0479-sieg-g1-gravar.json` M1-M8 (spec editada para o código novo), saída `rev=d7c1a53b259e`: 16 de 16 `morreu`; `-2` a `-6`: 38 `morreu`. Total 54 de 54, nenhum sobrevivente.
- `forge-mutante --cobertura --base 159362786f6f47913139fdf47f892ef07e9c1d07` (`base=159362786f6f mb=159362786f6f rev=d7c1a53b259e`): nenhuma condição `não coberta`; `isenta` bin/forge_autorizacao.py:359 com motivo; avisos conhecidos `spec editada · v0479-pv-a2-concessao-3.json` e `não coberto: tests/pesos-d4.json` (dado, não guarda).
- `forge-check parecer delta`: `revalida: sim` (o último parecer era reprovado); delta lido no diff de `bin/forge_autorizacao.py`, das specs de mutante e de `tests/test_autorizacao_gravar.py`.
