---
tipo: revisao-seguranca
contrato: 1
pedido: versao-034
branch: melhoria/lote-estoque-b
commit: 84472bfa6c63406c46a6c86ce6353939a39a53dc
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

## Detalhe dos achados
**Resolução de conflitos.** `git show --remerge-diff` dos 7 merges (4ae41ca, f3810c2, f1ea0ca, 7e250b5, 5d63b29, 04e1304, 7ee4a7b) sai vazio: nenhum conflito resolvido à mão, o resultado é a união textual. O 84472bf só move os 7 fragmentos para `changelog.d/lote-estoque-b.md` (sem código).

**Ordem catraca-ramo (4ae41ca) antes de catraca-fork (f3810c2).** A branch catraca-fork foi feita sobre um commit antigo da catraca-ramo (088a1e1), sem o merge da develop e o ajuste de testes da ponta dela (586d77d, e736881). Nessa ordem a junção é limpa e `tests/catraca.py` em 84472bf é idêntico ao de 838803f (o commit aprovado do catraca-fork): `git diff 838803f 84472bf -- tests/catraca.py` vazio. Na soma, `violacoes_de_pareceres` (tests/catraca.py:1118) chama `violacao_de_fork` antes de tudo e devolve a recusa sem ler parecer; só depois o filtro por `branch:` do catraca-ramo entra (tests/catraca.py:1164, `cmd_pr(..., ramo)`, assinatura `cmd_pr(raiz, pedido, ref, base, branch)` em bin/forge-check:896, já na base). As duas defesas se somam: fork é recusado (falha fechada, inclusive `head.repo` nulo e CI sem `BASE_REPO`), e na branch do próprio repositório só conta o parecer daquela branch. A ordem inversa conflitaria em `tests/catraca.py` e não muda o resultado.

**Workflow que alimenta a catraca.** O único chamador de `--modo pareceres` é ci.yml:237, que passa `HEAD_REPO` e `BASE_REPO` (ci.yml:226-227) a partir do contexto do evento, por `env:`, sem interpolação no `run:`. O catraca.yml não usa o modo pareceres (roda o modo regras e o pr-texto), então a recusa de CI sem `BASE_REPO` não deixa outro workflow vermelho por engano.

**CI (ci-env-argv0-v2, ci-ubuntu-26, ci-comentario-rapida).** O passo do env (ci.yml:56 e 260) instala `rust-coreutils` do apt assinado do Ubuntu e escreve no `GITHUB_PATH` (ci.yml:69 e 274); na `bateria` isso fica depois do download com checksum, do actionlint e do zizmor (ci.yml:152-170), como pede o CI-ORDEM-LINT (ci.yml:151). O job não tem segredo nem permissão de escrita (`contents: read`), e o código do PR já roda no mesmo job: sem caminho de ataque novo. Runner 26.04 em todos os jobs; `permissions:`, ações fixadas por SHA e `concurrency` sem mudança (confere com o parecer de devops do lote).

**lote-cilista-v2 com os demais.** A lista fechada de passos antes do lint (tests/test_ci_local.py) aceita o ci.yml somado: `test_ci_local.py` 55 testes OK sobre a árvore de 84472bf mais o parecer de devops.

**A1.** Evidência: bin/forge-changelog:191 (`e_parecer`) e :235 (atalho). Caminho de ataque: nenhum novo na soma; o atalho exige que todo arquivo mudado seja parecer, lido com `--no-renames`, e a catraca segue exigindo os pareceres. É informativo: o gate fica mais brando e por isso pede o rótulo do dono, que é processo, não vulnerabilidade. Severidade: informativa. Correção mínima: nenhuma no código; a E2.6 pede o rótulo `afrouxa-regra`. Esforço: P. Dono: Jarvis (pergunta ao dono).

Testes dos arquivos tocados (D-5), na worktree em ff7c246 (84472bf mais só o parecer de devops): `test_ci_local.py` 55 OK, `test_catraca.py` 280 OK, `test_changelog.py` 53 OK. A suíte inteira rodou no push de 84472bf (/tmp/push-lote-b2.log), sem rodar de novo aqui.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: `gitleaks`, `zizmor`, `actionlint`, `semgrep` e `osv-scanner` ausentes do PATH (lacuna; actionlint e zizmor rodam no job `bateria` do CI). Revisão por leitura do diff e do remerge-diff.
