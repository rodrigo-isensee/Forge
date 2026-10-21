---
tipo: qa
contrato: 1
pedido: regra-lote-por-arquivo
branch: melhoria/regra-lote-por-arquivo
commit: 6f61294442b6753b27725d1725b88bfbe056a558
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-21
---
# QA - regra-lote-por-arquivo (E1 a E4)

Sem UX nem API. Mudança de texto de agente (`agents/jarvis.md:33`, `:48`, `:96`), dois invariantes em `tests/config.json` e fragmento de changelog. Não escrevi o diff. Review e segurança com `parecer: aprovado` no commit `6f61294`; HEAD da branch `c1b6193` (só traz os pareceres).

## Obrigação -> teste -> resultado
| ID | Obrigação (pedido) | Teste | Fronteira protegida | Resultado |
|---|---|---|---|---|
| Q-1 | E1: regra do lote por arquivo, com os elementos da decisão de 08:26 | invariante `\*\*Lote por arquivo:\*\*`; leitura de `agents/jarvis.md:48` | rótulo da regra some | passou |
| Q-2 | E2: exceção em "uma melhoria por PR" | leitura de `agents/jarvis.md:96` (a linha de origem segue exigindo problema e medida) | exceção só para o lote da seção | passou (sem invariante próprio; recomendação da segurança, não bloqueante) |
| Q-3 | E4: conferência com o time na abertura, mesmo estágio, vale para projetos | invariante `Na abertura de cada pedido, confira com o time se ele cabe num lote` | frase some | passou |
| Q-4 | E3: invariantes e fragmento | `tests.test_forge.RegrasInviolaveis`; suíte completa | trecho removido | passou |
| Q-5 | Nada afrouxa nem custa (decisão de 2026-10-15) | leitura: "Nenhum portão cai", review, segurança e QA mantidos, nada pago | n/a | passou |

## Execução
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -q` na raiz da worktree: `Ran 1267 tests in 328.879s`, `OK`.
- `scripts/validar-plugin.sh`: `Validation passed`.
- Vermelho antes do verde, numa cópia em `$TMPDIR` (`git archive HEAD`), `RegrasInviolaveis.test_trechos_obrigatorios`: com o texto, `OK`; rótulo trocado por `**Lote:**`, `FAIL` no trecho `\*\*Lote por arquivo:\*\*`; frase do E4 trocada por "Na abertura, confira", `FAIL` no trecho `Na abertura de cada pedido, confira com o time se ele cabe num lote`; texto restaurado, `OK`. Os dois invariantes guardam o que dizem guardar.

## Leitura como o Jarvis de um projeto
- (a) Dois itens sem discovery no mesmo arquivo: o passo 1 manda conferir o encaixe no lote, aceita "os dois sem discovery" e a seção de paralelo manda juntar itens no mesmo arquivo. Resposta: um lote (uma branch, um commit por item, um review/segurança/QA, um PR). Bate com 08:26 e 09:30.
- (b) Um item com discovery e outro sem, no mesmo arquivo: o passo 1 diz "nunca um item sem discovery com um já descoberto". Resposta: dois caminhos separados, o descoberto segue, o outro faz discovery antes. Bate com 09:30.
- (c) Item novo sobre arquivo de item em andamento: o passo 1 só agrupa com "algo que ainda não está em andamento", então não entra no lote; cai na série por arquivo (`agents/jarvis.md:44`, `bin/forge-check sobreposicao`), que o pedido manteve intocada. Bate com 09:30.
- Lacunas, não bloqueantes: o bullet do lote diz "itens decididos" e não repete a regra de estágio (ela está no passo 1, que o bullet referencia); o texto não diz se um item, depois de descoberto, pode entrar num lote de itens já descobertos. A leitura natural do passo 1 permite. O revisor e a segurança já registraram as recomendações de cartão do lote x `R-WIP`, tamanho do lote e revalidação do parecer após revert.

## Achados
