---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0478-cobertura-c1
commit: c4ddc61daa61bd4341aded9ff3eb983893be3959
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-18
---
# Review: v0478 (E9.2, COBERTURA-ESTUDO C1, T1 como portão)

Diff `4182a6b9...c4ddc61d`: `tests/catraca.py` (+35 linhas de código, abaixo do teto H1, um comportamento), `tests/test_catraca.py` (classe `T1NoTextoDoPr`, 10 testes), duas specs de mutantes (11 guardas), `docs/engineering/praticas.md` (linha do T1) e o fragmento `changelog.d/v0478-cobertura-c1.md`.

## Conferido
- **Aperta, não afrouxa.** O modo `pr-texto` passa a somar `violacoes_do_t1` às violações do texto; nada sai. A regra de código, teste e classe é a do `forge-check` (`codigo_sem_teste`, `classe_para_o_t1`), sem duplicar mecanismo. Falha fechada: diff dos testes ilegível levanta `ErroDeGit`, que o `_main` torna vermelho; classe ilegível vale N. O passo só roda com `base_ref == develop`, então as promoções não mudam. O workflow já reage a `edited`, então a seção `## Sem teste` escrita depois reavalia o PR. Nenhuma linha de `invariantes` nem de `docs/regras/` foi tocada.
- **Citação por arquivo.** `citado` exige o caminho inteiro (bordas `[\w./-]`); `secao` tira os comentários HTML, então o comentário do modelo não conta como justificativa. O motivo é medido sem os caminhos (`MINIMO_SECAO`).
- **Custo de tempo.** O autor declara 0,41 s → 0,78 s (mediana de 5). Remedido aqui, mediana de 5, mesmo corpo, `--base 4182a6b9`: base 0,29 s → head 0,57 s. O acréscimo de cerca de 0,3 s vem de carregar o `forge-check` e calcular a classe. Num job de cerca de 1 min, é desprezível e não abre run novo (`R-CUSTO`).
- **Testes e mutantes.** `python3 -m unittest tests.test_catraca.T1NoTextoDoPr`: 10 testes OK. Mutante M4 aplicado à mão numa cópia (`if not faltam:`): `test_motivo_curto_barra` falha, então o mutante morre. A fila `R-TETO` estava ocupada, então a bateria do `forge-mutante` fica com o QA (E9.4). Cada guarda do diff tem mutante com teste do ramo de falha, e nenhum teste lê o texto da fonte.
- **Suíte.** Não rodei a suíte inteira, como o brief manda: vale o CI do PR.
- **Ressalva do autor sobre `.github/pull_request_template.md`.** Ela procede. O comentário da linha 14 ainda descreve a seção como aviso do `forge-check pr` que o review confere. Não diz que o CI barra nem que é preciso citar cada arquivo. Isso não quebra nada, porque `secao` ignora o comentário, mas induz o autor ao erro (A1).

## Achados
- A1 (recomendado) .github/pull_request_template.md:14 · o comentário trata a seção como aviso do forge-check; diga que a catraca do CI barra o PR sem ela e que é preciso citar cada arquivo com o motivo (T1). Fica para cartão próprio, se o .github for de outra trilha
- A2 (recomendado) tests/catraca.py:1685 · a violação aponta docs/regras/R-QA.md, que não fala do T1 (a decisão 9301b94c o deixou nas práticas); aponte docs/engineering/praticas.md para quem lê o CI achar a regra
- A3 (recomendado) .github/workflows/catraca.yml:50 · o pr-texto roda a catraca e o forge-check da cópia do PR, não da base como no passo de regras (a docstring de forge_check, catraca.py:1689, diz base); um PR pode mudar o próprio T1. Rodar da base como o passo das regras

## Parecer
Aprovado. A mudança torna portão de CI um aviso que já existia, reaproveita a regra única do `forge-check`, falha fechada e tem cada guarda coberta por mutante e teste do ramo de falha. O custo medido fica em cerca de 0,3 s por run. Os três achados são recomendados e não devolvem a entrega (`R-REVIEW`). O A3 já existia no modo `pr-texto` antes deste diff, e o T1 o herda.
