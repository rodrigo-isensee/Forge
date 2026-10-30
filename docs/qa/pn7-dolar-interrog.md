---
tipo: qa
contrato: 1
pedido: pn7-dolar-interrog
branch: melhoria/pn7-dolar-interrog
commit: 312ecf0d01b9072fa17446c87dd6174c65ac3b6b
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-30
---
# QA: PN7-DOLAR-INTERROG (H1-1 da P-N7, `R-QA`)

Código testado: `312ecf0` (worktree desanexada, base `31257c1`). Pedidos de origem: PN7-DOLAR-INTERROG e PN7-DOLAR-INTERROG-REV. O pedido não tem `CA-n` de UX; as obrigações são o escopo E1 e E2 e a decisão técnica de 00:07 (IFS também em `heredocs_simples`).

## Achados
- A1 (recomendado) tests/mutantes/pn7-dolar-interrog.json:1 · Sem mutante para `"IFS" in texto` (parecer.py:109): trocar `texto` por `linha` sobrevive (sonda Q1). Equivalente no efeito: só o `cat` puro chega ao caminho rápido (parecer.py:612). Declarar como equivalente ou testar.

## Critério → teste → resultado
| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1: `$?` entre aspas duplas sempre passa; fora de aspas só sem `IFS` (3 funções) | `CodigoDeSaida.test_dolar_interrogacao_por_posicao_aspas_e_ifs` (10 tokens × 4 posições × 3 aspas × com/sem IFS, mínimo 200) | `IFS` presente, aspas simples/duplas/fora, `$$?`, `$?$x`, `${?}` | passou |
| E1: todo outro `$`, crase, chaves, `<<'$'` seguem recusados, rc 2 | fixtures `pn7-dolar-interrog-*-bloqueia` (conformidade e parecer) | ANSI-C, chaves, crase, `IFS`, variável, push na main, merge sem parecer, redireção com merge no corpo | passou |
| E2: casos que passam a passar, em projeto e no clone | fixtures `pn7-dolar-interrog-*-libera` via `Hooks.test_fixtures` | push, commit com heredoc que cita merge, k3, add reviews | passou |
| Decisão 00:07: `heredocs_simples` recusa `$?` com `IFS` também entre aspas | mesmo teste de propriedade (3ª asserção) | `IFS` presente | passou |
| Motivo da guarda: `IFS` com dígito divide a palavra no bash | `CodigoDeSaida.test_ifs_com_digito_divide_o_codigo_fora_de_aspas` | `x$?main` com `IFS=1` | passou (teste de premissa, passa na base de propósito) |

## Cenários e resultado real
- `python3 -m unittest tests.test_hooks.CodigoDeSaida tests.test_hooks.Hooks.test_fixtures tests.test_hooks_volta_corpus`: 19 testes, OK, rc=0. Carga de 1 min abaixo de 7 no disparo (o pico de 10,9 foi do forge-testes, em outra chamada).
- Vermelho (`bin/forge-testes --vermelho 31257c14c8d245d66e7806edb7cd65e22b3aeb04 --modulos test_hooks`, rc=0):
```
vermelho: base=31257c14c8d2 head=312ecf0d01b9 módulos=test_hooks (restrito por --modulos)
revertidos à base: changelog.d/pn7-dolar-interrog.md, docs/adr/0011-analisador-de-comandos-gramatica-positiva.md, docs/hooks.md, hooks/_comum.py, hooks/parecer.py
tests.test_hooks.CodigoDeSaida.test_dolar_interrogacao_por_posicao_aspas_e_ifs · H=ok · B=falha · prova (asserção)
tests.test_hooks.Hooks.test_fixtures · H=ok · B=falha · prova (asserção)
contagem: não prova (passa na base)=52; prova (asserção)=2
```
- Mutantes (`bin/forge-mutante tests/mutantes/pn7-dolar-interrog.json`, rc=0): D1 a D12 todos `morreu` (_comum.py:1456, 1573, 1578; parecer.py:109).
- Cobertura (`bin/forge-mutante --cobertura --base 31257c1`): coberta `_comum.py:1456` (D1-D4) e `:1578` (D7-D9); `sem mutante` em `parecer.py:109` e `:110`, condições que D10-D12 mudam por inteiro.
- Conferência da lista contra o diff: linhas de guarda mudadas são `_comum.py:1456`, `:1573`, `:1578` e `parecer.py:109`, `:110`. Sondas minhas (spec descartável, fora da árvore, não commitada) em `parecer.py`: Q2 (`"$" in comando` vira `"$?" in comando`) morreu; Q3 (vira `False`) morreu; Q1 (`"IFS" in texto` vira `"IFS" in linha`) sobreviveu. Q1 é equivalente no efeito: o `IFS` só em outra linha do corpo é dado, não muda o `IFS` do bash, e o caminho rápido exige só `cat` (A1, recomendado).
- `scripts/verificar-contribuicao.sh origin/develop`: `ok: nenhum segredo nem caminho pessoal no diff contra origin/develop.` rc=0.
- Verificação do PA-7 (`docs/engineering/achados-recorrentes.md`), itens de QA: AR-1 (lista de mutantes incompleta) conferido, achado A1; AR-2 (ramo de falha sem teste de comportamento) sem ocorrência: todo ramo de recusa tem fixture rc 2.
- Acessibilidade e E2E de UI: não se aplicam (hooks de linha de comando). Sem `skip`, sem teste instável.
- Os pareceres de review e segurança do mesmo head são de outras delegações e não foram lidos.
