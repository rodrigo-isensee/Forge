---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-prova-tmpdir
commit: 3fc4724df0bfd01b97e7502826318fe091ed5af9
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-16
---
# QA: v047 prova com TMPDIR (E2.316, parecer E2.357)

Instância que não fez a entrega. Diff `1b88640e..a1eb19ef`: `tmpdir_da_prova` e o repasse em `rodar_prova` (`bin/forge-check`), 8 testes `TmpdirDaProva`, spec de 8 mutantes, fragmento de changelog. Obrigação: a prova `cmd` recebe o TMPDIR do ambiente só se for pasta absoluta, do próprio usuário, gravável e fora do repositório (E2.316, R-QA).

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E2.316 repasse | test_prova_recebe_o_tmpdir_gravavel | TMPDIR válido chega à prova | passou |
| E2.316 sem TMPDIR | test_sem_tmpdir_a_prova_roda_sem_ele | variável ausente, nenhuma nova | passou |
| E2.316 caminho | test_relativo_nao_vale | relativo | passou |
| E2.316 tipo | test_inexistente_ou_arquivo_nao_vale | inexistente, arquivo executável | passou |
| E2.316 dono | test_pasta_de_outro_usuario_nao_vale | uid diferente | passou |
| E2.316 escrita | test_pasta_sem_escrita_nao_vale | sem W/X | passou |
| E2.316 repositório | test_dentro_da_worktree_nao_vale, test_dentro_do_clone_da_worktree_nao_vale | dentro da worktree e do clone comum | passou |

## Cenários e resultado real
- `python3 -m unittest tests.test_forge_run` no head: 19 testes, OK.
- Vermelho antes do verde, `forge-testes --vermelho 1b88640e873485ee1d16bdd05307d058ec1d0ec8 --modulos test_forge_run`: `vermelho: base=1b88640e8734 head=a1eb19effa88`, revertidos à base `bin/forge-check, changelog.d/v047-prova-tmpdir.md`; contagem `não prova (passa na base)=12; prova (API ausente)=6; prova (asserção)=1`, rc=0. O único novo que passa na base é o "sem TMPDIR", que guarda a ausência de variável nova (obrigação negativa); os 12 são testes herdados.
- Mutação (`bin/forge-mutante tests/mutantes/v047-prova-tmpdir.json --processos 4`, rc=0): PT-M1 a PT-M8 `morreu` (forge-check:9009, 9013, 9016, 9018, 9020, 9023, 9024, 9034).
- Cobertura (`forge-mutante --cobertura --base 1b88640e...`, rc=0): toda condição mudada tem mutante declarado; nenhuma `não coberto` nem `isenta`. Lista conferida contra o diff: sem linha de guarda sem mutante.
- Suíte inteira: no CI do PR (check-run `bateria`), não rodada aqui.
- Remoto avançou (pareceres de review e segurança no mesmo head): trazido por merge, sem rebase.

## Revalidação por delta (E2.498, head 8614a2df)
- `forge-check parecer delta`: intervalo `a1eb19ef..8614a2df`, domínio código e testes. O que aparece em `bin/forge-check` (`juncao_limpa`, `--tempo` de voltas, `--media-por-agente`) veio da develop 86ac0fcb pelo merge 3fc4724d, não da entrega: `git diff 86ac0fcb 8614a2df` traz só `tmpdir_da_prova`, os testes, a spec de mutantes e os pareceres. Nenhuma linha do item mudou; os critérios E2.316 seguem valendo.
- `python3 -m unittest tests.test_forge_run` no head: 19 testes, OK.
- `bin/forge-mutante tests/mutantes/v047-prova-tmpdir.json --processos 4` em `rev=8614a2df01ec`, rc=0: PT-M1 a PT-M8 `morreu` (forge-check:9034, 9038, 9041, 9043, 9045, 9048, 9049, 9059; as linhas andaram com o merge).
- Suíte inteira: check-run `bateria` do CI do PR, não rodada aqui.
