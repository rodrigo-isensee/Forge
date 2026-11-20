---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-bp3-s2-container
commit: 14c690101de2a9a0442086d9fdad2c1d8deead31
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-20
---
# QA: BP3 S2, modelo de projeto e container (E39.5)

Base 004ce869; head testado 14c69010. Obrigações: decisões do dono D2 (container que não para) e D3 (tarefa do VS Code só anexa) da BP3 e o item de ambiente (tmux instalado pelo preparo).

## Achados
- A1 (recomendado) tests/test_forge.py:2166 · O teste confere `apt-get install -y -qq tmux` por substring (`assertIn`): o mutante `tmuxx` no apt sobrevive. Comparar a linha inteira ou por token.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| D3: tarefa roda ao abrir a pasta (`runOn: folderOpen`) | test_modelo_de_projeto_vscode_so_anexa_ao_jarvis_existente_e_container_nao_para | n/a | passou |
| D3: só anexa, nunca cria (sem `new-session`) | mesmo teste + test_tarefa_do_vscode_anexa_a_sessao_existente_e_nao_cria_outra (comando literal com tmux falso) | sessão ausente: só aviso, rc 0, nada criado; nome com `.` vira `_`, igual ao `scripts/jarvis` | passou |
| D2: container não para (`shutdownAction: none`) | test_modelo_de_projeto_vscode_so_anexa_ao_jarvis_existente_e_container_nao_para | n/a | passou |
| Preparo instala tmux pelo apt; `--verificar` lista `falta: tmux`; apt que falha vira `falta:` rc 1 | test_modelo_de_projeto_instala_tmux_pelo_apt_e_verificar_lista_a_falta | tmux presente (idempotência, `tmux já instalado`), ausente, apt falho | passou |

## Cenários e resultado real
- Vermelho antes do verde (`R-QA`): em cópia com os 3 arquivos do modelo revertidos à base e o teste mantido, os 3 testes novos caem (1 falha, 2 erros). `forge-testes --vermelho 004ce869...` rodou os 34 módulos, listou `revertidos à base: changelog.d/..., devcontainer.json, preparar-ambiente.sh, tasks.json` e `mantidos no HEAD: tests/test_forge.py`; a saída não trouxe o veredito por teste, então o vermelho acima é o manual.
- Verde local no head: `python3 -I -m unittest discover -s tests -p test_forge.py -k PrepararEstacao -k Modelo`: 52 testes, OK. Suíte inteira: só no CI do PR (não rodei).
- Mutação à mão no diff (7 mutantes, cópia descartável): new-session no lugar de attach, `folderOpen` trocado, `shutdownAction` stopContainer, nome da sessão sem `=` exato, `tem tmux` removido do `--verificar`, falha do apt engolida: todos mortos. Apt `tmuxx`: sobrevive (A1, recomendado, não bloqueia).
- `shellcheck` não existe neste ambiente: não rodei. O CI roda.
- Remoto avançou com os pareceres do review e da segurança (docs apenas); trazido por fast-forward, sem tocar código.
