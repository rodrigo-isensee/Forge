---
tipo: qa
contrato: 1
pedido: forge-check-fila
branch: melhoria/forge-check-fila
commit: fcaee1006ae30294353bc58e41d8dce9d381eea4
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 1
bugs_baixos: 0
aceite_usuario: sim
data: 2026-10-21
---
# QA - `forge-check fila` (P9, cartão FORGE-CHECK-FILA)

Links: `docs/pedidos/forge-check-fila.md`, seção "P9" de `docs/propostas/aq/p8-p9.md`, `docs/reviews/forge-check-fila.md`. Não há UX nem API; as obrigações são a seção P9 (ordem, motivos, só leitura, vagas de `R-TETO`). Sondas só em `$TMPDIR`, sem rede (`R-CUSTO`). Sem gatilho de segurança.

## Suíte
- `python3 -m unittest discover -s tests -q`: 1216 testes, OK (345 s).
- `scripts/validar-plugin.sh`: Validation passed (os avisos de rede bloqueada pelo sandbox não afetam o resultado).

## Resultados
| ID | Obrigação / cenário | Fronteira protegida | Resultado |
|---|---|---|---|
| CT-01 | Projeto de sonda com cartões em "Pronto para fazer", "Em andamento" e "Pronto"; pedido sem dependência, com dependência em andamento, com dependência pronta, sem a linha e em ciclo | dependência fora de "Pronto"; dependência em "Pronto" | Passou: `pode-comecar` livre, deppronto e semlinha (esta com `aviso: semlinha sem Depende de`); `espera ... depende de andando (coluna Em andamento)`; `espera ... ciclo de dependências`. Ordem do quadro mantida; resumo `fila: 3 podem começar, 16 vagas de 16 (0 ativos), 2 esperam` |
| CT-02 | Só leitura | escrita | Passou: rc 0, `git status --porcelain` vazio e mtime de todos os arquivos igual antes e depois |
| CT-03 | Teto fixo 2 com 1 agente vigente; depois teto 1 com 1 agente | vagas = 0, excedente | Passou: 1 pode começar e os demais `espera ... teto`; com teto 1, 0 vagas e todos `teto`; resumo `1 vagas de 2 (1 ativos)` |
| CT-04 | Coluna "Pronto" ausente e coluna "Pronto para fazer" ausente | coluna ausente | Passou: `aviso: o quadro não tem a coluna "Pronto"` (a recomendação do review já está implementada) |
| CT-05 | Pasta sem KANBAN.md (`--raiz`) | quadro ausente | Passou: mensagem SEM_QUADRO, rc 0, nada criado |
| CT-06 | Worktree do projeto, com `agentes.json` só na raiz principal | worktree | Passou com a config presente (1 ativo lido da raiz principal). Falhou sem `.forge/config.json`, ver A-R1 |

## Achados

## Recomendações (não bloqueiam; médio aberto, aceite do dono)
- A-R1 (médio) `bin/forge-check:1417-1420` (`agentes_vigentes`): a leitura de `.forge/config.json` e a de `agentes.json` ficam no mesmo `try`; se o config da raiz atual não existe ou está inválido, a lista de agentes vira vazia. Reprodução: projeto com 1 agente vigente em `.forge/run/agentes.json` e teto 1; sem `.forge/config.json` (ou numa worktree sem ele) a saída é `16 vagas de 16 (0 ativos)` em vez de `0 vagas de 1 (1 ativos)`. O modelo do projeto traz o config versionado, então o caso comum não é afetado, e o comando só recomenda (os hooks de `R-TETO` seguem decidindo); por isso não bloqueia. Correção sugerida ao implementador: ler a expiração com `try` próprio e manter o padrão de 2 h.
- Os demais itens do review (listar todas as dependências pendentes; pular o diff quando nenhum candidato tem branch; `FORGE_CARGA_LIVRE`) seguem como estão, sem impacto observado.
