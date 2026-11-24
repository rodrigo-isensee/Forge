---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-mutante-varias-trocas
commit: 191484effc2af5506ddfc05f3c44b3944efa2349
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-24
---
# Review de segurança: v0478 E162.12 (PR #846, revalidação por delta)

Delta lido: `forge-check parecer delta` de `3671c052..191484ef`. No domínio, só `bin/forge-mutante`: `MAXIMO_DE_TROCAS = 2` (`bin/forge-mutante:135`), a mensagem de `validar_spec` (`bin/forge-mutante:367-368`) e o texto do uso. Fora do domínio, mas lidos porque provam a correção: `tests/test_forge_mutante.py` (teste novo da S4, lista de 3 recusada) e o M19 da spec `-3`. Já lido nas rodadas anteriores (no git, `786cd40c` e `d8ee1052`): o resto do diff `0733715a..3671c052`.

Gatilhos: controle do Forge (ferramenta do portão de mutação).

Achados anteriores: A1 (`786cd40c`), corrigido em `d8ee1052`. A2 (`d8ee1052`, isca de 3+ pares), corrigido neste delta: o teto de 2 recusa a S4 como spec inválida (rc 2), também no `--cobertura`. Provam a correção o teste `test_isca_de_tres_pares_e_recusada_antes_de_rodar` e o M19, que guarda o teto.

## Só aperta ou neutro
- Teto de 2 pares: aperta. A lista de 3 a 8 pares, que antes rodava, agora é spec inválida e nada roda (rc 2). A recusa vem de `trocas` (`bin/forge-mutante:409`), que devolve `[]` fora de 2 pares. `validar_spec` a usa nos três caminhos: a rodada, o `--cobertura` (`bin/forge-mutante:755`) e o `--conferir` (`bin/forge-mutante:837`). Nenhum caminho aceita a lista de 3 sem validar.
- Com 2 pares, o par sozinho é o conjunto sem o outro, e a checagem `par_que_nao_sobrevive` (`bin/forge-mutante:986-998`) passa a provar que cada par é necessário à morte. Isso fecha o A2.
- Spec de uma troca, `equivalente`, mutante de lista que sobrevive e `--cobertura` de 2 pares: neutros (sem mudança no delta).
- Resto, fora do delta: "necessário" ainda não é "testado". Com 2 pares, um par pode servir só de escudo para o outro (A3, sonda S7).

## Achados
- A3 (recomendado) bin/forge-mutante:978 · par-escudo de 2 pares (S7): guarda G sem teste próprio + guarda P de outra condição que a esconde do teste; cada par sobrevive sozinho, o par morre e sai `morreu` na linha de G, que o `--cobertura` credita. Correção: a saída nomeia as duas linhas.

## Sondas

## Detalhe dos achados
**Sondas refeitas no head 191484ef** (repositório descartável no diretório temporário da sessão, fixture no molde de `Execucao`; os setups são os da rodada `d8ee1052`). Nenhuma prova bloqueante, por isso ficam aqui e não no bloco `## Sondas`.
- S1 (`--cobertura`, lista [guarda, `return 2`]): `coberta · lib.py:2 · tests/mutantes/s.json:M2 · declarado, não provado`. Neutro, igual à rodada anterior.
- S2 (M1 de uma troca e M2 de 2 pares): `M2 · inválido · lib.py:2 · o par 2 morre sozinho: vira mutante próprio`, rc 2. Igual.
- S3 (2 guardas, a 2.ª testada): `M2 · inválido · lib.py:2 · o par 2 morre sozinho`, rc 2. Igual.
- S4 (isca de 3 pares): a rodada sai `spec inválida; nada foi executado`, rc 2. O `--cobertura` sai `spec inválida (M2: ... de 2 pares)`, rc 2. Antes: `morreu`, rc 0. Corrigida.
- S5 (isca de comentário): `M2 · sobreviveu · lib.py:3`, rc 1. Não é isca, igual.
- S6 (o mesmo par nas duas ordens): `M2 · inválido · lib.py:2 · o par 2 morre sozinho` e `M3 · inválido · lib.py:6 · o par 1 morre sozinho`, rc 2. Igual.
- S7 (procura de isca de 2 pares). `lib.py`: `if x < 0: return 0` (linha 2), `if y > 500: return 3` (linha 4), `return max(x, 0)`; teste `limite(-5) == 0`. Spec M2: de=["if y > 500:","if x < 0:"], para=["if y < 500:","if x < -100:"]. Espera: sem morte creditada à linha 4. Obtido: `M2 · morreu · lib.py:4`, rc 0, e o `--cobertura` sai `coberta · lib.py:4 · tests/mutantes/s.json:M2 · declarado, não provado`. Contraprova: os mesmos testes deixam sobreviver cada troca sozinha e a troca de borda de G (`if y > 5000:`), todas com rc 1. G não tem teste próprio, e P não cobre a mesma condição: só desvia o teste para G.
- S8 (redundância legítima, [`if x < 0:`, `if x <= -1:`]): `M2 · morreu · lib.py:2`, rc 0. O recurso segue servindo ao uso dele.

**A3.** Evidência: S7. A checagem de `bin/forge-mutante:978-998` prova que cada par é necessário à morte, mas não que os dois guardam a mesma condição. Com 2 pares, P pode ser uma guarda de outra condição que fica antes de G no caminho. Desligada, P manda o teste para G, que o teste nunca alcança no programa sem mutação. O teste não prova o comportamento de G, e a troca de borda de G sobrevive. Mecanicamente, o par-escudo não se distingue da redundância legítima (S8), em que a 2.ª guarda também não é alcançada. Por isso a correção é tornar o escudo visível, não detectá-lo.
Caminho de ataque: o agente autor quer o merge de uma guarda sem teste. Ele a declara como 1.º par ao lado de uma guarda testada de outra condição e escolhe uma troca que inverte G (inverter o comparador é a troca padrão). A rodada do QA e o `--cobertura` mostram só a linha de G. Quem lê o relatório não vê o par. O desvio só aparece lendo a spec e comparando as duas condições.
Severidade: média. Anula a prova da guarda escolhida, como o A1 e o A2, mas pede um par visivelmente estranho na spec: duas guardas de variáveis diferentes, declaradas como "guardas que se cobrem".
Correção mínima (dono: o autor da E162.9, `bin/forge-mutante`), esforço P:
- A linha da saída do mutante de 2 pares e a linha `coberta` do `--cobertura` nomeiam as duas linhas, por exemplo `M2 · morreu · lib.py:4 (par com lib.py:2)`.
- O texto do uso diz que o par só vale se as duas guardas cobrirem a mesma condição, e que isso se confere na spec.
- A S7 entra como teste em `Execucao`, verificando que a saída traz as duas linhas.
Não há correção mecânica proporcional que separe a S7 da S8. A conferência semântica fica com o review da spec, e o recurso precisa mostrar ao revisor o que ele tem de conferir.

## Riscos aceitos e ferramentas
Nenhum risco aceito. O A3 é de segurança e, como `recomendado`, volta ao autor e é corrigido antes do merge (`R-REVIEW`). Teste do arquivo tocado: `python3 -m unittest tests.test_forge_mutante` no head 191484ef, 154 testes, OK (local; a suíte inteira roda no CI do PR #846). As sondas S1 a S8 rodaram só com a ferramenta local. O delta não tem segredo (revisão manual).
