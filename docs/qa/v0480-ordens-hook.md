---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-ordens-hook
commit: c63e96158e67cb61056a5552a12ed7a3f7354925
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-22
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
