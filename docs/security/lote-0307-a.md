---
tipo: revisao-seguranca
contrato: 1
pedido: lote-0307-a
branch: melhoria/lote-0307-a
commit: 05fd5c560c4d3c2ab22e7ecbc3fbcd71993e2c5b
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-29
---
# Review de segurança: lote-0307-a

Escopo: `git diff 3b94791a8e96771c061eabb8e2b77381151289d1...05fd5c560c4d3c2ab22e7ecbc3fbcd71993e2c5b`; revalidação por delta do parecer anterior (c8830a9, sobre 38f3f71) com `forge-check delta --parecer docs/security/lote-0307-a.md` (intervalo 38f3f71..05fd5c5: bin/forge-fechar:595, os dois modelos de segurança na linha 27, tests/test_fechar_base_andou.py:6 e 295-315, tests/mutantes/lote-0307-a.json:11-33) e releitura da guarda inteira (bin/forge-fechar:592-605), por ser controle do Forge.

## Gatilhos
Controles do Forge (`R-SEGURANCA`): `bin/forge-fechar` é o script do merge na `develop`; a volta 1 muda a condição da guarda do `index.lock` (bin/forge-fechar:595). Os modelos de parecer são lidos por quem grava os portões (`R-REVIEW`).

## Achados
- A2 (recomendado) bin/forge-fechar:598 · o teste -e não vê index.lock que é link simbólico pendurado (o git o trata como lock presente); sem caminho de ataque; aberto desde a rodada anterior
- A4 (recomendado) bin/forge-fechar:552 · o --dry-run não descreve o passo 0 da guarda, que docs/fechamento-integrador.md:13 lista; aberto desde a rodada anterior
- A5 (recomendado) docs/fechamento-integrador.md:13 · o passo 0 documentado não diz que a worktree registrada sem diretório é pulada (o passo 7 a trata com prune), comportamento novo de bin/forge-fechar:595

## Detalhe dos achados
**A1 (bloqueante na rodada anterior): resolvido.** docs/security/_modelo.md:27 e templates/projeto/docs/security/_modelo.md:27 agora dizem que, em parecer aprovado, as recomendações ficam em prosa ou no bloco `## Achados` como linhas `(recomendado)`, coerente com a linha 15 dos mesmos arquivos. Os dois arquivos são idênticos (`cmp`) e `test_modelo_de_seguranca_da_raiz_igual_ao_do_template` passa. Nenhum modelo de parecer (review, QA, segurança, raiz e template) diz mais que o bloco fica vazio em parecer aprovado (conferido por grep).

**A3 (recomendado na rodada anterior): resolvido pela volta.** A condição nova da linha 595 (`-n` e `-d` sobre o caminho da worktree) pula a guarda quando o diretório da worktree já sumiu, em vez de parar com a mensagem de pasta git ilegível. Conferências da guarda nova:
- **Continua só lendo e avisando, sem apagar o lock.** O bloco segue chamando só `git worktree list --porcelain`, `git -C <worktree> rev-parse --git-dir`, os testes `-d` e `-e`, `stat` e `date`; nenhum `rm`, `unlink` nem escrita; o `rm` só é impresso, escapado com `printf '%q'`, sem `eval`. O teste do lock presente confere o arquivo ainda lá (mutante L1), e o teste novo do git-dir relativo (mutante L2) também confere que o lock existe depois.
- **O pulo não abre caminho para mesclar com lock ativo.** Sem o diretório, não há árvore de trabalho onde um git possa estar rodando sobre aquele índice; o `index.lock` que restar na pasta administrativa da worktree sai com o registro no `git worktree prune` do passo 7 (bin/forge-fechar:406), que só respeita o arquivo `locked` da worktree, não o `index.lock`. O merge é feito no servidor (`gh pr merge --match-head-commit`), sem tocar nesse índice.
- **Falha fechada mantida nos demais casos.** Diretório presente que não é worktree legível ainda sai por `die` (linha 596). Diretório que é link para outro repositório faria o `rev-parse` apontar a pasta git desse outro repositório: só leitura de existência e mtime, sem ganho para quem já controla o sistema de arquivos.
- O teste `test_worktree_da_branch_com_a_pasta_apagada_nao_para_no_lock` cobre o pulo (mutante L3).

**A2 (recomendado; informativa, esforço P, dono tech-lead).** Sem mudança na volta (a linha passou de 600 para 598 na numeração atual). Correção mínima: acrescentar ao teste da linha 598 a alternativa `|| [ -L "$pasta_git/index.lock" ]`. Sem caminho de ataque: quem grava na pasta administrativa das worktrees já controla o repositório.

**A4 (recomendado; informativa, esforço P, dono tech-lead).** Sem mudança na volta. Correção mínima: uma linha `passo 0` no bloco do `--dry-run` (bin/forge-fechar:542-552), antes do passo 1, dizendo que procura index.lock na pasta git da worktree da branch, só lê e para se existir.

**A5 (recomendado; informativa, esforço P, dono tech-lead).** docs/fechamento-integrador.md:13 descreve o passo 0 sem o caso novo. Correção mínima: acrescentar que a worktree registrada cujo diretório já não existe é pulada (o passo 7 a remove com prune).

PA-7: o único item (AR-1, máscara do shell que esconde código) não se aplica ao delta: o `-d` novo é condição do `if`, sem `|| true` nem `|| echo`, e o `|| die` da linha 596 continua preservando a falha.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Leitura manual do diff e do delta; `forge-check delta --parecer` (cópia vigente 0.30.5, aviso de versão sem efeito no veredito); `python3 -m unittest tests.test_fechar_base_andou` verde (24 testes); `test_modelo_de_seguranca_da_raiz_igual_ao_do_template` verde; `shellcheck -x bin/forge-fechar` sem aviso. Lacunas no ambiente: `gitleaks`, `semgrep` e `zizmor` não estão no PATH; não instalados (`R-CUSTO`); a entrega não toca workflow nem segredo.
