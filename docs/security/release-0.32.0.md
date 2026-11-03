---
tipo: revisao-seguranca
contrato: 1
pedido: release-0.32.0
branch: melhoria/release-0.32.0
commit: 5e7f00387bd005269d11e99e5f80ab4e3c6bbf65
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-03
---
# Review de segurança: release-0.32.0

Etapa E1.3 do pedido release-0.32.0. Diff revisado: `5b6d13a...5e7f003` (main 0.31.0 até o commit de release), com os PRs #427 (HEREDOC-COMENTARIO), #428 (HEREDOC-DONOS), #429 (CI-SUITE-NO-TETO), #430 (LOTE-UNICO-032) e o commit de release 5e7f003. Veredito: **aprovado**, sem bloqueante.

## Gatilhos
`R-SEGURANCA`, gatilho `controles do Forge`: `hooks/_comum.py` e `hooks/conformidade.py` (#427, #428), `bin/forge-check`, `bin/forge-fechar`, `bin/forge-mutante`, `bin/forge-testes`, `scripts/suite-paralela.py` e `tests/config.json` (#430), e pipeline em `.github/workflows/ci.yml` (#429, #430). `.githooks/pre-push` não muda na leva (`git diff 5b6d13a 5e7f003 -- .githooks/` vazio).

## Achados
- A1 (recomendado) .github/workflows/ci.yml:107 · O gate do CI pula a bateria com commit só em `docs/ux/`; o `so_parecer` do pre-push (`.githooks/pre-push:225`) não a aceita. Sem caminho de ataque (só PR para a develop; a homolog roda tudo); alinhar as duas listas.
- A2 (recomendado) hooks/conformidade.py:747 · Continua aberto do heredoc-donos (A2): o contador de corpos pendentes só sobe depois de `tirar_heredocs`. Se o vigia vencer nessa janela, a linha sem marcador libera. Contar os `<<` antes fecha a janela.
- A3 (recomendado) hooks/_comum.py:1481 · Continua aberto do heredoc-donos (A1): `fronteira_limpa` não exige que a varredura de comentários atravesse o prefixo. Hoje não se alcança (o `citar` põe a substituição como `_`); exigir `varrer_comentarios(prefixo)[1] == len(prefixo)`.
- A4 (recomendado) bin/forge-check:1941 · Continua aberto do lote-unico-032 (A1): `fila` executa o `.githooks/pre-push` da raiz quando o texto traz a marca `--status`, que é só texto. Ler a trava com flock LOCK_NB em vez de executar o hook.
- A5 (recomendado) bin/forge-check:536 · Continua aberto do lote-unico-032 (A2): `gatilhos` casa `gatilhos_seguranca` só pelo pedido exato; casar pelo id e pelo slug.
- A6 (recomendado) bin/forge-mutante:684 · Continua aberto do lote-unico-032 (A3): `--processos K` não confere a trava da suíte; a regra C-33b está só no texto da skill qa-testing.
- A7 (recomendado) bin/forge-check:2058 · Continua aberto do lote-unico-032 (A4): o `custo total` soma `custo do trecho: N tokens` lido da célula inteira, motivo livre incluído. Ler só o sufixo que o `movimento` grava.

## Detalhe dos achados

### O que chega à main é o que foi revisado
Cada squash da develop tem, fora dos pareceres, a árvore do head que os portões do PR aprovaram:
- `git diff --stat d964f7c 032b4cb` (#427): só `docs/{qa,reviews,security}/heredoc-comentario.md`.
- `git diff --stat f16b60e 1b6f418` (#428): só os 3 pareceres heredoc-donos.
- `git diff --stat 1effb9e c6244ac` (#429): só os 4 pareceres ci-suite-no-teto.
- `git diff --stat cd93720 928e61b` (#430): só os 4 pareceres lote-unico-032.

O head revisado do #430 (`cd93720`) contém `c6244ac`. Por isso o conjunto final de código (hooks, CI, bin) foi revisado já integrado, e não PR a PR em separado. A main `5b6d13a` tem a mesma árvore que `b2580c6`, a base dos PRs (`git diff b2580c6 5b6d13a` vazio). O commit de release 5e7f003 só toca `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json` (0.31.0 para 0.32.0), o `CHANGELOG.md` e os 4 fragmentos de `changelog.d/` que ele apaga. Não toca nada de controle.

### Por controle
- **hooks/ (#427, #428):** o O(N²) com muitos donos distintos, que o parecer heredoc-comentario registrou como A1 (alta, pré-existente: liberação por prazo vencido com 1000 heredocs), é a classe que o #428 corrigiu. O `corpo_so_lido` passa a ser lido por partes com `fronteira_limpa`. O C-4 recusa com `corpos_pendentes > 0` no prazo vencido, mesmo sem marcador (`hooks/_comum.py`, `prazo_vencido`). A1 do heredoc-comentario: resolvido na leva. Os C-1 a C-6 e T1 a T6 dos dois modelos de ameaças foram conferidos nos pareceres de cada PR, com oráculo diferencial, e eu não os refiz. Restam A2 e A3 acima, como recomendações.
- **bin/forge-fechar (#430, L02 e L37):**
  - `trazer_a_base` só age em `melhoria/*`. Usa a árvore do `git merge-tree --write-tree` limpo e confere a árvore do commit criado. O `update-ref` leva o valor antigo, e a worktree avança por `--ff-only` com a árvore limpa. O envio é o `git push origin` de sempre, com o pre-push, sem `--force` nem `--no-verify`.
  - A cadeia recomeça com `--trazida`, o que limita a recursão a uma volta. Passar `--trazida` à mão só faz o 2b parar, então a falha é fechada.
  - Com conflito, o passo para e lista os arquivos. O merge da base não ganha passe: o `forge-check pr --base` só aceita o parecer cujo diff efetivo não mudou, e o CI do PR roda a bateria.
  - O reuso do rascunho exige um só PR aberto, sem fork, com a base igual ao alvo e o head igual ao conferido no passo 2.
- **bin/forge-check (#430):** os subcomandos novos (`decisoes`, `proximo`, `transcricao vereditos` e `recusas`, os relógios do `voltas`, o custo no `movimento`) só leem, e o texto lido sai por `sem_controle` e `nome_seguro`. O `movimento` passou a recusar coluna fora do KANBAN.md, o que só aperta. O `pr` ganhou a linha de veredito com rc 0 e manteve os mesmos exigidos (`exigidos_do_pr` foi extraído sem mudança). O L08 (`pedido_do_pr` sem brief e `escopo_pelo_primeiro_pai` com commit de um pai já na base) só troca o pedido quando um parecer da branch leva o slug. Nenhum exigido sai.
- **tests/config.json (#430, L35, L51):** conferi por conta própria contra a main. Os trechos de `invariantes` passaram de 365 para 369 e nenhum sumiu (os do Jarvis foram para as skills e para `docs/regras/R-BRIEF.md`). O `termos_proibidos_hash` está igual, e nenhuma chave existente mudou fora de `invariantes`. As chaves novas são `invariantes_motivo`, `invariantes_motivo_trecho` e `invariantes_sem_motivo` (o legado por trecho, com teto na soma, conferido no parecer do lote). Nada afrouxado.
- **.github/workflows/ci.yml (#429, #430):**
  - Os `timeout-minutes` passam de 10/15/15 para 20/25/25. Não muda nenhum `permissions:` nem `if:` de job, e as ações seguem fixadas por SHA.
  - O gate do commit só de parecer ganhou `docs/security/`, `docs/devops/` e `docs/ux/`. Os modelos `_*` e `docs/security/{ameacas,aceites}/` continuam rodando tudo, e o passo curto ganhou `NeutralidadeDoNucleo`. O gate só vale para PR com base develop e exige a bateria verde no commit anterior.
  - A divergência com o pre-push na pasta `docs/ux/` é o A1 deste parecer.
- **.githooks/pre-push:** sem mudança na leva.

### Versão minor (E3)
Nada na leva contraria uma minor. Nenhum subcomando, opção nem formato de parecer foi removido ou mudou de contrato. Os subcomandos e opções novos são aditivos, e o contrato dos pareceres continua o `contrato: 1`. A recusa nova do `movimento` (coluna fora do KANBAN.md) só aperta. O C-4 do hook recusa uma linha que antes liberava por prazo, o que é endurecimento de controle e não quebra o projeto. A mudança de `invariantes` é interna ao repositório do Forge. Quem já seguia o processo não é afetado.

### Achados recorrentes (PA-7)
Conferi AR-1 a AR-10 contra a leva:
- AR-3: o gate do CI e o `so_parecer` usam lista positiva de pastas, com as exceções rodando tudo.
- AR-5: não há caminho novo que chame `python` para decidir. O passo curto do CI já existia.
- AR-7: `trazer_a_base` usa o mesmo repositório que a worktree, cujos objetos são compartilhados.
- AR-10: não há texto isento executado. O único caso é o A4, aberto e recomendado.

AR-1, AR-2, AR-6, AR-8 e AR-9 ficam com o review e o QA e não têm ocorrência nova que eu tenha visto.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Fiz a revisão por leitura do diff, por comparação das árvores (head revisado contra squash) e por comparação dos `invariantes` com a main. Testes rodados (D-5, a carga da máquina estava em 10, então nada pesado): `tests.test_catraca.Workflows` e `tests.test_forge.RegrasInviolaveis`, 9 testes, OK. A bateria completa fica com o pre-push, o CI e o QA. Lacuna: `gitleaks`, `semgrep`, `osv-scanner`, `zizmor` e `actionlint` não estão no PATH. A leva não toca dependência nem segredo, e o CI roda `zizmor`, `actionlint` e a varredura de segredos.
