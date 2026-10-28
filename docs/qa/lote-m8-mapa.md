---
tipo: qa
contrato: 1
pedido: lote-m8-mapa
branch: melhoria/lote-m8-mapa
commit: 80d90ee950eca2b23983286520bff5107e415195
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-26
---
# QA: lote-m8-mapa

PR 1 do M8, opção C do dono (todo módulo de teste no diff roda a suíte inteira): `bin/forge-testes`, `tests/test_testes_tocados.py`, `tests/mutantes/lote-m8-mapa.json` e o fragmento `changelog.d/lote-m8-mapa.md`, diff `f142001..80d90ee` (8 commits). Critério verificável de fim de C: itens 1 a 5 da seção 2 de `docs/propostas/m8-caminho.md` (o item 6 é do PR 2). Worktree em HEAD solto `80d90ee`; sondas e logs em `$TMPDIR/qa-engineer-lote-m8-mapa/`, nunca no `~/Forge`.

## Achados
- A1 (recomendado) tests/mutantes/lote-m8-mapa.json:1 · a spec declara 7 mutantes e deixa sem mutante as linhas de guarda do MAPA mudadas (82, 97, 99, 103, 73 e 77) e o `elif pedidos` (520); o QA as cobriu com Q1-Q7, todos mortos. O teto de 8 por spec não comporta um mutante por linha neste diff.
- A2 (recomendado) bin/forge-testes:145 · o mutante Q8 (tirar `relativo == ".." or`) sobrevive: nenhum teste chama `--listar ..` na raiz. Sem a guarda, `..` cai em "suíte completa (.. sem mapa)", rc 0 (falha fechada, sem defeito); falta um caso em `test_caminho_fora_do_repositorio_e_recusado`.
- A3 (recomendado) tests/test_testes_tocados.py:664 · `test_vermelho_usa_o_modulo_de_teste_do_diff_mais_o_plano_dos_outros_caminhos` passa na base (o MAPA antigo dava o mesmo conjunto por outro caminho); só M2 e M3 o provam. Um cenário com `tests/test_forge.py` no diff (a base somava test_hooks e test_guarda_git) também falharia na base.
- A4 (recomendado) bin/forge-testes:25 · a docstring e a descrição do argparse já dizem que o pre-push filtra por este plano, e o `.githooks/pre-push` desta branch ainda não chama o script (isso vem no PR 2). O texto vale para o estado depois do PR 2.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| C.1 importação entre testes: cada `tests/test_X.py` importado dá completo, >= 31 arestas | `MapaCobreImportacaoEVarredura.test_todo_teste_importado_por_outro_leva_quem_importa_a_suite_inteira` | mínimo de 31 arestas (guarda contra suíte vazia) | passou; vermelho: prova (asserção) |
| C.2 varredura de pasta: glob/rglob/iterdir sobre caminho conhecido coberto; `tests/` dá completo | `MapaCobreImportacaoEVarredura.test_toda_varredura_de_pasta_conhecida_leva_o_modulo_a_suite_inteira_ou_ao_plano` | mínimo de 1000 arquivos; os três que varrem `tests/` | passou; vermelho: prova (asserção) |
| C.3 test_fechar, test_sugerir, novo e apagado dão completo com "sem mapa" | `Mapa.test_modulo_de_teste_no_diff_cai_na_completa_com_o_motivo_sem_mapa`, `Execucao.test_arquivo_novo_nao_versionado_conta`; à mão `--listar` (abaixo) | módulo novo, módulo apagado | passou; vermelho: prova (asserção); M1 morreu |
| C.3 `bin/forge-sugerir` segue dirigido | `Mapa.test_caminhos_conhecidos_rodam_so_os_modulos_do_mapa`, `Execucao.test_dirigido_roda_so_os_modulos_do_mapa_e_anota_o_log`; à mão `--listar` | n/a | passou |
| C.4 `--vermelho` sem `--modulos`: módulos de teste do diff mais o plano dos outros caminhos, sem "restrito" | `Vermelho.test_vermelho_usa_o_modulo_de_teste_do_diff_mais_o_plano_dos_outros_caminhos`, `Vermelho.test_vermelho_com_modulo_de_teste_apagado_no_diff_nao_o_roda` | módulo apagado | passou; M2, M3, M4 e M5 morreram; o primeiro passa na base (A3) |
| C.5 mutações: regra de `tests/` de volta ao MAPA; `--vermelho` de volta ao `planejar` puro | M1, M2 de `tests/mutantes/lote-m8-mapa.json` | n/a | morreram |
| CAMINHO na linha de comando: relativo, absoluto, `..`, subpasta, fora do repositório, `--`, incompatível com `--completa`/`--vermelho` | os seis `Execucao.test_caminho*` | fora do repositório, hífen inicial | passou; vermelho: prova (asserção); M6, M7 e Q7 morreram; Q8 sobreviveu (A2) |
| Regras novas do MAPA (forge-changelog, hooks/, conferir-reversao, dev/.claude-plugin, LEITORES_DE_TEXTO) | `MapaCobreOQueOsTestesLeem.test_a_familia_*`, `test_conferir_reversao_*`, `test_manifesto_do_plugin_de_dev_*`, `test_todo_arquivo_lido_*` | n/a | passou; vermelho: prova (asserção); Q1-Q6 morreram |

## Cenários e resultado real
- `python3 -m unittest tests.test_testes_tocados`: 77 testes, OK (19,6 s). `python3 -m unittest tests.test_forge` (o outro módulo do mapa de `bin/forge-testes`): 427 testes, OK. `scripts/validar-plugin.sh`: "Validation passed". A suíte completa fica no pre-push e no CI do PR, conforme o brief.
- Vermelho antes do verde, `bin/forge-testes --vermelho f142001c7e870c7b80c87d5e67438b70f538f2a6 --modulos test_testes_tocados`, rc=0:
```
vermelho: base=f142001c7e87 head=80d90ee950ec módulos=test_testes_tocados (restrito por --modulos)
revertidos à base: bin/forge-testes, changelog.d/lote-m8-mapa.md
mantidos no HEAD: tests/mutantes/lote-m8-mapa.json, tests/test_testes_tocados.py
... (16 "prova (asserção)", entre eles Mapa.test_modulo_de_teste_no_diff_cai_na_completa_com_o_motivo_sem_mapa,
     MapaCobreImportacaoEVarredura.* (2), Vermelho.test_vermelho_com_modulo_de_teste_apagado_no_diff_nao_o_roda,
     Execucao.test_caminho* (6), Execucao.test_arquivo_novo_nao_versionado_conta)
tests.test_testes_tocados.Vermelho.test_vermelho_usa_o_modulo_de_teste_do_diff_mais_o_plano_dos_outros_caminhos · H=ok · B=ok · não prova (passa na base)
contagem: não prova (passa na base)=61; prova (asserção)=16
```
- Mutação declarada, `bin/forge-mutante tests/mutantes/lote-m8-mapa.json`, rc=0:
```
forge-mutante: pedido=lote-m8-mapa rev=80d90ee950ec spec=034a3b05a08974fd5a805dfbe89edf980ad3b38fef2fbdc80ea6af22950f8afa
M1 · morreu · bin/forge-testes:81
M2 · morreu · bin/forge-testes:408
M3 · morreu · bin/forge-testes:409
M4 · morreu · bin/forge-testes:409
M5 · morreu · bin/forge-testes:409
M6 · morreu · bin/forge-testes:145
M7 · morreu · bin/forge-testes:501
```
- Conferência da lista contra o diff: as linhas de guarda mudadas são 73-77, 81-82, 97, 99, 103, 145, 160-165 (planejar), 408-409, 501 e 520. Faltava mutante em 73, 77, 82, 97, 99, 103 e 520; o QA escreveu `$TMPDIR/qa-engineer-lote-m8-mapa/qa-extra.json` (8 mutantes, mais um na outra metade da 145), `bin/forge-mutante`, rc=1:
```
forge-mutante: pedido=lote-m8-mapa-qa rev=80d90ee950ec spec=f98d7d479c418606b6645a55f1ccb7e2575b05699c873f74f0067ad505bc7a3c
Q1 · morreu · bin/forge-testes:82
Q2 · morreu · bin/forge-testes:97
Q3 · morreu · bin/forge-testes:99
Q4 · morreu · bin/forge-testes:103
Q5 · morreu · bin/forge-testes:77
Q6 · morreu · bin/forge-testes:73
Q7 · morreu · bin/forge-testes:520
Q8 · sobreviveu · bin/forge-testes:145
```
  Q8 é a disjunção `relativo == ".."`: sem ela, `forge-testes --listar ..` na raiz cai na suíte completa (falha fechada), em vez de rc 2. Mudança de mensagem e de código de saída, sem afrouxar nada; fica como recomendação (A2), não como bloqueio.
- À mão, `bin/forge-testes --listar` na worktree:
  - `tests/test_fechar.py` → `suíte completa (tests/test_fechar.py sem mapa)`, rc 0;
  - `bin/forge-sugerir` → `dirigido (test_forge, test_sugerir). O CI do PR roda a suíte inteira.`, rc 0;
  - `tests/test_qa_modulo_novo.py` (inexistente) → `suíte completa (tests/test_qa_modulo_novo.py sem mapa)`, rc 0;
  - `tests/test_fechar.py bin/forge-sugerir` → completa (o módulo de teste vence);
  - `..` → `forge-testes: ..: fora do repositório`, rc 2; `<raiz>/..` → idem; `..` a partir de `docs/` → `suíte completa (. sem mapa)`.
- Pelo git, num clone descartável em `$TMPDIR`: módulo apagado (`git rm tests/test_sugerir.py` commitado) → `suíte completa (tests/test_sugerir.py sem mapa)`; `tests/test_fechar.py` alterado sem commit → completa; `bin/forge-sugerir` alterado → dirigido (test_forge, test_sugerir).
- Achados recorrentes (PA-7): `docs/engineering/achados-recorrentes.md` não tem item; nada a conferir.

## Riscos
- O ganho do envio dirigido cai em todo envio que traz teste (esperado pela opção C, seção 2 da proposta); o dirigido segue para texto e código sem teste.
- O comportamento do pre-push só muda no PR 2; este PR não altera nenhum portão (`NaoEPortao` verde).
