---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-vigia-resumo-compactado
commit: 06a0220a908ce4a467361b9935e500b3c0d62af5
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: v0478 (E93.3, FALA-DO-DONO-RESUMO-COMPACTADO)

Escopo: `hooks/vigia.py` (novo `digitado_pelo_dono`, usado por `texto_do_dono`), consumidor `hooks/meta.py:31,156`, fixtures `tests/hooks/vigia/entrada-*.json`, mutantes e `tests/test_vigia.py`. Base fb3b670b.

## Gatilhos
Gatilhos: hook de controle (classificador da fala do dono, que decide aviso do vigia e a medida do meta).

## Achados
- A1 (recomendado) hooks/vigia.py:305 · A docstring diz que registro sem `origin` é a "forma antiga do cliente", mas o cliente da extensão de IDE atual ainda grava a fala digitada sem `origin`. Trocar para "cliente sem `origin` (versões antigas e a extensão de IDE)", para ninguém retirar o padrão achando que é legado.

## Sondas

## Detalhe dos achados
**Tentativas de passar texto do modelo ou de ferramenta como fala do dono** (gerador local com 20 formas sobre `vigia.texto_do_dono`, novo e antigo lado a lado; todas no esperado): `origin` com `kind` `Human`, `null`, string, lista, `peer` (forma real com `body`/`from`), `coordinator`, `task-notification` (com e sem `producer`/`runId`) e dict sem `kind`, todos fora; marca `is*` nova (`isQualquerCoisa: 1`), `isMeta: "false"` (string verdadeira), `isCompactSummary` com `isVisibleInTranscriptOnly`, `sourceToolAssistantUUID`, todos fora; `toolUseResult` vazio com bloco `tool_result` cai na checagem de blocos só `text` (`hooks/vigia.py:322-324`); conteúdo começando por `<` segue fora. Passam só: sem `origin` e `origin {"kind":"human"}`, como desenhado. `IsMeta` (maiúscula) passa, mas não é campo do cliente: sem caminho.

**Fronteira de confiança.** Os campos de forma (`origin`, `is*`, `toolUseResult`, `sourceTool*`) são gravados pelo cliente no transcrito, não pelo modelo; o modelo controla só o texto do conteúdo. Por isso uma marca que o modelo pudesse forjar não existe aqui; o risco real era o cliente gravar texto do modelo como `user` sem marca reconhecida, e o resumo de compactação era exatamente isso (antes aceito).

**Registro sem `origin` (escolha do autor).** Forma dos campos medida nos transcritos locais (só chaves, sem conteúdo): 14 registros `user` sem `origin` passam pelas outras condições, todos com `promptId`, `userType: external` e entrada `cli`/`claude-vscode`/`sdk-cli`, inclusive na versão mais nova do cliente de IDE; ou seja, fala digitada. Nenhuma forma não humana conhecida (resumo, aviso de tarefa, `peer`, `coordinator`, ferramenta) aparece sem `origin` ou sem marca. Exigir `origin` calaria o vigia para quem usa a extensão de IDE (perda de proteção), então o padrão é correto; a brecha residual é um tipo novo de registro do cliente sem `origin` e sem marca, já coberto em parte pela queda do conteúdo `<...>`. Severidade baixa, sem caminho de ataque pelo modelo. Daí A1 (só texto).

**meta.py segue protegido.** `hooks/meta.py:31` importa `texto_do_dono`, que agora chama `digitado_pelo_dono` no mesmo módulo; conferido que `meta.texto_do_dono is vigia.texto_do_dono` e `tests.test_meta` verde. O meta herda o aperto (resumo de compactação não é mais "última fala do dono").

**Só aperta.** As condições novas entram em conjunção com as antigas (`hooks/vigia.py:306-313`); nenhuma antiga saiu. Prova: no corpus local, o antigo aceita 1403 registros e o novo 1338, com 0 aceitos pelo novo e recusados pelo antigo; os 65 que saíram são todos `isCompactSummary` + `isVisibleInTranscriptOnly` (nenhuma fala digitada perdida).

A1: severidade informativa · correção mínima: o texto da docstring em `hooks/vigia.py:305` · esforço P · dono: autor da E93.1.

Fixtures novas trazem só a forma dos campos, sem conteúdo do dono.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Rodados: `tests.test_vigia` (10 testes, OK), `tests.test_meta` (OK), gerador de abuso e comparação antigo×novo sobre os transcritos locais (só chaves). Suíte inteira: fica para o CI do PR (não rodada aqui, por brief). Ferramentas de SAST e varredura de segredos não estão no PATH: lacuna registrada.
