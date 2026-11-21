---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-conformidade-trilha
commit: 6c0b0f039a3ad89220cf328244e8df66da31c7d9
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 2
bugs_medios: 2
bugs_baixos: 0
data: 2026-11-21
---
# QA: v0478 E63.4 (hooks/conformidade.py: controle só do jarvis, escrita no índice, substituição no envio do git; head 6c0b0f03)

## Achados
- A1 (bloqueante) hooks/conformidade.py:332 · `git stage` é sinônimo de `git add` e fica fora de INDICE_NO_GIT: `git stage .githooks/pre-push` sai 0 (dev, projeto), enquanto `git add` do mesmo caminho recusa. Reproduzido; sem fixture. Incluir `stage`.
- A2 (bloqueante) hooks/conformidade.py:3989 · na sessão do Forge `echo 'git push origin develop' | bash` (aspas) sai 0 (tech-lead, dev, jarvis); sem aspas recusa. changelog e docs/hooks.md dizem que o pipe para o shell recusa na sessão do Forge; as fixtures só cobrem o projeto.
- A3 (recomendado) hooks/conformidade.py:3989 · shell atrás de envolvedor no pipe passa também no projeto: `echo "git push origin feature/x" | env bash`, `| sudo bash`, `| timeout 5 bash` saem 0; só nomes[0] é testado contra SHELLS (ENVOLVEDORES, linha 908, não entra).
- A4 (recomendado) hooks/conformidade.py:332 · `git apply --cached p.patch`, `git apply --index p.patch` e `git read-tree` gravam no índice conteúdo que nunca esteve na árvore (a classe S1-S4) e saem 0; o caminho está dentro do patch. Declarar o limite em docs/hooks.md ou recusar.

## Critério → teste → resultado
O pedido não tem especificação de UX nem contrato de API; as obrigações são as três regras do E63.1 (nome da regra no changelog e em docs/hooks.md).
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| CONTROLE-PEDIDOS-E-BRIEFS-SO-JARVIS: só o jarvis grava pedido e brief da pasta de controle | Hooks.test_fixtures_do_controle_so_jarvis (cpb-*, 44 arquivos) | permissão por papel, leitura livre, pasta vizinha (propostas), variável, teto | passou no head; 31 fixtures falham na base |
| CONFORMIDADE-ESCRITA-NO-INDICE: git add e update-index em quem: [] | Hooks.test_fixtures_da_escrita_no_indice (idx-*, 30 arquivos) | S1-S4, `--cacheinfo` nas duas formas, curinga, pasta mãe, lista pela entrada, varredura sem caminho | passou no head; 22 falham na base; sonda achou `git stage` (A1) e `git apply --cached` (A4) |
| CONFORMIDADE-SUBSTITUICAO-NO-PROJETO: envio com parte opaca | Hooks.test_fixtures_da_substituicao_no_projeto (sub-*, 26 arquivos) | programa, subcomando, flag, destino, xargs, pipe para shell; commit em heredoc e leitura com `$(…)` livres | passou no head; 16 falham na base; sonda achou o pipe na sessão do Forge (A2) e o envolvedor (A3) |
| Custo do corpus | tests/provas/v0479-corpus-custo.md (diff) | filtro barato antes da leitura | lido no diff; sem execução local (sem suíte local, brief) |

## Cenários e resultado real
vermelho (`forge-testes --vermelho d4f0b10a --modulos test_hooks`, duas rodadas, `timeout 900`, saída em `/root/.forge-contrib/wt/qa-e634-vermelho.txt`): rc=124 nas duas, sem veredito (a ferramenta reserva 600 s por módulo e cópia; o módulo inteiro passa de 900 s no sandbox). Cabeçalho obtido: `vermelho: base=d4f0b10aead7 head=6c0b0f039a3a módulos=test_hooks (restrito por --modulos)`; `revertidos à base: ... hooks/conformidade.py ...`. Não vale como vermelho.

Vermelho à mão, no lugar dele (cópia do head com só `hooks/conformidade.py` da base, `python3 -I -m unittest discover -s tests -p test_hooks.py -k <os três testes>`): base `Ran 3 tests ... FAILED (failures=69)` (31 controle, 22 índice, 16 substituição); head `Ran 3 tests in 5.804s OK`.

Mutantes, uma chamada por spec, `timeout 900`, rc=0 em todas: trilha.json C1-C5 mortos; trilha-2 I1-I6 e I8 mortos; trilha-3 S1-S9 mortos; trilha-4 K1-K8 mortos; trilha-5 L1-L8 mortos. Total 37 mortos, nenhum sobrevivente (o brief diz 36; as specs somam 37). `forge-mutante --cobertura --base d4f0b10a`: rc=0, 32 linhas `coberta · ... · declarado, não provado`, nenhuma `não coberto`.

Sondas fora das fixtures (hook rodado por script próprio sobre a montagem das fixtures, `qa-e634-sonda.py`): controle, 38 formas (`tee`, `sed -i`, `mv`, `ln`, `install`, `dd`, `rsync`, `tar`, `unzip`, `cd` mais redirecionamento relativo, `..`, `//`, `${HOME}`, glob, python com `expanduser`) recusam; passam as leituras, `propostas/` e os limites já aceitos (`curl -o`, editor interativo, python com caminho relativo, nome da pasta numa variável). Índice, 40 formas: recusam o caminho com `--`, `./`, `..`, `:/`, `:(top)`, curinga, pasta mãe, `-C`, `cd`, `$PWD`, `--chmod`, `-f`, `--cacheinfo` separado, `--stdin`, `--index-info`, `--pathspec-from-file` e abreviação; `--cacheinfo=…` é rejeitado pelo próprio git (`takes no value`), então a passagem é inócua. Substituição, 60 formas: recusam `$(…)`, crase, `<(…)`, aspas, `xargs`, `env`, `command`; `bash <<<` e `bash -c "$(…)"` recusam pelas regras antigas; passam o commit com heredoc, `git status $(pwd)`, `git push origin melhoria/x 2>&1 | tail`, `git fetch origin $(…)` e o `echo … | cat`. Falso positivo aceito pelo desenho: `git push origin "melhoria/$(date +%s)"` recusa (destino por substituição).

Fixtures `pesado/mesma-sessao-libera` e `meta/v0454-caminhos-extra-*`: não rodadas por mim; o brief as dá como falhas na base também.

CI: este parecer não cita check-run `bateria`; o head ainda não tem PR (brief: sem PR). A suíte inteira não rodou aqui.

Provas de reprovação (reproduzíveis com a sonda, base `sub-sessao-forge-commit-heredoc-libera.json`, papel `forge:tech-lead`, e `idx-s4-add-chmod-bloqueia.json`, papel `forge:dev`):
- A1: `git stage .githooks/pre-push` rc=0; `git add .githooks/pre-push` rc=2.
- A2: `echo "git push origin develop" | sh` rc=0; `echo git push origin develop | sh` rc=2; `$(echo git) push origin develop` rc=2. Causa: na sessão do Forge a recusa passa por `trava_da_sessao_do_forge` → `toca_uma_trava`, que só marca shell no nível aninhado.

Bugs: não gravei `docs/qa/bugs/` (o brief manda commit só do parecer); A1 e A2 vão ao autor pelo bloco Achados.
