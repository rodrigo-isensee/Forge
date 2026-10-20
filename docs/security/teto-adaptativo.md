---
tipo: revisao-seguranca
contrato: 1
pedido: teto-adaptativo
branch: melhoria/teto-adaptativo
commit: 119bc506d0b199535b01eb9d367001921365079b
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-19
---
# Review de segurança: teto-adaptativo

Escopo: `git diff origin/develop 119bc506...`: `hooks/agentes.py`, `bin/forge-check` (kanban), `docs/regras/R-TETO.md`, `docs/regras/R-WIP.md`, fixtures e testes. Revisão estática; `tests.test_hooks` rodou verde (20 testes).

## Gatilhos
Hook de controle (`hooks/agentes.py`, ADR 0003) e regra de conformidade (R-TETO, R-WIP); `forge-check kanban` é verificador de regra.

## Achados

## Detalhe dos achados
Conferências pedidas (todas cumpridas):
- Sem leitura de /proc o teto cai em 3: `hooks/agentes.py:62-63` (`teto_adaptativo` devolve `RESERVA["teto_agentes"]`, que é 3 em `hooks/_comum.py:27`) e `agentes.py:80-81` (explicação). Sem medida, `carga_alta` não bloqueia (`agentes.py:55-56`), mas o teto de 3 segue valendo: falha segura, igual ao comportamento anterior.
- `teto_agentes` e `teto_maximo` continuam sobrepondo: `agentes.py:70-71` (fixo vence) e `agentes.py:75-77` (máximo limita); `bin/forge-check:243-245` usa a mesma função. A trava de carga vale antes e não é desligada por eles (`agentes.py:101`).
- FORGE_NPROC e FORGE_PROC (`agentes.py:32,40`): são variáveis do ambiente do processo do hook, que o Claude Code herda do dono; um agente, pelo Bash, não altera o ambiente do hook. Não são caminho realista para um agente desligar o teto; equivalem a `FORGE_CARGA_LIVRE=1`, já aceito como escape do dono (mas aquele registra no erros.log e estes não). Ver R1.
- Tarefas pesadas uma por vez: `hooks/pesado.py` não está no diff e não usa o teto; R-TETO mantém o texto (`docs/regras/R-TETO.md`, "tarefas pesadas uma de cada vez").
- Fator de coluna não remove o 1 cartão por agente: `bin/forge-check:274-275,281-287`: o fator só multiplica limites de tipo `total`; o tipo `agente` segue com `wip[0]` (1) e só instâncias extras com `worktree:` distinto até o teto (`instancias_do_agente`, `:254-265`). Entrada inválida (valor ausente, não inteiro, bool, 0) é descartada em `:242-243`. FORGE_NPROC inválido ou 0 cai em None, logo em 3; negativo bloqueia tudo (falha fechada).
- Erro interno do hook: `_comum.py:750-752` registra e libera (ADR 0003), inalterado.

Recomendações (não bloqueiam; sem caminho de ataque realista, por isso fora do bloco de achados):
- R1 (baixa, informativa, P, dono tech-lead): `FORGE_NPROC`/`FORGE_PROC` valem em uso real e sem registro. Se o dono ou um `settings.json` de projeto os definir, o teto e a trava de carga somem em silêncio e o `forge-check kanban` afrouxa os limites. Correção mínima: registrar no erros.log como o `FORGE_CARGA_LIVRE`, ou só honrá-los com uma variável de teste.
- R2 (baixa, P, tech-lead): `os.cpu_count()` (`agentes.py:32`) ignora afinidade e cota de cgroup; em container com cota menor que o host, nproc e o limite de 80% ficam superestimados. Preferir `len(os.sched_getaffinity(0))` quando existir. No WSL do dono (`.wslconfig`) não afeta.
- R3 (informativa): o load de 1 min atrasa; uma rajada de disparos antes de o load subir pode chegar a nproc agentes. O limite é o próprio nproc e a memória só é checada no disparo; aceitável para agentes de trabalho leve (R-TETO), observar na prática.
- R4 (informativa): o resultado de `forge-check kanban` agora depende da máquina (teto medido na hora); o mesmo quadro pode passar numa máquina e falhar em outra. É consequência da decisão do dono (adaptativo por hardware), não risco de segurança.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática e `unittest` do hook; gitleaks, osv-scanner e semgrep não foram necessários (sem dependência nem segredo novo no diff) nem executados.
