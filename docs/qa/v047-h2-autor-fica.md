---
tipo: qa
contrato: 1
pedido: v0474
branch: melhoria/v047-h2-autor-fica
commit: 6d73898a54d405cae438ed76d745fd32bc2436f4
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-17
---
# QA: v047-h2-autor-fica

Etapa E2.30, H2-AUTOR-FICA-ATE-O-MERGE (classe C, `hooks/agentes.py`). Intervalo `e2880b42..6d73898a`. Sem especificação de UX nem contrato de API: as obrigações são as da descrição do H2 (E2.10) e as condições novas do diff. Acessibilidade e E2E: n/a.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| H2-a: o `SubagentStop` grava o autor e as branches de escrita | fixtures `autor-fim-grava-o-autor`, `autor-fim-sem-escrita-nao-grava` | sem escrita: não grava | passou |
| H2-b: o disparo de escrita na branch do autor avisa sem recusar (código 0) | fixture `autor-retomavel-avisa`; `test_dois_avisos_saem_num_json_so` | aviso no stderr e no `systemMessage`, um JSON só | passou |
| H2-c: lápide, ativo, prazo vencido, outra branch e parecer não avisam | fixtures `autor-com-lapide-libera`, `autor-ativo-libera`, `autor-expirado-libera`, `autor-outra-branch-libera`, `autor-parecer-libera`; `test_lapide_e_ativo_tiram_o_autor_do_aviso` | prazo `expiracao_horas`, lápide, ativo | passou |
| H2-d: `autores` ilegível ou id fora da forma vale vazio, nunca recusa | fixtures `autor-ilegivel-libera`, `autor-id-invalido-libera`; `test_id_fora_da_forma_nao_vira_autor` | tipo errado, id inválido | passou |
| H2-e: autor novo troca só o anterior da mesma branch; retomada herda as branches e renova o prazo | fixtures `autor-fim-troca-o-anterior`, `autor-fim-retomada-herda`; dois testes de `Autores` | outra branch preservada | passou |

## Cenários e resultado real
Ambiente: clone `~/.forge-contrib/wt/v047-h2-autor-fica-E230`, head `6d73898a`, `TMPDIR=/tmp/claude-0`, máquina com carga 20 a 30.

- Mutantes (`bin/forge-mutante` nas duas specs, 14): todos morreram, rc 0. M11 morreu por erro do teste declarado (a spec declara isso). `--cobertura --base e2880b42`: 10 linhas `coberta`, nenhuma `não coberta`, nenhuma condição sem mutante; nada isento.
- Vermelho antes do verde: `forge-testes --vermelho e2880b42 --modulos test_hooks_agentes_autor`, saída 0: 5 testes provam por API ausente, `test_fixtures_do_pedido` prova por asserção, nenhum cai no HEAD.
- `python3 -I scripts/indice-fixtures.py --conferir`: `docs/hooks-fixtures.md: em dia`.
- `test_hooks_agentes_autor.py`: 6 testes OK.
- `test_hooks.py` inteiro (141 testes, 79 min sob carga): 3 falhas, do tipo prazo; o ramo `aviso` novo do `executar_fixture` roda nos fixtures `autor-*` e passa.
- `test_prazo_do_merge` (hook parecer, fora do diff): falha de ambiente, não do diff. Sob carga 21 a 29, `-k test_prazo_do_merge` falha com `R-REVIEW: o hook não decidiu em 8 s` (`failures=3`), e falha igual na base `e2880b42` (cópia via `git archive`, mesma carga, `failures=3`). `git diff e2880b42 HEAD` não toca `hooks/parecer.py`, `hooks/comum.py` nem `hooks.json`. O teste depende de tempo de parede (git lento de 4 e 9 s contra prazos de 3 e 8 s). Nas duas rodadas `-k test_fixtures` o único fixture que caiu foi `pesado/mesma-sessao-libera`, por prazo de 120 s estourado, também fora do diff; nenhum fixture `agentes/` falhou.

## Observações (sem bloqueio)
- O brief diz 12 fixtures `autor-*` com 2 avisando; só `autor-retomavel-avisa` traz `aviso` no esperado (1 avisa, 11 liberam). O segundo aviso (D3 + H2 juntos) é coberto por `test_dois_avisos_saem_num_json_so`. Contagem do brief imprecisa, cobertura completa.
- O `test_prazo_do_merge` e o fixture `pesado` não passam com a máquina saturada; no CI (`bateria` do mesmo sha) o veredito vale.
