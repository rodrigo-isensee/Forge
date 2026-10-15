---
tipo: review
contrato: 1
pedido: teto-bloqueia-carga-alta
branch: melhoria/teto-bloqueia-carga-alta
commit: 345da10
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-15
---
# Review independente: hook `agentes` bloqueia qualquer disparo com carga alta

Escopo: `git diff origin/develop..345da10` (`hooks/agentes.py`, 9 fixtures, `docs/hooks.md`, `CHANGELOG.md`). Revisor diferente do autor (`R-REVIEW`). Parecer: **aprovado**, sem bloqueantes.

## Fidelidade ao `R-TETO`
- Limites idênticos aos da regra para a faixa de 2 agentes: load de 1 min estritamente acima de 6 ou memória disponível estritamente abaixo de 2 GB (`carga > 6 or memoria < 2`; 6,0 e 2,0 passam). A leitura reaproveita `medir()` (`/proc/loadavg`, `MemAvailable`), a mesma do teto adaptativo.
- A regra diz "nesse caso não dispare nada novo": a trava vem antes de `calcular_teto`, então vale com 0 ou 1 ativo e com `teto_agentes` ou `teto_maximo` (a regra fala só em fixar e limitar o teto, não em desligar a trava). Sem leitura (`None`), mantém o fallback de 3 da regra.
- Os limites de 8 e 1,5 GB da regra são de tarefa pesada e continuam no hook `pesado`; não se misturam.

## Fixtures que mudaram de expectativa
- `adaptativo-2-libera` e `teto-fixo-acima-do-adaptativo`: usavam load 7 e esperavam liberar com 1 e 3 ativos. Com a regra cumprida, load 7 bloqueia sempre; passaram a load 5 e mantêm a intenção (teto 3 adaptativo libera com 1 ativo; teto fixo 4 libera com 3). Justificado; descrições atualizadas.
- `adaptativo-2-load-bloqueia` e `adaptativo-2-memoria-bloqueia`: continuam bloqueando (rc 2); só muda a mensagem esperada, agora a da trava. Justificado.
- Nenhuma expectativa foi afrouxada; duas passaram de "libera" para carga menor, não para tolerar carga alta. Fixtures novas cobrem 0 ativos com load 6,5, memória 1,5 GB com 1 ativo, teto fixo 5 com load 7, e as guardas de regressão (load 5 libera, sem `/proc` libera).

## Ramo de `calcular_teto` inalcançável: manter
`teto_adaptativo` ainda devolve 2 para carga alta, mas `lancar` já bloqueou antes. Manter: é a tabela de faixas da `R-TETO` em um só lugar, tem teste direto (`test_faixas_do_teto_adaptativo`, em `tests/test_hooks.py`) e removê-lo só aumentaria o diff e criaria uma tabela com buraco. Aceito como recomendado (não bloqueia): se um dia a trava sair, o 2 já está certo.

## Mensagem
`R-TETO: carga alta (load 7.0, 8.0 GB disponíveis; limite: load 6 e 2 GB): nenhum agente novo, mesmo com poucos ativos; espere a carga baixar.` (saída real do hook, rc 2). Cita o ID, os valores medidos, o limite e a ação (esperar); orienta o Jarvis sem ambiguidade.

## Latência
Hook inteiro (`python3 hooks/agentes.py`, projeto sintético com `FORGE_PROC`): 44 a 48 ms no bloqueio, 34 a 37 ms no ramo de liberação; abaixo de 100 ms. A leitura extra de `/proc` é de 2 arquivos pequenos.

## Evidência dos comandos
- `python3 -m unittest tests.test_hooks -v | tail -3`: `Ran 12 tests in 70.448s` e `OK`.
- `bin/forge-check docs`: rc 0, sem saída (nada a reportar).
- `praticas.md` do Forge não alcança este diff por regra de leitura além do checklist da skill; shellcheck não se aplica (Python).

## Checklist
- Faz o que o pedido manda, sem extras; reserva de 2 h do `agentes.py` intacta (fora do escopo). Sem dependência nova, sem custo (`R-CUSTO`), sem termo de projeto (`R-NEUTRO`). Linha nova em `## [Não publicado]` do `CHANGELOG.md`; versão sobe só na release (ADR 0006).
- Rótulo `afrouxa-regra`: não precisa, a mudança endurece e os arquivos não estão em `PROTEGIDOS`; confere com o parecer de autor. `hooks/` é sensível: a catraca exige o parecer de QA do pedido, a cargo do fluxo.
- Recomendado, não bloqueia: `carga_alta` exige as duas medidas; se só uma faltar, não bloqueia mesmo com a outra alta. É o mesmo critério do `teto_adaptativo` (fallback de 3) e a regra só trata "sem leitura"; aceitável, registrar se aparecer caso real.
- Reversão: reverter o commit `fix(hooks)`; não há estado persistido novo.
- Segurança e pipeline: nada que exija parecer do `security-engineer` ou do `devops-engineer`.
