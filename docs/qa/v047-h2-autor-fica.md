---
tipo: qa
contrato: 1
pedido: v0474
branch: melhoria/v047-h2-autor-fica
commit: 482ee7c773597cad435a49acbee8fb535b802493
parecer: reprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 2
bugs_baixos: 0
data: 2026-11-17
---
# QA: v047-h2-autor-fica

Etapa E2.30, H2-AUTOR-FICA-ATE-O-MERGE (classe C, `hooks/agentes.py`). Intervalo `e2880b42..6d73898a`. Sem especificação de UX nem contrato de API: as obrigações são as da descrição do H2 (E2.10) e as condições novas do diff. Acessibilidade e E2E: n/a.

## Achados
- A2 (bloqueante) tests/mutantes/trava-agente-morto-3.json:M19 · o diff mexeu em hooks/agentes.py e deixou duas specs antigas fora da fonte: M19 (`de` agora aparece 2 vezes, ambíguo) e v0440-decisoes-2.json:A4 (`if avisos:\n        texto = mensagem(` não existe mais). `python3 -m unittest tests.test_forge_mutante.ConferirTodas` falha no head (failures=1); a bateria do CI cai. Alinhar as duas specs no mesmo commit (agente: dev da stack do Forge)
- A3 (bloqueante) tests/test_hooks_agentes_autor.py:35 · `forge-testes --vermelho e2880b42 --modulos test_hooks_agentes_autor` sai 2 (sem veredito): na base `PeloHook.test_fixtures_do_pedido` dá erro (JSONDecodeError, hook sem saída JSON em autor-retomavel-avisa e nas duas fixtures de reserva), não asserção. Sem veredito não vale como vermelho; o autor deve fazer o teste falhar por asserção na base ou isolar o caso

## Revalidação do A1 (rodada anterior)
Resolvido: id não texto em lápide e em registro não perde a reserva. Fixtures `autor-lapide-id-lista-reserva`, `autor-registro-id-objeto-reserva`, `autor-lapide-id-lista-segundo-recusa` e 5 `autor-retom*` entram; `test_hooks_agentes_autor` 10 testes OK no head. Mutantes: 22 em 3 specs, todos morreram (M11, M14, M16, M17, M21 por erro do teste declarado, que a spec declara).

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

## Lacuna do plano e prova do achado
Os fixtures `autor-*` cobrem `autores` ilegível e id inválido de autor, mas nenhum põe `id` não texto em lápide ou em agente ativo, o caminho que `autores_retomaveis` percorre com `set`. Sonda no head: `autores_retomaveis([{'id': A, 'desde': 1.0, 'escrita': ['melhoria/a']}], [], [{'id': ['x']}], {'melhoria/a'})` dá `TypeError: unhashable type: 'list'`, depois do `agentes.append` e antes do `gravar_json`, e o hook libera com 0. Mesmo defeito do A1 do parecer de segurança (E2.29). Correção no agente da stack (developer do H2); depois, fixtures `autor-*` com lápide de `id` lista e registro de `id` objeto, esperando o disparo gravado e o segundo escritor recusado, e mutante na checagem de tipo.

## Observações (sem bloqueio)
- O brief diz 12 fixtures `autor-*` com 2 avisando; só `autor-retomavel-avisa` traz `aviso` no esperado (1 avisa, 11 liberam). O segundo aviso (D3 + H2 juntos) é coberto por `test_dois_avisos_saem_num_json_so`. Contagem do brief imprecisa, cobertura completa.
- O `test_prazo_do_merge` e o fixture `pesado` não passam com a máquina saturada; no CI (`bateria` do mesmo sha) o veredito vale.

## Execução da revalidação (head 482ee7c7, `forge-check parecer delta` lista código e testes)
- `bin/forge-mutante` nas 3 specs: M1 a M22 morreram, saída 0.
- Vermelho: `vermelho: base=e2880b42b81e head=482ee7c77359`; 9 provam por API ausente, `PeloHook.test_fixtures_do_pedido` H=ok B=erro sem veredito; rc 2 (A3).
- `python3 -I scripts/indice-fixtures.py --conferir`: `docs/hooks-fixtures.md: em dia`.
- `python3 -m unittest tests.test_hooks_agentes_autor tests.test_forge_mutante.ConferirTodas`: 14 testes, failures=1 (A2); o teste do autor passa.
