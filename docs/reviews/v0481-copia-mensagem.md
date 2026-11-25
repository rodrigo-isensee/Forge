---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-copia-mensagem
commit: 7bdd25d54a37943b23faf6d3dcd3fc558544eebc
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-25
---
# Review: v0481 (E14.3), forge-copia: mensagem certa e clone de revisão (#889)

Diff revisado: `8833d0f6..7bdd25d5` (1 commit), `bin/forge-copia` (+28 e -6, dentro do teto H1, um comportamento: o ponto de partida do clone e a mensagem dele), `tests/test_forge_copia.py`, `tests/mutantes/v0481-copia-mensagem.json`, `tests/mutantes/v0481-copia-base.json` (M2 acompanha a linha, AR-12), `changelog.d/v0481-copia-mensagem.md`. Sem parecer de review anterior na branch; o A1 recomendado do review do #879 é o que este item fecha.

## Achados
- A1 (recomendado) skills/checagem-do-brief/por-tema.md:5 · A skill que diz como criar a cópia não cita `forge-copia clone --revisao` para o caminho -rev, -qa ou -sec; sem isso o revisor segue no `git clone` à mão e a medida do PR não anda. Sugestão: uma frase com o comando do clone de revisão.
- A2 (recomendado) bin/forge-copia:143 · No modo --revisao o aviso diz "não de origin/develop", mas a base nunca é candidata ali (sonda S3 abaixo, só registro). Sugestão: omitir o "não de <base>" quando revisao.

## Sondas

## Parecer
**Aprovado.** Faz o que o E14.2 pede, sem mais.

Clone de revisão criado pelo próprio `--revisao` da branch (bin do `7bdd25d5` extraído por `git archive`): `/root/.forge-contrib/wt/v0481-copia-mensagem-rev` nasceu em `7bdd25d5`, na branch `melhoria/v0481-copia-mensagem`, sem `branch.<b>.remote`.

Caminhos conferidos (nenhum deixa clone na main nem sobre ref errada):
- `--revisao` com a branch no remoto: parte de `refs/remotes/origin/<branch>` (nome exato, checklist 12), `--no-track`; teste `test_clone_de_revisao_parte_do_head_remoto_sem_upstream` confere head e falta de upstream.
- `--revisao` sem a branch no remoto: `ponto_de_partida` devolve None antes do laço da base; `rmtree` e saída 1; a mensagem cita só `origin/<branch>`. Sonda com a origem real: rc=1, destino ausente.
- `--revisao --branch main`: o `switch -c main` falha, `rmtree`, saída 1, mensagem "o git switch falhou a partir de origin/main"; a cópia não fica na main.
- `worktree --revisao`: recusa (2) antes de qualquer escrita; sonda rc=2, destino ausente.
- Mensagem: `candidatas` não gera mais `origin/origin/...`; o teste afirma a lista exata nas duas formas de base e o `assertNotIn("origin/origin/")`.
- Nada que barrava deixou de barrar: a recusa nova entra depois de `--branch` e antes das demais, que ficam intactas; com base `origin/<x>` a tentativa extra `origin/origin/<x>` sai, o que não afrouxa (essa ref nunca existe num clone). O `rmtree` segue só no destino validado e recém-clonado.

Sondas executadas (script em `/root/.forge-contrib/wt/_tl113-v0481-sonda.sh`), só registro, nenhuma prova bloqueante: S1 branch fora do remoto rc=1 sem cópia; S2 worktree rc=2 sem cópia; S3 `--branch main --revisao` rc=1 sem cópia.

Ferramentas (citadas, não refeitas): `python3 -m unittest tests.test_forge_copia` no clone, 85 testes OK. `bin/forge-mutante --processos 1 tests/mutantes/v0481-copia-mensagem.json` em `7bdd25d5`: M1 a M6 morreram (linhas 135, 145, 155, 157, 301, 331); `--ids M2 tests/mutantes/v0481-copia-base.json`: morreu (135). `--cobertura --base 8833d0f6`: toda condição mudada coberta, sem linha "sem mutante". `--conferir --base 8833d0f6`: trechos no lugar. `--conferir --todas`: rc=1 com 26 linhas, idênticas às da base `8833d0f6` (specs antigas com trecho repetido), nenhuma das specs deste diff. Suíte inteira: CI do PR #889 em andamento no momento do parecer (catraca verde, `bateria` pendente); cito o PQ do autor.
