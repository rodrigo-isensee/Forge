---
tipo: revisao-seguranca
contrato: 1
pedido: lote-0307-a
branch: melhoria/lote-0307-a
commit: 38f3f7194f36fd0e9b0dd1e0e01bf4c7280e4c19
parecer: reprovado
revisor: forge:security-engineer
data: 2026-10-28
---
# Review de segurança: lote-0307-a

Escopo: `git diff 3b94791a8e96771c061eabb8e2b77381151289d1...38f3f7194f36fd0e9b0dd1e0e01bf4c7280e4c19` (bin/forge-fechar, docs/fechamento-integrador.md, os três modelos de parecer de templates/projeto/docs/, docs/security/_modelo.md, tests/test_fechar_base_andou.py, tests/mutantes/lote-0307-a.json, changelog.d/lote-0307-a.md).

## Gatilhos
Controles do Forge (`R-SEGURANCA`): `bin/forge-fechar` é o script do merge na `develop`; a entrega acrescenta a guarda do `index.lock` antes do passo 1 (bin/forge-fechar:592-604). Os modelos de parecer são lidos por quem grava os portões (`R-REVIEW`).

## Achados
- A1 (bloqueante) docs/security/_modelo.md:27 · classe requisito: a seção Detalhe dos achados ainda diz que parecer aprovado deixa o bloco Achados vazio, contra a linha 15 nova e o objetivo (2) do LOTE-0307-A; o mesmo em templates/projeto/docs/security/_modelo.md:27
- A2 (recomendado) bin/forge-fechar:600 · o teste -e não vê index.lock que é link simbólico pendurado (o git o trata como lock presente); sondado: o fechamento segue e abre o PR; sem caminho de ataque
- A3 (recomendado) bin/forge-fechar:596 · worktree registrada com o diretório ausente agora para antes do passo 1 com "não consegui ler a pasta git", sem dizer a saída (git worktree prune); falha fechada
- A4 (recomendado) bin/forge-fechar:552 · o --dry-run não descreve o passo 0 da guarda, e docs/fechamento-integrador.md:13 o lista entre os passos

## Detalhe dos achados
**A1 (bloqueante, classe requisito; severidade baixa, esforço P, dono tech-lead).** Evidência: docs/security/_modelo.md:27 e templates/projeto/docs/security/_modelo.md:27 terminam com "Em parecer aprovado, as recomendações não bloqueantes ficam aqui, em prosa, e o bloco `## Achados` fica vazio", enquanto a linha 15 dos mesmos arquivos passou a dizer "Parecer aprovado traz só linhas `(recomendado)` ou o bloco vazio". O objetivo (2) do pedido é o modelo deixar de dizer que parecer aprovado tem o bloco vazio; o modelo de segurança continua dizendo, e agora se contradiz. Não é falha explorável: é requisito da especificação não cumprido (o E2 cobre "os modelos de QA e de segurança"). Os modelos de review e de QA não têm a frase (conferido por grep). Correção mínima, idêntica nos dois arquivos (o teste `test_modelo_de_seguranca_da_raiz_igual_ao_do_template` exige igualdade): trocar o fim da frase por "Em parecer aprovado, as recomendações não bloqueantes ficam aqui, em prosa, e o bloco `## Achados` traz só as linhas `(recomendado)` delas, ou fica vazio sem recomendação." Lista completa dos arquivos a corrigir: `docs/security/_modelo.md`, `templates/projeto/docs/security/_modelo.md`.

**A2 (recomendado; informativa, esforço P, dono tech-lead).** bin/forge-fechar:600 usa `[ -e "$pasta_git/index.lock" ]`, que segue o link: um `index.lock` que é link simbólico para destino inexistente dá falso, e o git (abertura exclusiva) o trata como lock presente. Sondado em cópia do ambiente de teste: rc=0 e o PR aberto. Caminho de ataque: nenhum realista (quem grava em `.git/worktrees/` já controla o repositório; o lock órfão de um git morto é arquivo comum). Correção mínima: `if [ -e "$pasta_git/index.lock" ] || [ -L "$pasta_git/index.lock" ]; then`.

**A3 (recomendado; informativa, esforço P, dono tech-lead).** Com a worktree da branch registrada e o diretório apagado (estado `prunable`), o `git -C` de bin/forge-fechar:596 falha e o script para antes do passo 1 (sondado: rc=1, "não consegui ler a pasta git da worktree ..."). É falha fechada, sem risco de segurança; o custo é a mensagem não dizer a saída. O `--limpar` roda antes da guarda e não é afetado. Correção mínima: acrescentar à mensagem "se o diretório não existe mais, rode git worktree prune e repita".

**A4 (recomendado; informativa, esforço P, dono tech-lead).** O bloco do `--dry-run` (bin/forge-fechar:542-552) imprime os passos 1 a 7 e não o passo 0 novo, que docs/fechamento-integrador.md:13 documenta. Correção mínima: uma linha `passo 0 "procura index.lock na pasta git da worktree de $ref (só lê; para se existir)"` antes do passo 1 do `--dry-run`.

Conferências que sustentam os requisitos do brief:
- **Só lê e avisa, nunca apaga.** A guarda (bin/forge-fechar:594-604) chama só `git worktree list --porcelain`, `git -C <worktree> rev-parse --git-dir`, `[ -e ]`, `stat` e `date`; nenhum `rm`, `unlink` nem escrita. O comando `rm` só é impresso. O teste `test_lock_presente_na_worktree_da_branch_para_com_codigo_1_e_nao_apaga` confere o lock ainda presente, e o mutante L1 morre.
- **Não deixa o fechamento seguir com o lock presente.** A guarda sai por `die` (código 1) antes do passo 1, sem PR nem merge (o teste confere criações e merges vazios). Toda falha de leitura da pasta git também para (falha fechada). A guarda fica depois das saídas do `--dry-run` e do `--limpar`, que não mesclam.
- **O caminho impresso não abre leitura fora da pasta git da worktree.** A pasta vem do registro de worktrees do próprio repositório e do `rev-parse --git-dir` da worktree (a pasta que o git usa de fato); do lock só se lê a existência e o mtime, nunca o conteúdo. O `$ref` passa por `git check-ref-format --branch` (bin/forge-fechar:70) antes de entrar no `awk -v`. O `rm` impresso sai com `printf '%q'`: sondado com worktree em caminho com espaço, `;` e `$(...)`, o comando vem escapado e nada é executado (só o `die` imprime; não há `eval`).
- **PA-7:** o único item (AR-1, máscara do shell que esconde código) não se aplica: o `|| die` de bin/forge-fechar:596 preserva a falha, e o `|| echo ""` do `stat` (linha 599) cai em "idade desconhecida" sem mudar a decisão, que depende só do `[ -e ]`.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Leitura manual do diff; sondas próprias em `$TMPDIR` sobre o ambiente de `tests/test_fechar_base_andou.py` (worktree sem diretório, caminho com metacaractere, lock como link pendurado); `python3 -m unittest tests.test_fechar_base_andou` verde (22 testes); `shellcheck -x bin/forge-fechar` sem aviso. Lacunas no ambiente: `gitleaks`, `semgrep` e `zizmor` não estão no PATH; não instalados (`R-CUSTO`); a entrega não toca workflow nem segredo.
