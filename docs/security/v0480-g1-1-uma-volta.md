---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-g1-1-uma-volta
commit: e103b9a634e630e698b5b78e046bee553eec7cd6
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-22
---
# Review de segurança: v0478 E100.16 (G1.1, revalidação da terceira volta)

Revalidação por delta (DECISÃO DO DONO 22/11 06:07, mais uma volta). A rodada anterior (E100.11, `4d2c5333`, aprovado) fica no git.

Delta lido: `forge-check parecer delta docs/security/v0480-g1-1-uma-volta.md`, intervalo `4d2c5333..e103b9a6`. No domínio só `bin/forge-check:4273`: sai o `bool(branch) and` da contagem em `voltas_da_branch`. Fora: specs de mutantes (`tests/mutantes/v0480-g1-1-uma-volta-2.json` e `-3.json`) e os pareceres de review e QA. Já lido e não relido: o resto do `bin/forge-check`.

Gatilhos: código de controle do Forge (`bin/forge-check`).

Suíte: não rodada aqui (só no CI; o PR ainda não existe). Rodei a classe `BriefDeVolta` (32 testes, com `test_s7_*` e `test_s8_*`): OK.

## Achados
- A1 (bloqueante) bin/forge-check:4247 · corrigido em rodada anterior; sem mudança no delta
- A2 (bloqueante) bin/forge-check:4278 · corrigido; sem mudança no delta; S7 e S8 seguem dando rc 1
- A3 (recomendado) bin/forge-check:4255 · aberto, sem mudança no delta: a autorização segue sendo uma linha que o Jarvis escreve (ADR 0018); falta declarar o limite no R-QA e na skill antes do merge

## Detalhe

**Delta (`:4273`), sem efeito de segurança.** Com `branch` vazio a comparação agora conta os briefs de volta sem `Branch:` (`None == None`), onde antes somava 0. Os dois chamadores já barram esse caso antes: `gerar_volta` (`:4317`) retorna rc 1 por `branch_do_anterior_diferente` sem chegar à contagem; `conferir_volta` (`:4451`) já anexa o achado bloqueante e, se contar mais voltas, só antecipa a recusa do teto (falha fechada). Não há caminho em que a remoção aumente o teto de voltas.

**A3, aberto (recomendado).** Mesma correção mínima: uma linha no `R-QA` e na skill `briefs-e-conferencia` dizendo que a autorização da volta é uma linha que o Jarvis escreve com a leitura dele (ADR 0018), ou o ato `volta-extra` nas concessões. Esforço P. Dono: autor da E100.9.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: o diff do delta e a classe `BriefDeVolta`. `gitleaks` e `semgrep` não estão no PATH (lacuna); o delta não tem segredo nem dependência.
