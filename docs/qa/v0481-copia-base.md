---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-copia-base
commit: 1571a36f79ed939ceca9979c969ef65136faa926
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-24
---
# QA: v0481 copia-base (#879, classe C)

Escopo: `bin/forge-copia clone` (COPIA-BASE). Diff lido contra Base-sha d49accf8: `bin/forge-copia`, `tests/test_forge_copia.py`, `tests/mutantes/v0481-copia-base.json`, fragmento do changelog.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| `--base develop` vale como `origin/develop` | `test_clone_que_nasce_na_main_aceita_base_sem_origin` (HEAD = develop, não main) | clone na main sem `develop` local | passou |
| Branch já no remoto parte do head remoto, sem upstream | `test_branch_que_ja_existe_no_remoto_parte_do_head_dela` | `--no-track`, sem `--base` | passou |
| Sem ponto de partida: cópia apagada, rc 1 | `test_clone_com_base_que_nao_existe_falha_com_1` | base inexistente | passou |
| Falha ao criar a branch: cópia apagada, rc 1 | `test_switch_que_falha_apaga_a_copia` | branch = `develop` já existente | passou |
| Clone que falha não procura base | `test_clone_que_falha_sai_1_antes_de_procurar_a_base` | origem inexistente | passou |
| Nada que barrava deixa de barrar | recusas anteriores ao clone (classes `Recusa`, `Projeto`) inalteradas, verdes | destino, `..`, opção, disco | passou |

Nenhum caminho deixa a cópia na main nem sobre ref errada: todo retorno 1 após o clone passa pelo `rmtree`; o rc 0 só ocorre com a branch criada sobre `ponto`. Nenhum outro código lê o estado da cópia após rc 1.

## Provas
- Módulo: `python3 -I -m unittest discover -s tests -p test_forge_copia.py` · 81 testes, OK.
- Vermelho: `forge-testes --vermelho d49accf8… --modulos test_forge_copia` → `vermelho: base=d49accf8c5d7 head=1571a36f79ed`; `prova (API ausente)=6; prova (asserção)=4` (os 71 restantes passam na base, são anteriores).
- Mutação: `forge-mutante tests/mutantes/v0481-copia-base.json` · rev=1571a36f79ed, M1 a M7 todos `morreu`. `--cobertura --base d49accf8…` lista as condições mudadas (linhas 127, 133, 137, 307, 310) cobertas por M7/M1/M3/M6/M4; 136 (M2) e 311 (M5) também têm mutante.
- Suíte inteira: no CI do PR (check-run `bateria`), não rerrodada aqui.

Medida do item (voltas e tempo por item): não medida por QA; o ganho esperado é eliminar a volta causada pela cópia deixada na main.
