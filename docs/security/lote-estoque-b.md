---
tipo: revisao-seguranca
contrato: 1
pedido: versao-034
branch: melhoria/lote-estoque-b
commit: fb390efc8e6e3b27c4a1f18b5a22bfc997231cb3
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-06
---
# Review de segurança: versao-034 (E2.3, junção do lote B)

Escopo: a junção `d9b26bb..84472bf` (7 merges na primeira linha de pais e o commit 84472bf do changelog), a resolução de conflitos e o que a soma dos itens muda nos gatilhos. Cada item já tem o próprio parecer aprovado; aqui não se revê o item, só a soma.

## Gatilhos
`R-SEGURANCA`: CI/CD (`.github/workflows/ci.yml`, `catraca.yml`, `release.yml`) e controles do Forge (`tests/catraca.py`). Hooks e `hooks/conformidade.json`, `docs/regras/` e `tests/config.json`: o lote não os toca (`git diff --stat d9b26bb 84472bf`).

## Achados
- A1 (recomendado) bin/forge-changelog:235 · release-pr-so-parecer afrouxa o gate do changelog (PR só de parecer dispensa fragmento) e não tem parecer de segurança próprio (fora da lista de gatilhos); o PR do lote precisa do rótulo afrouxa-regra do dono (E2.6).

## Por item (o que vi e onde)
- Resolução de conflitos (os 7 merges 4ae41ca, f3810c2, f1ea0ca, 7e250b5, 5d63b29, 04e1304, 7ee4a7b): `git show --remerge-diff` de cada um sai vazio; nenhum conflito resolvido à mão, o resultado é a união textual. O 84472bf só move os 7 fragmentos para `changelog.d/lote-estoque-b.md` (sem código).
- Ordem dos merges, catraca-ramo (4ae41ca) antes de catraca-fork (f3810c2): a branch catraca-fork foi feita sobre um commit antigo da catraca-ramo (088a1e1), sem o merge da develop e o ajuste de testes da ponta dela (586d77d, e736881); nessa ordem a junção é limpa e `git diff 838803f 84472bf -- tests/catraca.py` (838803f é o commit aprovado do catraca-fork) sai vazio. A ordem inversa conflitaria em `tests/catraca.py` e não muda o resultado.
- catraca-ramo-cmd-pr (4ae41ca; tests/catraca.py, tests/test_catraca.py): na soma, o filtro por `branch:` entra em tests/catraca.py:1164 (`cmd_pr(..., ramo)`, assinatura `cmd_pr(raiz, pedido, ref, base, branch)` em bin/forge-check:896, já na base), depois da recusa de fork; na branch do próprio repositório só conta o parecer daquela branch.
- catraca-fork (f3810c2; tests/catraca.py, ci.yml): `violacoes_de_pareceres` (tests/catraca.py:1118) chama `violacao_de_fork` antes de tudo e devolve a recusa sem ler parecer (falha fechada, inclusive `head.repo` nulo e CI sem `BASE_REPO`). O único chamador de `--modo pareceres` é ci.yml:237, que recebe `HEAD_REPO` e `BASE_REPO` (ci.yml:226-227) do contexto do evento por `env:`, sem interpolação no `run:`; o catraca.yml não usa o modo pareceres (roda o modo regras e o pr-texto), então a recusa de CI sem `BASE_REPO` não deixa outro workflow vermelho por engano. As duas defesas da catraca se somam.
- ci-env-argv0-v2 (7e250b5; ci.yml): o passo do env (ci.yml:56 e 260) instala `rust-coreutils` do apt assinado do Ubuntu e escreve no `GITHUB_PATH` (ci.yml:69 e 274); na `bateria` isso fica depois do download com checksum, do actionlint e do zizmor (ci.yml:152-170), como pede o CI-ORDEM-LINT (ci.yml:151). O job não tem segredo nem permissão de escrita (`contents: read`) e o código do PR já roda no mesmo job: sem caminho de ataque novo.
- ci-ubuntu-26-migracao (5d63b29, só os pareceres; a troca do runner, fd3a3e1, chegou pelo f1ea0ca): runner 26.04 em todos os jobs (ci.yml:27, 46 e 98; catraca.yml:20; release.yml:14); `permissions:`, ações fixadas por SHA e `concurrency` sem mudança (confere com o parecer de devops do lote).
- ci-comentario-rapida (f1ea0ca; ci.yml:3-8): só o comentário do topo do ci.yml muda (o que o job `rapida` roda), mais o runner do item acima; nenhum passo, permissão ou gatilho novo.
- release-pr-so-parecer (04e1304; bin/forge-changelog:191 e :235): o atalho exige que todo arquivo mudado seja parecer (`e_parecer`), lido com `--no-renames`, e valida fragmento presente antes do atalho; a catraca segue exigindo os pareceres. Nenhum caminho de ataque novo na soma; o gate fica mais brando, ver A1.
- lote-cilista-v2 (7ee4a7b; tests/test_ci_local.py): a lista fechada de passos antes do lint aceita o ci.yml somado: `test_ci_local.py` 55 testes OK sobre a árvore de 84472bf mais o parecer de devops.
- A1 (bin/forge-changelog:191 e :235): severidade informativa; caminho de ataque: nenhum novo na soma; é processo, não vulnerabilidade. Correção mínima: nenhuma no código; a E2.6 pede o rótulo `afrouxa-regra` ao dono. Esforço: P. Dono: Jarvis (pergunta ao dono).
- Testes dos arquivos tocados (D-5), na worktree em ff7c246 (84472bf mais só o parecer de devops): `test_ci_local.py` 55 OK, `test_catraca.py` 280 OK, `test_changelog.py` 53 OK. A suíte inteira rodou no push de 84472bf (/tmp/push-lote-b2.log), sem rodar de novo aqui.

## Revalidação das voltas do CI
Delta `237c130..fb390ef` (7ec3a35, 83b3e55, fb390ef), que corrige as falhas do CI do PR #455 (/tmp/ci-455.log: o actionlint recusou o label `ubuntu-26.04`, e a bateria teve 288 falhas no processo dos testes do corpus); o resto do intervalo depois de 84472bf é só parecer. Não sou o autor das voltas.
- Label no actionlint (.github/actionlint.yaml:4-6): só acrescenta `ubuntu-26.04` à lista `self-hosted-runner.labels`; nenhuma regra desligada, nenhum `ignore` nem `paths`, e o actionlint segue rodando em todos os workflows. O label é um runner hospedado do GitHub (ci.yml:27, 46 e 98; catraca.yml:20; release.yml:14), não um runner próprio: sem superfície nova. O zizmor não lê esse arquivo.
- Pacote e passo novos do CI (ci.yml:64 e 273; ci.yml:76-79 e 285-288): `gnu-coreutils` vem do mesmo apt assinado do Ubuntu que já trazia o `rust-coreutils`, com `--no-install-recommends`, no passo que já tinha `set -euo pipefail`; o passo novo só confere que o `gnuenv` existe e divide `--s` como o GNU, sem escrever no `GITHUB_PATH` (o `env` do PATH continua o do uutils, conferido nas linhas de cima), sem segredo, sem interpolação de contexto no `run:` e com `permissions:` intactas. Falha fechada: a falta ou o comportamento errado reprova o job.
- Critério do env_gnu (tests/apoio_volta_unica.py:436-460): o `env` só é aceito se dividir `echo a  b` em toda grafia de `OPCOES_DE_DIVISAO` (tests/apoio_volta_unica.py:626), e não mais só no `-S` separado; os modelos são constantes da classe, executados por lista de argumentos (`shlex.split` do modelo, sem shell), com timeout e stdin fechado. O critério ficou mais estrito: o gerador do corpus deixa de usar um `env` que recusa parte das grafias e cobriria menos a dimensão "lançador que divide texto" do filtro.
- Falha fechada no teste (tests/apoio_volta_unica.py:458-459): `env` que divide o `-S` separado mas recusa alguma grafia, sem outro que divida tudo, levanta `AssertionError` com a grafia e o caminho, em vez de cair no skip; o skip fica só para a máquina sem `env` que divida o `-S` separado. Fecha o caminho em que a bateria do controle passaria verde sem ter rodado a dimensão. O `lru_cache` sobre o `classmethod` não guarda exceção, então a recusa se repete em cada chamada.
- Testes dos arquivos tocados (D-5), sobre a árvore de fb390ef mais os pareceres: `test_hooks_volta_corpus` (o único que usa o `env_gnu`) 16 OK com o `env` GNU 9.4 local. A suíte inteira rodou no push de fb390ef (/tmp/push-lote-b8.log: 2632 testes, OK, skipped=30), sem rodar de novo aqui.
- Veredito: nenhum achado novo; o delta endurece o CI e o teste do controle, sem afrouxar regra. A1 segue como estava (recomendado, rótulo `afrouxa-regra` na E2.6). Parecer mantido: aprovado, agora sobre fb390ef.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: `gitleaks`, `zizmor`, `actionlint`, `semgrep` e `osv-scanner` ausentes do PATH (lacuna; actionlint e zizmor rodam no job `bateria` do CI). Revisão por leitura do diff e do remerge-diff.
