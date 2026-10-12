---
id: R-TETO
titulo: Teto de recursos da máquina
verificada_por: revisão
---
# R-TETO: Teto de recursos da máquina

Propósito: texto único desta regra; os outros arquivos citam o ID. Público: todo o time. Revisão: 2026-10-12.

Teto de recursos da máquina (obrigatório). Padrão da fábrica, pensado para uma estação de desenvolvimento (ex.: WSL com 8 GB e 8 núcleos), onde paralelismo sem teto já esgotou a memória e travou tudo. O `CLAUDE.md` do projeto pode ajustar os números; na falta dele, vale:
- **teto de agentes adaptativo** (somando todos os pedidos), decidido antes de cada disparo com `uptime` (load de 1 min) e `free -m` (coluna *available*):
  - **5 agentes** com load abaixo de 3 e mais de 4 GB disponíveis;
  - **4 agentes** com load abaixo de 4 e mais de 3 GB disponíveis;
  - **3 agentes** (padrão) nos demais casos;
  - **2 agentes** com load acima de 6 ou menos de 2 GB disponíveis; nesse caso não dispare nada novo até a carga baixar;
  - equilíbrio: subir o teto nunca relaxa as regras abaixo (pesadas uma por vez, worktrees), e agentes extras vão para trabalho leve (discovery, documentação, revisão de código), não para tarefas pesadas;
- **tarefas pesadas uma de cada vez**, nunca em paralelo: testes E2E, testes de banco, build de produção, `docker compose up` de pilha completa, carga de volume para teste de performance;
- no máximo **2 cópias de trabalho** (`git worktree`) além do diretório principal; cada instância paralela usa a sua, e a worktree é removida assim que a branch dela for mesclada;
- antes de disparar uma tarefa pesada, confira `uptime` e `free -m`: com load average acima de 8 ou menos de 1,5 GB disponíveis, espere a carga baixar;
- containers e servidores de desenvolvimento que não estão em uso são parados ao fim da etapa;
- melhoria da fábrica também entra no teto, como cartão próprio.
