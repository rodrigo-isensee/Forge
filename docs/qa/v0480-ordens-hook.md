---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-ordens-hook
commit: 8e84ef3b57fa6fe7cee56e7b640dfecaba1a8271
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-23
---
# QA: hook ordens e laço das fixtures do vigia (v0478 E123.5)

## Critério → teste → resultado
| Critério (E123.1) | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Reinjeta as ordens no UserPromptSubmit e no SessionStart (startup, resume, compact), com linha fixa | `injeta-no-userpromptsubmit`, `sessionstart-compact-injeta`, `test_hooks_json_registra_o_ordens_nos_matchers_da_emenda` | controle (tab, ESC) vira espaço | passou |
| Teto de 15 linhas e 2000 caracteres, com aviso do corte | `teto-linhas-corta-e-avisa`, `teto-caracteres-corta-e-avisa` | limite e logo acima | passou |
| Arquivo ausente ou vazio: silêncio | `arquivo-ausente-silencio`, `vazio-silencio` | ausente, 0 byte | passou |
| Link para fora da raiz: silêncio | `link-para-fora-silencio` | symlink externo | passou |
| Erro interno: sai 0, linha no erros.log | `erro-interno` | exceção em `ler_ordens` | passou |
| Fora de projeto do Forge: silêncio; sessão do Forge lê o contrib | `sem-forge-versao`, `sessao-do-forge-le-o-contrib` | sem `.forge/versao` | passou |
| Só o Jarvis grava o arquivo | `test_so_o_jarvis_escreve_o_arquivo_de_ordens` | permissão | passou |
| Laço das fixtures do vigia aceita decision/reason só no Stop do item 7 | 4 fixtures `time-parado-*` | subagente, `stop_hook_active`, id fora do formato | passou |

## Sondas manuais (hook real, projeto temporário com `.forge/versao`)
- Ausente, vazio (0 byte), 70000 bytes (acima de 64 KiB), link para fora, diretório no lugar do arquivo: silêncio, rc=0.
- 40 linhas: 15 linhas e `ordens cortadas no teto: 40 linhas, 149 caracteres`, rc=0.
- FIFO no lugar do arquivo: não trava (O_NONBLOCK, rejeitado como não regular), rc=0.
- Bytes UTF-8 inválidos: viram U+FFFD, sem erro.
- Erro interno: fixture `erro-interno` (erros.log com `ordens RuntimeError`).

## Execução
- `python3 -I -m unittest discover -s tests -p test_hooks.py -k fixtures_fatia -k ordens -k conformidade_tem`: 19 testes, OK (todas as fixtures de `tests/hooks/ordens` e `tests/hooks/vigia`).
- `tests/test_vigia_parado.py`: 22 testes, OK.
- `bin/forge-mutante tests/mutantes/v0480-ordens-hook.json tests/mutantes/v0480-ordens-hook-2.json`: M1 a M14 `morreu`, nenhum sobrevivente (M2, M5, M12, M13 por erro do teste sob o mutante com o controle verde).
- `bin/forge-mutante --cobertura --base 48d6f4b86`: toda condição mudada de `hooks/ordens.py` coberta por mutante declarado.
- Suíte inteira: no CI do PR, fora deste parecer (sem suíte local, como pede o brief).

## Revalidação do delta (E123.9, head cf679683, base do delta c63e9615)
Delta no domínio (`forge-check parecer delta`): modelo de projeto sem o arquivo de ordens; `hooks/conformidade.py` com o arquivo nas listas `CAMINHOS_DO_CONTROLE` e `CONTROLE_NO_TEXTO`; `hooks/ordens.py` lendo da cópia principal (`fontes`, `diretorio_comum`) e `sem_controle`; 8 fixtures `tests/hooks/conformidade/ordens-*`; `tests/test_hooks.py`; mutantes M15 a M20.

| Mudança do delta | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Escrita do arquivo recusada ao dev e ao security, liberada ao Jarvis (Write, `>>`, ln, mv, rm, variável) | 8 fixtures `ordens-*` da conformidade | permissão por papel; pasta mãe em variável | passou |
| Lê da cópia principal, nunca da worktree | `test_na_worktree_le_so_a_copia_principal` | worktree com arquivo próprio | passou |
| `.git` nu ou que não se resolve cala | `test_worktree_de_repositorio_nu_cala` | repositório nu | passou |
| Pasta `kanban` por link sai da base | `test_no_forge_a_pasta_kanban_por_link_sai_da_base` | link para fora | passou |
| Sequência de controles vira um espaço | `test_sequencia_de_controles_vira_um_espaco_so` | sequência de controle | passou |

## Provas
- `env -i PATH HOME TMPDIR python3 -I -m unittest discover -s tests -p test_hooks.py -k OrdensEmVigor -k test_cada_hook -k ordens`: 22 testes, OK.
- As 8 fixtures `ordens-*` pelo lote do `Hooks.executar_em_lote`: 8 verificadas, OK.
- `bin/forge-mutante --base c63e96158e67cb61056a5552a12ed7a3f7354925` sobre as 3 specs (`base=c63e96158e67cb61056a5552a12ed7a3f7354925 ... rev=cf6796830336`): M1 a M20 `morreu`, nenhum sobrevivente (M15 a M20 em `v0480-ordens-hook-3.json`).
- `bin/forge-mutante --cobertura --base c63e96158e67`: condições mudadas de `hooks/ordens.py` (linhas 40 e 65) cobertas por M17 e M20; as de `hooks/meta.py` pertencem à base e as não cobertas (`.sh`, `pesos-d4.json`) não são do delta.
- Observação: uma rodada com `-k fixtures_fatia` deu 1 falha em 4 testes (497 s, sob carga, em paralelo aos mutantes) e a repetição sozinha deu OK (subtestes de pid pulados pelo ns de pid do sandbox, 550 s). Não reproduzida; a suíte inteira roda no CI do PR (check-run `bateria` do mesmo sha).

## Revalidação do delta (E123.13, head 8e84ef3b, base do delta e34c7466, 2ª volta)
Delta no domínio: pasta própria `docs/ordens/` do Forge (`hooks/ordens.py`), a pasta como pasta em `CAMINHOS_DO_CONTROLE` e `CONTROLE_NO_TEXTO` (A1), guarda pela cópia principal `relativos_a_copia_principal` (A2), `.forge/ordens-em-vigor.md` nos ignorados do `bin/forge-init` (A3), fixtures `ordens-s1` a `s5`, specs de mutantes 3 e 4, `tests/test_hooks.py`, `tests/test_forge.py`.

| Mudança do delta | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Pasta das ordens recusada ao dev (cp, curinga, mover ou remover pasta forjada) | `test_conformidade_recusa_a_pasta_das_ordens_e_a_copia_principal`, fixtures `ordens-s1` a `s3` | permissão por papel; pasta inteira | passou |
| Escrita pela cópia principal a partir da worktree (absoluto, `../`, `>>`) recusada ao dev, liberada ao Jarvis | `test_conformidade_ve_o_arquivo_pela_copia_principal`, fixtures `ordens-s4-*` | worktree para cópia principal | passou |
| Pasta das ordens trocada por link sai da base | `test_no_forge_a_pasta_das_ordens_por_link_sai_da_base` | link para fora | passou |
| Worktree forjada injeta só o dono | fixture `s5-worktree-forjada-injeta-so-o-dono` | worktree com arquivo próprio | passou |
| Arquivo de ordens fora do git | `test_o_arquivo_de_ordens_fica_fora_do_git` | `.gitignore` do projeto | passou |

## Provas (2ª volta)
- `env -i PATH HOME TMPDIR python3 -I -m unittest discover -s tests -p test_hooks.py -k OrdensEmVigor -k test_cada_hook -k ordens -k conformidade_tem`: 24 testes, OK.
- `bin/forge-mutante --base e34c7466e <specs 3 e 4> --processos 3` (`base=e34c7466e61b785683baf48201f20110ce3b2af2 ... rev=8e84ef3b57fa`): M15 a M26 e M28 `morreu`, nenhum sobrevivente (M26 por erro do teste sob o mutante com o controle verde). A spec 4 não tem M27: a sequência salta de M26 para M28, sem efeito no veredito.
- `bin/forge-mutante --cobertura --base e34c7466e`: linhas 1610, 1642 e 1645 de `hooks/conformidade.py` cobertas por M23, M24 e M25; `hooks/conformidade.json` e `bin/forge-init` (shell) saem `não coberto` pela checagem e têm M28 e M26 declarados e mortos.
- Suíte inteira: no CI do PR (check-run `bateria` do mesmo sha), fora deste parecer.
