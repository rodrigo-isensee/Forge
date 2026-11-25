### Corrigido
- `forge-fechar`: o CI do push no merge cancelado porque a develop andou não sai mais com código 5; decide o CI do topo que contém o merge (vermelho de verdade continua 5). De um clone da develop sem o commit da branch, o passo 1 busca o head e cria a branch local nesse sha; rodado da cópia principal na própria branch, para antes do passo 1 e diz de qual cópia rodar (v0481 E13.1)
