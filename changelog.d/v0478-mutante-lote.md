### Adicionado
- `bin/forge-mutante SPEC --ids M22,M32` roda só esses mutantes da spec; o id que nenhuma spec declara (ou o vazio) sai 2 sem rodar nada, com a lista dos ids; `--ids` sem SPEC é recusado (v0478 FORGE-MUTANTE-POR-ID).

### Corrigido
- `forge-mutante --cobertura`: a isenta que não cruza condição listada saía rc 2 e escondia a cobertura inteira; agora a lista sai inteira e a isenta sai à parte, `isenta velha · <spec>: <arq> · <trecho>` (rc 1). A isenta da condição nova vale para cada ocorrência do trecho dentro do nó; na volta (`--base` no head aprovado), a isenta que a spec da base já trazia sai `isenta fora do diff`, fora do rc. A skill `qa-testing` passa a dizer o que a ferramenta faz: erro de um teste declarado sob o mutante, com o controle verde, mata e sai `morreu · ... · (erro)` (v0478 E17.1).
