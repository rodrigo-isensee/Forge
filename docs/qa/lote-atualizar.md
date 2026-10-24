---
tipo: qa
contrato: 1
pedido: lote-atualizar
branch: melhoria/lote-atualizar
commit: 1776e2dcdad82e4f9ae0e2bf69612993988875c5
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-23
---
# QA: lote-atualizar (F4-A9 e publicar sem `__pycache__`)

Revalidação (rodada 2) sobre o head `1776e2d`; o delta desde `bafc740` é só `tests/test_atualizar.py` (código de `bin/forge-atualizar` inalterado desde `8353dae`). Base `db55859`. Sem especificação de UX: as obrigações são as do pedido LOTE-ATUALIZAR (F4-A9, review A1 e A2) e de `docs/regras`.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| F4-A9: erro depois do commit da resolução desfaz de verdade e a mensagem é verdadeira | `test_erro_depois_do_commit_da_resolucao_desfaz_a_mesclagem_e_diz_que_desfez` + sonda de ponta a ponta (cenário b) | HEAD volta a `antes`, sem commit de mesclagem, árvore limpa | passou |
| Desfazer recusado (`index.lock`) não diz "Desfiz" e ensina o comando | `test_desfazer_recusado_nao_diz_que_desfez_e_ensina_o_comando` + sonda (cenário c) | a mensagem não mente quando o checkout falha | passou |
| Review A1: teste usa o ambiente isolado (`self.env`) | os dois acima, sob `mock.patch.dict(os.environ, self.env, clear=True)` | sem `.gitconfig` herdado | passou |
| Publicar não copia `__pycache__` | `publicar()` com `ignore_patterns`; suíte do módulo | n/a | passou |
| "n" na pergunta desfaz a mesclagem | `test_conflito_em_forge_versao_recusado_pelo_dono_desfaz_a_mesclagem` + sonda (cenário d) | sem commit de mesclagem, árvore limpa | passou |
| Erro, Ctrl-C e EOF com a mesclagem aberta desfazem por abort (A1 resolvido) | `test_erro_com_a_mesclagem_aberta_desfaz_por_abort`, `test_ctrl_c_com_a_mesclagem_aberta_desfaz_por_abort_e_repassa`, `test_eof_com_a_mesclagem_aberta_desfaz_por_abort_e_repassa` | MERGE_HEAD ausente, HEAD em `antes`, árvore limpa, exceção repassada | passou |

## Cenários e resultado real
- `python3 -m unittest tests.test_atualizar`: 75 testes, OK (`$TMPDIR/qa-loteatualizar/unit1.log`). Suíte completa fica para o pre-push.
- Sonda de ponta a ponta (`$TMPDIR/qa-loteatualizar/sonda_qa.py`; HOME e remoto locais em `$TMPDIR/qa-loteatualizar/`; script `bin/forge-atualizar` do head, com falha injetada numa cópia de `trazidos`), 4 cenários OK (`sonda1.log`):
  - a) conflito só em `.forge/versao`, "s": "Conflito resolvido", rc 0, commit de mesclagem com 2 pais.
  - b) erro simulado depois do commit: "Desfiz a mesclagem", HEAD de volta ao commit de antes, sem commit de mesclagem, árvore limpa, rc 1.
  - c) o mesmo com `index.lock`: sem "Desfiz"; sai "Não consegui desfazer a mesclagem" e o comando `git checkout -B forge/upgrade-9.9.0 <sha de antes>`; a mesclagem ficou (esperado).
  - d) "n": "Desfiz a mesclagem", sem commit de mesclagem, árvore limpa, rc 1.
- Vermelho antes do verde: `bin/forge-testes --vermelho db55859529da47652babded81461d2b0500ef79f --modulos test_atualizar`, rc 0: "vermelho: base=db55859529da head=6ecddee78694 módulos=test_atualizar", "revertidos à base: bin/forge-atualizar, ..."; os dois testes novos `H=ok · B=falha · prova (asserção)`; contagem: prova=2, não prova (passa na base)=73.
- Mutação (`bin/forge-mutante`, spec escrita pelo QA, pois o autor não declarou; 5 mutantes, um por guarda de `desfazer_mesclagem` e das mensagens), rc 1:

```
M1 · morreu · bin/forge-atualizar:123
M2 · morreu · bin/forge-atualizar:143
M3 · morreu · bin/forge-atualizar:142
M4 · morreu · bin/forge-atualizar:140
M5 · sobreviveu · bin/forge-atualizar:138
```

M5 também sobrevive com a classe inteira `AtualizarComDevelopQueAvancou` como testes, e não é equivalente: sem o abort a função devolve False e diz que não conseguiu desfazer, comportamento diferente. Correção sugerida (agente de dev da stack): teste em que `fv.confirmar` ou o commit levante com a mesclagem aberta e espere "Desfiz", MERGE_HEAD ausente e HEAD em `antes` (cobre também o A5 do review).

## Revalidação (rodada 2, só o delta)
- `python3 -m unittest tests.test_atualizar`: 78 testes, OK (`$TMPDIR/qa-loteatualizar2/unit2.log`); os 3 novos cobrem erro, Ctrl-C e EOF com a mesclagem aberta.
- Mutante M5 (`if False:` no lugar da guarda do `merge --abort`), `bin/forge-mutante` rc 0: `M5 · morreu · bin/forge-atualizar:138` (`$TMPDIR/qa-loteatualizar2/mut.log`). A1 do parecer anterior resolvido. M1 a M4 não dependem do delta (código inalterado).
