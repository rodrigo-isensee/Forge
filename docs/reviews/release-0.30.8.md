---
tipo: review
contrato: 1
pedido: release-0.30.8
branch: melhoria/release-0.30.8-fecha
commit: 9f4cc095249ec158b49e520d9a13a42b336bc60f
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-31
---
# Review: release-0.30.8

Escopo: a leva da 0.30.8 contra a main, `git diff 6c17ca7...57baeb6` (22 commits, PRs #373 a #398, todos `MERGED` na develop), 148 arquivos, +5919 −147. Li o diff de código inteiro (`bin/forge-check`, `bin/forge-fechar`, `bin/forge-mutante`, `bin/forge-testes`, `hooks/_comum.py`, `hooks/parecer.py`, `.githooks/pre-push`, `scripts/promover-homolog.py`), os textos de agentes, regras e skills por amostra e o `tests/config.json`; corpus, fixtures e specs de mutante pela lista. Cada PR da leva já teve review, QA e, quando havia gatilho, segurança próprios; este parecer julga o conjunto e o commit de release, sem refazer o que eles provaram.

## Achados
- A1 (recomendado) docs/engineering/achados-recorrentes.md:18 · AR-4 (teste herda o ambiente) voltou duas vezes na leva (tests/test_fechar_orfao.py:99, tests/test_esperar_estado.py:68) e a contagem segue em 2; grave vezes: 4 no próximo PR de processo (este brief só toca o parecer).
- A2 (recomendado) tests/test_atualizar.py:889 · fora da leva: o pre-push desta branch caiu 2 vezes em testes de tempo sob carga (este, download falso; e test_hooks_volta_propriedades.py:175, 10,06 s contra 10 s) e ambos passaram isolados; vale cartão para folga ou relógio falso.
- A3 (recomendado) bin/forge-fechar:415 · segue em aberto o A1 do review worktree-orfas: saída vazia do prune grava um registro `[prune] ` sem texto no log; só cosmético.
- A4 (recomendado) bin/forge-check:4358 · seguem em cartão os A1 a A4 do review pn4-decisao-aprovacao (conferencias.md só da --raiz, guarda `len(c) >= 6` sem teste, texto do conferente sem o aviso novo, comparação no minuto); todos falham para o lado cobrado.
- A5 (recomendado) hooks/_comum.py:1457 · seguem no cartão HOOK-SAIDA-CODIGO os A5, A6 e A9 da segurança pn7-dolar-interrog (`"$?"` levado a código por `| sh` ou por caminho montado com IFS); lacuna antiga do caminho montado, sem capacidade nova.

## Parecer
Aprovado. Nenhum defeito provado, requisito descumprido nem achado de segurança com gatilho no conjunto; os cinco achados são recomendações já rastreadas ou de processo e não devolvem (`R-REVIEW`).

- **Release (57baeb6):** versão 0.30.8 em `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json`, conforme a decisão do dono de 2026-10-30 15:11. A seção `[0.30.8] - 2026-10-31` tem 21 entradas, uma por fragmento que o commit apaga (21, conferido com `grep -xF` linha a linha contra `57baeb6^`, ok=21, sem falta nem duplicata); `[Não publicado]` vazio e `changelog.d/` ausente. `scripts/conferir-release.py --base origin/main`: `ok: changelog.d/ sem fragmentos pendentes`, `versão base: 0.30.7 | versão da release: 0.30.8`. O escopo bate com P-REL-0308-ESCOPO (A): #390, #392, #394 e #397 estão na leva.
- **Afrouxamentos:** os PRs #375, #376, #380, #384, #389, #395 e #397 levam o rótulo `afrouxa-regra` (lido do `gh pr view`); o de maior alcance é o #384 (P-N7, `"$?"` entre aspas duplas nos hooks `conformidade` e `parecer`), com emenda H1-1 na ADR 0011, critério de reversão e corpus próprio de bloqueia e libera; fora de aspas e com marcador crítico o `$?` segue recusado. O `tests/config.json` só acrescenta invariantes (painel Aguardando o dono, R-WIP, R-DECISAO); nenhum sai.
- **Coerência entre PRs:** o hook `parecer` e o `forge-check pr` passam a ler a mesma base pela função `base_do_delta` (K-164); a base fora do fluxo cai no modo estrito nos dois, com fixture que bloqueia. `veredito_do_desde` é a regra única do `entrega` e do `gerar --volta` (P-N1 e P-N6 se compõem sem divergência). O `promover-homolog.py` roda o `forge-check pr release-<versão> --base main` só quando a versão muda, e é ele que exige este parecer (P-N3). A ordem pedida no review impl-pre-push (c6 antes ou junto da c4) está cumprida: o #397 entrou nesta leva.
- **Teto M14 e um comportamento por PR:** julgados nos reviews de cada PR; nenhum parecer da leva ficou reprovado, e os bloqueantes registrados (k164-mesma-base A1, pn3-pr-contra-main A1) constam resolvidos com mutante que morre.
- **Ferramentas citadas, não refeitas:** `python3 -m unittest tests.test_changelog` OK (46 testes); `bin/forge-check docs` rc 0. O pre-push desta branch rodou a suíte inteira em 4 processos (2330 testes): duas tentativas caíram por um teste de tempo fora do diff cada (A2), ambos verdes isolados; a terceira passou. O review não reexecutou mutação nem shellcheck: estão nos QA de cada PR e no CI.
- **Neutralidade e custo:** nenhum termo de projeto ou de stack nos textos novos de agentes, skills e modelos; nada novo consome serviço pago (`R-NEUTRO`, `R-CUSTO`).
- **Devops:** a leva não toca `.github/`, contêiner nem IaC; sem parecer de devops. Segurança e QA da leva têm parecer próprio, em paralelo (`R-SEGURANCA`, `R-QA`).

## Revalidação no head 9f4cc09 (volta por delta)
- **Delta lido:** `forge-check delta --parecer docs/reviews/release-0.30.8.md` listou o intervalo `57baeb6..9f4cc09` e só `CHANGELOG.md` +1 (linha 24, `pareceres de review, segurança e QA da leva da 0.30.8`, na seção `[0.30.8]`); li essa linha. Do fragmento `changelog.d/release-0.30.8.md` (PR #399, duas linhas removidas), li o diff: a linha movida é a mesma do CHANGELOG, e `changelog.d/` fica ausente.
- **Já lido:** todo o código da leva (parecer anterior); os pareceres de segurança e QA em `docs/` não são do meu escopo. Nenhum arquivo de código, teste ou hook mudou entre os dois commits.
- **M14:** `git diff --numstat --no-renames origin/develop...HEAD` dá `1 0 CHANGELOG.md` e `0 2 changelog.d/release-0.30.8.md`; nenhum arquivo de código ou teste, 0 linhas contáveis, um só comportamento (fechar o fragmento no CHANGELOG). A branch cumpre a M14.
- **Achados A1 a A5:** inalterados, seguem recomendados; o parecer continua aprovado.
