---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-recomendado-restos
commit: 8d9f2b959719c61ea66e182f5e3720514e82d539
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: v0479-recomendado-restos (revalidação)

Etapa E46.3 do pedido v0478. Revalidação do parecer aprovado no head 985cf4e3 (a rodada anterior fica no git, commit 98705fbd), agora no head 8d9f2b95, depois da volta do CI (E46.6).

Gatilhos: controle do Forge (`docs/regras/R-REVIEW.md`), agente com portão (`agents/devops-engineer.md`), modelo de parecer copiado aos projetos (`templates/projeto/docs/devops/_modelo.md`).

## Delta lido
`forge-check parecer delta docs/security/v0479-recomendado-restos.md`: intervalo `985cf4e3..8d9f2b95`, sem o que veio da base (`develop`); no domínio, só `agents/devops-engineer.md` (uma linha, a 17, 5187 → 5155 bytes). O resto do intervalo veio da `develop` ou são pareceres de outros papéis (`docs/qa/`, `docs/reviews/`).

Já lido na rodada anterior e sem mudança: `docs/regras/R-REVIEW.md:14`, `templates/projeto/docs/devops/_modelo.md:17`, `tests/test_achado_teto_doc.py`, `changelog.d/v0479-recomendado-restos.md`.

## A mudança continua só apertando
Sim, por escrito. Em `agents/devops-engineer.md:17` a volta do CI só encurta a redação, sem mudar o sentido:
- "`R-SEGURANCA` quando houver gatilho" passa a "`R-SEGURANCA` com gatilho", e "na passada do code review" passa a "no code review": mesmo sentido.
- "o `recomendado` vira cartão depois do merge; promover `recomendado` exige `critério mudou:`" passa a "o `recomendado` vira cartão depois do merge e promovê-lo pede `critério mudou:`": o destino e a marca continuam. A regra que obriga a marca é `R-REVIEW` ("exige a marca `critério mudou:` com o motivo"), que não mudou.
- O critério de bloqueio ("defeito provado, requisito ou segurança com gatilho") e a obrigação do parecer de devops em `.github/`, `Dockerfile*`, `compose*` e IaC continuam iguais.
- As frases sob guarda continuam presentes: `tests/test_achado_teto_doc.py:56` e `tests/test_forge.py` (`BloqueanteSoComDefeitoProvado`: frase curta, "`critério mudou:` com o motivo", "(`R-REVIEW`)").

Achados anteriores: nenhum (a rodada em 985cf4e3 aprovou sem achado); nada novo neste delta.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Suíte: só no CI do PR, não rodada aqui. Rodados para tirar a dúvida: `python3 -I tests/test_achado_teto_doc.py` (8 testes, OK) e `python3 -m unittest test_forge.BloqueanteSoComDefeitoProvado` em `tests/` (2 testes, OK). Varreduras de segredo e de dependências não se aplicam (só texto).
