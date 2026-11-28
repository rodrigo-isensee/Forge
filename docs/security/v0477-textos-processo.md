---
tipo: revisao-seguranca
contrato: 1
pedido: v0477
branch: melhoria/v0477-textos-processo
commit: 447a4c8da0973a8fd04121d8a32032948e0a8570
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-18
---
# Review de segurança: v0477 (E2.3, textos de processo H8 e SIEG-G6)

Primeira rodada, leitura integral do diff `038249c5..447a4c8d` (4 arquivos, +6/-3).

## Gatilhos
Gatilhos: controles do Forge (docs/regras/R-LIMITES.md, texto de agente e skill)

## Achados

## Sondas

## Detalhe dos achados
- **H8 sem escape de portão.** `agents/tech-lead.md:21` só troca a contagem inline por ponteiro para `skills/engineering-practices/tamanho-por-item.md`, cuja seção H8 (linhas 20-25, já na develop desde #644) mantém: a classe decide (`forge-check classe`), segurança com gatilho (`R-SEGURANCA`), nenhum portão sai sem decisão do dono, e texto de skill/agente, `bin/` e `hooks/` são classe C, fora do caminho curto. O comando de contagem continua em `tamanho-por-item.md:10`. Esta própria branch prova o freio: `forge-check classe` deu C com review, segurança e QA no mesmo head.
- **SIEG-G6 sem escape.** `skills/trabalho-em-paralelo/ritmo-e-corte.md:16` agrupa item dependente na mesma branch ou lote; os portões do lote continuam valendo (linha 17: "nenhum portão cai"). Não abre caminho para entrar sem parecer.
- **R-LIMITES não afrouxa.** `docs/regras/R-LIMITES.md:44` troca "Vale também para" por "Vale para": o alcance (melhoria de fábrica vinda de qualquer projeto) e a exigência de autorização expressa do dono (`R-CUSTO`) ficam iguais; a frase não é invariante em `tests/config.json`, e os invariantes de `R-CUSTO` seguem presentes.
- `changelog.d/v0477-textos-processo.md`: só texto, em português.

Sem achados bloqueantes nem recomendações.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Rodados: `python3 -I tests/catraca.py --base origin/develop` (saída 0), `python3 -m unittest tests.test_metricas_texto` (OK, 2 testes), `forge-check classe` (C, gatilho R-LIMITES). Suíte inteira: no CI do PR. Ferramenta ausente no PATH: gitleaks (sem impacto: diff só de texto, sem segredo).
