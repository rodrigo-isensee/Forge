---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-textos-correcao
commit: 061f0091bbe46b3936106595434fcc5d993233fc
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-15
---
# Review de segurança: v047-textos-correcao (lote DOC1, E2.158)

Parecer completo (não havia parecer anterior nesta branch). Base `bf475209`, head `061f0091`; diff lido inteiro: `agents/tech-lead.md`, `skills/trabalho-em-paralelo/SKILL.md`, `docs/adr/0012-main-por-merge-commit.md`, `tests/test_textos_034.py`, `changelog.d/v047-textos-correcao.md`.

## Gatilhos
Texto de regra de processo da fábrica (agente e skill que descrevem portões, `R-REVIEW`, `R-FLUXO`) e ADR sobre proteção de branch (`R-MAIN`). Sem código executável, hook, workflow nem segredo. Pergunta do portão: algum texto afrouxa regra? Resposta: não.

- E8-TEXTO-ANTIGO (ADR 0012): a conferência do dono passa a pedir a regra "branch atualizada com a base" desmarcada no `portoes`. Não afrouxa: alinha a ADR ao `docs/protecao-de-branch.md:21` (passo 8) e ao risco já aceito pelo dono na E8 da 0.45.6 (`docs/protecao-de-branch.md:45`). Mantém a conferência de merge commit na `main` e de nenhum ator de bypass em `main-do-dono` e `portoes` (`R-MAIN`).
- CORRECAO-ANTES-DOS-PORTOES: regra nova e mais restritiva (`skills/trabalho-em-paralelo/SKILL.md:15`, ponteiro em `agents/tech-lead.md:35`, ambas com `R-REVIEW`).
- Compactação: os invariantes de `tests/config.json` para os dois arquivos seguem casando (conferido por regex). Nenhum ID de regra sumiu; `R-CONFORMIDADE`, `R-TETO`, `R-WIP`, `R-DECISAO`, `R-FLUXO`, `R-REVIEW`, `R-SEGURANCA` permanecem.

## Achados
- A1 (recomendado) agents/tech-lead.md:14 · A compactação tirou "numa passada" do code review; o `R-REVIEW` (título) e os textos do QA e da segurança mantêm. Sem perda de regra, pois o ID é citado, mas devolver as duas palavras deixa os três papéis com o mesmo texto.
- A2 (recomendado) agents/tech-lead.md:27 · "entra na develop quando fica pronto" virou "entra pronto na develop": perde o sentido de não esperar lote nem versão; o `R-FLUXO` citado e a D2 da skill seguem dizendo isso. Sugestão: "entra na `develop` ao ficar pronto".

## Sondas

## Detalhe dos achados
A1 e A2: severidade informativa; sem caminho de ataque (texto de processo cuja regra fonte, citada pelo ID, não mudou). Correção mínima: devolver as palavras na própria linha, se couber no teto de caracteres. Esforço P. Dono: `tech-lead` (autor do lote). Não bloqueiam (`R-REVIEW`).

## Riscos aceitos e ferramentas
Sem risco aceito novo. O risco de quebra semântica sem conflito por ter a regra "branch atualizada" desmarcada já é aceito pelo dono (E8 da 0.45.6, `docs/protecao-de-branch.md:45`); este diff só alinha a ADR 0012 a ele.
Ferramentas: leitura do diff; regex dos `invariantes` de `tests/config.json`; `tests/test_textos_034.py` rodado local (9 testes, OK). A suíte inteira roda no CI do PR (ainda não aberto). Sem varredura de segredo necessária (diff só de texto). PA-7 conferido: nenhum AR se aplica (AR-9 limite antigo no texto: o "150" ficou coerente nos dois arquivos).
