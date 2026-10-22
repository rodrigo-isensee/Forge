---
tipo: review
contrato: 1
pedido: impl-d4-textos-dono2
branch: melhoria/impl-d4-textos-dono2
commit: d6da6d539de472120b3cfcfc3de0b3aa2001ddb9
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-22
---
# Review: impl-d4-textos-dono2 (RET-TEXTOS-DONO2, E1.1)

Code review (R-REVIEW) da entrega inteira, `38c58247fdae5482ed441db4dd21bff4d55471d7..d6da6d539de472120b3cfcfc3de0b3aa2001ddb9`: 3 commits da branch (2a96c99 F7, 8c1b650 F10, be4a398 fragmento) e o merge da `develop` (`af79bef`). O pedido de origem se perdeu; o escopo lido é o dos commits e do fragmento `changelog.d/impl-d4-textos-dono2.md` (suposição registrada no pedido RET-TEXTOS-DONO2). Segurança: parecer próprio do `forge:security-engineer` em `docs/security/` (toca hook), não refeito aqui.

## Achados
- A1 (recomendado) hooks/vigia.py:270 · Gravação feita por subagente não aparece na transcrição principal: o Jarvis que delega o registro do pedido recebe o aviso mesmo com a lista gravada. Registrar em docs/hooks.md, "O que não detecta", ou contar o Agent cujo prompt cita docs/pedidos/.
- A2 (recomendado) hooks/vigia.py:247 · Bash de escrita conta como registro se o destino aparece em qualquer parte do comando (ex.: ler docs/pedidos/x.md e redirecionar para outro arquivo), o que cala o aviso. Heurística aceitável para aviso; registrar o falso negativo em docs/hooks.md.
- A3 (recomendado) tests/test_textos_dono_f10.py:25 · O teste proíbe para sempre "diário de retomada" em R-DECISAO e no Jarvis, mas docs/retomada-de-sessao.md (vigente, cartões R-3 a R-7) prevê esse diário; quando ele existir, o teste barra a volta da citação. Amarrar a proibição à ausência do diário ou citar o cartão no docstring.
- A4 (recomendado) hooks/vigia.py:234 · O filtro de lembrete olha o texto já juntado: mensagem em blocos cujo primeiro bloco começa com "<" (lembrete ou comando anexado) descarta também a lista do dono nos blocos seguintes. Filtrar bloco a bloco e cobrir com uma fixture de blocos mistos.

## Conferência
| Item | Veredito | Evidência |
|---|---|---|
| Merge da `develop` (d6da6d5) | ok | Merge sem conflito: `git show --cc d6da6d5` sem hunks; pais `be4a398` e `af79bef` (develop atual). |
| F7 (2a96c99) | ok | `agents/jarvis.md:39` e `docs/economia-de-tokens.md`, regra 1, com a mesma condição ("só quando a entrega muda interface"); teste `tests/test_textos_dono_f7.py` amarra os dois textos. Faz o que diz, nada além. |
| F10, textos (8c1b650) | ok | `R-DECISAO` e o Jarvis passam a falar de "pedido, lista ou decisão do dono", tiram a citação ao diário (não implementado: não há skill nem CLI de retomada) e vedam o scratchpad; `verificada_por` cita o vigia. |
| F10, vigia (8c1b650) | ok | Só no `Stop` principal, deslocamento próprio (`entradas`) para o `SubagentStop` não consumir as linhas, deduplicação por id (`listas`, limitada a `LIMITE_IDS`), aviso de gravidade 1, nunca bloqueio. Texto do dono não vai à saída (`TEXTOS_FIXOS`) nem ao log (só contagem e id saneado). Regex de item sem repetição aninhada; leitura limitada a 64 KB por mensagem. Erros seguem o tratamento do hook (sai 0, `erros.log`). |
| Fixtures (13 novas em `tests/hooks/vigia/`) | ok | Cobrem: aviso, 2 itens (silêncio), Write/Edit/Bash nos três destinos, lembrete de sistema, resultado de ferramenta, blocos de texto, não reavisar, SubagentStop ignorado e antes do Stop. O teste de fixtures afirma mínimo (`minimo(..., 460, ...)`). |
| Documentação | ok | `docs/hooks.md` descreve a checagem, os limites e o que vai ao log; docstring do `vigia.py` atualizada. |
| `changelog.d/impl-d4-textos-dono2.md` | ok | Nome bate com a branch sem prefixo; seções `Alterado` e `Adicionado`; `CHANGELOG.md` não editado. |
| `tests/config.json` | ok | Não tocado: nenhum invariante afrouxado. |
| Commits | ok | Conventional Commits em português, um por mudança coerente, com o ID do pedido. |
| R-NEUTRO, R-CUSTO | ok | Nada de projeto nem de stack; só biblioteca padrão, sem serviço pago. |
| Ferramentas | ok | `python3 -m unittest discover -s tests` e `scripts/validar-plugin.sh` na worktree sobre d6da6d5: resultado no relatório da etapa (provas PQ-2 e PQ-3 do brief). |

## Parecer
Aprovado. A entrega faz o que os commits e o fragmento dizem, com a privacidade do texto do dono tratada no código e nas fixtures, e o merge da `develop` não exigiu resolução. Os quatro achados são recomendados (limites da heurística a documentar ou estreitar e um teste de ausência rígido demais) e não bloqueiam; podem ir numa volta futura ou como cartão. Segue para o QA (E1.3).
