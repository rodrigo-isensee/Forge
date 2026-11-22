---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-ambiente-recriacao
commit: 1fa9db9660757bbfa03baa2ff273acd8a411d181
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-22
---
# QA: v0478 E119.1 (AMBIENTE-SOBREVIVE-RECRIACAO, Claude Code atual no preparo do container)

Revisão completa e única no head 09457540 (base 38c37de9e). Só os testes afetados, as sondas e os mutantes da spec; sem suíte local (a bateria é o check-run do PR). Sem rede: curl falso. `shellcheck` ausente nesta máquina (não rodado; fica com o CI).

## Critério → teste → resultado
| Critério (E119.1) | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Sem binário em ~/.local/bin, instala pelo instalador oficial (nos 2 scripts) | ClaudeNoPreparo.test_sem_claude_local_instala... | claude antigo do PATH não conta | passou |
| Idempotente: 2ª rodada não baixa nem duplica o PATH no .bashrc | mesmo teste | 2ª rodada | passou |
| Sem rede: vira `falta:`, sem binário, sem barrar | test_instalacao_que_falha_vira_falta... | curl com saída 22 | passou |
| Baixa para arquivo, nunca por pipe | test_o_instalador_e_baixado... | n/a | passou |
| --verificar diz o comando e não altera nada | test_verificar_diz_o_que_falta... | home vazio, sem .local nem .bashrc | passou |
| Com binário presente, nada é baixado | test_com_claude_local_nada_e_baixado | n/a | passou |
| --simular não altera nada | test_forge.test_container_simular_nao_altera_nada | simulação (sonda manual: sem .bashrc) | passou; guarda coberta por M16 e test_simular_nao_grava_o_bashrc... |
| postStart do container aciona o preparo, sem segredo | ConfiguracaoDoContainer (2 testes) | falha do preparo não impede subir | passou |
| Hook de ambiente continua ok com o novo requisito | test_ambiente_hook (9) | n/a | passou |

## Provas
- test_ambiente_recriacao.py: 7 testes, OK. test_ambiente_hook.py: 9 testes, OK. test_forge.py -k PrepararEstacao: 27 testes, OK.
- `bin/forge-mutante tests/mutantes/v0480-ambiente-recriacao.json`: M1..M9 todos `morreu` (saída 0), rev=09457540dde8.
- Mutante meu (remover o guarda de simular, linha 193): sobreviveu, base do A1.
- `forge-mutante --cobertura --base ...`: shell sai `não coberto` por desenho da ferramenta; não é pedido de controle (sem bin/, hooks/).
- Sonda `--container --simular` em home vazio: `[simular] baixar https://claude.ai/install.sh...`, sem .bashrc. `--verificar`: `falta: Claude Code atual ausente em .../.local/bin/claude ...: rode bash .../preparar-estacao.sh --container`.
- Vermelho antes do verde: `forge-testes --vermelho` não rodado (fila R-TETO ocupada); os mutantes M1..M9 mortos mostram que os testes caem sem o código novo.

## Revalidação no head 93a2123c (volta única, escopo incremental)
Delta (`forge-check parecer delta`): 09457540..93a2123c, só os dois scripts, o teste, a spec de mutantes e o changelog. A1 e A2 fechados.
- A1: `test_simular_nao_grava_o_bashrc_e_nao_roda_o_instalador` + M16 (guarda de simular em garantir_path_local): morreu.
- A2: `test_sem_curl_vira_falta_em_dois_passos_sem_baixar_nem_instalar` (PATH sem curl, nos dois scripts): afirma a linha "sem curl aqui", nenhuma chamada e nenhum binário. M8 (preparar-ambiente.sh:107) morreu.
- Endurecimentos do delta (https com limite, falta em dois passos, export real no .bashrc) cobertos por M10..M15, todos `morreu`.
- test_ambiente_recriacao.py (discover): 10 testes, OK.
- `bin/forge-mutante tests/mutantes/v0480-ambiente-recriacao.json --base 09457540dde8f8b4d47c47d32cc6d57e9b883b10`: `base=09457540... rev=93a2123c...`, M1..M16 todos `morreu`, saída 0.
- Sem bugs novos. Suíte inteira: check-run `bateria` do PR no mesmo sha (não rerrodada aqui).

## Revalidação no head a0be36e6 (volta de CI do #792, escopo incremental)
Delta (`forge-check parecer delta`): 93a2123c..a0be36e6, sem o que veio da develop. No domínio: `bin/forge-testes` (regras do MAPA para `test_ambiente_recriacao`), os dois scripts (`command grep` e `$HOME` na mensagem de PATH, sem mudar guarda), `tests/test_ambiente_recriacao.py` (git init sem manutenção, `iterdir` e `is_symlink` no PATH sem curl), `tests/test_forge.py` (briefs G1.1), `tests/test_testes_tocados.py` e `tests/pesos-d4.json`. Nenhuma linha de guarda mudou nos scripts; os mutantes M1..M16 seguem válidos. Mudanças só de teste e de mapa: sem teste novo de regra, sem vermelho novo.
- Spec do item (E119.1): os 10 testes de `test_ambiente_recriacao` cobrem os critérios da tabela acima, todos passando; o teste de PATH sem curl não ficou frágil com link quebrado.
- `test_ambiente_recriacao.py`: 10 testes, OK. `test_ambiente_git.py`: 20, OK. `test_salvar_desfazer.py`: 38, OK. `test_testes_tocados.py`: 196, OK (skipped=1, `skipIf` que já existia na base, fora do delta).
- Sem bugs novos. Suíte inteira: check-run `bateria` do PR no mesmo sha (não rerrodada aqui).

## Revalidação no head 1fa9db96 (3ª volta, escopo incremental)
Delta (`forge-check parecer delta`): a0be36e6..1fa9db96, sem o que veio da develop. No domínio: `tests/mutantes/v0480-ambiente-recriacao.json` (M16 alinhado à linha `command grep -qE`; só o `de`/`para` da spec, nenhum script mudou) e `tests/pesos-d4.json` (peso de `test_forge_contador`). Nenhuma guarda mudou.
- `bin/forge-mutante --conferir --base a0be36e6...`: `base=a0be36e6... mb=a0be36e6... rev=1fa9db96...`, `conferidas: o trecho de cada spec do diff está no lugar`.
- M16 (`--ids M16`): `M16 · morreu · scripts/preparar-estacao.sh:194`.
- `--base a0be36e6`: M1..M16 todos `morreu`.
- Sem bugs novos. Suíte inteira: check-run `bateria` do PR no mesmo sha (não rerrodada aqui).
