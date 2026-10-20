---
tipo: review
contrato: 1
pedido: teto-adaptativo
branch: melhoria/teto-adaptativo
commit: 119bc506d0b199535b01eb9d367001921365079b
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-19
---
# Code review: TETO-ADAPTATIVO (o teto de agentes segue a máquina real)

Diff revisado: `origin/develop...119bc50` (base 2359f3c, o merge da develop já está dentro; 28 arquivos, 492 inserções, 118 remoções). A develop andou depois (6408d8c, DV-6); por isso o diff de dois pontos mostra a remoção de `dv-6`, que não pertence a esta entrega.

Ferramentas, rodadas pelo revisor só no recorte (a suíte inteira é prova do autor, 867 OK, e o pre-push a roda; R-TETO, pesado um por vez):
- `python3 -m unittest tests.test_hooks`: 20 testes, OK.
- `python3 -m unittest tests.test_forge -k kanban -k instancias -k limites`: 7 testes, OK.
- `python3 -m unittest tests.test_forge -k invariante -k Invariante -k regra -k Neutralidade`: 6 testes, OK.

## Contra o escopo e as decisões do dono
- E1, `docs/regras/R-TETO.md`: sem número fixo de máquina; dispara com load de 1 min < 0,8 × nproc e `MemAvailable` > max(1 GB, 15% de `MemTotal`), no máximo nproc agentes, sem leitura 3; worktrees seguem os agentes ativos e o disco livre; pesadas seguem uma por vez (fora do escopo, intacta). Bate com a decisão técnica do Jarvis e com "adaptativo para cada hardware".
- E2, `hooks/agentes.py`: `nucleos`, `medir` (agora com `MemTotal`), `carga_alta` e `teto_adaptativo` aplicam a regra; `teto_agentes` fixa e `teto_maximo` limita, como antes; a trava de carga continua valendo para qualquer teto e o escape `FORGE_CARGA_LIVRE=1` continua só na trava de carga.
- Fórmula num lugar só: `bin/forge-check` (`teto_calculado`) importa `agentes.calcular_teto` do hook, sem repetir o limite de carga nem o de memória. O fator de coluna (`teto // 3`, mínimo 1) só existe no `forge-check` e é a regra de R-WIP, não uma segunda cópia da fórmula. A única regra a mais no `forge-check` é aplicar `teto_maximo` também sobre o `teto_agentes` fixo (ver A2).
- Modelo dos projetos: `templates/projeto/.forge/config.json` só tem `pesados`, e `templates/projeto/CLAUDE.md` não fixa teto. Nenhum teto menor por padrão, como pede a decisão "Mesma coisa aplica para os projetos".
- Volta 1 (worktrees e WIP): `R-WIP` sem "2 worktrees", instâncias até o teto de R-TETO, limites de coluna mínimos até teto 3 e ×(teto ÷ 3) acima disso, Em andamento fora da escala ("1 cartão por agente" continua). `agents/jarvis.md:45` cita R-TETO sem números. Bate com a decisão do dono sobre worktrees e WIP.
- R-CUSTO e R-NEUTRO: nada pago; nada de projeto nem de máquina específica (os 16 núcleos e os 7,9 GB aparecem só no pedido, não na regra, no hook nem no modelo).
- Fragmento `changelog.d/teto-adaptativo.md` presente; `CHANGELOG.md` e versão intocados.

## Testes por hardware e do kanban
- Hook, unidade (`tests/test_hooks.py`, `test_faixas_do_teto_segue_o_hardware`): 1, 8 e 16 núcleos, com os limites exatos (12,7 e 12,8 em 16; 6,39 e 6,4 em 8; 0,7 e 0,8 em 1), piso de 15% (2,4 e 2,5 GB de 16) e piso de 1 GB (1,0 e 1,1 GB de 4); cada medida ausente cai no 3 e nunca é carga alta.
- Hook, fixtures: `nproc-3`, `nproc-4` (libera e bloqueia), `nproc-8` (libera e bloqueia), `nproc-16-libera`, load abaixo, no limite e acima de 80%, memória abaixo e acima do piso, piso de 1 GB nos dois lados, `teto_maximo`. O padrão do fixture virou "sem leitura" e o `FORGE_NPROC` é sempre fixado (8), então o resultado não depende da máquina que roda a suíte.
- Kanban (`tests/test_forge.py`): `check` fixa `FORGE_NPROC` e um `/proc` folgado só para `kanban`; `test_instancias_seguem_o_teto_adaptativo` cobre 4, 6 e 16 núcleos e os dois ajustes de config; `test_limites_de_coluna_escalam_com_o_teto` cobre 1, 3, 6, 7 e 16 núcleos (fatores 1, 2 e 5, os dois lados de cada limite).

## Invariantes (`tests/config.json`)
Só três linhas saíram, todas trocadas pela decisão do dono; nada mais mudou na lista:
- R-TETO: antes `\*\*2 agentes\*\* com load acima de 6`; depois `menor que 0,8 × nproc`.
- R-WIP: antes `respeitando o \`R-TETO\` inteiro: o teto de agentes, o limite de 2 worktrees além do principal, as tarefas pesadas uma por vez`; depois a mesma frase com `as worktrees \(uma por instância, com disco livre\)`.
- R-WIP: antes `são no máximo 3 \(o diretório principal e as 2 worktrees`; depois `são no máximo o teto de agentes de \`R-TETO\``, mais um novo, `cresce na proporção \*\*teto ÷ 3, arredondado para baixo\*\*`.
Os demais invariantes de R-TETO (obrigatório, adaptativo, "nunca relaxa as regras abaixo", pesadas uma de cada vez) e de R-WIP ficam. O PR precisa do destaque no título, como o autor já registrou.

## Segurança
O review de segurança do hook de controle é a E1.3 (`security-engineer`, `docs/security/teto-adaptativo.md`), em paralelo; não o refaço. Para ele, sem achado meu: `FORGE_NPROC` é variável nova lida em produção, no mesmo modelo de `FORGE_PROC` (ambiente do processo do hook, que o agente não define); um valor alto sobe o teto.

## Achados
- A1 (bloqueante): `docs/hooks.md:11` e `docs/hooks.md:77` ainda descrevem a regra antiga ("load acima de 6 ou menos de 2 GB disponíveis", "faixas de `R-TETO` (2 a 5 ...)"); é a referência dos hooks para todos os projetos e agora contradiz R-TETO e o próprio hook. Definição de pronto: a documentação afetada entra na mesma entrega. Sugestão: as duas linhas dizem "load de 1 min a partir de 0,8 × nproc ou `MemAvailable` até max(1 GB, 15% do total)" e "teto adaptativo de `R-TETO`: até nproc agentes; sem leitura, 3", sem número de máquina.
- A2 (recomendado): `bin/forge-check:245` aplica `teto_maximo` também ao `teto_agentes` fixo, e o hook não (`hooks/agentes.py:73-74`; `docs/hooks.md:79`: "não afeta o `teto_agentes` fixo"). Com `teto_agentes: 8` e `teto_maximo: 5`, o hook deixa 8 agentes e o kanban barra a sexta instância. É mais estrito e o R-WIP o descreve ("menos se `teto_maximo` ou `teto_agentes` ... for menor"), então não afrouxa nada; mas são duas regras para o mesmo par de chaves. Sugestão: num PR futuro, uma linha em `docs/hooks.md:79` dizendo que o kanban usa o menor dos dois, ou alinhar os dois.
- A3 (recomendado): `hooks/agentes.py:63-66`: sem leitura de `/proc`, o teto é 3 mesmo com nproc 1 ou 2, e R-TETO diz "nunca passa de nproc". Sugestão: `min(3, nproc)` quando `nucleos()` responder.
- A4 (recomendado): `hooks/agentes.py:32` usa `os.cpu_count()`, que conta todos os núcleos da máquina; o `nproc` da regra respeita afinidade e cpuset (`os.sched_getaffinity(0)`). Em container ou com afinidade restrita, o teto e o limite de 80% sobem acima do que o processo usa. Sugestão: `len(os.sched_getaffinity(0))` quando existir, com `os.cpu_count()` de reserva.

**Reprovado** por A1, ajuste só de texto em `docs/hooks.md`. Código, testes e invariantes estão corretos e batem com as decisões do dono; A2 a A4 não pedem nova volta. A revalidação da volta é só do delta de `docs/hooks.md`.
