---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-fala-e-decisoes
commit: 1c330fe64c8687225e4847f84cf17b030c2a4353
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-16
---
# Review de segurança: v047 (fala só no marco e pedido das decisões)

Intervalo revisado: `origin/develop` (c5c3a449) até 05797223, um commit (E1.282): `agents/jarvis.md`, `skills/falar-com-o-dono/SKILL.md`, `skills/modo-iniciante/SKILL.md`, `tests/config.json` e o fragmento `changelog.d/v047-fala-e-decisoes.md`.

## Revalidação por delta (14a29d8f..1c330fe6, E2.396)
Lido por `forge-check parecer delta`: no domínio, só `tests/config.json`; os merges trazem pareceres e o bug do QA, fora do domínio.

**A3 resolvido:** o trecho restaurado "diga sempre ao usuário para qual agente passou" (`agents/jarvis.md:34`, `tests/config.json:223`) ganhou o seu motivo em `invariantes_motivo_trecho` (`tests/config.json:756`, `regra` R-DECISAO e `porque` com mais de 30 caracteres), e a contagem do legado de `agents/jarvis.md` fica em 48 (`tests/config.json:696`). É a correção que mantém "o legado só encolhe": nenhuma proteção removida nem afrouxada, sem rótulo `afrouxa-regra`. Os achados recorrentes (PA-7) não se aplicam a um delta só de dados de invariantes.

Conferido no head 1c330fe6: `python3 -m unittest tests.test_forge.RegrasInviolaveis tests.test_jarvis_nucleo tests.test_forge.Neutralidade tests.test_invariante_gatilho` OK (27 testes). A1 e A2 (recomendados) seguem abertos, sem bloquear. Parecer: aprovado.

## Revalidação por delta (fd0a0172..14a29d8f, E2.333)
Lido por `forge-check parecer delta` (sem o que veio da develop no merge 1298992d): no domínio, `agents/jarvis.md` e `tests/config.json`; fora, o fragmento do changelog e `tests/test_jarvis_nucleo.py`.

**O invariante volta (decisão do dono de 2026-11-16 09:52, `docs/pedidos/v047.md:947`):** "diga sempre ao usuário para qual agente passou" está de novo em `agents/jarvis.md:34` e em `tests/config.json:223`, como na develop (5e74c70e); só o momento muda, com o trecho novo "no recibo e no aviso de marco, nunca em mensagem extra" protegido e com `regra` e `porque` (`tests/config.json:755`). `RETIRADOS_047` sai do teste do núcleo. Contra a base, o delta só acrescenta: o afrouxamento anterior deixa de existir e o pedido não precisa mais do rótulo `afrouxa-regra` por esse trecho. As outras linhas de `agents/jarvis.md` no delta são redação, sem mudar barreira.

**Defeito no controle (A3, bloqueante):** a contagem do legado de `agents/jarvis.md` ficou em 48 (`tests/config.json:696`), a do afrouxamento, mas o arquivo volta a ter 49 trechos sem motivo por trecho. `tests.test_forge.RegrasInviolaveis` falha no head (S1), e o CI do PR também falharia. Correção mínima, sem afrouxar: dar ao trecho restaurado o seu motivo em `invariantes_motivo_trecho` de `agents/jarvis.md` (`regra` R-DECISAO e `porque` de 30+ caracteres), mantendo 48; ou devolver a contagem a 49, o valor da develop (soma 246, abaixo do teto 284). A primeira mantém a regra "o legado só encolhe".

Conferido no head 14a29d8f: `tests.test_jarvis_nucleo`, `tests.test_forge.Neutralidade` e `tests.test_invariante_gatilho` OK; `tests.test_forge.RegrasInviolaveis` com 1 falha (27 testes, S1).

## Revalidação por delta (a4a47661..fd0a0172, E1.348)
Lido por `forge-check parecer delta`: no domínio, `agents/jarvis.md` (uma linha da triagem) e `tests/config.json`; fora, o fragmento do changelog e `tests/test_jarvis_nucleo.py`.

**Afrouxamento pedido pelo dono (decisão 2 de 2026-11-15 06:34, `docs/pedidos/v047.md:593`):** sai o invariante "diga sempre ao usuário para qual agente passou" e entra "diga qual agente faz o quê só nos marcos, num resumo", com `regra` (R-DECISAO) e `porque`; a contagem de `agents/jarvis.md` cai de 49 para 48 (troca de um padrão protegido por um conjunto à parte). O teste do núcleo registra a retirada em `RETIRADOS_047`. A catraca, rodada local contra a4a47661, acusa a remoção e pede o rótulo `afrouxa-regra` (R-CONFORMIDADE): o portão técnico continua, e o rótulo é do dono no PR, não deste parecer.

**Impacto de segurança:** nenhum na barreira técnica. O aviso por agente era só fala; a janela de permissão, o hook `conformidade` e as decisões que saem na hora (aceite de risco de `R-SEGURANCA`, problema que muda prazo ou risco) não mudam. O efeito é de auditoria, já coberto por A2: quem fez o quê passa a chegar ao dono no marco. Sem achado novo.

Conferido no head fd0a0172: `tests.test_jarvis_nucleo`, `tests.test_forge.RegrasInviolaveis` e `tests.test_forge.Neutralidade` OK (26 testes); `tests.test_invariante_gatilho` OK.

## Revalidação por delta (05797223..a4a47661, E1.302)
Lido por `forge-check parecer delta`: `skills/falar-com-o-dono/SKILL.md`, `skills/kanban-scrum/SKILL.md`, `skills/modo-iniciante/SKILL.md`, três arquivos novos ao lado das skills (`resposta-curta.md`, `experimentos.md`, `numeros.md`) e `tests/config.json`; fora do domínio, o fragmento do changelog.

**Nada apagado nem resumido (diretriz 25), conferido por script contra a base c5c3a449:** a linha "Resposta curta (O4)" da base volta idêntica em `resposta-curta.md`, com `decisoes --resposta` e os campos `origem:`, `procurado:`, `seguir:`, `não seguir:` do corte recomendado; o "Ritmo" volta à forma da base. A tabela e a frase dos experimentos e os três itens de "Números da pergunta" mudaram de arquivo sem alteração de texto. A frase de Scrum só ganhou o trecho do `tech-lead` e do `agile-coach`. As demais linhas da base ausentes no head são as do commit anterior, já revisadas acima (A2).

**Invariantes:** o delta só acrescenta: 7 padrões em listas existentes e 3 listas novas para os arquivos novos, todos com `regra` e `porque` (R-DECISAO); nenhuma linha de proteção removida nem afrouxada, sem rótulo `afrouxa-regra`. Os arquivos novos não são lidos por hook nem por ferramenta (`hooks/`, `bin/` sem referência), então mover o texto não muda nenhuma barreira técnica; continuam protegidos pelos invariantes novos.

O A1 e o A2 abaixo (recomendados) não foram tocados no delta e seguem abertos, sem bloquear.

## Gatilhos
Controles do Forge (`R-SEGURANCA`): `tests/config.json` (invariantes). Os demais arquivos são texto de agente e skill, sem autenticação, segredo, dependência, CI, hook nem `docs/regras/`.

**Invariantes:** o diff só acrescenta. As três linhas removidas de `tests/config.json` voltam idênticas no mesmo lugar (a lista de `skills/modo-iniciante/SKILL.md` vira superconjunto; nas listas de `agents/jarvis.md` e `skills/falar-com-o-dono/SKILL.md` só muda a vírgula). São 15 padrões novos, todos com `regra` e `porque` (R-DECISAO). Nenhuma proteção foi afrouxada, e o pedido não precisa do rótulo `afrouxa-regra`.

**Texto removido, conferido contra a fonte:**
- `agents/jarvis.md`: a lista "à pessoa, só decisão, rótulo, merge na `main` e comando em arquivo travado" saiu da regra do dono, mas está inteira na linha nova "Falar só no marco". A frase "quando algo dá errado e muda prazo ou risco" e as decisões (o que inclui o aceite de risco de `R-SEGURANCA`) continuam saindo na hora, fora do resumo de 30 min. Recibo e perguntas seguem completos (invariante novo). "Telegram ... sem segredo; não mude a allowlist" não mudou.
- `skills/falar-com-o-dono/SKILL.md`: saíram a menção a `decisoes --resposta` e os campos do corte recomendado (`origem:`, `procurado:`, `seguir:`, `não seguir:`). Quem os exige é a ferramenta (`bin/forge_dono.py`), que não muda. "Uma decisão por mensagem" e a origem de cada decisão continuam na fonte (`docs/regras/R-DECISAO.md:14`). A trava da Q2 (a escolha provisória não cobre aceite de risco, gasto, `afrouxa-regra`, merge na main nem ato destrutivo) não mudou, e o pedido das decisões grava cada resposta por `forge-check anotar`.
- `skills/modo-iniciante/SKILL.md`: a tradução de recusa sem orientar contorno (`R-CONFORMIDADE`), a fila do `forge sugerir` e a confirmação na janela de permissão não mudaram.

Neutralidade (`R-NEUTRO`): a extensão citada é um editor genérico, não um projeto. O teste de neutralidade passa (abaixo).

## Achados
- A1 (recomendado) skills/modo-iniciante/SKILL.md:55 · O modo foco recolhe comandos e agentes. Diga ao iniciante que a janela de permissão continua aparecendo e que ele pode abrir a linha para ver o comando antes de aprovar, para que o foco não vire aprovação sem leitura.
- A2 (recomendado) skills/modo-iniciante/SKILL.md:21 · Saiu o aviso "o que já foi feito depois" de um ato no GitHub. Um ato visível fora (comentário, issue, rótulo) que não fecha marco fica sem registro à pessoa. Mantenha uma frase depois de um ato externo no GitHub, ou registre que o marco o cobre.

## Sondas
- S1 · python3 -m unittest tests.test_forge.RegrasInviolaveis (head 14a29d8f) · espera: OK · obtido: FAIL test_invariante_traz_regra_e_porque_e_o_legado_so_encolhe, 'agents/jarvis.md: trecho novo em arquivo do legado sem regra e porque' (prova do A3, resolvido no head 1c330fe6: OK)

## Detalhe dos achados
**A1.** Evidência: `skills/modo-iniciante/SKILL.md:55`. Caminho: um texto injetado (de uma issue ou de um arquivo lido) leva um agente a propor um comando. O sistema de permissões ainda pede confirmação, mas o iniciante, com a visão recolhida, tende a aprovar sem abrir o comando. A barreira técnica (permissão e hook `conformidade`) não muda, por isso não bloqueia. Severidade: baixa. Correção mínima: meia frase na mesma linha. Esforço: P. Dono: o autor do pedido.

**A2.** Evidência: `skills/modo-iniciante/SKILL.md:21`, antes "e o que já foi feito depois, em uma frase". Caminho: não há atacante. O risco é de auditoria: um ato público feito em nome do dono não chega a ele até o próximo marco ou resumo. Severidade: informativa. Correção mínima: devolver o aviso só para o ato externo no GitHub, ou dizer explicitamente que o resumo de 30 min o cobre. Esforço: P. Dono: o autor do pedido.

**A3 (resolvido no head 1c330fe6).** Evidência: `tests/config.json:696` (48) contra os 49 trechos de `agents/jarvis.md` sem motivo por trecho; `tests/test_forge.py:576`. Caminho: não há atacante; é o controle que protege os invariantes do Forge vermelho, o que barra o merge pelo CI e, se "corrigido" baixando o teste, abriria espaço para afrouxar sem rótulo. Severidade: baixa (defeito provado em controle do Forge, `R-SEGURANCA`). Correção mínima: entrada em `invariantes_motivo_trecho` para o trecho restaurado, ou contagem 49 (valor da develop). Esforço: P. Dono: o autor do pedido.

## Riscos aceitos e ferramentas
Sem riscos aceitos.

Conferido no head a4a47661: `tests.test_forge.Neutralidade`, `NeutralidadeDoNucleo` e `RegrasInviolaveis` OK (9 testes); testes de invariantes OK (2 testes).

Conferido no head 05797223:
- Os padrões de `invariantes` dos três arquivos casam com o texto (script local, sem falta).
- `python3 -m unittest tests.test_forge.Neutralidade tests.test_forge.NeutralidadeDoNucleo`: OK (6 testes).
- `tests.test_forge.RegrasInviolaveis`: OK (3 testes).

A branch ainda não tem PR nem execução de CI. A suíte inteira roda no CI do PR e é obrigatória para o merge (`R-QA`).

Ferramentas de varredura de segredo, de dependência e de workflow: não se aplicam, porque o diff é só texto e configuração de teste, sem segredo, dependência nem workflow.
