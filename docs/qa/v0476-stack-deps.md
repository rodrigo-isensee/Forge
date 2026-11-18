---
tipo: qa
contrato: 1
pedido: v0474
branch: melhoria/v0476-stack-deps
commit: 8727471d9fdde8d6e9bf04edb75a3c8a91adf9ba
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-18
---
# QA: v0476-stack-deps (E3.249)

Primeira rodada de QA neste pedido para a branch (sem parecer anterior; escopo completo). Diff `a1674911..95605e66` lido contra a decisão do dono 4 (cópia com dependências no pacote da stack, ADR 0001) e contra os achados A1 e A2 da segurança (head 89f7ef2f), que os commits `7ec76dca` e `95605e66` corrigem.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| `--instalar` é opt-in (clone) | `Instalar.test_sem_a_opcao_nao_instala` | sem a opção: zero comando | passou (M1 morre) |
| `--instalar` vale no worktree | `Instalar.test_worktree_tambem_instala` | segundo modo de criação | passou (M2 morre) |
| roda o comando declarado, dentro da cópia | `Instalar.test_roda_o_comando_declarado_dentro_da_copia` | cwd = cópia | passou |
| sem lockfile: avisa e sai 0 | `Instalar.test_stack_nao_detectada_avisa_e_sai_0` | `detecta` ausente | passou (M3, M4) |
| sem pasta `stacks/` / pacote sem `instalar.json` | `test_sem_pasta_de_stacks_avisa_e_sai_0`, `test_pacote_sem_instalar_json_e_ignorado` | vazio | passou |
| comando falho: sai 1 e diz qual | `test_comando_que_falha_sai_1_e_diz_qual` | rc diferente de zero | passou (M6) |
| comando ausente: sai 1 com mensagem | `test_comando_ausente_sai_1_com_mensagem` | OSError | passou (M5) |
| falha interrompe os seguintes | `test_falha_interrompe_os_comandos_seguintes` | ordem | passou |
| spec inválida: sai 1 | `test_spec_invalida_sai_1` | tipos e formato | passou (M7 a M10) |
| recusa de pasta não afrouxa | `test_nao_afrouxa_a_recusa_de_pasta` | fora da pasta liberada, rc 2 | passou |
| ambiente sem credencial (A2) | `test_instalacao_roda_sem_credencial_no_ambiente`, `test_ambiente_da_instalacao_mantem_o_resto` | GH_TOKEN, GIT_CONFIG_* fora; resto preservado | passou |
| pacotes reais válidos e congelados (A1) | `test_pacotes_reais_declaram_instalar_valido`, `test_todo_instalar_json_usa_modo_congelado_ou_hash_e_detecta_o_lockfile`, `test_instalacao_real_so_com_lockfile` | `detecta` = lockfile; hash/frozen | passou |
| skill e ADR | `tests.test_jarvis_nucleo`, `tests.test_metricas_texto` | frases protegidas, teto de texto | passou |

## Cenários e resultado real
Ambiente: clone `/root/.forge-contrib/wt/v0476-stack-deps-E3249`, head 95605e66, árvore limpa, `TMPDIR` do sandbox.

- `python3 -m unittest tests.test_forge_copia`: 30 testes, OK.
- `python3 -m unittest tests.test_ambiente_git`: 20 testes, OK.
- `python3 -m unittest tests.test_metricas_texto`: 2 testes, OK.
- `python3 -m unittest tests.test_sobreposicao_quadro`: 61 testes, OK.
- `python3 -m unittest tests.test_jarvis_nucleo`: 43 testes, OK.
- `python3 -I tests/catraca.py --base origin/develop`: rc 0.
- Suíte inteira: fica para o check-run `bateria` do CI do PR no mesmo sha (a branch ainda não tem PR); não citada aqui.

### Vermelho antes do verde
`bin/forge-testes --vermelho a1674911c7188c25afe0ab0e05ae1bb18bff728e --modulos tests.test_forge_copia`, rc 0:
`contagem: não prova (passa na base)=17; prova (API ausente)=3; prova (asserção)=10`
Os 13 testes novos de comportamento do `--instalar` provam (10 por asserção, 3 por API ausente: `test_instalacao_real_so_com_lockfile`, `test_pacotes_reais_declaram_instalar_valido`, `test_todo_instalar_json_usa_modo_congelado_ou_hash_e_detecta_o_lockfile`). Os que passam na base são guardas de regressão do que já existia (recusa de pasta) ou do comportamento "sem a opção não instala", que a base cumpre por ausência; este último é morto pelo mutante M1.

### Mutantes (duas specs, pedidos distintos; uma chamada por spec)
`bin/forge-mutante tests/mutantes/v0476-stack-deps.json`, rc 0, `rev=95605e662d55`: M1 a M10 morreram (`bin/forge-copia:115, 109, 85, 72, 79, 82, 66, 69, 61, 59`).
`bin/forge-mutante tests/mutantes/v0476-stack-deps-2.json`, rc 0, `rev=95605e662d55`: M1 a M14 morreram (`bin/forge-copia:78, 50 (x5), 52 (x3)`, `stacks/python/instalar.json:1` (x3), `stacks/node-react/instalar.json:1` (x2)).
Sobreviventes: nenhum. A chamada com as duas specs juntas é recusada pela ferramenta (pedidos de nome diferente), por isso a rodada em duas. Cada uma é uma chamada por pedido; os ids M1..M14 se repetem entre elas sem conflito.
`bin/forge-mutante --cobertura --base a1674911...`, rc 0: toda condição Python mudada em `bin/forge-copia` está `coberta` (linhas 52, 59, 61, 66, 69, 72, 82, 85, 110, 115); `stacks/*/instalar.json` saem `não coberto` por serem JSON, mas têm os mutantes M10 a M14 da spec 2, que morreram.

## Bordas conferidas
Sem lockfile (aviso, rc 0); lockfile presente; comando ausente da máquina; rc não zero no meio da lista; spec inválida (tipo errado, lista vazia); pasta fora da liberada (rc 2 antes de criar); `GH_TOKEN`, `GIT_ASKPASS`, `SSH_AUTH_SOCK` e `GIT_CONFIG_KEY_n` removidos, demais variáveis mantidas. Acessibilidade e E2E: n/a (CLI, sem interface).

## Bugs
Nenhum aberto.

## Observações (sem achado)
- A segurança reprovou o head 89f7ef2f (A1 e A2); os commits `7ec76dca` e `95605e66` os tratam, e os testes novos de lockfile/hash e de ambiente os guardam. A revalidação da segurança é do portão dela.
- Parecer de review e de segurança no diretório `docs/` ainda citam o head 89f7ef2f; a atualização é do portão deles.

## Revalidação (delta 95605e66..ecfc40c3, E3.259)
Escopo incremental: `forge-check parecer delta` lista no domínio `bin/forge-copia`, `changelog.d/v0476-stack-deps.md`, `tests/mutantes/v0476-stack-deps-2.json`, `-3.json` e `tests/test_forge_copia.py`. A mudança é a E3.253: o ambiente da instalação perde `GIT_CONFIG_PARAMETERS` e todo nome com TOKEN, SECRET ou PASSWORD (comparação em maiúsculas). Parecer anterior (aprovado, head 95605e66) segue válido para o resto.

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| ambiente sem config injetada e sem nome de segredo | `Instalar.test_instalacao_tira_config_injetada_e_nomes_de_segredo` | `GIT_CONFIG_PARAMETERS`, `FOO_TOKEN`, `bar_secret_x` (minúscula), `MEU_PASSWORD`, `TOKEN` exato; `MINHA_VAR` mantida | passou (M1 a M5 morrem) |
| pacotes reais só com lockfile | `test_todo_instalar_json_usa_modo_congelado_ou_hash_e_detecta_o_lockfile` | `"lock" in f` para todo `detecta` | passou |

O teste `test_instalacao_real_so_com_lockfile` foi removido no delta; é redundante com o de cima (`detecta` só com lockfile exclui `package.json` e `pyproject.toml`), sem perda de obrigação.

Execução (ambiente: clone do head ecfc40c3, `TMPDIR` do sandbox):
- `python3 -I tests/catraca.py --base origin/develop`: rc 0.
- `python3 -m unittest tests.test_forge_copia`: 30 testes, OK.
- `python3 -m unittest tests.test_ambiente_git`: 20 testes, OK.
- `tests.test_metricas_texto`: não rodado; o delta não toca .md medido (só o fragmento de changelog).
- Vermelho: `bin/forge-testes --vermelho 95605e662d55742e4af9b64e640878ea0bfa085b --modulos tests.test_forge_copia`: `vermelho: base=95605e662d55 head=ecfc40c35501`; `tests.test_forge_copia.Instalar.test_instalacao_tira_config_injetada_e_nomes_de_segredo · H=ok · B=falha · prova (asserção)`; `contagem: não prova (passa na base)=29; prova (asserção)=1`.
- Mutantes: `bin/forge-mutante tests/mutantes/v0476-stack-deps-3.json`, rc 0, `rev=ecfc40c35501`: M1 a M5 morreram (`bin/forge-copia:50, 51 (x3), 54`).
- `bin/forge-mutante tests/mutantes/v0476-stack-deps-2.json` (com e sem `--base 95605e66...`; saída igual, `base=95605e662d55742e4af9b64e640878ea0bfa085b`), rc 1, `rev=ecfc40c35501`: M2 `sobreviveu` (`bin/forge-copia:50`), M3 `sobreviveu` (`bin/forge-copia:50`); os demais (M1, M4 a M14) morreram. Causa: o padrão de nome TOKEN, novo no delta, torna redundante GH_TOKEN e GH_ENTERPRISE_TOKEN na lista fixa; mutante equivalente não declarado como tal. Ver A1.
- `bin/forge-mutante --cobertura --base 95605e66...`: linha 53 `coberta` (spec 2 M7 a M9, spec 3 M5); sem condição nova sem mutante.
- Suíte inteira: check-run `bateria` do CI do PR (a branch não tem PR); não citada.

Bugs: nenhum. Acessibilidade e E2E: n/a (CLI).

## Revalidação (delta ecfc40c3..f1091255, E3.270)
`forge-check parecer delta` lista no domínio `bin/forge-copia`, `stacks/node-react/pronto.md` e `tests/mutantes/v0476-stack-deps-2.json`. O A1 está corrigido: a lista fixa de `env_sem_credencial` perdeu `GH_TOKEN`, `GITHUB_TOKEN`, `GH_ENTERPRISE_TOKEN` e `GITHUB_ENTERPRISE_TOKEN` (já cobertos pelo padrão TOKEN, sem mudança de comportamento) e os mutantes equivalentes M2 e M3 saíram da spec 2. A frase nova em `pronto.md` documenta que `NPM_TOKEN` e afins não chegam à instalação.

Execução (clone do head f1091255, árvore limpa, `TMPDIR` do sandbox):
- `python3 -I tests/catraca.py --base origin/develop`: rc 0.
- `tests.test_forge_copia`: 30 testes, OK. `tests.test_ambiente_git`: 20, OK. `tests.test_metricas_texto`: 2, OK (o delta toca `pronto.md`).
- `bin/forge-mutante tests/mutantes/v0476-stack-deps.json`: `rev=f10912559b05`, M1 a M10 morreram.
- `bin/forge-mutante tests/mutantes/v0476-stack-deps-2.json`: `rev=f10912559b05`, M1 e M4 a M14 morreram; sem sobreviventes.
- `bin/forge-mutante tests/mutantes/v0476-stack-deps-3.json`: `rev=f10912559b05`, M1 a M5 morreram.
- `bin/forge-mutante --base ecfc40c355010520c48d15ded98990fe3b66464b tests/mutantes/v0476-stack-deps-2.json`: `base=ecfc40c355010520c48d15ded98990fe3b66464b`, rc 0.
- Vermelho: sem teste novo no delta (só remoção de entradas da lista fixa, comportamento igual); n/a.
- Suíte inteira: check-run `bateria` do CI do PR (a branch não tem PR); não citada.

Bugs: nenhum. Acessibilidade e E2E: n/a (CLI).

## Revalidação (delta f1091255..8727471d, E3.307)
`forge-check parecer delta` lista no domínio `bin/forge-copia`, `tests/test_forge.py` e `tests/test_forge_copia.py` (sem o que veio da develop). Mudanças: `PacotesDeStack` passa a aceitar `instalar.json` (valida o JSON e o inclui nos arquivos permitidos; corrige o vermelho do CI do PR 660); junção com a develop traz o MP6 (recusa por disco em `bin/forge-copia`, via `forge_disco.py`); o pacote falso dos testes copia `forge_disco.py`. Critérios anteriores seguem válidos; o novo (recusa por disco acima do limiar ou ilegível, antes de criar) é guardado pelos mutantes `v0474-mp6-disco*` (M1 a M3, `bin/forge-copia:117-118`).

Execução (clone do head 8727471d, `TMPDIR` único, sandbox):
- `python3 -I tests/catraca.py --base origin/develop`: rc 0.
- `tests.test_forge_copia`: 36 testes, OK. `tests.test_forge.PacotesDeStack`: 4, OK. `tests.test_forge_fechar`: 17, OK. `tests.test_ambiente_git`: 20, OK. `tests.test_metricas_texto`: 2, OK.
- `forge-mutante tests/mutantes/v0476-stack-deps.json`: `rev=8727471d9fdd`, M1 a M10 morreram. `-2.json`: M1, M4 a M14 morreram. `-3.json`: M1 a M5 morreram.
- `v0474-mp6-disco.json`: M1 a M8 morreram (M4 e M5 por erro do teste declarado sob o mutante, que passa sem ele; morte válida pela ferramenta). `-2.json`: M9, M10, M12 a M16 morreram. `-3.json`: M17 a M19 morreram. Todas rc 0, sem sobreviventes.
- Vermelho: o delta não traz teste novo de regra; a mudança em `test_forge.py` conserta teste que o CI marcava vermelho por `instalar.json` fora da forma do pacote. n/a.
- Suíte inteira: check-run `bateria` do CI do PR 660 no mesmo sha; não citada daqui.

Bugs: nenhum. Acessibilidade e E2E: n/a (CLI). Achados abertos: nenhum.

## Achados
