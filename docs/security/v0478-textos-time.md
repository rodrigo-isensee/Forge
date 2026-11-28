---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0478-textos-time
commit: 932c43c7b8550a2c9e2759ed38825fe969cfe8ad
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-18
---
# Review de segurança: v0478 (textos do time, E19.3)

Diff lido inteiro: `0c47762a..932c43c7` (2 commits, 6 arquivos: `agents/jarvis.md`, `agents/tech-lead.md`, `tests/config.json`, `skills/falar-com-o-dono/SKILL.md`, `skills/falar-com-o-dono/toda-mensagem.md`, fragmento em `changelog.d/`). Base igual a `origin/develop`.

## Gatilhos
Gatilhos: controles do Forge (`tests/config.json` invariantes e motivos), texto de agente com regra (`agents/jarvis.md`, `agents/tech-lead.md`)

## Achados

## Sondas

## Detalhe dos achados
Pergunta do portão: algum trecho encurtado tirou regra ou trava? Não.

- **Invariantes:** nenhum trecho saiu de `invariantes` em relação à base (comparação lista a lista contra `git show 0c47762a:tests/config.json`); três entraram (`agents/jarvis.md`, `agents/tech-lead.md`, `toda-mensagem.md`), e os de `jarvis.md` e `tech-lead.md` têm motivo em `invariantes_motivo_trecho` (`tests/config.json:867`, `tests/config.json:902`). Todo padrão de `invariantes` dos quatro arquivos de texto tocados casa com o arquivo no head (verificação com `re.search`, saída `ok`).
- **Encurtamentos, um a um:** `agents/jarvis.md:31` ("só se a entrega muda interface" → "só se muda a interface"), `:33` ("Antes de pedi-la" → "Antes"), `:37` ("e você avisa" → "e avisa"); `agents/tech-lead.md:3` (descrição: "desenvolvimento" → "código", "junto do" → "com"), `:13` ("e pelo arquiteto" → "e o arquiteto"), `:28` ("entra pronto" → "entra"; a condição continua: pareceres da classe aprovados por `forge-check classe` e CI verde), `:44` (versão: mesmo limite de 2 por dia, PR `homolog` → `main` e merge pelo usuário mantidos). Nenhum tirou condição, portão, ID de regra (`R-MAIN`, `R-VERIFY`, `R-FLUXO`, `R-REVIEW` seguem citados) nem limite numérico.
- **Endurecimentos:** `agents/tech-lead.md:39` ganha o gatilho de leitura do `ritmo-e-corte.md`; `agents/jarvis.md:13` e `skills/falar-com-o-dono/toda-mensagem.md:9` ganham o recibo no meio da rodada. Só acrescentam dever.
- **Segredo e custo:** o diff não traz credencial, URL nem chamada de serviço (`R-CUSTO`).

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Suíte: não rodada localmente (brief: sem suíte local); o CI do PR é a prova da bateria e não pôde ser consultado daqui (sem credencial do `gh` no sandbox). Ferramentas: `git diff`, checagem dos invariantes com a biblioteca padrão; `gitleaks` ausente do PATH (lacuna; o diff é só texto e foi lido inteiro).
