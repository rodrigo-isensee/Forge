---
tipo: qa
contrato: 1
pedido: termos-hash
branch: melhoria/termos-hash
commit: 503830f
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-13
---
# QA - termos proibidos por hash (ADR 0008)

Execução em clone descartável da branch; nenhum termo foi gravado em arquivo ou relatório (só contagens).

| ID | Cenário | Resultado real |
|---|---|---|
| CT-01 | Suíte completa (`unittest discover`) | 189 testes, todos OK |
| CT-02 | `claude plugin validate . --strict` | passou |
| CT-03 | `scripts/verificar-contribuicao.sh` | ok, sem segredo nem caminho pessoal |
| CT-04 | Equivalência: 8 regras antigas (base em memória), 220 variações (caixa, colado, no meio de frase, markdown/código, prefixo/sufixo, espaço duplo, hífen, quebra de linha) | 215 iguais; 5 divergências, todas na variante com acento: o detector novo acusa, a regex antiga não (mais estrito, intencional pela normalização sem acento) |
| CT-05 | Fuzz diferencial antigo × novo, 20000 textos (palavras neutras e mutações de 1 caractere dos termos) | 0 divergências; palavras parecidas mas diferentes não são acusadas |
| CT-06 | Teste `Neutralidade` com arquivo temporário contendo uma ocorrência de cada regra | falhou como esperado, acusando por hash; arquivo removido |
| CT-07 | Catraca: remover um hash | barra (exit 1), mostra "termo nº 3" e prefixo do hash |
| CT-08 | Catraca: alterar um hash | barra (exit 1), mesma mensagem |
| CT-09 | Saída da catraca (CT-07/08) contra as 8 regex antigas | 0 ocorrências do termo |

## Observações
- CT-04: o ganho de cobertura com acento é compatível com a especificação (forma normalizada) e não gera falso positivo no fuzz.
- Sem bugs abertos.
