---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-bp12-dado-real
commit: 0fedb7b6886125f54f600c9d1f569005621f4a1a
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-23
---
# Review: v0478 (E144.7, BP12, PR #832, revalidação)

## Delta lido
`forge-check parecer delta docs/reviews/v0480-bp12-dado-real.md`: intervalo `82277931..0fedb7b6`, no domínio só `skills/ux-design/SKILL.md` (volta E144.6, A1 da segurança). Os commits de parecer do QA e da segurança ficam fora do domínio.

## A volta
- Empatizar: "prova de dado real antes de painel simulado" vira "prova de dado real ou amostra anonimizada antes de painel simulado". Alinha a skill à constituição do modelo e fecha o A1 da segurança (nada de dado pessoal real gravado em `docs/ux`).

## Os quatro trechos encurtados
1. Idear: "(esboço em texto ou ASCII)" vira "(esboço em texto)". Esboço ASCII é texto; o mínimo (3 alternativas, prós, contras, esforço, matriz, escolha) ficou. Nada perdido.
2. Prototipar: "sem build e sem dependências externas" vira "sem build nem dependência externa". Mesma proibição, singular genérico. Nada perdido.
3. Regras: "marcada como hipótese" vira "marcada como tal". O referente é "Hipótese" no início da frase; a regra é a mesma.
4. Necessidades de dados: "precisa ler/gravar" vira "lê e grava". A seção segue pedindo o que a tela lê e grava para o back-end. Nada perdido.

Nenhum dos textos removidos é procurado por `invariantes` ou por teste (grep em `tests/`, `agents/`, `skills/`, `templates/`, `docs/regras/`).

## Testes e CI
- Rodados no clone, só os dos arquivos tocados: `tests.test_metricas_texto` (2, OK; skill com 5265 caracteres, antes 5268, teto sem alteração) e `tests.test_forge -k ux -k constituicao -k Neutralidade -k metricas -k nvariante` (21, OK).
- CI do PR #832 no head 0fedb7b6, na hora da leitura: catraca, baterias e instalação verdes; partes da suíte pendentes. A suíte completa é do CI e não foi rerrodada aqui.

## Commits
Um commit, Conventional Commits em português, mensagem com o motivo (A1 da segurança) e o encurtamento para caber no orçamento. Só documentação, dentro do H1; sem guarda, sem mutante.
