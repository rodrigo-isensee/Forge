---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-meta85-recomendado
commit: eba8b7d01c0dd892615d9846c97c8eeb17dd6f34
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-19
---
# Review de segurança: v0479-meta85-recomendado

Pedido v0478, etapa E35.9 (revalidação; a rodada anterior, E35.3 no commit `cdea2f38`, fica no git).

## Gatilhos
Gatilhos: controles do Forge (`docs/regras/R-REVIEW.md`, `docs/regras/R-SEGURANCA.md`)

## Detalhe
Delta lido: `forge-check parecer delta` no intervalo `cdea2f38..eba8b7d0`, no domínio `docs/regras/R-REVIEW.md`, `docs/regras/R-SEGURANCA.md`, `skills/briefs-e-conferencia/SKILL.md`, `skills/engineering-practices/rigor-por-classe.md` (novo), `skills/trabalho-em-paralelo/SKILL.md` e `ritmo-e-corte.md`.

Ponto central (decisão do dono E35, recomendado de segurança corrigido antes do merge): continua valendo. Em `docs/regras/R-SEGURANCA.md:17` e `docs/regras/R-REVIEW.md:16` o delta só parte a frase da evidência em duas; o destino do recomendado de segurança não muda (citado pelo ID, `R-SEGURANCA` e `R-REVIEW`). As invariantes de `R-REVIEW` em `tests/config.json` seguem presentes na fonte.

Movimentos sem efeito de segurança: a tabela T/N/C e a frase de como os gatilhos são achados saem da regra para `skills/engineering-practices/rigor-por-classe.md`, com o mesmo conteúdo; a lista de gatilhos de `R-SEGURANCA` fica inteira na regra, e a classe continua vindo de `forge-check classe`. Em `skills/briefs-e-conferencia/SKILL.md:24` o recomendado da segurança segue no brief de volta. As mudanças de `skills/trabalho-em-paralelo/` só deslocam a menção a `forge-copia clone --instalar`.

Achados anteriores: nenhum. Achados novos: nenhum.

Suíte: inteira só no CI; rodei `tests.test_forge.AntiDuplicacao.test_regra_so_na_fonte`, que reprovava este parecer por cópia de texto da regra, agora citada pelo ID.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Revisão estática do delta; sem segredo nem dependência nova.
