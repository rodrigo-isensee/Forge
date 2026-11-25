---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-d6-resto
commit: 50a40e28844435d4bf43c8b23d3880e1b37af7b9
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-25
---
# QA: v0481 E11.20 (PR #877, hook salvar, volta E11.18 pela decisão do dono, opção b; classe C)

Delta lido: `git diff 1afd54b5..50a40e28` na parte do #877 (`hooks/salvar.py`, `tests/test_hooks.py`, specs de mutantes, ADR 0003, R-LIMITES; o resto do diff é o merge da develop, fora do domínio). O hook só grava o commit WIP na cópia local: sem `push`, sem `fetch`, sem `ls-remote`, sem script de varredura. **Aprovado.** Os bloqueantes do parecer anterior (A3: segredo em commit anterior levado pelo push e base da varredura lida de ref local; A4: M8 e M9 vivos pelo fixture não rastreado) eram do envio ou do fixture e saíram: o envio e a varredura foram removidos do `hooks/salvar.py`, e o `setUp` rastreia `docs/a.md2`.

## Achados
- A5 (recomendado) hooks/salvar.py:127 · A `catraca` do CI do head está vermelha por R-QA: "guarda de hooks/salvar.py mudada sem mutante declarado: só equivalente · hooks/salvar.py:127 · tests/mutantes/v0481-d6-resto-4.json:M29; sem mutante · hooks/salvar.py:156 · `__name__ == '__main__'`". A linha 127 só tem o M29 (equivalente declarado, que não prova) e a 156 não tem mutante. Não é do delta (as duas linhas já estavam assim em 1afd54b5; a catraca de hoje lê a regra mais estrita): o autor declara um mutante não equivalente para a 127 e outro (ou a `isenta` com motivo) para a 156, ou o dono libera pelo rótulo `afrouxa-regra`. Ordem do dono de 25/11: problema antigo vira cartão e não segura o item; o merge, porém, só sai com a `catraca` verde ou o rótulo, e isso é do `tech-lead`.

## Revalidação do que o delta mudou
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

## Execução (clone `/root/.forge-contrib/wt/v0481-d6-resto-qa`, HEAD = `50a40e288`)
- `python3 -m unittest tests.test_hooks.SalvarAoParar tests.test_hooks.Hooks.test_hooks_json tests.test_hooks.Hooks.test_cada_hook_tem_caso_que_passa_e_que_bloqueia`: 31 testes, OK. O `tests.test_hooks` inteiro fica para o CI.
- Vermelho, à mão (cópia em pasta descartável, testes do head com o `hooks/salvar.py` do 1afd54b5, que ainda envia): `python3 -m unittest tests.test_hooks.SalvarAoParar`: `Ran 29 tests`, `FAILED (failures=4)`; os testes do E11.18 caem sem a correção.
- Mutantes: `bin/forge-mutante --processos 4` das 6 specs `tests/mutantes/v0481-d6-resto*.json`, `rev=50a40e288444`: 35 `morreu` (incluindo M8, M9, M10, M11 e M39), nenhum `sobreviveu`, nenhum sem veredito; M29 `equivalente` (aceito, mas ver A5). Rodei as 6 specs inteiras, sem `--base`.
- CI do head: check-runs do `commit:` (50a40e28): `suíte (python 3.12, partes 1 a 5)`, `suíte (python 3.14, partes 1 a 5)`, `teto de pulados` (3.12 e 3.14), `bateria (passos)`, `bateria (verificações longas)`, `bateria (python 3.14)`, `instalação (python 3.14)` e `árvore já provada na develop` verdes. Vermelhos: `bateria (pareceres)` (espera o parecer), `bateria` (log: `passos: success; pareceres: failure; verificações: success; partes: success; pulados: success`, ou seja, falha só pelos pareceres) e `catraca` (causa: A5, lida no log do run 45690633015, com `XDG_CACHE_HOME` num diretório gravável para o `gh`).
- ci: 50a40e28844435d4bf43c8b23d3880e1b37af7b9 verde

## Melhoria vista
Classe AR-1 (lista de mutantes incompleta) voltou: `hooks/salvar.py:156` sem mutante e `:127` só com equivalente, apontadas pela `catraca` (run 45690633015). O autor deveria rodar `bin/forge-mutante --cobertura --base <Base-sha>` antes do push; a linha do AR-1 sobe para 10 vezes, última `hooks/salvar.py:156`, no PR do tech-lead (o brief manda este commit só com o parecer).
