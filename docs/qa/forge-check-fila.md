---
tipo: qa
contrato: 1
pedido: forge-check-fila
branch: melhoria/forge-check-fila
commit: 160f37063baf2a3ac7f3d169f8d331a4795a52f1
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-21
---
# QA - `forge-check fila` (P9, cartão FORGE-CHECK-FILA), volta 2

Links: `docs/pedidos/forge-check-fila.md`, seção "P9" de `docs/propostas/aq/p8-p9.md`, `docs/reviews/forge-check-fila.md`. Não há UX nem API; as obrigações são a seção P9 (ordem, motivos, só leitura, vagas de `R-TETO`). Código testado: 160f370 (o HEAD 1345909 só acrescenta o parecer de review). Sondas só em `$TMPDIR`, sem rede (`R-CUSTO`). Sem gatilho de segurança. Este parecer substitui o da volta 1 (2d14b8c), que tinha o médio A-R1 e `aceite_usuario: sim`; o médio está corrigido e não sobrou bug aberto, então não há aceite a gravar.

## Suíte
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -q`: 1217 testes, OK (371 s).
- `scripts/validar-plugin.sh`: Validation passed (avisos de rede bloqueada pelo sandbox não afetam o resultado).

## Resultados
| ID | Obrigação / cenário | Fronteira protegida | Resultado |
|---|---|---|---|
| CT-01 | Sonda git com cartões em "Pronto para fazer", "Em andamento" e "Pronto"; pedidos sem dependência, com dependência em andamento, com dependência pronta, sem a linha e em ciclo | dependência fora de "Pronto"; em "Pronto" | Passou: livre, deppronto e semlinha (com `aviso: semlinha sem Depende de`) podem começar; `espera ... depende de andando (coluna Em andamento)`; ciclo1 e ciclo2 `espera ... ciclo de dependências`; ordem do quadro mantida; rc 0; resumo `3 podem começar, 3 vagas de 4 (1 ativos), 3 esperam` |
| CT-02 | Só leitura | escrita | Passou: `git status --porcelain` vazio e mtime de todos os arquivos igual antes e depois |
| CT-03 | Teto 4 com 1 agente vigente; teto 1 com 1 agente | vagas = 0, excedente | Passou: 3 vagas de 4; com teto 1, 0 vagas e `espera ... teto` |
| CT-04 | Coluna "Pronto" ausente; coluna "Pronto para fazer" ausente | coluna ausente | Passou: `aviso: o quadro não tem a coluna "..."` nos dois casos |
| CT-05 | Pasta sem KANBAN.md (`--raiz`) | quadro ausente | Passou: SEM_QUADRO, rc 0, nada criado |
| CT-06 | Refaz o A-R1: worktree da sonda sem `.forge/config.json`, com 1 agente vigente em `.forge/run/agentes.json` da cópia principal | config ausente; worktree | Passou: `15 vagas de 16 (1 ativos)` (antes: `0 ativos`). Também com config inválido na worktree e com a cópia principal sem config: 1 ativo contado. O teto cai no padrão sem config, como a suposição do autor registra |

## Achados

## Recomendações (não bloqueiam)
- Sem bug aberto. Os itens menores do review (listar todas as dependências pendentes; pular o diff quando nenhum candidato tem branch) seguem como estão, sem impacto observado.
