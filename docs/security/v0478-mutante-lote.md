---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0478-mutante-lote
commit: 5520fd0d156beede30c54efb16227559be919e85
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-18
---
# Review de segurança: v0478 mutante-lote (E17.7, revalidação)

Gatilhos: controle (bin/forge-mutante, cuja `analisar` é a mesma que a catraca usa em MUTANTES-SPEC-HOOKS, tests/catraca.py:864).

Delta lido (`forge-check parecer delta`, b11631b2..5520fd0d): no domínio, só bin/forge-mutante:585-615 (`cabe`, `ocorrencias`, `cruza` com `nova` = nós das cópias) e :657 (`irmas`); fora do domínio, tests/test_forge_mutante.py:1065 (teste novo) e as specs em tests/mutantes/. Já lido na rodada anterior (E17.3, no git): o resto do lote, sem achado. Suíte: não rodada localmente (brief E17.7); rodei só as sondas abaixo, sobre o módulo do head e de b11631b2.

## Estado dos achados anteriores
- A1 (bloqueante): resolvido. `cruza` exige o trecho dentro do nó e toda ocorrência dele no arquivo (sobrepostas inclusive) inteira num nó de condição nova de mesmo texto (bin/forge-mutante:607-610, chamada em :657), a forma proposta. S1 e S2 refeitas; as variantes (cópia fora do hunk, comentário, string, trecho contido noutra condição) falham fechadas no head e passavam em b11631b2.
- A2 (recomendado): resolvido. tests/test_forge_mutante.py:1065 cobre outra condição (S1), comentário e cópia fora do hunk, esperando rc 1 e `sem mutante`.

## Sondas
- S1 · analisar("hooks/h.py") com `x.startswith('adm')` e `y.startswith('../') or y.startswith('/')` novas, isenta `.startswith(` · espera: sem mutante nas 2 · obtido: head sem mutante nas 2 (b11631b2: isenta nas 2)
- S2 · `x is None or y is None` nova 2 vezes, isenta do texto inteiro · espera: isenta nas 2 · obtido: isenta nas 2 (caso legítimo mantido)
- S3 · base com 1 cópia de `x is None or y is None`, head acrescenta outra no hunk, mesma isenta · espera: sem mutante · obtido: head sem mutante (b11631b2: isenta)
- S4 · `# x is None or y is None` em comentário + a condição nova · espera: sem mutante · obtido: head sem mutante (b11631b2: isenta)
- S5 · `M = 'x is None or y is None'` em string + a condição nova · espera: sem mutante · obtido: head sem mutante (b11631b2: isenta)
- S6 · `x is None` e `x is None or y` novas, isenta `x is None` · espera: sem mutante nas 2 · obtido: head sem mutante nas 2 (b11631b2: isenta nas 2)
- S7 · cópias com aspas diferentes (`'a'` e `"a"`, mesmo unparse), isenta `x.startswith(` · espera: isenta nas 2 (mesma condição) · obtido: isenta nas 2

## Custo da checagem
`ocorrencias` é uma varredura com lookahead de trecho literal (`re.escape`, até MAXIMO_DO_TRECHO) sobre o arquivo limitado por MAXIMO_DO_ARQUIVO, vezes as cópias (MAXIMO_DE_CONDICOES); sem retrocesso explosivo.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do delta e sondas locais com a biblioteca padrão (`python3 -I`) sobre cópias do módulo; sem segredo nem dependência no delta.
