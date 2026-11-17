---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-parecer-seguranca-curto
commit: c2138efd8de14c9412bc8f6e6bced8187a8b5283
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-16
---
# Review de segurança: v047 (parecer de segurança curto; revalidação por delta, E2.378)

Escopo: volta por delta. A rodada anterior (head `02fe845d`, aprovada) fica no git. Delta lido: `forge-check parecer delta` no intervalo `02fe845d..c2138efd`, sem o que veio da develop; no domínio, só `agents/security-engineer.md` (commit `f60b080a`, enxugo para caber no teto de orçamento). O merge `c2138efd` só traz a develop.

## Gatilhos
Gatilhos: texto do agente do portão de segurança (`R-SEGURANCA`), com invariantes em `tests/config.json`; não toca `hooks/`, `bin/`, `.github/`, `docs/regras/`, dependência, segredo nem dado pessoal.

## Achados
- A1 (recomendado) bin/forge-check:3039 · Estado: aberto, sem mudança (o delta não toca bin/). O esqueleto do parecer ainda escreve a marca antiga em `## Gatilhos`, não a forma `Gatilhos: ...`. Dono: tech-lead.

## Sondas

## Detalhe dos achados
A1: igual à rodada anterior; consistência, sem caminho de ataque.

Delta conferido, sem achado novo (só redação; nenhuma obrigação de segurança some):
- Oráculo (EXT-1): sai "e nunca leva código de produção"; fica "num commit próprio que só toca esse arquivo", que é mais forte e já exclui código de produção.
- Ferramentas (`R-CUSTO`): saem "as varreduras rodam no CI" e "recurso pago fica fora"; os dois seguem na skill `cyber-security` (seção Ferramentas), que o agente carrega, e `R-CUSTO` segue citado.
- `R-CONFORMIDADE`, limite de workflow e matriz do analisador: frases encurtadas, mesmo conteúdo.
- Invariantes: os 15 de `agents/security-engineer.md` em `tests/config.json` casam no head (conferido por expressão regular).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Testes do item na raiz do clone, no head: `tests.test_achado_teto_doc` (4, OK) e `tests.test_forge.Orcamento` (2, OK; teto de tamanho dos prompts). A suíte inteira fica para o CI do PR. Sem varredura de segredos nem de dependências: o delta não toca nenhuma das duas.
