---
tipo: revisao-seguranca
contrato: 1
pedido: release-0.27.0
branch: melhoria/release-0.27.0
commit: 23ecec1054c2b946d22eaa934c05c93996a92945
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-21
---
# Review de segurança: release-0.27.0

## Gatilhos
Controles do Forge (`R-SEGURANCA`) que a leva mudou, de 0f480c8 (0.26.0) a 10c838f: `tests/catraca.py` (S-16-PROMOCAO-DEVELOP #250), `bin/forge-check` (FORGE-CHECK-LOTE #252), `hooks/conformidade.json` (CONF-SO-LEITURA-FIX #253) e `.github/workflows/ci.yml` (CI-POSTINSTALL-CLI #251). TEXTOS-A1 (#249) mexe em texto de regra e em testes do hook do aq. O commit 23ecec1 só muda a versão nos dois `plugin.json`, o `CHANGELOG.md` e apaga os fragmentos de `changelog.d/`; não tem código.

## Achados

## Detalhe dos achados
Veredito: aprovado. Nenhum bloqueante na leva, e os cinco pareceres da leva estão `aprovado` com o bloco `## Achados` vazio (docs/security/textos-a1.md, s-16-promocao-develop.md, forge-check-lote.md, ci-postinstall-cli.md, conf-so-leitura-fix.md).

**O que entrou é o que foi revisado.** Para cada PR, comparei por `git patch-id --stable` o patch do commit revisado (sobre o merge-base) com o patch mesclado na develop (M^1..M). Comparei os controles (`tests/catraca.py`, `bin/forge-check`, `hooks/conformidade.json`, `hooks/conformidade.py`, `hooks/parecer.py`, `.github/workflows`, `tests/test_catraca.py`, `agents/conferente.md`, `docs/regras`) e, à parte, todo o patch fora de `docs/`. Os pares b9a8d75→2960f1a, f804072→6ec81e1, b69dbe9→4c0ba8a, d346475→f911dfa e f3d68cb→10c838f batem nas duas comparações. O parecer do lote aponta 9c09ae0: o patch dos controles dele é igual ao de b69dbe9 (8431ad0b), e 9c09ae0..b69dbe9 só muda pareceres e um literal em `tests/test_forge.py`.

**As mudanças juntas não abrem caminho novo.**
- **Catraca (S-16 com squash).** O caminho novo (tests/catraca.py:747, `prova_do_squash`) só roda depois que o caminho por ancestralidade falhou e exige mais provas: M com um pai, na cadeia de primeiro pai de base..head, `head.sha` como SHA completo, ref trazido igual a ele, S ancestral dele e o mesmo arquivo em M e em S (tests/catraca.py:825), além do mesmo arquivo no head. O fetch (tests/catraca.py:732) escreve só em `refs/catraca/pull/<n>`, sem tags, submódulos nem FETCH_HEAD, com manutenção desligada; erro do git, prazo estourado e `HTTPException` valem como sem rótulo (tests/catraca.py:629 e :834). O caminho segue atrás da guarda `custo` (tests/catraca.py:981), então `R-CUSTO` e o diff que falha continuam fora dele.
- **A catraca usa o `bin/forge-check` da base.** `tests/catraca.py:861-864` carrega o `forge-check` ao lado do script, e o workflow roda o script da worktree da base (.github/workflows/catraca.yml:40-44). O lote do `forge-check` não muda a catraca da promoção em que ele próprio entra.
- **Conferente só de leitura (CONF-SO-LEITURA-FIX) com os subcomandos novos do lote.** A lista `so_leitura.comandos` (hooks/conformidade.json:89) libera `forge-check pr|docs|brief|entrega|delta`. Os acréscimos do lote nesses subcomandos (`brief gerar --volta --incluir`, `entrega --brief`, a etapa `seguranca`) só leem e imprimem na saída padrão. Os únicos pontos do `bin/forge-check` que gravam arquivo são `movimento`, `conferencia registrar` e `transcricao anonimizar`, fora da lista. A opção que grava continua barrada pelo nome (hooks/conformidade.py:189). Com a correção, a regra passa a valer também na sessão do Forge, onde antes o conferente não tinha restrição: só aperta.
- **CI (`--allow-scripts`).** `.github/workflows/ci.yml:120` libera o postinstall de um pacote nomeado e de versão fixa, o mesmo que o passo já instalava. Nenhum `if:` nem passo da bateria muda, e `permissions` e segredos ficam iguais. O residual (código do fornecedor no runner) é o do parecer ci-postinstall-cli e não pede nada.
- **TEXTOS-A1.** A linha de `R-FLUXO` só ganhou a origem remota da base da trava, o que aperta. Os casos novos do hook do aq só acrescentam testes que esperam bloqueio.

**Informativa: a promoção desta leva roda a catraca da base.** A homolog está em 8e9c6bb (0.26.0), sem o caminho do squash. Por isso, os PRs develop → homolog e homolog → main desta leva mudam `tests/catraca.py`, `bin/forge-check` e `hooks/conformidade.json`, e só passam com o rótulo do dono posto no próprio PR de promoção. Isso só afeta a disponibilidade, fica do lado restritivo e não pede nada.

**Recomendações pendentes (não bloqueiam), com os cartões a conferir pelo Jarvis.**
- **S-16-PROMOCAO-DEVELOP.**
  - R1 é informativa: o motivo da isenção em tests/test_ambiente_git.py:29-32 ficou desatualizado.
  - R2 é baixa: a checagem de SHA completo em S. Não tem caminho de ataque, porque só o GitHub escreve o campo.
  - R3 é a A1 do parecer s-16, que segue aberta.
  - Se R1 e R2 não estiverem no KANBAN, o Jarvis deve registrar um cartão para cada uma.
- **FORGE-CHECK-LOTE.**
  - R1 (baixa): falha aberta do filtro do E4 quando o `git diff` falha (bin/forge-check, `nomes_do_intervalo`). É a de maior peso da leva e merece cartão próprio.
  - R2 (baixa): o `grep` de reserva do conferente.
  - R3 a R5 são informativas.
  - A R4 cabe no cartão CONF-ANEXO-PARALELO.
- **CONF-SO-LEITURA-FIX.** GREP-OPCOES-EXEC (`grep` com opções que executam programa) segue em cartão próprio.
- **TEXTOS-A1.** ROTEIRO-CLONE-ORIGEM já foi aberto pelo QA.
- **CI-POSTINSTALL-CLI.** Ao subir a versão do pacote, revisar o script de instalação. Não precisa de cartão.

**Sem rede paga (`R-CUSTO`).** A única rede nova da leva é o `git fetch` anônimo do `origin` na catraca, e as GET à API do GitHub com o token do próprio run já existiam. O `bin/forge-check` e o hook não ganharam rede. O passo do CI instala o mesmo pacote público de antes.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas usadas: `git` (diff, patch-id, show, merge-base) e leitura estática. Não rodei a suíte nem `tests.test_catraca` nesta revisão, porque o `.githooks/pre-push --status` mostrava a suíte de outro revisor rodando (R-TETO). As provas por mutação ficam as dos pareceres de cada PR, e os patches batem com o que foi revisado. Não estão no PATH: `gitleaks`, `zizmor`, `actionlint`, `semgrep`, `osv-scanner` e `trivy`. Essa lacuna está registrada. Do lado de workflow, a leva só muda uma linha de `ci.yml`, e as varreduras ficam no CI.
