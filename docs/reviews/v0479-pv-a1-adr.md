---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-pv-a1-adr
commit: ac1069d300ba52321c145959c446dbecf2dfb838
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 (E57.10, PR-VERDE A1, emenda das ADR 0018 e 0008)

Diff revisado: `5ccac0bf..ac1069d3`, 3 arquivos (ADR 0018, ADR 0008 seção 3, fragmento `changelog.d/v0479-pv-a1-adr.md`), 0 linha de código (H1 dentro do teto). Sem suíte local (brief); sem PR nesta etapa, logo sem CI a citar.

## Achados
- A1 (recomendado) docs/adr/0018-autorizacao-do-dono-gravada.md:114 · E3 protege docs/autorizacoes/ contra Bash com quem: [] e diz que o commit do arquivo é do agente; `git add <caminho>` nomeia o caminho e cairia na barreira. Dizer no PV-A3 como o arquivo entra no índice (o declarar o põe, ou git add liberado por ser só leitura).
- A2 (recomendado) docs/adr/0018-autorizacao-do-dono-gravada.md:117 · E6 manda gravar no PV-A4 a constante do fim da transição (14 dias depois do merge do PV-A4), mas o commit do PV-A4 é anterior ao merge e não sabe a data; definir quem grava a data e quando (commit seguinte ao merge, ou 14 dias da data escrita).
- A3 (recomendado) docs/adr/0018-autorizacao-do-dono-gravada.md:116 · E5 confere o arquivo só ao abrir o PR; a Retirada: do E2 chega ao CI só se o agente enviar o commit. Conferir também no merge (forge-fechar) se há R-<Id> no registro local, para a retirada não depender do envio.
- A4 (recomendado) docs/adr/0008-governanca-de-contribuicoes.md:56 · As duas ADR citam docs/propostas/v0479-pr-verde-de-primeira.md, ausente na develop e nesta branch (está só na melhoria/v0479-pr-verde-de-primeira, sem PR); mesclar o desenho antes ou junto desta emenda.

## Sondas

## Parecer
Aprovado. A emenda segue o desenho (PV-A, opção A-a; D1 e D2) e a decisão do dono de 2026-11-20 13:51, inclusive a condição da D1, escrita como regra E3 (só o dono ou a ferramenta gravam o arquivo; hook barra pelo caminho; teste com agente recusado; confirmação escrita da segurança antes do PV-A4). Traz modelo de ameaças por item, "Afrouxa?" declarado (`R-DECISAO`), "Por que o existente não basta" com a medida (52 de 121) e a referência conferida (`tests/catraca.py:1104` é `rotulo_do_dono`), critério de reversão com tabela de leituras, classes novas no Critério de parada com oráculo, e diz que nada se libera antes do PR de cada item. A ADR 0008 recebe a nota na seção 3 e nos dois jobs da catraca, coerente com E4 e E6; `R-CUSTO` e N-CAT1 seguem não liberáveis. Fragmento de changelog com o nome da branch. Os quatro achados são recomendados (texto a precisar nos itens PV-A3 a PV-A5 e ordem de merge) e viram cartão; o parecer de segurança (E57.11) confere o modelo de ameaças.
