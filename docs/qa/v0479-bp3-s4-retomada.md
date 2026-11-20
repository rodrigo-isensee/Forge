---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-bp3-s4-retomada
commit: 687112b1ed9755fd1935f2dee26c75b5c048db2c
parecer: aprovado
escopo: completo
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

## Cenários e resultado real
Provas (comandos no clone, TMPDIR próprio, head 687112b1):
- Módulo: `python3 -I -m unittest discover -s tests -p test_forge_check_retomada.py` → `Ran 41 tests ... OK`.
- Mutantes: `bin/forge-mutante tests/mutantes/v0479-bp3-s4-retomada-{1,2,3}.json --processos 2` → rc 0, 33 linhas `morreu` (M1 a M34, sem M21 na lista rodada); três com `(erro)` (M3, M18, M28), que mata com o controle verde.
- Vermelho: `bin/forge-testes --vermelho cf097822 --modulos test_forge_check_retomada`:
  `vermelho: base=cf097822f2c3 head=687112b1ed97 módulos=test_forge_check_retomada (restrito por --modulos)`
  `contagem: não prova (passa na base)=3; prova (API ausente)=6; prova (asserção)=29; sem veredito=3` → rc 2. Os 3 sem veredito são o A1; 35 outros provam e nenhum cai no HEAD. Os 3 "não prova" (argumento inválido, descrição nunca impressa, só leitura) guardam comportamento que a base já tinha por construção.
- A suíte inteira: não rodada localmente; vale o check-run `bateria` do CI do PR.
