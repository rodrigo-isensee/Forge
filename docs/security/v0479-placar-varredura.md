---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-placar-varredura
commit: 3907f4bb628f8a919a6b756ce8db7c321514f776
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-19
---
# Review de segurança: v0479-placar-varredura

Gatilhos: entrada não confiável analisada por controle (`fundo_demais` em `bin/forge-placar`), orçamento de tempo da entrada.

Fecha o A2 do parecer anterior do placar (regex quadrático na varredura de string).

## Detalhe
- Custo linear: `bin/forge-placar:194-217` lê cada caractere uma vez. Sonda S9 e variações (até 4.000.000 repetições; strings com escape, só aspas, só barras, `[` repetido, `"a"` repetido): no máximo 0,75 s, proporcional de 10^5 a 4x10^6. O teste novo (`tests/evals/test_placar.py:546`) prova uma leitura por caractere sem relógio.
- Falha fechada: fuzz de 200.000 entradas aleatórias contra a versão antiga: 9.780 divergências, todas em texto que não é JSON (string sem fecho, que a antiga contava como fora de string). Zero divergência em JSON válido. Em sem-fecho com 100 `[` a antiga dava True e a nova dá False, mas `json.loads` rejeita (`bin/forge-placar:228-231`, saída 2). JSON fundo válido segue barrado.
- Escape: barra escapada deixa a aspa fechar; aspa escapada não fecha; escape no fim sem fecho não quebra. Casos no teste; mutantes M44 a M48 cobrem as condições.
- Teste novo do placar roda verde no head; a suíte inteira fica para o CI.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Só ferramentas locais; nenhuma faltou.
