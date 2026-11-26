---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-d6-resto
commit: 1f127ddd1ac05ae80a9306dda56802dec43ee50d
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-25
---
# QA: v0481 E11.20 (PR #877, hook salvar, volta E11.18 pela decisão do dono, opção b; classe C)

Delta lido (volta E11.24): `git diff 50a40e28..200d8b37`; no domínio do QA só entrou `tests/mutantes/v0481-d6-resto-7.json` (M40 e M41); o resto é a develop trazida (a50975e8, com o #885), já revisada no PR de origem. Antes, `git diff 1afd54b5..50a40e28` na parte do #877 (`hooks/salvar.py`, `tests/test_hooks.py`, specs de mutantes, ADR 0003, R-LIMITES; o resto do diff é o merge da develop, fora do domínio). O hook só grava o commit WIP na cópia local: sem `push`, sem `fetch`, sem `ls-remote`, sem script de varredura. **Aprovado.** Os bloqueantes do parecer anterior (A3: segredo em commit anterior levado pelo push e base da varredura lida de ref local; A4: M8 e M9 vivos pelo fixture não rastreado) eram do envio ou do fixture e saíram: o envio e a varredura foram removidos do `hooks/salvar.py`, e o `setUp` rastreia `docs/a.md2`.

## Revalidação do que o delta mudou
- A5 do parecer anterior (catraca, linhas 127 e 156 sem mutante): resolvido. M40 (`hooks/salvar.py:127`, `if e` para `if not e`) e M41 (`:156`, `__main__` para `if False:`) estão declarados e morrem; a `catraca` do head está verde.
- `bin/forge-mutante tests/mutantes/v0481-d6-resto-7.json`, `rev=200d8b378582`: `M40 · morreu · hooks/salvar.py:127`, `M41 · morreu · hooks/salvar.py:156`; nenhum sobrevivente.
- `python3 -m unittest tests.test_hooks.SalvarAoParar`: 29 testes, OK.
- Afrouxa do #877 (salvar só local, sem checagem de cada gravação): aprovado pelo dono em 25/11 17:37; sem ressalva.
- Sem rede: `hooks/salvar.py` não chama `push`, `fetch` nem `ls-remote`; `test_branch_ja_no_remoto_fica_como_esta` prova que o remoto e o `origin/melhoria/x` da cópia ficam como estavam; `test_salva_so_o_escopo_na_copia` prova `no_remoto()` vazio.
- Escopo exato x prefixo (antigo M8 e M9): `docs/a.md2` agora é rastreado no `setUp`, o `status --untracked-files=no` o vê e os dois mutantes morrem.
- ADR 0003: o item 2 segue sem exceção; a exceção do R-VERIFY está só na emenda (regra 4); `docs/regras/R-LIMITES.md` volta ao texto sem exceção (núcleo do Jarvis sem folga). Coerente com a decisão do dono de 25/11 (07:37).
- Testes com remotos bare sem manutenção automática (`remoto_sem_manutencao`, de `ambiente_git`): usado nos remotos bare do `SalvarAoParar`.
- Config da cópia, não rastreado, prazo de 50 s: sem mudança no delta, testes verdes.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Decisão do dono (opção b): só commit local, sem rede | `test_branch_ja_no_remoto_fica_como_esta`, `test_salva_so_o_escopo_na_copia` | remoto intacto com a branch já enviada | passou |
| ADR 0003 regra 2: só o escopo, exato x prefixo | `test_salva_so_o_escopo_na_copia` | `docs/a.md2` fora, `docs/b.md` não rastreado fora | passou; M8 e M9 morrem |
| Regra 2: nada no escopo, nenhum commit | `test_nada_no_escopo_nao_faz_commit` | escopo vazio | passou |
| Regra 1: brief único, cópia e branch certas | `test_sem_brief_citado_nao_age`, `test_dois_briefs_de_escrita_nao_grava`, `test_branch_de_integracao_nunca`, `test_copia_em_outra_branch_nao_grava`, `test_brief_de_parecer_nao_grava`, `test_duas_copias_citadas_nao_grava`, `test_copia_fora_da_pasta_das_copias_nao_grava` | ambiguidade, integração | passou |
| Regra 4: git sem código do agente | `test_hooks_do_git_da_copia_nao_rodam`, `test_git_herdado_nao_desvia_a_copia`, `test_config_local_fora_da_lista_nao_age`, `test_config_so_com_gpgsign_nao_age`, `test_origin_diferente_da_principal_nao_age`, `test_config_global_de_fora_nao_roda` | chave fora da lista, origin trocada | passou |
| Regra 3: prazo de 50 s | `test_prazo_total_dividido_entre_os_comandos` | prazo esgotado | passou |
| Regra 5: operação em andamento | `test_mesclagem_em_andamento_nao_grava`, `test_conflito_no_indice_nao_grava` | MERGE_HEAD, conflito | passou |
| Regra 6: nunca bloqueia, erro vai ao erros.log | `test_status_que_falha_vai_ao_erros_log`, `test_add_que_falha_nao_faz_commit`, `test_hooks_json`, `test_cada_hook_tem_caso_que_passa_e_que_bloqueia` | falha de git | passou |

## Execução (clone `/root/.forge-contrib/wt/v0481-d6-resto-qa`, HEAD = `200d8b378`; a parte do 50a40e28 segue válida, o delta não toca o hook)
- `python3 -m unittest tests.test_hooks.SalvarAoParar tests.test_hooks.Hooks.test_hooks_json tests.test_hooks.Hooks.test_cada_hook_tem_caso_que_passa_e_que_bloqueia`: 31 testes, OK. O `tests.test_hooks` inteiro fica para o CI.
- Vermelho, à mão (cópia em pasta descartável, testes do head com o `hooks/salvar.py` do 1afd54b5, que ainda envia): `python3 -m unittest tests.test_hooks.SalvarAoParar`: `Ran 29 tests`, `FAILED (failures=4)`; os testes do E11.18 caem sem a correção.
- Mutantes: `bin/forge-mutante --processos 4` das 6 specs `tests/mutantes/v0481-d6-resto*.json`, `rev=50a40e288444`: 35 `morreu` (incluindo M8, M9, M10, M11 e M39), nenhum `sobreviveu`, nenhum sem veredito; M29 `equivalente` (aceito, mas ver A5). Rodei as 6 specs inteiras, sem `--base`.
- CI do head (`gh pr checks 877`, headRefOid 200d8b37): verdes `suíte (python 3.12 e 3.14, partes 1 a 5)`, `teto de pulados`, `bateria (passos)`, `bateria (verificações longas)`, `bateria (python 3.14)`, `instalação (python 3.14)`, `árvore já provada na develop` e `catraca`. Fora, só `bateria (pareceres)` e `bateria`, que esperam este parecer.

## Volta E11.28 (delta `e66e30a2..1f127ddd`, só a resolução do conflito com a develop e o #895)
- Lógica do item: `git diff e66e30a2..1f127ddd -- hooks/salvar.py tests/mutantes/v0481-d6-resto*.json docs/adr docs/regras` vazio; o hook, as specs e as regras do #877 não mudaram.
- `tests/test_hooks.py`: o delta só acrescenta (`import stat`, `ModoPorGrupo`, `Travou` e o teste de FIFO da develop); nenhuma linha removida. `SalvarAoParar` segue inteira e as quatro classes (`SalvarAoParar`, `ModoPorGrupo`, `Travou`, `RecusaComFifoNoRegistro`) estão no arquivo; nenhum teste perdido.
- `docs/hooks-fixtures.md`: `python3 scripts/indice-fixtures.py --conferir` sai `em dia`.
- `python3 -m unittest tests.test_hooks.SalvarAoParar tests.test_hooks.ModoPorGrupo tests.test_hooks.RecusaComFifoNoRegistro`: 40 testes, OK.
- `bin/forge-mutante tests/mutantes/v0481-d6-resto-7.json`, `rev=1f127ddd1ac0`: `M40 · morreu · hooks/salvar.py:127`, `M41 · morreu · hooks/salvar.py:156`.
- CI (run 45737895249, headSha 1f127ddd, `gh pr checks 877`): verdes as suítes 3.12 e 3.14 (partes 1 a 5), `teto de pulados`, `bateria (passos)`, `bateria (verificações longas)`, `bateria (python 3.14)`, `instalação (python 3.14)`, `árvore já provada na develop` e `catraca`; só `bateria (pareceres)` e `bateria` aguardam os pareceres.
- ci: 1f127ddd1ac05ae80a9306dda56802dec43ee50d verde
- Afrouxa do #877 aprovado pelo dono em 25/11 17:37. **Aprovado** no head 1f127ddd.

## Melhoria vista
Classe AR-1 (lista de mutantes incompleta) voltou no E11.20 e foi corrigida pelo M40 e M41; o autor deveria rodar `bin/forge-mutante --cobertura --base <Base-sha>` antes do push.
