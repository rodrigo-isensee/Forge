---
tipo: qa
contrato: 1
pedido: conf-base-dono
branch: melhoria/conf-base-dono
commit: aa7d3d12f9609a2b5f3daf0c0c3a7aeab87a6e52
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-23
---
# QA: conf-base-dono

Código testado: o de `d47d1b4728cae7d6811a21649eb333025b264d7b` (o head `aa7d3d1` só soma pareceres). Review e segurança revalidados e aprovados antes deste parecer.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1 base fixada pelo dono, com origem dita | `test_conferencia_base_dono` (BaseDoDono) e sonda 1 | linha exata; DECISÃO DO DONO obrigatória | passou |
| E1 frase no meio da linha, sem decisão, sha curto ou fora da branch, base == head | `test_a_base_do_dono_so_vale_...`, `test_base_do_dono_igual_ao_head_...`, sondas 2, 3, 3b | forma exata; delta vazio | passou (recusa, rc 1) |
| E2 merge de integração sozinho | testes de integração e sonda 4 | escopo só do que difere dos dois pais | passou |
| E2 dois merges seguidos com arquivo do autor no primeiro | `test_dois_merges_seguidos_nao_escondem_arquivo_do_autor` e sonda 5 | arquivo do autor não some | passou (`autor.txt` aparece) |
| E3 `--raiz-pedidos` | `test_a_opcao_recusa_pasta_fora_...` e sondas | dentro de `~/.forge-contrib` aceita; fora, `..` e symlink recusam (rc 2) | passou |
| Sem linha do dono e sem merge: igual à `origin/develop` | sonda 6 (diff byte a byte, 3 variações de `--desde`) | regressão | passou |

## Cenários e resultado real
- `python3 -m unittest tests.test_conferencia_base_dono`: 21 testes, OK.
- Módulos do `forge-check` (mapa `FORGE_CHECK` de `bin/forge-testes`, 13 módulos sem `test_hooks`/`test_forge`, rodados antes de 'forge-testes --vermelho' completo): 533 testes, OK. `forge-testes --vermelho origin/develop` sem restrição roda a suíte inteira (o diff mexe em `bin/forge-testes`): 1727 "passa na base", 16 "prova (asserção)", sem falha no HEAD.
- Vermelho antes do verde, `bin/forge-testes --vermelho origin/develop --modulos test_conferencia_base_dono`, rc=0: `vermelho: base=139a3b451a1c head=aa7d3d12f960`; revertidos à base `bin/forge-check`, `bin/forge-testes` e agentes; saída `contagem: não prova (passa na base)=7; prova (asserção)=14`; exemplo: `test_a_pq_gerada_passa_no_entrega · H=ok · B=falha · prova (asserção)`. Os 7 que passam na base são os de recusa (comportamento preservado, esperado).
- Sonda em `$TMPDIR/qa-cbd/run1` (HOME próprio, sem rede, script `$TMPDIR/qa-cbd/sonda.sh`), `bin/forge-check` do head contra o da `origin/develop`:
  1. linha exata com DECISÃO DO DONO: rc 0, `base: fixada pelo dono (linha do Histórico)`, escopo só `c.txt`.
  2. mesma frase no meio da linha: rc 1, `--desde sem conferência anterior`.
  3. base igual ao head: rc 1, mesma recusa; sem DECISÃO DO DONO: rc 1.
  4. merge de integração sozinho: `escopo: integração da base (o que difere dos dois pais)` e `pendente`, sem listar os arquivos da base.
  5. dois merges seguidos, arquivo do autor no primeiro: `autor.txt` aparece.
  6. sem linha do dono e sem merge: saída idêntica à da `origin/develop` (`--desde` ausente, conferida atual e antiga).
  7. `--raiz-pedidos`: dentro de `~/.forge-contrib` rc 0 (antes e depois do subcomando); `/tmp`, pasta fora, `..` escapando e symlink para fora: rc 2.
- Mutação: o pedido não declara `tests/mutantes/` e o diff toca `bin/forge-check`; o vermelho por teste (14 provas de asserção) cobre as guardas novas (forma exata, decisão, base == head, dois pais, raiz). Sem mutante rodado.
