---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-pedido-arquiva
commit: 2c61be46e408759ced4ab72cbe2509bd3643a048
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-25
---
# QA: v0481 E9.15 (delta do #874, de 8b312446 a 2c61be46)

## Critério → teste → resultado (delta)
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| A1 do QA E9.11: cada corte do trecho de `entregue` tem caso próprio | `test_parecer_ponto_e_virgula_e_segunda_etapa_cortam_o_entregue` (`.md=`, `;`, 2ª etapa) | `.md=`, `;`, id entre parênteses | passou; M21, M23, M24 e M38 morreram |
| A2 do QA E9.11: o hífen colado não fecha | `test_entregue_com_hifen_nao_fecha` (2 linhas fora, `entregue - falta o PR` ainda fecha) | `entregue-se`, `Entregue-a` | passou; M49 morreu |
| Forma estrita de `entregue` (E9.11) | testes inalterados, 7 specs realinhadas a `(?![\w?-])` | negação, futuro, interrogação | passou; M40 a M48 morreram |
| Saída saneada: o nome do arquivo passa por `caminho_impresso` | `tests.test_forge.SaidaSanitizada` (10) | nome com controle | passou |
| Trechos das specs de outros pedidos voltam a ser únicos | `tests.test_forge_mutante.ConferirTodas` (4) | trecho `de` duplicado | passou |

## Conferências do pedido
- Nada que barra deixa de barrar: a regex só ficou mais estreita (`-` entra na exclusão); `test_brief_tamanho` (25) e `test_forge_tamanho` (24) OK no head 2c61be46. A troca de `i` por `j` no laço de `arquivar_etapas_fechadas` não muda o comportamento e deixa o trecho de FC2-M2 único (`bin/forge-check:4352` é a única ocorrência).
- Mutantes realinhados mantêm a mesma guarda: est-m12-gerar M3, v0474-h1-ferramenta-3 M16, v0479-ae4-ordens M5, v0479-ae4-ordens-2 M16 e v047-forge-check-fc2 (FC2-M2) rodados um a um, todos `morreu`, nenhum sobrevivente. Passar as 5 specs juntas dá "spec inválida" por serem de pedidos diferentes; não é defeito do item.

## Provas
- `forge-mutante --processos 4` nas 7 specs do pedido (`rev=2c61be46e408`): M1 a M49 todos `morreu` (M5 e M37 por erro com controle verde, aceitos desde o parecer anterior); nenhum sobrevivente.
- Vermelho: `forge-testes --vermelho 8d7914bc93e2410f1cd301bcf6c22dd9570b8534 --modulos test_brief_tamanho` termina em `contagem: não prova (passa na base)=5; prova (API ausente)=15; prova (asserção)=5`, rc 0. `test_parecer_ponto_e_virgula_e_segunda_etapa_cortam_o_entregue` prova (API ausente).
- `forge-check parecer delta`: `bin/forge-check`, `changelog.d` e `tests/` no domínio do QA; todos lidos.
- ci: partes que contam verdes no sha 2c61be46 (run 45601508436): suíte python 3.12 e 3.14 (partes 1 a 5), teto de pulados, instalação, bateria (passos), verificações longas, árvore já provada. Vermelhos: `bateria (pareceres)` e `catraca`, que leem os pareceres ainda no head anterior; não leio o log no sandbox (cache do `gh` só leitura).
- Diferenças só da develop (fragmentos, índice) não são do item.
