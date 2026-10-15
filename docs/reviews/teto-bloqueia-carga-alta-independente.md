---
tipo: review
contrato: 1
pedido: teto-bloqueia-carga-alta
branch: melhoria/teto-bloqueia-carga-alta
commit: b96bef4
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

## Re-review volta 1
Escopo: `git diff 711d9ca..26b1006` (código em `b96bef4`; `26b1006` só acrescenta a seção do parecer de autor). Revisor diferente do autor (`R-REVIEW`). Parecer: **aprovado**, sem bloqueantes. Parecer anterior: aprovado em `345da10`. Prova: `python3 -m unittest tests.test_hooks -v | tail -3` termina em `OK`.

### O escape pula só a trava de carga
- Em `lancar` (`hooks/agentes.py`) o `if os.environ.get("FORGE_CARGA_LIVRE") == "1"` fica dentro de `if carga_alta(...)`: só troca o `bloquear` da carga por `registrar_escape`. A deduplicação vem antes e o `calcular_teto` depois, ambos intactos. Comparação com `== "1"` exata: `true`, `0`, vazio e `1 ` não liberam.
- `registrar_escape` usa `registrar_erro`, que engole qualquer falha: o registro nunca bloqueia nem muda o código de saída (0). Sem `/proc`, nada muda (como antes). `R-TETO.md` e a reserva de 2 h não foram tocados.
- Variável do processo hospedeiro, mesmo padrão de `FORGE_GUARDA_ABERTA`; o agente não a define. O teste `rodar` limpa a variável do ambiente, então o escape do dono não vaza para as demais fixtures.

### Fixtures
- Novas (4): `carga-livre-libera` (load 7, 0 ativos: rc 0 e linha no `erros.log`); `carga-livre-respeita-teto` (load 7 com 2 ativos: rc 2 por teto, e a linha do escape registrada, coerente porque a trava de carga foi pulada antes do teto); `carga-livre-valor-invalido` (`true`: rc 2); `carga-alta-cita-escape` (sem a variável: rc 2 e a mensagem cita o escape). Cobrem libera, limite do escape, valor inválido e mensagem.
- Alteradas (2): `carga-alta-ignora-teto-fixo` e `memoria-baixa-bloqueia-com-um-ativo`: só o trecho esperado de stderr cresceu para a nova mensagem; o bloqueio (rc 2) permanece. Nenhuma expectativa afrouxada.
- Observação (não bloqueia): não há fixture do escape com deduplicação (mesmo tipo e descrição). O código garante a ordem (duplicado antes da trava), então o risco é baixo; vale uma fixture se o trecho voltar a mudar.

### Mensagem de recusa
`R-TETO: carga alta (load X, Y GB disponíveis; limite: load 6 e 2 GB): nenhum agente novo; espere a carga baixar; só o dono: FORGE_CARGA_LIVRE=1.` Mantém ID, valores medidos, limite e ação de espera. Ponto de atenção: citar o escape ao Jarvis pode induzir tentativa de "usá-lo"; o agente não consegue defini-lo, e o texto diz "só o dono". Aceito; reduz o risco de o Jarvis improvisar outro contorno (`R-CONFORMIDADE`).

### Rótulo `erro-hook` no `vigia`: aceitável, sem cartão
O uso do escape aparece como `Aviso: ...` no `erros.log` e o `vigia` o mostra como `aviso(s)` (gravidade 1, sem ser `contorno`). É o efeito desejado: o dono vê cada uso do escape, e não é tratado como violação. O rótulo "erro-hook" é impreciso (não é erro), mas o texto da linha diz o que ocorreu e `docs/hooks.md` documenta a correspondência. Se o ruído incomodar, um rótulo próprio fica para melhoria futura; não vale cartão agora. Segurança segue no parecer próprio (`docs/security/`), não refeito aqui.

### Reversão e documentação
Reversão registrada (remover o `if` do escape). `docs/hooks.md` e a linha de `## [Não publicado]` do `CHANGELOG.md` atualizados, sem alterar a versão. `R-NEUTRO` preservada.
