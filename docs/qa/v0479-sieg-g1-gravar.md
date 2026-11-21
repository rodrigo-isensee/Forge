---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-sieg-g1-gravar
commit: 2a0e46204eb6e731fec268e2d01fa32d142479eb
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-21
---
# QA: v0479-sieg-g1-gravar (E90.5)

Escopo: `forge-check autorizacao gravar` (G1.2a, ADR 0018) e a concessão solta de alvo `item:` (PV-A2), no head 2a0e4620, contra a base 15936278. Sem suíte local; a suíte inteira é o check-run `bateria` do PR.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Corpo = mensagem inteira do dono, byte a byte | `MensagemInteira.test_corpo_e_a_mensagem_inteira_...` | mensagem única, sem opção de texto | passou |
| Só a fala digitada na sessão principal | `test_so_a_mensagem_digitada_pelo_dono_...` | 12 origens inválidas, uuid ausente/repetido, link, teto | passou |
| Uma concessão por mensagem | `test_a_mesma_mensagem_so_gera_uma_concessao` | repetição | passou |
| Escopo e pendência pelo texto todo | `EscopoPeloTextoTodo.*` | marcas de negação, recorte, ato diferente | passou |
| Validade e conflito | `Validade.*` | mapa fechado, fim mais cedo | passou |
| PV-A2: solta nunca nasce ativa | `ConcessaoSolta.*` | commit fora do head, sem ramo, sha inválido | passou |
| Leitor lê o que o gravar grava | `test_forge_check_autorizacao_gravar_grava_o_que_o_ler_aceita` e ponta a ponta abaixo | ativa, pendente, recusada | passou |

## Provas
- Sem skip: `grep -nE "skip|expectedFailure" tests/test_autorizacao_gravar.py` vazio; 20 testes.
- Vermelho antes do verde (`forge-testes --vermelho 159362786f6f47913139fdf47f892ef07e9c1d07 --modulos test_autorizacao_gravar`): `vermelho: base=159362786f6f head=2a0e46204eb6`; contagem: prova (API ausente)=18; prova (asserção)=1; não prova (passa na base)=1. O que passa na base é `test_nao_existe_opcao_de_texto_no_comando` (guarda negativa: opção de texto que nunca existiu, rc 2 nos dois lados); com 19 provas e nenhum caindo no HEAD, o veredito vale.
- Mutantes (`bin/forge-mutante <spec> --processos 3`, uma chamada por spec, rc 0 em todas): `v0479-sieg-g1-gravar.json` M1-M8, `-2` M9-M16, `-3` M17-M24, `-4` M25-M30, `-5` M31-M38, `-6` M39-M46: 46 de 46 `morreu`, nenhum sobrevivente nem equivalente. Os "(erro)" (M21, M31, M32, M35, M44, M45) são morte com o controle verde.
- PV-A2: `tests/mutantes/v0479-pv-a2-concessao-3.json` (M17-M24, com M24 já editado para `return (git(...`) e `-4.json` (M25-M32, com M26): todos `morreu`, rc 0.
- `forge-mutante --cobertura --base origin/develop`: rc 0; todas as condições Python mudadas `coberta` ou `isenta` com motivo; únicos avisos: `spec editada · v0479-pv-a2-concessao-3.json` (M24, rodado acima) e `não coberto: tests/pesos-d4.json` (dado, não guarda).
- Ponta a ponta pelo CLI real, em repositório descartável com a fala no instante atual: `autorizacao gravar` de "pode mesclar a main 0.47.3" saiu `A-1 gravada · ativa`; de "... 0.47.4, mas só depois do review", `A-2 gravada · pendente-confirmacao (palavra fora do vocabulário ...)`; de fala com `isSidechain`, `autorizacao: recusada: a mensagem não é uma só, digitada pelo dono nesta sessão`, rc 1, sem `A-3` nem `M-<uuid>` gravados. Depois, `autorizacao ler`: `A-1 · ativa`, `A-2 · pendente (mesmo motivo)`, corpos iguais à fala, `0 adulterada(s), 0 erro(s) de leitura, 1 ativa(s)`, rc 0. A recusada não aparece no leitor. A mesma fala com data de 18/11 saiu `vencida` no leitor (validade de 48 h), como esperado.
- O teste `test_raiz_depois_do_subcomando_e_git_isolado` não foi rodado (falha na base, ambiente, como o brief informa).
