---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-pesado-versoes
commit: 4d3f76d441f1c276b554497e69c4330556dc3433
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-20
---
# QA: v0478 E64.1 (forge-testes só é leve pela lista fechada das opções, hooks/pesado.py)

Escopo: `hooks/pesado.py` (`LEVES_DO_FORGE_TESTES`, `opcao_leve`, `leve_pelos_argumentos`), `tests/test_forge_pesado.py`, `tests/test_hooks.py` (a lista de formas leves trocou `--dirigida` por `--afetados`), as 3 fixtures `tests/hooks/pesado/forgetestes-*` e a spec `tests/mutantes/v0478-pesado-versoes.json`. Sem suíte local; a suíte inteira é do check-run `bateria` do mesmo sha no CI do PR.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E64.1: `--versoes` (inteiro, abreviado, com `=`, depois de `--`, junto de opção leve) pesa | `FormasLevesDoForgeTestes.test_versoes_e_opcao_fora_da_lista_pesam` + fixture `forgetestes-versoes-espera-a-vez` | `--vers`, `--versoes --base=x`, `-- --completa` | passa; no vermelho, falha na base (prova por asserção) |
| E64.1: opção desconhecida, `--executar`, `-kx`, `-h` pesam | mesmo teste + fixture `forgetestes-opcao-desconhecida-espera-a-vez` | opção fora da lista, `-` curta | passa; vermelho prova |
| E64.1: formas da lista seguem leves (sem argumento, caminho, `--listar`, `--afetados`, `--base=`, `-k`, `-k=`, `--texto`, `--registros`, `--regerar`, `--list`, `-- caminho`) | `test_formas_da_lista_seguem_leves` + fixture `forgetestes-forma-leve-libera` | vazio, prefixo, `=`, separador | passa; na base já passava (esperado: guarda contra afrouxar) |
| Nenhuma opção leve abrevia `--c*`, `--v*` | `test_nenhuma_opcao_leve_abrevia_completa_vermelho_nem_versoes` | piso de 6 opções | passa; vermelho prova (API ausente) |
| Regressão: `--completa`/`--vermelho` e abreviaturas seguem pesados, `forge-mutante` só leve com `--listar` | `test_hooks.PesadoClassePelosArgumentos` | `--comp`, `--verm=x`, `--c` | passa (ver Provas) |

## Provas
vermelho (`timeout 900 bin/forge-testes --vermelho 8ee73d15 --modulos test_forge_pesado`, rc=0):
```
vermelho: base=8ee73d156db5 head=f8210fe5ab1e módulos=test_forge_pesado (restrito por --modulos)
revertidos à base: changelog.d/v0479-pesado-versoes.md, docs/hooks-fixtures.md, docs/hooks.md, hooks/pesado.py
tests.test_forge_pesado.FormasLevesDoForgeTestes.test_nenhuma_opcao_leve_abrevia_completa_vermelho_nem_versoes · H=ok · B=erro · prova (API ausente)
tests.test_forge_pesado.FormasLevesDoForgeTestes.test_versoes_e_opcao_fora_da_lista_pesam · H=ok · B=falha · prova (asserção)
contagem: não prova (passa na base)=16; prova (API ausente)=1; prova (asserção)=1
```
mutante (`timeout 900 bin/forge-mutante tests/mutantes/v0478-pesado-versoes.json`, rc=0):
```
M1 · morreu · hooks/pesado.py:299
M2 · morreu · hooks/pesado.py:301
M3 · morreu · hooks/pesado.py:309
```
cobertura (`bin/forge-mutante --cobertura --base 8ee73d15`, rc=0):
```
base=8ee73d156db5 mb=8ee73d156db5 rev=f8210fe5ab1e
coberta · hooks/pesado.py:299 · tests/mutantes/v0478-pesado-versoes.json:M1 · declarado, não provado
coberta · hooks/pesado.py:309 · tests/mutantes/v0478-pesado-versoes.json:M3 · declarado, não provado
```
Mutantes extras meus (spec fora da árvore, 4 de 4 mortos, rc=0): Q1 tirar `--` do separador (morreu), Q2 `all` para `any` (morreu), Q3 tirar `--regerar` da lista (morreu), Q4 pôr `--versoes` na lista (morreu).

Execução local dos arquivos tocados (TMPDIR no clone): `test_forge_pesado.py` 18 testes OK; as 3 fixtures `pesado/forgetestes-*` passam no lote (3 de 3). `test_hooks.PesadoClassePelosArgumentos` passa; `test_hooks.Hooks.test_fixtures_do_v0442` falha em 6 fixtures `meta/v0454-caminhos-extra-*` (`forge-ferramenta-v0454`, rc=erro), e as mesmas 6 falham na base 8ee73d15: ambiente do sandbox, não do item. A fixture `pesado/mesma-sessao-libera` estoura 120 s no sandbox também na base (triagem): não atribuída.

Sondas diretas de `pesado.pesado(comando, PESADOS_DO_FORGE)` (50 formas): pesam `--versoes`, `--vers`, `--ver=x`, `--v`, `--versoes=1`, `-- --versoes`, `--listar -- --versoes`, `-k x --versoes`, `--versoes -k x`, `--base=x --versoes`, `--VERSOES`, `'--versoes'`, com `timeout`, `nice`, `FOO=1` e depois de `;`, `--completa`, `--comp`, `--co`, `--vermelho`, `--verm=x`, `--modulos`, `--prazo`, `--executar`, `-kx`, `-`, `---versoes`. Leves: sem argumento, `tests/a.py`, `--afetados`, `--base origin/develop`, `--b=x`, `--l`, `--t`, `--a`, `-k=--versoes`, `--listar && bin/forge-testes`. Nenhuma forma real de `--versoes` ficou leve. Leves sem efeito pesado: `--registro r` (prefixo de `--registros`; sozinho o forge-testes roda o dirigido leve), `--re`/`--listar=x`/`--=x` (o argparse recusa). `bash -c '…--versoes'` fica leve (limite anterior do hook para `bash -c`, fora deste diff). Leitura de `bin/forge-testes:1143-1159`: as opções leves da lista batem com as do argparse e as pesadas (`--completa`, `--vermelho`, `--versoes`, `--modulos`, `--prazo`, `--executar`) ficam fora.

Mudança de comportamento notada e coberta por teste: `--listar --modulos a` agora pesa (antes era leve); declarado em `test_versoes_e_opcao_fora_da_lista_pesam`.

Simulação de merge: não feita; o remoto da branch estava em edaa2466 (à frente do head testado) e o parecer segue sobre o `commit:` acima.

## Revalidação no head 4d3f76d4 (E64.10, escopo incremental sobre f8210fe5)
Delta (`forge-check parecer delta`): só `tests/mutantes/v0451-a1b.json` no domínio (M5 alinhado a `all(opcao_leve(a) for a in argumentos if`; A1-prefixo, A1-igual e A1-separador apontados também a `FormasLevesDoForgeTestes.test_formas_da_lista_seguem_leves`); o teste citado já constava neste parecer e não mudou.
- `bin/forge-mutante tests/mutantes/v0451-a1b.json` (rc=0): M1 a M7, A1-prefixo, A1-igual, A1-separador, todos `morreu` (10 de 10), `rev=4d3f76d441f1`.
- `bin/forge-mutante tests/mutantes/v0478-pesado-versoes.json` (rc=0): M1, M2, M3 `morreu`. As duas specs juntas saem 2 (pedidos diferentes); rodadas uma por spec.
- `python3 -m unittest tests.test_forge_mutante.ConferirTodas`: 4 testes OK. `python3 -m unittest tests.test_forge_pesado`: 18 testes OK (TMPDIR no clone).
Parecer mantido: aprovado.
