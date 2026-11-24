---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-mutante-varias-trocas
commit: 3671c05271cd1760044a2bdc874b064cd28e835a
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-24
---
# Review de segurança: v0478 E162.8 (PR #846, revalidação por delta)

Delta lido: `forge-check parecer delta` de `e18a5b07..3671c052`. No domínio, só `bin/forge-mutante` (`provar` e a nova `par_que_nao_sobrevive`, `bin/forge-mutante:977-998`, e o texto do uso). Fora do domínio, mas lidos porque são a prova da correção: `tests/test_forge_mutante.py` (2 testes novos) e as specs `-2` e `-3`. Já lido na rodada anterior (no git, `786cd40c`): o resto do diff `0733715a..e18a5b07`.

Gatilhos: controle do Forge (ferramenta do portão de mutação).

## Só aperta ou neutro
- Par que morre sozinho, ou que não roda sozinho: aperta. Um mutante de lista morto passa a ser `inválido` (rc 2) se algum par sozinho não sobrevive (`bin/forge-mutante:977-980`), e na dúvida fecha: `sem veredito` ou `inválido` do par sozinho também invalidam (`bin/forge-mutante:995-996`).
- Spec de uma troca, `equivalente` e mutante de lista que sobrevive: neutros. A checagem só roda com `morreu` e mais de um par.
- `--cobertura`: neutra. Segue creditando cada par, mas com `declarado, não provado`. A prova continua sendo a rodada, que agora recusa a isca de 2 pares.
- **Não fica neutro: com 3 ou mais pares** (A2). Cada par sobreviver sozinho não prova que todos são necessários. Uma guarda sem teste ainda entra como 1.º par ao lado de um par legítimo de guardas que se cobrem.

## Achados
- A1 (bloqueante) bin/forge-mutante:755 · par-isca dá morte de graça. Estado: corrigido para o par que morre sozinho (S1 a S3 refeitas); resta a forma de 3 pares, aberta como A2.
- A2 (bloqueante) bin/forge-mutante:989 · com 3+ pares, [guarda sem teste, guarda A, guarda B], onde A e B se cobrem, todo par sobrevive sozinho e o conjunto morre: a rodada sai `morreu` na linha da guarda sem teste (rc 0). Correção: cada conjunto sem um dos pares também precisa sobreviver.

## Sondas
- S1 · spec M2 de=["if y > 500:","        return 2\n"] para=["if y > 5000:","        return 3\n"]; forge-mutante --cobertura --base <base> · espera: a rodada recusa (a cobertura é declarativa) · obtido: coberta · lib.py:2 · s.json:M2 · declarado, não provado, rc 0 (neutro)
- S2 · mesma spec com M1 de="if y > 500:"; forge-mutante spec.json · espera: M2 inválido · obtido: M2 · inválido · lib.py:2 · o par 2 morre sozinho: vira mutante próprio, rc 2
- S3 · M2 de=["if y > 500:","if x > 10:"] para=["if y > 5000:","if x > 99:"] · espera: M2 inválido · obtido: M2 · inválido · lib.py:2 · o par 2 morre sozinho, rc 2
- S4 · guarda `if y > 500:` sem teste e redundantes `if x < 0:`/`if x <= -1:` (teste limite(-5)==0); M2 de=["if y > 500:","if x < 0:","if x <= -1:"] para=["if y > 5000:","if x < -100:","if x <= -100:"] · espera: M2 inválido · obtido: M2 · morreu · lib.py:2, rc 0
- S5 · isca de comentário: M2 de=["if y > 500:","# limite de x"] para=["if y > 5000:","# limite de y"] · espera: sem morte · obtido: M2 · sobreviveu · lib.py:2, rc 1 (não é isca)
- S6 · o mesmo par em outra ordem: M2=[guarda, `return x`→`return -x`] e M3=[`return x`→`return -x`, guarda] · espera: os dois inválidos · obtido: M2 · inválido · o par 2 morre sozinho; M3 · inválido · o par 1 morre sozinho, rc 2

## Detalhe dos achados
**A2.** Evidência: `par_que_nao_sobrevive` (`bin/forge-mutante:985-998`) testa só os conjuntos de um par. Com 2 pares, "o outro par sozinho" é o mesmo que "o conjunto sem este par", e a checagem basta. Com 3 a `MAXIMO_DE_TROCAS` (8, `bin/forge-mutante:135`) pares, não basta: o par 1 pode ser dispensável (o conjunto sem ele também morre) e mesmo assim recebe a morte na linha da saída (a do 1.º par) e o crédito da `--cobertura`. Na S4, a `--cobertura` sai `coberta · lib.py:2 · s.json:M2`.
Caminho de ataque: é o mesmo do A1. O agente autor quer o merge de uma guarda sem teste e a põe como 1.º par de uma lista em que os outros pares são guardas redundantes já testadas. A redundância é a forma legítima do recurso, por isso a isca não chama atenção no review. A rodada do QA sai `M2 · morreu · lib.py:<guarda>` (rc 0).
Severidade: alta (a mesma do A1: anula a prova do portão para a guarda escolhida e não deixa rastro na saída).
Correção mínima (dono: o autor da E162.5, `bin/forge-mutante`): em `par_que_nao_sobrevive`, além de rodar cada par sozinho, rodar cada conjunto sem o par n (os outros N−1 pares juntos), que também precisa sobreviver. Se morrer: `inválido · o par <n> não é necessário: o conjunto sem ele morre`. Com N=2 os dois testes coincidem, e dá para pular o repetido. O custo fica em 2N+1 rodadas, até 17 com 8 pares. Outra saída, mais simples: limitar `MAXIMO_DE_TROCAS` a 2, o que torna a checagem atual suficiente. Teste de abuso: S4 como teste em `Execucao` (rc 2 e a mensagem do par 1).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Testes do arquivo tocado: `python3 -m unittest tests.test_forge_mutante` no head 3671c052, 153 testes, OK (local; a suíte inteira roda no CI do PR #846). As sondas S1 a S6 rodaram em repositório descartável (fixture `Execucao`) no diretório temporário da sessão, só com a ferramenta local. O delta não tem segredo (revisão manual).
