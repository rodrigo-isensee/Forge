---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-bp3-s4-retomada
commit: 126e98b664c6229921f01a34a8dbc3c2d3fd5c74
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-20
---
# QA: v0479-bp3-s4-retomada (E39.38)

Subcomando `forge-check retomada [--contar]` (`bin/forge_retomada.py`), só leitura. Sem CA-n próprio: as obrigações são as do comportamento do subcomando (registro ilegível rc 4, matriz de ação, guardas de argumento), cada uma com teste.

## Achados
- A1 (recomendado) tests/test_forge_check_retomada.py:311 · 3 testes da Matriz (fecha_sempre_com_a_pergunta, item_sem_id_tipo_ou_branch, linha_traz_brief_sha256) dão IndexError na base em vez de asserção; `--vermelho` sai rc 2 (sem veredito). Afirmar o stdout antes de indexar.

- A2 (recomendado) tests/mutantes/v0479-bp3-s4-retomada-recomendados.json:2 · `pedido` é v0478, as outras três specs são v0479-bp3-s4-retomada: forge-mutante recusa a rodada junta (uma chamada por pedido) e `--cobertura` lista `forma()` (:41) como `sem mutante`. Alinhar o campo `pedido`.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Registro ilegível (JSON inválido, não lista, infinito, link) sai rc 4 sem stdout | classe RegistroIlegivel (4 testes) | registro corrompido | passou |
| `--contar` devolve só o número, sem git | classe Contar | vazio, zero itens | passou |
| Matriz: brief com selo válido, vencido, ausente, link fora de docs/briefs, FIFO, 256 KiB e +1 byte | classe Matriz | limite de tamanho do brief | passou |
| Worktree suja nunca é descartada; limpa ou de outra branch manda relançar | classe Matriz | arquivo não commitado | passou |
| Campos com controle ou curinga não imitam outra linha nem achado transcript | classe Matriz | caracteres especiais | passou |
| Só leitura: registro e árvore iguais após a execução | Matriz.test_so_leitura | n/a | passou |
| Argumento inválido sai rc 2 | Guardas | entrada inválida | passou |
| Campo do registro fora da forma sai `?`, com teto (900 KB não chega ao contexto) | Matriz.test_campo_do_registro_fora_da_forma..., test_campo_de_900_kb..., test_campo_valido_sai_como_veio | tamanho máximo, controle, `..` | passou (M1-M3 novos morrem) |
| `git status` da worktree não regrava o index | Matriz.test_status_da_worktree_nao_regrava_o_index | só leitura | passou (M4 morre) |

## Cenários e resultado real
Revalidação no head 126e98b6 (delta sobre 687112b1: `forge_retomada.py` com `forma()`, `--no-optional-locks`, ramo `sem_brief`/`vencido` fundido; 4 testes novos; M1-M4 novos em `-recomendados.json`; M19 retirado). As provas abaixo valem para o head 126e98b6; o texto da rodada anterior fica só como histórico.
Provas (comandos no clone, TMPDIR próprio, head 126e98b6):
- Módulo: `python3 -I -m unittest discover -s tests -p test_forge_check_retomada.py` → `Ran 45 tests ... OK`.
- Mutantes: `bin/forge-mutante tests/mutantes/v0479-bp3-s4-retomada-{1,2,3}.json --processos 2` → rc 0, 33 linhas `morreu` (M1 a M34, sem M21 na lista rodada); três com `(erro)` (M3, M18, M28), que mata com o controle verde.
- Mutantes novos: `bin/forge-mutante tests/mutantes/v0479-bp3-s4-retomada-recomendados.json --processos 4` → rc 0, M1 a M4 `morreu`. Rodada completa das specs -1,-2,-3 com `--base 687112b1ed97...` → rc 0, 31 `morreu` (M19 retirado, M21 inexistente; M3, M18, M28 com `(erro)` que mata).
- ConferirTodas: `python3 -I -m unittest discover -s tests -p test_forge_mutante.py -k ConferirTodas` → `Ran 4 tests ... OK`.
- Vermelho (reexecutado no head novo): `bin/forge-testes --vermelho cf097822 --modulos test_forge_check_retomada`:
  `vermelho: base=cf097822f2c3 head=687112b1ed97 módulos=test_forge_check_retomada (restrito por --modulos)`
  `contagem: não prova (passa na base)=3; prova (API ausente)=6; prova (asserção)=32; sem veredito=4` → rc 2 (head 126e98b6). Os 4 sem veredito são o A1 mais o novo `test_campo_do_registro_fora_da_forma...` (mesmo IndexError na base); 38 outros provam e nenhum cai no HEAD. Os 3 "não prova" (argumento inválido, descrição nunca impressa, só leitura) guardam comportamento que a base já tinha por construção.
- A suíte inteira: não rodada localmente; vale o check-run `bateria` do CI do PR.
