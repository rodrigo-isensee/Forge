---
id: R-TETO
titulo: Teto de recursos da máquina
verificada_por: revisão e hooks `agentes` e `pesado`
---
# R-TETO: Teto de recursos da máquina

Propósito: texto único desta regra; os outros arquivos citam o ID. Público: todo o time. Revisão: 2026-10-12.

Teto de recursos da máquina (obrigatório). O teto se adapta ao hardware de cada máquina, calculado na hora; nenhum número fixo de máquina vale. O Linux já limita a memória; o que se protege é o processador. O `CLAUDE.md` do projeto só diverge dele com motivo, e o modelo da fábrica não fixa um teto menor por padrão. Na falta de ajuste, vale:
- **teto de agentes adaptativo** (somando todos os pedidos), decidido antes de cada disparo: dispara enquanto o load de 1 min (`/proc/loadavg`) for **menor que 0,8 × nproc** (80% dos núcleos) **e** `MemAvailable` (`/proc/meminfo`) for **maior que max(1 GB, 15% de `MemTotal`)**; o total de agentes ativos nunca passa de **nproc**. Com load a partir de 80% ou memória no piso, nada novo dispara até a carga baixar;
  - equilíbrio: o teto nunca relaxa as regras abaixo (pesadas uma por vez, worktrees), e agentes extras vão para trabalho leve (discovery, documentação, revisão de código), não para tarefas pesadas;
- o hook de teto (ADR 0003) aplica essa regra sozinho, lendo `nproc` (`os.sched_getaffinity(0)`, senão `os.cpu_count()`), o load e a memória de novo antes de cada disparo, sem cache nem janela: o teto sobe e desce com a carga medida; sem leitura, usa 3 (ou nproc, se menor). `teto_agentes` em `.forge/config.json` fixa o teto e sobrepõe o adaptativo; `teto_maximo` limita os dois. O Jarvis ainda decide por disparo dentro do teto;
- a **suíte do Forge** (`scripts/suite-paralela.py`) mede a folga durante toda a execução, a cada 1,5 s, pela CPU de `/proc/stat` (os núcleos ocupados por processos de fora da suíte) e pelo `MemAvailable`, não pelo load de 1 min (decisão do dono, 2026-11-04 20:41): um processo por módulo, mais processos enquanto a suíte cabe em 0,8 × nproc junto com a carga de fora, menos quando ela aperta (descer é não lançar o próximo), de min(2, nproc) a nproc e nunca abaixo de min(4, nproc) com folga; sem teto fixo (SUITE-FLUIDA, decisão do dono em 2026-11-04). `FORGE_SUITE_PROCS` fixa o número, de 1 a nproc;
- **tarefas pesadas uma de cada vez**, nunca em paralelo: testes E2E, testes de banco, build de produção, `docker compose up` de pilha completa, carga de volume para teste de performance;
- o limite de **cópias de trabalho** (`git worktree`) segue os agentes ativos (cada instância paralela usa a sua) e o disco livre, sem número fixo; a worktree é removida assim que a branch dela for mesclada;
- antes de disparar uma tarefa pesada, confira o load e a memória disponível: com load a partir de 80% de nproc ou memória no piso, espere a carga baixar;
- containers e servidores de desenvolvimento que não estão em uso são parados ao fim da etapa;
- melhoria da fábrica também entra no teto, como cartão próprio.
