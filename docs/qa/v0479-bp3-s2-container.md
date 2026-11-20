---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-bp3-s2-container
commit: ed21f2bd663c730ab23446ac2554504ad2e91319
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 1
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-20
---
# QA: BP3 S2, modelo de projeto e container (E39.5)

Base 004ce869; head testado ed21f2bd (revalidação do aprovado em 14c69010; escopo completo regravado). Obrigações: decisões do dono D2 (container que não para) e D3 (tarefa do VS Code só anexa) da BP3 e o item de ambiente (tmux instalado pelo preparo).

## Achados
- A1 (recomendado) tests/test_forge.py:2166 · O teste confere `apt-get install -y -qq tmux` por substring (`assertIn`): o mutante `tmuxx` no apt sobrevive. Comparar a linha inteira ou por token.

- A2 (bloqueante) changelog.d/v0479-bp3-s2-container.md:4 · Tipo `### Segurança` inválido (só Adicionado, Alterado, Corrigido): o pre-push reprova (`tipo 'Segurança' inválido`) e o CI reprova igual; mover a entrada para `### Alterado`.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| D3: tarefa roda ao abrir a pasta (`runOn: folderOpen`) | test_modelo_de_projeto_vscode_so_anexa_ao_jarvis_existente_e_container_nao_para | n/a | passou |
| D3: só anexa, nunca cria (sem `new-session`) | mesmo teste + test_tarefa_do_vscode_anexa_a_sessao_existente_e_nao_cria_outra (comando literal com tmux falso) | sessão ausente: só aviso, rc 0, nada criado; nome com `.` vira `_`, igual ao `scripts/jarvis` | passou |
| D2: container não para (`shutdownAction: none`) | test_modelo_de_projeto_vscode_so_anexa_ao_jarvis_existente_e_container_nao_para | n/a | passou |
| E39.17 (A1 da segurança): `.vscode/tasks.json` fora do alcance de Write, Edit e Bash | test_write_edit_e_bash_no_arquivo_em_vigor_saem_2 | os 3 caminhos de escrita saem 2 | passou |
| E39.17 (A2): `.devcontainer/devcontainer.json` idem | mesmo teste | idem | passou |
| E39.17: a proteção é por arquivo, não por pasta | test_vizinho_na_mesma_pasta_segue_gravavel | `.vscode/` vizinho segue gravável | passou |
| D2 no container do Forge (`shutdownAction: none`) | test_devcontainer_prepara_sozinho_sem_rodar_o_work_tree (asserção nova) | n/a | passou |
| Preparo instala tmux pelo apt; `--verificar` lista `falta: tmux`; apt que falha vira `falta:` rc 1 | test_modelo_de_projeto_instala_tmux_pelo_apt_e_verificar_lista_a_falta | tmux presente (idempotência, `tmux já instalado`), ausente, apt falho | passou |

## Cenários e resultado real
- Vermelho antes do verde (`R-QA`): em cópia com os 3 arquivos do modelo revertidos à base e o teste mantido, os 3 testes novos caem (1 falha, 2 erros). `forge-testes --vermelho 004ce869...` rodou os 34 módulos, listou `revertidos à base: changelog.d/..., devcontainer.json, preparar-ambiente.sh, tasks.json` e `mantidos no HEAD: tests/test_forge.py`; a saída não trouxe o veredito por teste, então o vermelho acima é o manual.
- Verde local no head: `python3 -I -m unittest discover -s tests -p test_forge.py -k PrepararEstacao -k Modelo`: 52 testes, OK. Suíte inteira: só no CI do PR (não rodei).
- Mutação à mão no diff (7 mutantes, cópia descartável): new-session no lugar de attach, `folderOpen` trocado, `shutdownAction` stopContainer, nome da sessão sem `=` exato, `tem tmux` removido do `--verificar`, falha do apt engolida: todos mortos. Apt `tmuxx`: sobrevive (A1, recomendado, não bloqueia).
- `shellcheck` não existe neste ambiente: não rodei. O CI roda.
- Remoto avançou com os pareceres do review e da segurança (docs apenas); trazido por fast-forward, sem tocar código.

## Revalidação no head ed21f2bd (E39.16)
`forge-check parecer delta` listou no domínio: devcontainer.json, hooks/conformidade.json, tests/test_conformidade_vscode_container.py, tests/test_forge.py, spec de mutantes, changelog e docs/engineering (patch do dono, não executável aqui). Lido só esse delta.
- Teste novo: `python3 -I -m unittest discover -s tests -p test_conformidade_vscode_container.py`: 2 testes, OK. `test_modelos_projeto.py`: 20 testes, OK.
- Vermelho: `forge-testes --vermelho 14c69010 --modulos test_conformidade_vscode_container` saiu 0: `base=14c690101de2 head=ed21f2bd663c`; `test_write_edit_e_bash_no_arquivo_em_vigor_saem_2 · H=ok · B=falha · prova (asserção)`; `test_vizinho_na_mesma_pasta_segue_gravavel · H=ok · B=ok · não prova (passa na base)` (guarda de regressão contra proteção larga, morta pelo M3).
- Mutantes (`forge-mutante tests/mutantes/v0479-bp3-s2-container.json`, rc 0): M1 morreu (conformidade.json:33), M2 morreu (:34), M3 morreu (:33), M4 morreu (devcontainer.json:21). Delta `--base 14c69010`: mesmos 4 mortos, linha `base=14c690101de2...`. Uma entrada de guarda mudada por linha: cada linha tem mutante. `--cobertura` lista só shell/JSON como `não coberto` (fora do Python); as 2 entradas do hook e o `shutdownAction` têm M1 a M4.
- Patch do dono (`denyWrite`): não aplicado; a segunda camada fica pendente do dono, sem bloquear.
- A1 (recomendado, `tmuxx`) segue aberto, sem mudança no delta.
- Remoto igual ao head local (`ls-remote` = ed21f2bd). Suíte inteira e shellcheck: só no CI do PR.
- Defeito novo no delta: ver A2. Prova: `git push origin melhoria/v0479-bp3-s2-container` no head ed21f2bd: `changelog.d/v0479-bp3-s2-container.md: tipo 'Segurança' inválido (use Adicionado, Alterado, Corrigido)`, rc 1. Este parecer só sobe depois da correção do fragmento.
