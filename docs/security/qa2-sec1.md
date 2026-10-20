---
tipo: revisao-seguranca
contrato: 1
pedido: qa2-sec1
branch: melhoria/qa2-sec1
commit: 1093bc1036069b2d5757750b6ad374da75e7c64e
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-20
---
# Review de segurança: qa2-sec1

Intervalo revisado: `bd204b8..1093bc1` (8862c1c texto de agentes e skills; 1093bc1 invariantes e fragmento). Os commits seguintes da branch (c734276, 5580bc2) só trazem `docs/reviews/qa2-sec1.md` e `docs/qa/qa2-sec1.md`, fora de controle do Forge.

## Gatilhos
- Controles do Forge (`R-SEGURANCA`): `tests/config.json`, lista `invariantes`. Não há mudança em hook, CI, `bin/forge-check` nem workflow.

## Achados

## Detalhe dos achados
Conferências feitas, sem achado bloqueante:

1. **Invariantes só entram.** O diff de `tests/config.json` (linhas 432-451) acrescenta 6 trechos e uma chave nova (`skills/cyber-security/SKILL.md`); as duas linhas com `-` só ganham vírgula (`` `R-QA` `` e `afirma um mínimo de itens` continuam, iguais). Nenhum trecho saiu nem foi trocado por outro mais fraco. A catraca (`python3 tests/catraca.py --base bd204b8 --head 1093bc1 --eventos <vazio>`) não listou violação. Cada um dos 13 trechos das três chaves tocadas casa exatamente uma vez no arquivo de destino, inclusive o escape `\*\*` em `tests/config.json:450`.
2. **QA não dá veredito antes do review.** `skills/qa-testing/SKILL.md:46` diz que o parecer sai só sobre o commit final e depois do review, com `R-REVIEW` e `R-QA` intactos; `agents/qa-engineer.md:13` repete e remete à seção. O que se antecipa é só a escrita do plano e dos testes; o plano nasce sem ler o código (`skills/qa-testing/SKILL.md:44`), o que preserva a independência.
3. **Parecer de segurança só no commit final.** `agents/security-engineer.md:18` e `agents/qa-engineer.md:28` dizem que o parecer de segurança continua sobre o commit final; a SEC-2 (parecer por etapa) ficou fora, como o dono decidiu.
4. **Casos de abuso continuam saindo da segurança.** `skills/cyber-security/SKILL.md:18` põe a lista no modelo de ameaças (`docs/security/ameacas/`, escrita do `security-engineer`), com entrada, caminho e resultado esperado; o QA só os transforma em teste, em arquivo seu (`agents/qa-engineer.md:13`, `skills/qa-testing/SKILL.md:47`), e continua sem declarar "seguro" (`agents/qa-engineer.md:28`). O QA não ganha escrita em `docs/security/`.

Recomendação (informativa, não bloqueante): o trecho que prende o parecer do QA depois do review está protegido por invariante na skill (`tests/config.json:447`, sobre `skills/qa-testing/SKILL.md:46`), mas não na frase equivalente de `agents/qa-engineer.md:13`. Caminho de risco: uma edição futura do agente poderia apagar "depois do review" sem o teste avisar, e o agente lê o próprio arquivo antes da skill. Severidade informativa, porque `R-REVIEW` e `R-QA` continuam protegidos pelas próprias regras e pela catraca. Correção mínima: invariante `depois do review` em `agents/qa-engineer.md`. Esforço P. Dono: `tech-lead`, em pedido futuro.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Revisão estática do diff, do texto e de `tests/config.json`; catraca local em modo `regras`. A entrega é só texto e configuração de teste, sem segredo, dependência nem workflow; `gitleaks`, `zizmor`, `actionlint`, `semgrep` e `osv-scanner` não estão no PATH (lacuna registrada) e não se aplicam a este diff.
