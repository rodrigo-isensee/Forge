---
tipo: qa
contrato: 1
pedido: teto-bloqueia-carga-alta
branch: melhoria/teto-bloqueia-carga-alta
commit: b96bef4
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-15
---
# QA: o hook `agentes` bloqueia qualquer disparo com carga alta

Links: `docs/reviews/teto-bloqueia-carga-alta.md` (resumo e "Volta 1"), `docs/security/teto-bloqueia-carga-alta.md`, trecho da trava de carga em `docs/hooks.md`. Sem UX nem API. Obrigações: `R-TETO` (load acima de 6 ou menos de 2 GB: nenhum disparo) e a decisão B do dono (escape `FORGE_CARGA_LIVRE=1`, só a trava de carga). Offline, sem custo (`R-CUSTO`).

HEAD da branch: a1805aa; o código testado é o de b96bef4. `git diff b96bef4 origin/melhoria/teto-bloqueia-carga-alta -- hooks tests bin` é vazio (os commits depois só mexem em pareceres).

## Critério → teste → resultado
Método: `git archive origin/melhoria/teto-bloqueia-carga-alta` num diretório descartável em `$TMPDIR`, projeto com `.forge/versao`, `/proc` simulado por `FORGE_PROC` (como as fixtures), o hook `hooks/agentes.py` real, evento `PreToolUse`/`Agent`, ambiente sem `FORGE_*` herdado.

| ID | Obrigação | Cenário | Fronteira protegida | rc esperado | rc obtido | Resultado |
|---|---|---|---|---|---|---|
| PQ-1a | R-TETO libera abaixo do limite | carga 3, 8 GB, 0 ativos | carga normal | 0 | 0 | passou |
| PQ-1b | R-TETO bloqueia carga | carga 6,5, 0 ativos | logo acima de 6 | 2 | 2 | passou. Mensagem: `R-TETO: carga alta (load 6.5, 8.0 GB disponíveis; limite: load 6 e 2 GB): nenhum agente novo; espere a carga baixar; só o dono: FORGE_CARGA_LIVRE=1.` (cita R-TETO, a carga medida e o escape) |
| PQ-1c | R-TETO bloqueia memória | 1,5 GB, load 1, 0 ativos | logo abaixo de 2 GB | 2 | 2 | passou (`1.5 GB disponíveis`) |
| PQ-1d | Escape libera só a carga | carga 7, escape `1`, 0 ativos | escape válido | 0 | 0 | passou. `erros.log`: `agentes Aviso: FORGE_CARGA_LIVRE=1 liberou o disparo com carga alta (load 7.0, 8.0 GB disponíveis)` |
| PQ-1e | Escape não pula o teto | carga 7, escape, 2 ativos (teto 2) | teto cheio | 2 | 2 | passou (`2 agentes ativos, teto 2`) |
| PQ-1f | Escape não pula a deduplicação | carga 7, escape, ativo com o mesmo tipo e descrição | duplicado | 2 | 2 | passou (`já há um agente forge:qa-engineer ativo...`) |
| PQ-1g | Sem leitura, a trava não age | sem arquivos em `/proc`, 0 ativos | sem medida | 0 | 0 | passou |
| PQ-1h | Só o valor `1` libera (extra) | carga 7, `FORGE_CARGA_LIVRE=true` | valor inválido | 2 | 2 | passou (mensagem de recusa com o escape) |

Observação do método: na primeira execução o caso 1f usou tipo diferente do ativo e devolveu 0; era erro do meu cenário, não do hook. Refeito com o mesmo tipo e a mesma descrição: rc 2.

## Vermelho antes do verde
Contra o hook de `origin/develop` (sem a trava), com os mesmos `/proc` simulados: PQ-1b (carga 6,5) rc 0 e PQ-1c (1,5 GB) rc 0, quando o esperado é 2. Falham sem a implementação e passam com ela. Mutação: sem ferramenta gratuita na stack do Forge; não executada.

## PQ-2: latência (20 chamadas, processo completo, incluindo a partida do Python)
- Disparo liberado, carga 3, estado limpo: 20 chamadas, mediana 86 ms, mínimo 57, máximo 119; 9 de 20 acima de 100 ms na primeira série. Segunda série: mediana 84, máximo 113; terceira (misturada com o `develop`): mediana 86, p90 107.
- Disparo bloqueado, carga 7: mediana 75 ms, mínimo 66, máximo 99.
- Referência: o `develop` (sem a trava) mede mediana 89 ms, p90 103, máximo 122, em 60 chamadas na mesma máquina; um `python3 -c pass` sozinho mede cerca de 31 ms. A mudança não acrescenta latência mensurável (86 ms contra 89 ms).
- Leitura: a mediana fica abaixo de 100 ms em todas as séries; chamadas isoladas passam de 100 ms (máximo 145 ms) por ruído do WSL2 com sandbox, igual ao `develop`. Quem ler o critério como "cada chamada abaixo de 100 ms" não o verá cumprido de forma estrita, nem no `develop`. Ressalva registrada, sem bug.

## PQ-3: suíte do hook
`python3 -m unittest tests.test_hooks -v | tail -3`, na branch em a1805aa: `Ran 12 tests in 82.353s` / (linha em branco) / `OK`.

## Bugs
Nenhum aberto.

## Veredito
Aprovado em b96bef4. Zero bugs; a ressalva é a latência isolada acima de 100 ms, igual à do `develop`.
