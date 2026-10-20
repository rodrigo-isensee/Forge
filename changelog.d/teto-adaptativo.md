### Alterado
- R-TETO: o teto de agentes passa a ser adaptativo ao hardware (dispara com load de 1 min < 0,8 × nproc e MemAvailable > max(1 GB, 15% do total), no máximo nproc agentes; sem número fixo de worktrees); o hook agentes aplica a regra lendo nproc, /proc/loadavg e /proc/meminfo
