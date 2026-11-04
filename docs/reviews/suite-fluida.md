---
tipo: review
contrato: 1
pedido: suite-fluida
branch: melhoria/suite-fluida
commit: 24499f721c2c7be8868fef7eb62aa826a9773056
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-04
---
# Review: suite-fluida

Etapa E1.5 do cartão SUITE-FLUIDA. Diff lido: `git diff b45e40a...24499f7` (commits fe61323 e 24499f7, do dono), seis arquivos. Rodada única, em paralelo com os pareceres de devops (`docs/devops/`) e de segurança (`docs/security/`), que este parecer não refaz.

## Ferramentas
- `python3 -m unittest tests.test_suite_paralela` na worktree, no head 24499f7: `Ran 49 tests in 47.492s`, `OK`; a árvore ficou limpa. A suíte inteira fica com o QA (D-5).
- O Forge não tem `docs/engineering/praticas.md`: valeu o checklist da skill `engineering-practices`.
- Teto M14: 253 linhas de código e teste (`scripts/suite-paralela.py` 161+27, `tests/test_suite_paralela.py` 63+2). Não toca `hooks/` nem `PROTEGIDOS`, e carrega um comportamento só (a suíte fluida; o segundo commit corrige o primeiro). Aceito a exceção desde que o corpo do PR (E1.6b) traga `teto: excedido, 253 linhas, <motivo>`.

## Medida por CPU de /proc/stat x decisão do dono (E1, E2)
Diverge. A decisão do dono de 2026-11-04 pede o limite pela folga medida com o load de 1 min e o MemAvailable, a mesma conta do R-TETO. A memória segue essa conta (`medir_carga`, linha 474). A CPU, não: `Medidor` (linha 234) lê `/proc/stat` e os ticks dos grupos da suíte, e `quantos_em_paralelo` (linha 252) decide pelos núcleos ocupados por outros, com a suíte descontada. O load de 1 min não entra mais na decisão do modo fluido; só aparece em `registrar_vermelha`. O motivo, dado no commit 24499f7, é técnico e plausível: o load de 1 min chega atrasado, e os módulos com subprocessos usam mais de um núcleo cada. Mesmo assim, a troca é do dono decidir. **Ponto para o dono:** aceitar a medida por `/proc/stat` (e o texto do R-TETO passa a descrevê-la) ou voltar ao load de 1 min. Não peço reimplementação neste parecer. O A2 cobra só o texto, que hoje afirma a mesma conta.

## Critérios C1 a C15 (desenho, `## E1-E2`)
- C1 (um só nproc): cumpre em parte. `nucleos()` (linha 180) usa `sched_getaffinity` e cai para `cpu_count`, e `orquestrar` passou a usá-la (linha 649). Mas é cópia de `hooks/agentes.py:nucleos()`, sem o `FORGE_NPROC` e sem o teste que compara as duas (A4). Há outro detalhe: a medida de CPU usa as CPUs de `/proc/stat` (linha 209), que num cpuset podem ser as do host.
- C2 (limite superior): cumpre no efeito. `alvo` nunca passa de nproc (linhas 263-266), e `while pendentes and rodando < alvo` (linha 480) não passa dos módulos que faltam. Diverge no texto: `TETO = 4` (linha 59) continua, agora como piso e não como teto. Não há teste do laço com nproc=2 e 88 módulos (A5).
- C3 (piso e progresso): cumpre. O alvo mínimo é min(2, nproc), que nunca é menor que 1, então a fila sempre anda. Diverge do desenho: com carga alta o piso é 2, não 1. É o mesmo comportamento de antes da branch, portanto conservador. Falta o teste de carga alta contínua no laço (A5).
- C4 (descer): cumpre. Descer é não lançar (linha 480), e nenhum processo é morto por carga. Diverge: com folga, a suíte não desce abaixo de min(4, nproc) (linha 266).
- C5 (subir com histerese): diverge com justificativa. A subida é de +1 por medida, e só com `livre >= 1` núcleo (linhas 264-265). O intervalo é de 1,5 s, não 5 s: a regra dos 5 s existia por causa do atraso do loadavg, que a medida por `/proc/stat` não tem. O W inicial é 4 ("sem medida da CPU" na primeira volta), não min(2, ...).
- C6 (frequência): cumpre o teto de 5 s, com 1,5 s (linha 486). Diverge: o término de um módulo não dispara medida, e a vaga espera até 1,5 s. A política (`quantos_em_paralelo`) é pura e testada, mas sem relógio injetável.
- C7 (sem /proc): diverge. Sem medida da CPU, vale min(4, nproc), não min(3, nproc, módulos). Com nproc desconhecido, vale 1, e isso cumpre (linha 260; teste `q(None, ...) == 1`).
- C8 (FORGE_SUITE_PROCS): não cumpre. O código aceita até max(4, nproc) (linha 192), e o teste fixa que 4 vale com nproc=2 (`tests/test_suite_paralela.py:114`). O desenho, o R-TETO:14, a docstring (linha 15) e o fragmento dizem "1 a nproc". Esse é o A1. A recusa antes do `discover` e o teste com nproc+1 cumprem.
- C9 (higiene): cumpre. Todo processo nasce por `lancar_um`, com `nice`, grupo próprio, TMPDIR 700 e `vigiar_pai`. O sinal levanta `Interrompido`, que sai de `rodar_fluido` antes de qualquer outro `Popen`, e `encerrar` cobre `filhos`. O detalhe de trava e sinal fica com a segurança.
- C10 (completude): cumpre. É um módulo por processo, tirado da fila por `pop(0)`. `conferir_particao` roda sobre as partes lançadas (`erros_fila`), e a completude por multiconjunto e a conferência da árvore não mudaram. O teste do brinquedo vermelho reprova (`test_modo_fluido_reprova_um_modulo_vermelho`).
- C11 (uma suíte por vez): cumpre. A trava e o `pre-push` não mudam.
- C12 (ordem da fila): cumpre. `ordem_da_fila` vai do mais pesado ao mais leve, com a mediana para módulo sem peso, e tem teste. `FORGE_SUITE_MEDIR` e o K6 não mudam.
- C13 (observabilidade): cumpre em parte. A linha de origem diz "fluido", e a linha final `Ran N tests ... (M processos, até P em paralelo)` mantém o prefixo e o `OK`/`FAILED`. A linha de mudança (linha 478) não traz o instante nem os GB, e só sai quando o alvo difere de quem roda. `montar_resumo` (linha 548) continua dividindo por "processos", que agora são os 88 módulos (A6).
- C14 (CI): cumpre no código. O script é o mesmo, sem ramo de CI e sem serviço novo. O tempo nos runners fica com o devops.
- C15 (escopo): cumpre. `forge-mutante`, `trabalhadores_do_pool` e `apoio_volta_unica` não aparecem no diff.

## E3: textos com o teto fixo de 4
A busca do brief no head 24499f7 deu uma linha só: `scripts/suite-paralela.py:59: TETO = 4  # com folga, a suíte nunca roda com menos que min(TETO, nproc) ...`. Ela é intencional (o piso). Item a item da lista "A mudar na branch do dono":
- `suite-paralela.py:2`, `:9`, `:10` (docstring): tratados, nas linhas 2 e 9-15.
- `:53` `TETO = 4`: mantido como piso. Diverge de C2 no texto, sem efeito de teto.
- `:174`, `:177-178` (faixa 1..TETO): trocados por `max(TETO, nproc)`, que é a origem do A1.
- `:180-183` (`min(TETO, nproc)`, `min(2, base)`): continuam em `numero_de_processos`, mas o modo fluido não usa esse ramo, e sem `FORGE_SUITE_PROCS` ele é código morto (A3).
- `:529` `os.cpu_count()`: tratado (`nucleos()`).
- `README.md:68` e `docs/hooks.md:115`: tratados.
- `tests/test_suite_paralela.py:105` e `:111`: mantidos. Ainda passam porque testam o ramo morto (A3).
- `:109-110`: mantidos (o mesmo ramo). O "não repõe" de C4 é coberto por `test_quantos_em_paralelo_segue_a_carga_de_fora`.
- `:113` ("5" inválido): trocado por "17" com nproc=16. `:591-593`: trocado para max(4, cpu_count)+1.
- `docs/regras/R-TETO.md`: item novo acrescentado (linha 14). O texto diz "a mesma conta", e a medida é outra (A2); a faixa de `FORGE_SUITE_PROCS` não bate com o código (A1).
- `tests/config.json`: intacto. Os invariantes do R-TETO (linhas 407-413) seguem.

## E4: teto de agentes
A troca proposta em `## E4` do desenho é só texto e não afrouxa: acrescenta "de novo", "sem cache nem janela" e "o teto sobe e desce com a carga medida", sem tirar limite nem condição, e o invariante de `tests/config.json` não cita a frase. A branch ainda não a tem: o R-TETO:13 está igual à base. O ajuste é a E1.2b, numa outra delegação.

## E5: fragmento de changelog
`changelog.d/suite-fluida.md` existe, com o tipo `Alterado` (um dos tipos de `bin/forge-changelog`) e um texto que descreve o comportamento e a marca "afrouxa R-TETO". A faixa "de 1 a nproc" do texto precisa acompanhar o desfecho do A1.

## Achados recorrentes (PA-7)
Conferi AR-1 a AR-11. O AR-9 (limite antigo no texto) foi conferido pela busca do E3, e nenhum texto ainda cita "até 4 processos". O caso inverso, texto novo que não bate com o código, está no A1 e no A2, e não é a mesma classe. O AR-4 (teste que herda o ambiente do CI) foi conferido: os testes novos do brinquedo passam pelo `roda`/`self.env` de sempre. Nenhum achado deste parecer repete uma classe registrada, então não há linha AR nova.

## Achados
- A1 (bloqueante) scripts/suite-paralela.py:192 · FORGE_SUITE_PROCS aceita até max(4, nproc), e o teste fixa 4 com nproc=2 (tests/test_suite_paralela.py:114), mas o R-TETO:14, a docstring (linha 15), o fragmento e o C8 dizem 1 a nproc. Alinhe o código ao texto, ou o texto ao código com aval do dono.
- A2 (bloqueante) docs/regras/R-TETO.md:14 · O item novo diz que a suíte segue a mesma conta do R-TETO, mas ela decide pela CPU de /proc/stat sem a própria suíte, não pelo load de 1 min. Descreva a medida real, ou volte ao load se o dono preferir (ponto para o dono no parecer).
- A3 (recomendado) scripts/suite-paralela.py:196 · O ramo sem FORGE_SUITE_PROCS de numero_de_processos (linhas 196-199) virou código morto no modo fluido, e os testes das linhas 105-111 testam só esse ramo. Tire o ramo e esses testes, ou use-o como a origem do modo fixo.
- A4 (recomendado) scripts/suite-paralela.py:180 · nucleos() copia hooks/agentes.py:nucleos() sem o FORGE_NPROC, e não há teste que compare as duas (C1). Importe a mesma função ou acrescente o teste.
- A5 (recomendado) scripts/suite-paralela.py:465 · Nenhum teste dirige rodar_fluido com medida simulada (C3, C5): troque rodando < alvo por <= e o brinquedo de 3 módulos segue verde. Acrescente um teste com Medidor e lancar_um falsos que confira a sequência de W.
- A6 (recomendado) scripts/suite-paralela.py:548 · No modo fluido, montar_resumo divide a soma e o desequilíbrio pelos 88 processos-módulo, e a linha de mudança (linha 478) não traz o instante nem os GB (C13). Mostre o W máximo e o mínimo no resumo.
- A7 (recomendado) scripts/suite-paralela.py:247 · Quando um neto termina, os ticks dele entram de novo no cutime do pai, e o worker que acabou sai dos grupos com o último intervalo: a medida oscila. Registre o limite na docstring ou meça por cgroup ou por pids vivos.

## Parecer
Reprovado, pelos achados A1 e A2. Os dois são texto contra código num arquivo de regra e se resolvem numa volta curta. O comportamento central está correto: a fila do mais pesado ao mais leve, um módulo por processo, a completude, os sinais, o piso que garante progresso e o limite em nproc. O módulo de teste está verde. A troca do load de 1 min pela CPU de `/proc/stat` é ponto para o dono (seção acima) e não pede reimplementação. Os achados A3 a A7 são recomendações e não devolvem a entrega. Na revalidação, rodo `forge-check delta --parecer docs/reviews/suite-fluida.md` e leio só o que ele listar.
