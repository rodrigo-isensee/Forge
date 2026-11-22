---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-trilha-forge-check
commit: 06ab19882f2550d175dbd077d85d02f0d2d1d16c
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-21
---
# Review: v0478 E91.15 (TRILHA-FORGE-CHECK, revalidação)

Delta lido (E91.15): `forge-check parecer delta` de d2f79996..06ab1988, sem o que veio da develop 27169ed1 (merge ce5b60de); no domínio só `tests/mutantes/v0479-trilha-forge-check-2.json`. O `para` do M7 passou a `f"origin/{'develop'}"`: a mutação é a mesma (ignora a `base` dada), agora dentro do nó `base or 'develop'` que a catraca exige. `forge-mutante --ids M7`: morreu em bin/forge-check:466. `--cobertura --base 27169ed1`: :466 coberta pelo M7. Sem achado novo; o aprovado abaixo segue.

Escopo: delta 95994eec..d2f79996 lido por `forge-check parecer delta` (bin/forge-check, changelog.d, specs revisor-wt-e6a-1, revisor-wt-e6a-4 e -3, test_revisor_wt). H1: o item soma 79 linhas de código desde o Base-sha 15936278 (`bin/forge-check` 62+15, `bin/forge-testes` 1+1); a volta tem 25+13. Dentro do teto.

## Parecer
Aprovado. O A1 da segurança foi atacado na causa: `de_outra_branch` não decide mais pelo nome do arquivo.

- `de_outra_branch` (bin/forge-check:2428): só pula a linha quando cada parecer citado existe na `ref` ou numa base do fluxo e, em todas onde existe, tem `branch:` diferente. Ausente, sem frontmatter, `branch:` igual em qualquer ref, subpasta ou prefixo forjado (contagem de citações contra ocorrências da pasta) mantêm a falha fechada. `blob_de` usa `--end-of-options`; o `cat-file` só roda nas refs onde o blob existe.
- A ref chega aos três chamadores: `pr` (`ref or "HEAD"`, :2012), `entrega` (`head`, :3372) e a volta (`conferidos_fora_da_ref`, :2466).
- Teste: o caso final troca o HEAD para outra branch com `p1.md` de `branch: melhoria/outra` e o `pr --ref melhoria/x` segue acusando; é o que mata o M20. Os casos S1 a S4 estão cobertos um a um.
- Realinhamentos: M6 (e6a-1) e M3 (e6a-4) trocam só o texto do `de`/`para` para a nova assinatura; a mutação é a mesma e o teste apontado é o mesmo. Os dois morreram. As specs da -3 passaram de classe inteira para o teste exato, o que estreita sem enfraquecer: todos morrem com ele.
- `forge-mutante --conferir`: a única recusa é revisor-wt-e6a-1 M2 ("o trecho aparece 2 vezes"). O trecho já aparece 2 vezes no Base-sha 15936278, na origin/develop e em 95994eec (vem de a59e1539 e a95cd2d0); o código novo usa `(raiz, r, nome)`, outro texto. Não é deste item.

Verificação: `PrLeParecerConferido`: 9 OK. Spec -3: M13 a M20 morreram; M6 (e6a-1) e M3 (e6a-4) morreram. `--cobertura --base 95994eec`: as guardas 2434, 2438, 2439, 2441 e 2454 estão cobertas. Suíte completa: CI do PR.
