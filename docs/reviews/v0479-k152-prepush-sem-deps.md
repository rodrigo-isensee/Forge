---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-k152-prepush-sem-deps
commit: ce1d79bd030ae0c1d33b4443d91bd311ad043155
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-21
---
# Review: v0478 (E81.2, K152 no head ce1d79bd)

Diff `adc52def..ce1d79bd`: `bin/forge-init` (marcador `{{INSTALAR}}`), `bin/forge-testes` (mapa), proposta `docs/propostas/k152-pre-push.md` (patch do `pre-push.local` travado, o dono aplica), `tests/test_prepush_k152.py`, mutantes, peso D4, duas entradas em `CITACOES_CONHECIDAS` e o fragmento do changelog.

## Achados
- A1 (recomendado) docs/propostas/k152-pre-push.md:61 · Linha de guarda mudada (`bash -c "$rapido" || {...; exit 1; }`, só o texto) sem mutante declarado; o ramo de falha tem teste de comportamento (test_pronto_reprovado_barra...), mas a spec pede um mutante por linha (abrir -2.json).
- A2 (recomendado) docs/propostas/k152-pre-push.md:51 · Trecho vazio no pronto rápido (`;` no fim) dá programa vazio e deixa espaço sobrando na lista do que falta; cosmético, não barra envio sem motivo. Pular `[ -z "$programa" ] && continue`.

## Sondas

## Parecer
Aprovado. Faz o que o K152 pede e só aperta: o envio com código continua barrado, agora dizendo o que falta e o comando de instalar; com as ferramentas presentes o pronto rápido roda como antes. Respeita o arquivo travado (mudança do modelo só como proposta, `R-CONFORMIDADE`) e a neutralidade da prosa da proposta (`R-NEUTRO`: nomes de ferramenta mascarados nas saídas).

`forge-init`: `shlex.join` mais a recusa de aspa simples deixa o valor seguro dentro de `instalar='...'`; o `escapar` cobre `&`, `|` e `/` do sed; falha de leitura vira vazio sem derrubar o `set -e`. Python chamado com `-I`.

Testes: `python3 -m unittest tests.test_prepush_k152` rodado no head: 8 testes, OK, nenhum pulado (o ponta a ponta com `git worktree add` e `git push` rodou). O teste aplica o bloco diff da proposta numa cópia, limpa o git herdado e cobre os ramos de falha por comportamento. `bin/forge-mutante tests/mutantes/v0479-k152-prepush-sem-deps.json`: M1 a M8 morreram. Tamanho bem abaixo do teto H1 (cerca de 30 linhas de código). Suíte completa: fica no CI do PR (`R-CUSTO`), não rerrodada aqui.

Os dois achados são recomendados e viram cartão depois do merge (`R-REVIEW`); o A1 pode ir junto quando o dono aplicar o patch.
