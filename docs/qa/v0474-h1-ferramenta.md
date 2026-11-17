---
tipo: qa
contrato: 1
pedido: v0474
branch: melhoria/v0474-h1-ferramenta
commit: 4ddaa68bb20c6f79d68e518b9c7e2ab72aa04782
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-17
---
# QA: v0474 (E2.27, H1 ferramenta)

## Achados
- A1 (bloqueante) tests/test_forge_tamanho.py:20 · `forge-testes --vermelho 681d4b33 --modulos test_forge_tamanho` sai 2 (sem veredito): o módulo carrega bin/forge_tamanho.py no import e, na base, o FileNotFoundError mata o executor sem registro. Não vale como vermelho (R-QA); carregue dentro de setUpModule/try ou torne o erro por teste.
- A2 (bloqueante) bin/forge-check:1411 · mutante sobrevivente: trocar `ref or "HEAD"` por `"HEAD"` mantém os 20 testes verdes; `--cobertura` lista a linha como `sem mutante`. O tamanho do PR com `ref` diferente de HEAD (forge-fechar, --ref) não tem teste nem mutante. Dê teste com ref e M20.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| H1: aviso acima de 150 linhas de código | test_borda_do_teto_de_linhas, sonda 150/151 | exatamente 150 sem aviso, 151 com | passou |
| H1: testes e documentação não contam | test_so_codigo_conta_e_binario_fica_fora, sonda | só testes, só docs: 0 linhas | passou |
| H1: reprova só com PR aberto sem a linha de motivo | classe NoPr, motivo vazio e forma errada | sem PR, sem rede, motivo vazio | passou |
| PEDIDO-TETO-BRIEF: aviso acima de 50 etapas e brief a 90% do teto | sonda das funções (50 sem, 51 com; 8999 sem, 9000 com de 10000) | 50, 90% | passou |
| ref diferente de HEAD no tamanho do PR | nenhum | ref explícita | sem teste (A2) |

## Cenários e resultado real
- Vermelho: `vermelho: base=681d4b33f753 head=4ddaa68bb20c módulos=test_forge_tamanho`, depois `test_forge_tamanho · sem veredito (prazo, sinal ou executor sem registro em B)`, `contagem: sem veredito=1`, saída 2, repetida com `--prazo 500`. Causa reproduzida à mão numa cópia da base: FileNotFoundError em tests/test_forge_tamanho.py:20.
- Mutantes (3 specs, `--processos 4`): `bin/forge-mutante` das 3 specs saiu 0, M1 a M19 todos `morreu` (M2, M7, M9, M17 por erro do teste declarado, que passa sem o mutante).
- Cobertura (`--cobertura --base 681d4b33`, rc 1): linhas sem mutante `bin/forge-check:1411` (ver A2) e `bin/forge-check:8474` (coberta por M19, a troca sai do nó da condição; aceito); `spec editada · tests/mutantes/lote-l08-e7.json`.
- Testes: `python3 -m unittest tests.test_forge_tamanho tests.test_testes_tocados tests.test_forge_mutante.ConferirTodas`: 186 testes OK, 1 pulado (sandbox, /proc de outro namespace; teste do autor, não meu).
- Sondas de borda de `forge_tamanho`: 100+50 de código com 999 em tests e docs soma 150, sem aviso; 151 avisa; 151 sem motivo reprova, com motivo passa; 150 sem motivo passa; sem PR e sem rede cobertos por NoPr (gh falso, origin local).
- Suíte inteira: não rodada aqui; vale o check-run `bateria` do CI do mesmo sha.
