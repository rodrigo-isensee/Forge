---
tipo: review
contrato: 1
pedido: rotulo-sobrevive-merge
branch: melhoria/rotulo-sobrevive-merge
commit: 4a4d468
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-13
---
# Code review (parecer de autor): rótulo e parecer sobrevivem a merge da base e a commit de parecer

Escopo: `origin/develop..4a4d468` (1 commit): `tests/catraca.py`, `bin/forge-check`, `tests/test_catraca.py`, ADR 0004 (item 3), ADR 0008 (tabela da catraca), `CHANGELOG.md`. Referências: ADR 0008, ADR 0004, R-CONFORMIDADE, R-REVIEW, R-CUSTO.

Este é o parecer do autor. O PR muda `tests/catraca.py` (protegido): falta a review independente e o rótulo `afrouxa-regra` do dono.

## Problema
O rótulo só valia se aplicado depois do último push, e o `commit` do parecer só valia se o diff direto até o head tocasse apenas pareceres e quadro. Um merge da `develop` na branch invalidava os dois. Um commit só de parecer invalidava o rótulo. O conteúdo revisado não mudava em nenhum dos casos.

## Desenho escolhido
1. **Diff efetivo** (`forge-check`: `diff_efetivo`, `mesmo_diff`): é o patch de um commit sobre o seu merge-base com a base, sem os caminhos ignorados e sem as linhas `index` (o hash do blob muda quando a base mexe no arquivo). A comparação é **estrita**: texto, contexto e número de linha. Se a base mexer perto do trecho do PR, o diff muda e o rótulo ou o parecer cai. É uma falha fechada e foi escolhida de propósito. Não usei `git patch-id`: ele ignora espaço em branco, que é semântico em Python e YAML.
2. **Rótulo** (`catraca.py`): a regra antiga continua igual (rótulo depois do último push). Se ela falhar, a catraca tenta a regra nova:
   - `commit_do_rotulo` encontra o head no instante do rótulo. É o head da última execução `pull_request` deste PR criada antes do rótulo, pelo `created_at` do servidor e nunca pela data do commit.
   - Esse head precisa ter outra execução **depois** do rótulo, que é a execução do próprio `labeled`. Sem ela, o head do instante do rótulo pode não ter execução nenhuma (`[skip ci]`, workflow desligado no PR) e a atribuição cairia num head anterior que o dono não viu.
   - Se houver `head_ref_force_pushed`, `head_ref_deleted` ou `head_ref_restored` depois desse head, a regra nova não vale.
   - Com o head encontrado, o diff efetivo dele, fora de `docs/reviews/` e `docs/qa/`, tem de ser idêntico ao do head avaliado.
   - Os dados vêm de `GET /pulls/{n}` (para saber a branch) e de `GET /actions/runs?event=pull_request&branch=...` (filtrado pelo número do PR). As duas consultas são gratuitas e só de leitura (R-CUSTO). Se faltar token, a API falhar, não houver execução ou o commit não existir localmente, a regra nova não vale. Um PR de fork não tem `pull_requests` nas execuções e fica só com a regra antiga.
   - R-CUSTO continua sem exceção pelo rótulo.
3. **Parecer:** `commit_vale(..., base)` e `cmd_pr(..., base)` mantêm a checagem antiga e aceitam também o caso em que o diff efetivo, fora de `LIVRES`, é igual ao do `commit`. O modo `pareceres` passa a base. Sem `--base`, o `forge-check pr` continua estrito como antes, e o hook `parecer` não foi tocado. O veredito continua sendo lido do arquivo de parecer no head, então trocar `aprovado` por `reprovado` continua barrando.

Alternativa descartada: ignorar os commits de merge no diff. Um merge pode resolver conflito com código novo, e isso furaria a regra.

## Testes (vermelho antes, verde depois)
- São 17 casos novos em `tests/test_catraca.py`: `Pareceres` (4), `CommitDoRotulo` (5), `RotuloSobreviveAoConteudo` (6) e `ExecucoesDoPr` (2).
- **Vermelho** sobre o código antigo: 15 dos 17 falharam (9 falhas e 8 erros). Os dois que já passavam são guardas de não regressão: código mudado depois do merge invalida o parecer, e o veredito trocado no parecer continua barrando.
- **Verde:** `python3 -m unittest discover -s tests` deu 267 OK, e `scripts/validar-plugin.sh` passou.
- Os quatro casos pedidos estão cobertos:
  - o merge da base mantém o rótulo e o parecer;
  - um commit só de parecer mantém o rótulo;
  - código mudado depois do rótulo invalida, inclusive `KANBAN.md` e mudança junto com o merge;
  - o veredito trocado é conferido pelo modo `pareceres`.

## Checklist
- O PR faz o que foi pedido e nada além. O hook `parecer` local ficou de fora de propósito.
- Nenhuma checagem existente foi afrouxada: as duas regras novas só somam caminhos de aceitação, e cada uma falha fechada.
- Só biblioteca padrão; sem custo; neutro.
- Os testes não dependem da hora atual: os instantes são fixos.

## Riscos
- **Corrida no instante do rótulo:** se houver um push segundos antes do rótulo e a execução dele ainda não existir, o head atribuído é o anterior. A execução do `labeled` então terá outro SHA, e a regra nova falha fechado.
- **Atribuição depende das execuções:** a confiança é a mesma da regra antiga. Se alguém com permissão de administrador apagar execuções, a atribuição pode mudar.
- **Base que mexe perto do trecho do PR** (por exemplo, a mesma seção do `CHANGELOG.md`) muda o contexto do diff e pede o rótulo de novo. Escolhi o rigor.
- **Hook `parecer` local:** continua estrito depois de um merge da `develop`. Se o dono quiser o mesmo comportamento local, isso fica para outro pedido.

Parecer: **aprovado** (parecer de autor; a review independente vem a seguir).
