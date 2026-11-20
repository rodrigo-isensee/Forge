---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-recomendado-restos
commit: 985cf4e3dba073c6c6eaca14195a4ac94f4575da
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: v0479-recomendado-restos

Etapa E46.3 do pedido v0478 (META85-RECOMENDADO-RESTOS, decisão do dono na E35: recomendado de review e QA vira cartão; o de segurança continua corrigido antes do merge).

## Gatilhos
Gatilhos: controle do Forge (`docs/regras/R-REVIEW.md`, texto que decide a volta dos pareceres), agente com portão (`agents/devops-engineer.md`), modelo de parecer copiado aos projetos (`templates/projeto/docs/devops/_modelo.md`).

## Escopo lido
Diff inteiro `004ce869..985cf4e3` (5 arquivos, +8 −4): `agents/devops-engineer.md:17`, `docs/regras/R-REVIEW.md:14`, `templates/projeto/docs/devops/_modelo.md:17`, `tests/test_achado_teto_doc.py:55-56,68`, `changelog.d/v0479-recomendado-restos.md`.

## A mudança só aperta
Sim, por escrito: a mudança só aperta.
- `docs/regras/R-REVIEW.md:14` ("Uma passada") passa a mandar de volta ao autor, além dos bloqueantes, o `recomendado` de segurança. Antes a linha falava só dos bloqueantes e contradizia a linha 16, que já mandava corrigir o recomendado de segurança antes do merge; agora as duas batem, e o que volta só cresce.
- `agents/devops-engineer.md:17` e `templates/projeto/docs/devops/_modelo.md:17`: o recomendado de devops já não devolvia ("não devolve"); o texto novo acrescenta o destino (cartão depois do merge), sem tirar nenhum critério de bloqueio. Bloqueante continua sendo defeito provado, requisito ou segurança com gatilho; a exigência de `critério mudou:` para promover fica intacta.
- `tests/test_achado_teto_doc.py:55-56,68`: duas frases novas sob guarda e o piso da contagem sobe de 12 para 14; nenhuma entrada sai do mapa `CARTAO`, nem a da segurança (`templates/projeto/docs/security/_modelo.md` e `docs/security/_modelo.md`, "na segurança, volta ao autor e é corrigido antes do merge").
- Nenhum trecho de `invariantes` é removido; nenhum código executável, hook, workflow ou ferramenta muda.

## Achados

## Sondas

## Detalhe dos achados
Sem achado de segurança. Caminho de abuso considerado: usar o texto do devops ("vira cartão") para empurrar para depois do merge um problema de segurança apontado no parecer de devops. Não se sustenta: o bloqueio por segurança com gatilho continua `bloqueante` no mesmo parágrafo (`agents/devops-engineer.md:17`), e o recomendado de devops já não voltava antes desta mudança.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Suíte: não rodada aqui (a bateria é do CI do PR); rodado só o teste tocado, `tests/test_achado_teto_doc.py` (8 testes, OK, a partir de `tests/`). Varreduras de segredo e de dependências não se aplicam (só texto e teste estrutural).
