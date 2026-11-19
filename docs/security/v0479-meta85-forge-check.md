---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-meta85-forge-check
commit: 6853e0ee2ac9c19305db2419ddbcfbb3f5dcf1f0
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-19
---
# Review de segurança: v0478 META85 (bin/forge-check), E34.4

Intervalo lido: `eca1d21b..6853e0ee`, `bin/forge-check` (+109 -19), `bin/forge-testes`, os três testes `test_meta85_*`, as specs de
mutante, `skills/briefs-e-conferencia/autor-ate-o-merge.md`, `skills/engineering-practices/tamanho-por-item.md`, os dois
`stacks/*/pronto.md` e a proposta `docs/propostas/meta85-forge-check.md`.

## Achados
- A1 (recomendado) bin/forge-check:3575 · `revalida: não (... o parecer segue valendo)` sai para o `riscos-aceitos` sem aceite do usuário, que o `forge-check pr` recusa (S1); a proposta (linha 32) manda `sim` para todo parecer que não é `aprovado`. Fail-closed: o `pr` segue barrando.

## Sondas
- S1 · `riscos-aceitos` sem aceite + commit só de docs/guia.md; `parecer delta docs/security/p1.md` e `pr p1` · espera: respostas iguais · obtido: delta `revalida: não (... segue valendo)`; pr rc 1 `parecer: o último parecer não é aprovado`

## Gatilhos
Gatilhos: controle do Forge (`bin/forge-check`: classe, entrega e parecer delta, que decidem portões); rótulo `afrouxa-regra` pedido.

## Confirmação para o rótulo `afrouxa-regra`
A mudança **só aperta**: nenhum caminho aceita o que antes era recusado. Conferido ponto a ponto no head 6853e0ee:
1. **`parecer delta` / `revalida:`** (bin/forge-check:3554, 3571-3583). A linha é só informativa: nenhum portão a lê (nem `cmd_pr`,
   nem o hook `hooks/parecer.py`, nem a catraca; `git grep "revalida:"` fora do `forge-check` só acha o texto da skill). `cmd_pr`
   (bin/forge-check:1953-2069), `commit_vale` (:894) e o hook `parecer` não estão no diff. Um `revalida: não` divergente (A1) não faz
   o `pr` aceitar: S1 mostra o `pr` com rc 1 no mesmo estado. O efeito máximo da divergência é uma rodada a mais (falha fechada),
   nunca um merge com parecer recusado. O `revalida: não` nunca sai para parecer `reprovado` ou de valor desconhecido (:3575, falha
   fechada para qualquer valor fora de `aprovado`/`riscos-aceitos`).
2. **Contagem de arquivos** (bin/forge-check:1220-1249). `classe_da_entrega`, `gatilhos_do_diff`, `portoes_da_classe` e
   `pareceres_exigidos` são calculados antes e sem olhar a contagem; `arquivos_do_item` só decide o `rc` (0 → 1) e a linha `item:`. A
   classe, os portões e os pareceres impressos (texto e `--json`) são os mesmos de antes; o `pr` e o hook usam `classe_da_entrega`
   direto, não o `cmd_classe`, e nenhum script consome o rc do `forge-check classe` (`git grep` em `bin/`, `hooks/`, `scripts/`,
   `.github/`, `.githooks/`). Não há rota em que a contagem baixe a classe ou dispense parecer. Esquivar a contagem (nome com cara de
   teste, base ilegível dando lista vazia) só escapa do teto novo, não de nada que existia.
3. **`entrega --mutantes/--pronto`** (bin/forge-check:3172-3219). Só acrescenta linhas `pendente:` com reprova; `provas=None` (a
   conferência `--pedido`) mantém o comportamento anterior; o `--pedido` com as opções novas é recusado pelo argparse (:10257). O log é
   só lido (teto de 8 MiB, sem executar nada dele).
4. **Textos** (skill e `pronto.md`): o `revalida: não` dispensa a retomada do revisor, mas o `pr` continua exigindo o parecer válido;
   nada de skill ou stack dispensa portão.

## Detalhe dos achados
**A1.** `revalida_do_parecer` trata `riscos-aceitos` como "não barrou" sem conferir o aceite (`aceite_do_usuario`), enquanto o `cmd_pr`
(:2014) recusa o `riscos-aceitos` sem aceite. Outras fontes da mesma classe de divergência, não sondadas: o `cmd_pr` usa
`base_do_delta` (base `None` com o head já contido na base, modo estrito), e o `revalida` usa `ref_da_base` sempre; o `cmd_pr` também
recusa `commit:` só de parecer (AQ-5), violação de forma e autoria, que o `revalida` não olha. Caminho de ataque: nenhum (a linha não é
portão); o custo é o Jarvis não disparar a volta certa e o PR travar no `pr`. Severidade baixa. Correção mínima: no `riscos-aceitos`,
`revalida: sim` sem `aceite_do_usuario(raiz, pedido, commit, fim)` (ou a linha dizer "aguarda o aceite do usuário"), base pela
`base_do_delta` como o `pr`, e alinhar a proposta (linha 32) ao código. Dono: autor do item (E34.1).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Testes rodados: `python3 -m unittest tests.test_meta85_revalida tests.test_meta85_item_arquivos
tests.test_meta85_entrega` (22 testes, OK) e a sonda S1; a suíte inteira fica com o CI do PR (sem suíte local, pelo brief). Sem
segredo no diff (revisão manual; `gitleaks` não usado neste intervalo só de código Python e texto).
