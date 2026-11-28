---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-ordens-adr
commit: e7a946039c29d146b7f8350f9ce00b64ce3f4f59
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-22
---
# Review: v0480-ordens-adr

Etapa E104.6, revisão completa única, classe T (só documentação, review apenas). Diff `900bfdfe..e7a94603`: `docs/adr/0003-hooks-deterministicos-e-silenciosos.md` (+46, emenda "ordens em vigor", itens 1 a 7) e `changelog.d/v0480-ordens-adr.md` (+2). Sem código, sem guarda, sem mutante; sem suíte local (brief).

## Achados
- A1 (recomendado) docs/adr/0003-hooks-deterministicos-e-silenciosos.md:85 · a lista do que afrouxa omite tests/test_hooks.py:854 (stdout vazio fora de vigia, conformidade e agentes) e :156-157 (passos no SessionStart sem stdout); o ordens escreve texto puro e cai nos dois. Citar ambos na lista do PR do hook.
- A2 (recomendado) docs/adr/0003-hooks-deterministicos-e-silenciosos.md:74 · o teto de 16 caracteres do ID tira o `primeiro <ID>` de 597 dos 835 IDs do KANBAN.md (71%, p.ex. VIGIA-TIME-PARADO, 17); a lista positiva de [A-Za-z0-9.-] já basta, subir o teto para o maior ID medido.
- A3 (recomendado) docs/adr/0003-hooks-deterministicos-e-silenciosos.md:72 · o item 7 é outro hook com vigência própria dentro da lista de regras do ordens, sob o "Estado da emenda" do E104.1; e "Por que o existente não basta" (:79) não cobre o item 7 (por que o systemMessage do vigia não chega ao modelo). Separar em subseção.
- A4 (recomendado) changelog.d/v0480-ordens-adr.md:2 · "hook ordens em vigor" sugere que o hook entrou nesta mudança e omite o item 7 do vigia; texto sugerido: "ADR 0003: emenda para o hook ordens e o aviso de time parado do vigia".

## Parecer
Aprovado. A emenda cumpre a ORDEM DO DONO de 22/11 (os dois hooks existem pela ADR) e o corte da DECISÃO DO TIME de 05:35/05:42 (ADR antes, hook e invariantes depois, com `afrouxa-regra`). Conferido na leitura:

- `R-DECISAO`: critério de reversão para os dois hooks, medida com quem e quando (tabela), afrouxamento declarado com o título do PR; nenhum trecho de `invariantes` de `tests/config.json` sai.
- Referências de linha batem no head: `tests/test_hooks.py` 830-837 (laço das fixtures do `vigia`), 1487 (códigos `{0}`), 1493 e 1496-1499 (`test_hooks_json`); `tests/test_doutor.py` 608. `sem_controle` existe (`hooks/agentes.py:929`), `raiz_de_estado` em `hooks/_comum.py:83`; o arquivo `~/.forge-contrib/docs/kanban/ordens-em-vigor.md` existe (evidência do "Por que").
- Segurança do item 7: `reason` só de texto fixo, `<N>` inteiro, ID por lista positiva, `stop_hook_active` evita laço, `vigia` segue em códigos `{0}`. Parecer do `security-engineer` fica com o PR de cada hook (E104.1, E105.4), como a emenda manda.
- `R-NEUTRO`: o caminho do clone do Forge é da fábrica, não de projeto.

Os quatro achados são de texto e não mudam a decisão; viram cartão depois do merge (`R-REVIEW`). O A1 vale como aviso ao autor do E104.1: a lista do `afrouxa-regra` no PR do hook precisa das duas asserções.
