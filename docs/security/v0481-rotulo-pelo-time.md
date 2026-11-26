---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-rotulo-pelo-time
commit: c58e140907dc71b44160b5bad0859321732048ac
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-26
---
# Review de segurança: v0481 (E24.8, #918, FORGE-ROTULO-PELO-TIME, volta por delta)

Delta lido: `forge-check parecer delta` (`ab5871d1..c58e1409`, sem a base). No domínio: só `docs/adr/0018-autorizacao-do-dono-gravada.md:203`. Fora do domínio: `tests/test_autorizacao.py`, lido mesmo assim porque traz as sondas S1 e S2. O merge `c58e1409` da `develop` `707fea56` (#916) foi refeito com `git merge-tree --write-tree 3f79880b 707fea56`, e a árvore `c68694ce` é igual à do commit. `git show --cc` vem vazio, então não houve resolução à mão. O que entrou da base é o `recusa_do_publicar` do #916 (`bin/forge-check:3883-3911`), que já passou pelos pareceres dele e não toca `bin/forge_autorizacao.py`.

- ci: c58e140907dc71b44160b5bad0859321732048ac verde nas partes; `bateria (pareceres)` vermelho só pela ordem da construção

CI do head (run 45867133788, `headSha` c58e1409): verdes as 10 partes da suíte, os dois tetos de pulados, `bateria (python 3.14)`, `bateria (passos)`, `bateria (verificações longas)`, `instalação (python 3.14)`, `catraca` e `árvore já provada na develop`. `bateria (pareceres)` (job 140072744583) cai em R-REVIEW porque o parecer de review ficou desatualizado pela ADR 0018 mudada. É o mesmo portão que este parecer e o novo parecer de review fecham. O agregador `bateria` (job 140077895486) também está vermelho; não li o log dele (o acesso ao host do log foi negado) e o conto como dependente do `pareceres`, como na 1ª rodada.

Rodado aqui, no `c58e1409`: `python3 -m unittest tests.test_autorizacao tests.test_autorizacao_gravar` (65 testes, OK; eram 63 mais os dois das sondas).

Gatilhos: controle do Forge (autorização gravada do dono, ADR 0018), afrouxamento de regra por ordem do dono (R-CONFORMIDADE, R-DECISAO).

## Estado dos achados anteriores
- **A1 (recomendado): resolvido.** `docs/adr/0018-autorizacao-do-dono-gravada.md:203` traz agora a correção mínima pedida: R1 só produz efeito depois do merge de R3 na `develop`, e até lá o rótulo segue com o dono, item a item, mesmo com a concessão ativa. Fecha o intervalo em que o time rotularia sem a lista da `main` conferida. A guarda continua sendo de procedimento, porque nenhum código consome o ato para pôr o rótulo (como na 1ª rodada: `exigir_dono` em `hooks/conformidade.py:3514` compara só a conta). Agora quem ler a emenda não tem leitura que libere o rótulo antes de R3. Quem implementar o consumidor do ato (R3 ou depois) deve condicioná-lo ao R3 na `develop`. Isso fica como nota para aquele PR, não como achado deste.

## O que aperta, o que é neutro e o que afrouxa (delta)
**Aperta:**
- A emenda (`:203`) adia o efeito de R1 até R3 estar na `develop`. Até lá o rótulo `afrouxa-regra` fica com o dono, item a item, e a concessão gravada não muda nada na prática.
- A sonda S2 vira teste (`tests/test_autorizacao.py`, `test_sonda_s2_projeto_com_o_origin_do_forge_fica_inativo`). Raiz com `.forge/versao` e o `origin` do Forge fica inativa, com controle negativo (sem o arquivo, o mesmo `origin` é o Forge). A fronteira contra projeto (R2) passa a ter regressão própria.

**Neutro:**
- A sonda S1 vira teste (`test_sonda_s1_qualquer_host_antes_de_github_com_vale`). Ele fixa que qualquer host ou `file://` antes de `github.com/<slug>` conta como Forge. Não é caminho de ataque, porque quem escreve o `origin` já grava a URL exata, e a fronteira é o `.forge/versao` (1ª rodada). O teste só documenta o comportamento, e apertar o padrão no futuro pede inverter o teste de forma consciente.
- O merge da `develop` `707fea56` é limpo e idêntico ao remerge. Ele não muda nada do ato nem da autorização.

**Afrouxa:** nada novo neste delta. O afrouxamento da entrega (o rótulo pelo time no Forge, R1) é o da 1ª rodada, por ordem do dono (26/11 12:57), e agora só vale depois de R3.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Ferramentas: `forge-check parecer delta`, `git merge-tree`, `git show --cc`, os dois módulos de teste e `gh pr checks` com a API dos jobs. Faltou o `gitleaks` no PATH; o delta não traz credencial.
