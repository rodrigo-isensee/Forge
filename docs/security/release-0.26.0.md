---
tipo: revisao-seguranca
contrato: 1
pedido: release-0.26.0
branch: melhoria/release-0.26.0
commit: 998fdd5115212ef7ad892c0874574d859f60703c
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-20
---
# Review de segurança: release-0.26.0

## Gatilhos
Controles do Forge (`R-SEGURANCA`) que a leva mudou, de 74e5bb7 (0.25.0) a a4d2eac: `tests/catraca.py` (S-16 #242 e CATRACA-ENDURECER #244), `bin/forge-check` (CONF-CORRECAO #245) e `bin/forge-fechar` (FECHAR-ESTAVEL #243). O commit 998fdd5 só muda a versão nos dois `plugin.json`, o `CHANGELOG.md` e os fragmentos apagados de `changelog.d/`.

## Achados

## Detalhe dos achados
Veredito: aprovado. Nenhum bloqueante na leva, e nenhum dos quatro pareceres deixou bloqueante aberto.

**O que entrou é o que foi revisado.** Para cada PR, comparei por `git patch-id --stable` o patch do commit revisado (sobre o seu merge-base) com o patch do squash na develop (M^1..M). Comparei `tests/catraca.py`, `bin/forge-check`, `bin/forge-fechar`, `hooks/conformidade.json` e `.github/pull_request_template.md`. Os pares foram eb16bb2→ef71b3c, 6a1f2b3→bd8b696, 568757c→7556bca e fb5028e→a4d2eac. Os patches batem nos quatro. Os quatro pareceres estão `aprovado` e têm o bloco `## Achados` vazio (docs/security/s-16.md, docs/security/fechar-estavel.md, docs/security/catraca-endurecer.md, docs/security/conf-correcao.md).

**A S-16 junto com a CATRACA-ENDURECER não abre caminho novo.**
- **Diff que falha não chega ao caminho do PR mesclado.** O rótulo não libera violação de diff, e a guarda `custo` (tests/catraca.py:911) fecha os três caminhos de liberação. Um deles é o `liberado_por_pr_mesclado` (tests/catraca.py:921-926). Há também uma segunda trava: `arquivo_da_violacao` devolve None para a mensagem de diff, e `None in arquivos` recusa (tests/catraca.py:760-761).
- **Um diff que falha dentro da S-16 não falha aberto.** Isso cobre o `regra_protegidos` sobre o head rotulado S (tests/catraca.py:773). O `ErroDeDiff` escapa até `main`, que o captura e sai com rc 1 (tests/catraca.py:870-876).
- **As outras falhas também não liberam.** Se o `git log` dos candidatos falha, a lista sai vazia e nada é liberado (tests/catraca.py:709-710). Se `base_efetiva` falha, ela devolve a própria ref (tests/catraca.py:103-105). O pior caso é `de_s` vazio, e então nenhum arquivo fica coberto.
- **Ordem dos caminhos.** O caminho por conteúdo (`rotulo_vale_pelo_conteudo`) roda antes. Um diff que falha nele também sai com rc 1 antes da S-16, que é o lado restritivo (recomendação 1 da CATRACA-ENDURECER).
- **`scripts/conferir-release.py` em `PROTEGIDOS`.** Com a S-16, uma mudança nesse arquivo só passa se o mesmo blob foi rotulado pelo dono num PR mesclado. A violação conta o arquivo como protegido no S segundo a lista do script da base, que a CI roda (.github/workflows/catraca.yml:40-43). Isso só aperta.
- **Sonda.** Rodei `python3 -m unittest tests.test_catraca` numa cópia de 998fdd5 por `git archive` em `$TMPDIR`: 161 testes, OK. Cobrem o caso `test_git_diff_com_erro_vira_violacao` e os casos da S-16, com o rótulo que não libera o diff falho (tests/test_catraca.py:439-470 e 1196-1203).

**As outras combinações também não abrem caminho.**
- **FECHAR-ESTAVEL.** O `bin/forge-fechar` só fecha para a develop. Os atalhos de "já mesclado" não mesclam nada, e o merge segue preso ao head conferido. Ele não interage com o caminho de promoção da S-16.
- **CONF-CORRECAO.** O diff do `bin/forge-check` não toca a catraca nem a lista `PROTEGIDOS`. Ele só lê arquivos locais e imprime.
- **`.github/pull_request_template.md`.** O item do rótulo não libera nada, porque a catraca não o lê.

**Recomendações pendentes e cartões.**
- **S-16.**
  - R1 (prazo total e `IncompleteRead`): cartão CATRACA-PRAZO-API, no KANBAN.
  - Teste de "continua pedindo" para as chaves: cartão S16-TESTE-CHAVES, no KANBAN.
  - R2 é informativa e já está registrada em docs/adr/0008-governanca-de-contribuicoes.md.
- **FECHAR-ESTAVEL.**
  - R1 (o passo 6 prende o MERGED ao número do PR e ao `headRefOid`): cartão FECHAR-MERGED-HEAD, no KANBAN.
  - R2 e R3 são informativas.
- **CONF-CORRECAO.**
  - R1 (Cc, Cf, Zl e Zp nos campos do cabeçalho): cartão CABECALHO-RECUSA-TODOS.
  - A mensagem de recusa do campo tem o cartão FC-RECUSA-CAMPO-TEXTO.
  - **A R2 (baixa, ordem das raízes do registro citado no layout do Forge, bin/forge-check:2747) não tem cartão.** O Jarvis deve registrar um, por exemplo REGISTRO-RAIZ-FORGE.
  - R3 é informativa.
- **CATRACA-ENDURECER.** As recomendações 1 a 3 são informativas e não têm cartão. Vale registrar a 2 (manter o teste que prende a ordem `regra_arquivos_de_regras` antes de `regra_protegidos`), por exemplo CATRACA-ORDEM-TESTE. Nenhuma delas tem caminho de ataque.
- **Release 0.25.0.** As lacunas de cartão que o parecer anterior apontou foram fechadas: TRAVA-MODO-SUBPASTA, DV5-R2-FETCH, FECHAR-R1-DOC-REGRA e FC-AQ-TESTES-EXTRA estão no KANBAN. A R1 (CONFERIR-RELEASE-PROTEGIDO) foi cumprida nesta leva (tests/catraca.py:40-41).

**Informativa: as promoções desta leva rodam a catraca da base.** A catraca roda o script da base (.github/workflows/catraca.yml:40-43), e a homolog e a main ainda têm a catraca da 0.25.0, sem a S-16. Por isso, os PRs develop → homolog e homolog → main desta leva, que mudam `tests/catraca.py` e `bin/forge-check`, só passam com o rótulo do dono posto no próprio PR de promoção. Isso só afeta a disponibilidade, fica do lado restritivo e não pede nada.

**Sem rede paga (`R-CUSTO`).** O `bin/forge-check` e o `bin/forge-fechar` não importam módulo de rede nem chamam URL. O `grep` por `urllib`, `http.client`, `requests`, `curl` e `wget` não achou nada. As únicas chamadas novas da leva são as GET da S-16 a `api.github.com`, com o `GITHUB_TOKEN` do próprio run, que são gratuitas. O commit 998fdd5 não tem código.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: `git` (diff, patch-id, archive) e `python3 -m unittest`. Não estão no PATH: `gitleaks`, `zizmor`, `actionlint`, `semgrep` e `osv-scanner`. Essa lacuna está registrada. A leva não muda workflow nem dependência, e as varreduras ficam no CI.
