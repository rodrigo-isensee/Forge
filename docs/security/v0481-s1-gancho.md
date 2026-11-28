---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-s1-gancho
commit: e4b6bc4a8417bdb90338f24687c99219b19142fe
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-26
---
# Review de segurança: v0481 (E20.28, #920, hook `estado`, volta 2: merge da develop)

Volta por delta sobre o head `e4b6bc4a` (delta `5d558642..e4b6bc4a`: o merge de `origin/develop` em `346a7860`, que trouxe o #921, hook `ordens_teto`; as rodadas anteriores ficam no git). `forge-check parecer delta`, sem o que veio da base: no domínio `hooks/hooks.json`, `bin/forge-testes` e a emenda da ADR 0003; fora do domínio `docs/hooks-fixtures.md`, `docs/indice-forge.md` e `tests/pesos-d4.json`. Os conflitos do merge foram `hooks/hooks.json` e `bin/forge-testes`. Achados anteriores: A1 e A2 seguem fechados (volta 1); nada novo.

Gatilhos: controles do Forge (`hooks/hooks.json`, registro dos hooks), regra afrouxada (ADR 0003 itens 1 e 2, já avaliada na 1ª rodada).

## Detalhe
**Conflito em `hooks/hooks.json`.** Comparei os registros (evento, matcher, comando, args, timeout, tipo) das quatro versões: base do merge `3c833f3f`, lado da branch `5d558642`, develop `346a7860` e o resultado `e4b6bc4a`. O resultado é exatamente develop mais o delta da branch: nenhum registro da develop sumiu, e o único somado é `UserPromptSubmit` (sem matcher) → `python3 -s -E ${CLAUDE_PLUGIN_ROOT}/hooks/estado.py`, timeout 10, depois do `ordens.py` no mesmo grupo, igual ao aprovado na volta 1. O `ordens_teto` (PreToolUse, matcher `Write|Edit|MultiEdit`, `-s -E`, timeout 10) entra idêntico ao da develop, na mesma posição (matchers do PreToolUse: `Agent|Task`, `SendMessage`, `Bash|Write|Edit|MultiEdit|NotebookEdit`, `Write|Edit|MultiEdit`, `Bash`). A `description` junta as duas frases (ordens_teto, depois estado), só texto.
**Conflito em `bin/forge-testes`.** O `git show --cc` mostra só a união: a linha do MAPA com `estado.py` e `test_hook_estado` (branch) ao lado da linha `hooks/(ordens|ordens_teto)\.py` (develop); `tests/pesos-d4.json` soma os dois pesos. Nenhum outro arquivo do merge difere dos dois pais.
**A emenda da ADR 0003** no delta contra a develop é a mesma já avaliada nas rodadas anteriores; o trecho da exceção do `ordens` vem da develop sem mudança.

**O que o delta aperta, o neutro e o que afrouxa**
- Aperta: nada novo nesta branch; o `ordens_teto` (recusa gravar as ordens em vigor acima do teto) chega pela develop, já revisado no #921.
- Neutro: a resolução do conflito; os dois hooks lado a lado sem interação (o `estado` só lê e não grava o arquivo de ordens; o `ordens_teto` só olha a escrita de ferramenta); nenhum gatilho, matcher, comando, flag do Python ou prazo mudou além do somado; nenhuma dependência, segredo, workflow ou permissão no delta.
- Afrouxa: nada no delta. Os afrouxamentos da emenda da ADR 0003 seguem como avaliados na 1ª rodada.

CI do head `e4b6bc4a` (run 45917071630): as dez partes da suíte, `catraca`, passos, verificações longas, instalação, `python 3.14`, teto de pulados e árvore já provada verdes. `bateria (pareceres)` e `bateria` vermelhos só pela falta dos pareceres sobre este head (log: `R-REVIEW` com `docs/reviews/v0481-s1-gancho.md` desatualizado depois da mudança em `bin/forge-testes`); não há defeito de código no vermelho.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: `forge-check parecer delta`, `git show --cc`, comparação estrutural dos registros do `hooks.json` nas quatro versões (script da biblioteca padrão) e o CI do head. Sem varredura de segredo ou de dependência: o delta não toca configuração, credencial nem dependência.
