---
tipo: qa
contrato: 1
pedido: v0474
branch: melhoria/v0476-stack-deps
commit: 95605e662d55742e4af9b64e640878ea0bfa085b
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-18
---
# QA: v0476-stack-deps (E3.249)

Primeira rodada de QA neste pedido para a branch (sem parecer anterior; escopo completo). Diff `a1674911..95605e66` lido contra a decisão do dono 4 (cópia com dependências no pacote da stack, ADR 0001) e contra os achados A1 e A2 da segurança (head 89f7ef2f), que os commits `7ec76dca` e `95605e66` corrigem.

## Achados

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
