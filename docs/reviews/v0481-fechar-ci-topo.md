---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-fechar-ci-topo
commit: 58852bf22fd6dcd4912d14b65813f701995cb38e
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0481

## Sondas

## Parecer
Aprovado, por delta de dd2fcada a 58852bf2 (E13.11). O `forge-check parecer delta` deu "revalida: sim" (bin/forge-fechar mudou depois do parecer anterior). Li só o delta: 10 linhas a mais e 3 a menos em `bin/forge-fechar`; o item inteiro segue dentro do teto H1.

Os três recomendados do parecer anterior estão resolvidos:
- A1 (branch criada que fica velha): `fim()` (bin/forge-fechar:443-445) apaga a branch com `git update-ref -d refs/heads/<ref> <sha criado>`, de modo que só a apaga se ela ainda está no sha criado. `branch_criada` se esvazia logo depois do passo 2 (1755), então o merge e a limpeza continuam usando a branch. Nas saídas antes do passo 3 (die no 1, 1c e 2) a branch sai, e entre a criação e o passo 3 não há `exit` de sucesso.
- A2 (vermelho do topo): o aviso só aparece quando o vermelho é de um topo diferente do merge (1245-1246). A reversão impressa continua sendo a do merge, e o aviso manda conferir o culpado.
- A3 (`--sem-limpar`): a parada da cópia principal só vale com `sem_limpar=0` (1693). Manual e fragmento descrevem os três como o código faz.

Alinhamento das specs: IL-M21 (`v047-integracao-em-lote-3.json`) e M2 (`mp1311-fechar-cartao.json`) voltaram a casar com a fonte, e o M8 aponta para o nome devolvido `test_commit_que_falta_aqui_pede_o_fetch`. `bin/forge-mutante --conferir --todas` no head sai com rc 1 e 26 linhas, mas são as mesmas 26 da base d49accf8 (diff vazio, conferido numa cópia exportada da base) e nenhuma é de `bin/forge-fechar` nem das specs do item. O item não traz desalinhamento novo.

Verificadores que rodei no Revisar-sha:
- `tests.test_fechar_ci_topo` e `tests.test_fechar_sha_conferido`: 21 testes, OK.
- `bin/forge-mutante --processos 1 tests/mutantes/v0481-fechar-ci-topo-2.json`: M9 (444), M10 (1755), M11 (1246) e M12 (1693) morreram.
- `--ids` IL-M21 (1244), M2 (1662) e M8 (1668): morreram.

As guardas mudadas no delta são 444, 1246, 1693 e 1755. Cada uma tem um mutante e um teste do ramo de falha; a linha 1670 só atribui, não é guarda. Não há `shellcheck` neste ambiente, então ele fica com o CI do #880. A suíte inteira também fica com o CI do #880: no head 58852bf2 há partes pendentes, e `bateria (pareceres)` está vermelha à espera dos pareceres.

Sondas (nenhuma prova bloqueante, por isso ficam fora do bloco), todas com o harness de `SoBranchRemota`:
- S1: o cenário do A1 de ponta a ponta. A primeira rodada para no passo 1, o autor reenvia, e a segunda rodada fecha com rc 3 (`--sem-limpar`) e `--match-head-commit` no sha novo; não aparece mais o "envie a branch".
- S2: outro processo move a branch criada durante o passo 1. O passo 1 para com rc 1 ("mudou"), a branch fica no sha novo e não aparece "apaguei".
- S3: uma branch local que já existia e o passo 1 parando. A branch fica, sem "apaguei".
