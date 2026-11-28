---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-g1-1-uma-volta
commit: 45d1fc2728a489d04950a6a304369f6f4f6e8fa5
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-22
---
# Review de segurança: v0478 E100.21 (G1.1, revalidação da quarta volta)

Revalidação por delta (DECISÃO DO DONO 22/11 07:23, mais uma volta). A rodada anterior (E100.16, `e103b9a6`, aprovado) fica no git.

Delta lido: `forge-check parecer delta docs/security/v0480-g1-1-uma-volta.md`, intervalo `e103b9a6..45d1fc27`. O `bin/forge-check` que a ferramenta lista no domínio veio todo da `develop` (merge `027af0c6`, que traz `a6d4d17e` #780, já ancestral de `origin/develop` `bfed8033`): o diff próprio da branch em `bin/forge-check` contra a base (`bfed8033..45d1fc27`) é idêntico, linha a linha, ao da rodada anterior (`2d73a35e..e103b9a6`). Commit próprio da volta (`45d1fc27`): só `tests/test_forge.py` e `tests/test_revisor_wt.py`, fora do domínio. **O domínio de segurança da branch não mudou.**

Gatilhos: código de controle do Forge (`bin/forge-check`).

Suíte: não rodada aqui (só no CI; o PR ainda não existe). Rodei as duas classes tocadas, `VoltaComRecomendacao` e `VoltaLeParecerConferido` (19 testes): OK.

## Achados
- A1 (bloqueante) bin/forge-check:4247 · corrigido em rodada anterior; sem mudança no delta
- A2 (bloqueante) bin/forge-check:4278 · corrigido; sem mudança no delta; S7 e S8 seguem dando rc 1
- A3 (recomendado) bin/forge-check:4255 · aberto, sem mudança no delta: a autorização segue sendo uma linha que o Jarvis escreve (ADR 0018); falta declarar o limite no R-QA e na skill antes do merge

## Detalhe

**Delta de testes, sem afrouxamento.** As duas mudanças ajustam o fixture ao G1.1 (o brief anterior ganha `Branch:`; a volta já conferida é apagada antes de regerar, para não suceder o anterior). Nenhuma asserção sai nem muda; a falha fechada do `SHA_FALSO` segue conferida nos dois lados.

**A3, aberto (recomendado).** Mesma correção mínima da rodada anterior: uma linha no `R-QA` e na skill `briefs-e-conferencia` dizendo que a autorização da volta é uma linha que o Jarvis escreve com a leitura dele (ADR 0018), ou o ato `volta-extra` nas concessões. Esforço P. Dono: autor da E100.9.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: o diff do delta, a comparação do diff próprio contra a base e as duas classes de teste. `gitleaks` e `semgrep` não estão no PATH (lacuna); o delta não tem segredo nem dependência.
