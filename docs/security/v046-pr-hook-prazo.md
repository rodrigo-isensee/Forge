---
tipo: revisao-seguranca
contrato: 1
pedido: v046
branch: melhoria/pr-hook-prazo
commit: 4ae51318d06223e29c3d09913965dd081d4ddb62
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-12
---
# Review de segurança: v046 (E20.4, PR-HOOK-PRAZO)

Diff revisado: `origin/develop...4ae51318` (bin/forge-check, hooks/_comum.py, hooks/parecer.py, tests/apoio_volta_unica.py, bin/forge-testes, fixtures, mutantes e tests/test_pr_hook_prazo.py). O `forge-check pr` grava o resultado por head em `<diretório comum do git>/forge/pr/<head>/` e o hook `parecer` passa a liberar o `gh pr create` lendo o aprovado do mesmo head, branch e base.

## Gatilhos
Controle do Forge (hook `parecer`, `R-REVIEW`) e estado lido por hook fora da árvore versionada.

## Achados
- A1 (recomendado) bin/forge-check:1537 · o registro não diz quem o gravou: o `bin/forge-check` de uma branch em obra (no clone do Forge) grava aprovado que o hook, com o forge-check vigente, aceita; gravar o sha256 do próprio forge-check e o hook exigir o do PLUGIN
- A2 (recomendado) hooks/conformidade.py:951 · escrita com `$(git rev-parse --git-common-dir)/forge/pr/...` ou variável da linha (`d=.../.git; cp x $d/forge/...`) passa: o resto depois de `$(…)` é resolvido na raiz da cópia, não no diretório comum; já existia, e agora forja o aprovado que libera o gh pr create

## Sondas
- S1 · hook conformidade, papel tech-lead, Bash `cat > "$(git rev-parse --git-common-dir)/forge/pr/a.json" < x` · espera: rc 2 (.git/forge/ protegido) · obtido: rc 0
- S2 · hook conformidade, papel tech-lead, Bash `d=/workspaces/Forge/.git; cp x $d/forge/pr/a.json` · espera: rc 2 · obtido: rc 0
- S3 · hook conformidade, papel tech-lead, Write em `<comum>/forge/pr/<head>/a.json` (caminho literal) · espera: rc 2 · obtido: rc 2 (R-CONFORMIDADE, marca de sessão)

## Detalhe dos achados
Respostas às perguntas do brief:
- **Fora do repositório?** Sim: `pasta_dos_resultados` (bin/forge-check:1520) usa `--git-common-dir` absoluto, dentro do `.git/` comum às worktrees, nunca na árvore versionada; o head precisa casar `SHA40` antes de virar caminho (sem travessia).
- **Quem escreve e lê:** escreve qualquer processo que rode `forge-check pr` sem `--previo` nem `--pr` e com a ref numa branch (bin/forge-check:9444); lê só o hook no `gh pr create` (hooks/parecer.py:602). A pasta folha nasce com 0o700, os pais e o arquivo com o umask; a troca por `os.replace` é atômica. Num computador de um só usuário, informativo.
- **Envenenamento:** head forjado não serve (a pasta é por head e o registro precisa trazer o mesmo head, a mesma branch e o mesmo `base_sha`, bin/forge-check:1568); cache de outro repositório não serve (o diretório comum é do repositório da raiz; worktrees do mesmo repositório compartilham, como devem). Registro ilegível, malformado ou de outra base vira `ausente`, que recusa. Os dois caminhos restantes são A1 e A2.
- **O contorno do prazo libera um PR que devia ser barrado?** Não. `ausente` roda a conferência de hoje só para dar o motivo e recusa mesmo sem violação (hooks/parecer.py:578); `reprovado` recusa (hooks/parecer.py:562); o prazo vencido continua recusando a chamada crítica em sessão vigiada, só com outro "Corrigir" (hooks/_comum.py:2784). O `gh pr merge` e o `gh pr ready` seguem refazendo a conferência sem cache.

**A1** · evidência bin/forge-check:1537 (registro sem autor) e hooks/parecer.py:559 (aceita o registro) · caminho de ataque: no clone do Forge, o tech-lead que mexe em `bin/forge-check` na branch (por engano ou para destravar) roda `bin/forge-check pr <pedido> --ref <branch> --base develop` da worktree; a versão da branch grava aprovado no `.git/` comum e o hook, que antes refazia a conferência com o forge-check vigente, aceita. O mesmo vale para o registro de uma versão vigente anterior, mais frouxa. Ganho: PR fora do rascunho sem os pareceres; o merge refaz a conferência e barra · severidade baixa · correção mínima: gravar no registro `escritor: sha256(<arquivo do forge-check que grava>)` e o hook só aceitar o registro com o sha256 de `PLUGIN/bin/forge-check` · esforço P · dono tech-lead.

**A2** · evidência hooks/conformidade.py:951 (`alvos_da_escrita` resolve o resto depois de `$(…)` na raiz da cópia) e hooks/conformidade.json (`.git/forge/` e `.git/`, quem: nenhum) · caminho de ataque: o agente grava o JSON aprovado com `$(git rev-parse --git-common-dir)/forge/pr/<head>/x.json` ou com uma variável definida na linha (S1, S2); o hook não reconhece o `.git/` e libera; a escrita não deixa rastro no git. A mesma forma alcança `.git/config` e `.git/hooks/` (sondado com rc 0; o sandbox do Bash protege o `.git/config` à parte). Já existia antes desta branch (hooks/conformidade.py igual na develop); esta entrega só torna o `.git/forge/pr/` um ponto de confiança. Ganho igual ao de A1 · severidade média para o hook de conformidade, baixa para esta entrega · correção mínima: com `$(…)` ou variável no caminho de escrita, somar como alvo o mesmo resto resolvido a partir do diretório comum do git (como `pastas_do_curinga` já faz) e conferir contra os protegidos `.git/forge/`, `.git/`, `.git/config`, `.git/hooks/`, `.git` · esforço P · dono tech-lead (cartão separado, fora desta branch).

Nenhum dos dois bloqueia: a decisão do dono (pedido v046, E20) aceitou o cache para o `gh pr create`; o merge, o `gh pr ready` e o CI continuam conferindo sem cache, e no clone do Forge o `gh pr create --draft` já passava sem parecer.

## Riscos aceitos e ferramentas
Sem risco aceito. Testes rodados: `python3 -m unittest tests.test_pr_hook_prazo` (15 testes, OK, 49 s); o resto da suíte fica com o CI do PR. Sondas S1 a S3 rodadas contra `hooks/conformidade.py` do head, com entrada JSON no stdin. Ferramentas da skill fora do PATH (lacuna): gitleaks, semgrep, zizmor, actionlint, osv-scanner; nenhuma é necessária a este diff (sem workflow, dependência nem segredo).
