---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-mutante-varias-trocas
commit: e18a5b07c706a2e559c6dabb5b17fb357b51097e
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-24
---
# Review de segurança: v0478 E162.4 (PR #846, melhoria/v0480-mutante-varias-trocas)

Escopo: diff `0733715a..e18a5b07` (base = develop), 7 arquivos: `bin/forge-mutante` (MUTANTE-VARIAS-TROCAS), `tests/test_forge_mutante.py` (5 testes novos), specs `tests/mutantes/v0480-mutante-varias-trocas{,-2}.json` (M1 a M12, 1 isenta), realinhamento de CF5 (`v047-mutante-avisos.json`) e M6 (`vel-p1p10.json`), fragmento do changelog.

## Gatilhos
Gatilhos: controle do Forge (ferramenta do portão de mutação: a rodada que o QA usa como prova e a `--cobertura` do autor e do envio).

## Só aperta ou neutro
- Isenção: neutra. O mecanismo das `isentas` (`validar_isentas`, `cruza`, `isenta`, `MAXIMO_DE_ISENTAS`) não muda no diff. A única isenta nova (`v0480-mutante-varias-trocas-2.json`) cruza só a condição apagada `ocorrencias != 1` (`bin/forge-mutante:473(base)`), cuja guarda foi para `vezes_fora_de_uma` (`bin/forge-mutante:413`), provada por M7 e M10; `--cobertura --base 0733715a --rev e18a5b07` sai rc 0 com ela usada e nenhuma `isenta velha`.
- Validação da spec: aperta. A forma em lista fecha na dúvida (`trocas`, `bin/forge-mutante:402`): tamanho diferente, lista de 1 ou de 9+, par não texto, `de` vazio, `para == de` em qualquer par e `de` repetido são spec inválida (`ValidacaoDaSpec.test_varias_trocas_...`). Cada `de` uma vez no arquivo e sem sobreposição em `mutar` (`bin/forge-mutante:508-513`). A spec de uma troca segue com as mesmas mensagens.
- CF5 e M6: neutros. Mesma guarda na linha nova (AR-12); os dois morrem no head.
- Troca que não muda nada: na `--cobertura`, o par que não muda o ast da condição segue barrado por `casa` (`bin/forge-mutante:617`), por par.
- **Não fica neutro: a morte de graça** (A1). O mutante de várias trocas morre se qualquer par sozinho é morto pelo teste; a rodada reporta a morte na linha do 1.º par e a `--cobertura` credita cada par. Um par-isca que o teste mata empresta a morte a uma guarda sem teste.

## Achados
- A1 (bloqueante) bin/forge-mutante:755 · par-isca dá morte de graça: [guarda sem teste, troca que o teste mata] sai `morreu` na linha da guarda (rodada rc 0) e `coberta` na --cobertura (rc 0); o mesmo par sozinho sobrevive. Correção: cada par roda só e precisa sobreviver; senão o mutante é inválido.

## Sondas
- S1 · spec M2 de=["if y > 500:","        return 2\n"] para=["if y > 5000:","        return 3\n"] (lib.py:8 sem teste, return 2 testado); forge-mutante --cobertura --base develop · espera: sem mutante · lib.py:8 · obtido: coberta · lib.py:8 · x.json:M2, rc 0
- S2 · mesma spec; forge-mutante tests/mutantes/x.json · espera: M2 inválido ou sobreviveu (a guarda de lib.py:8 não tem teste) · obtido: M2 · morreu · lib.py:8, rc 0
- S3 · spec M1 de="if y > 500:" para="if y > 5000:" e M2 de=["if y > 500:","if x > 10:"] para=["if y > 5000:","if x > 99:"] · espera: M2 não morre se M1 sobrevive · obtido: M1 · sobreviveu · lib.py:8 e M2 · morreu · lib.py:8

## Detalhe dos achados
**A1.** Evidência: `trocas` (`bin/forge-mutante:402`) aceita pares em qualquer ponto do arquivo, sem relação entre eles; `mutar` (`bin/forge-mutante:501-523`) aplica todos e devolve a linha do 1.º par; a rodada classifica o mutante pelo teste da cópia com todas as trocas; `mutantes_do_diff` (`bin/forge-mutante:755`) parte o mutante em pares com o mesmo id, e `casa` credita cada par que toca uma condição do diff. Nada exige que a morte venha da combinação.
Caminho de ataque: o agente autor (atacante interno do portão, o mesmo modelo dos pareceres anteriores do mutante) quer o merge de uma guarda sem teste. Põe na spec um mutante de lista: o 1.º par muta a guarda sem teste, o 2.º muta uma linha que um teste já cobre (um `return`, outra condição). A `--cobertura` sai `coberta · arq:L` (rc 0), a rodada do QA sai `M · morreu · arq:L` (rc 0) na linha da guarda: a prova lida pelo review e pelo QA aponta a guarda certa e é falsa. Com uma troca só, isso não sai: a troca precisa cair no nó da condição e é ela que tem de ser morta. A forma legítima (guardas que se cobrem) e a isca são, hoje, indistinguíveis na saída.
Severidade: alta (anula a prova do portão de mutação para a guarda escolhida, sem rastro na saída; exige spec escrita pelo autor, que passa por review, por isso não crítica).
Correção mínima (dono: o autor da E162.1, `bin/forge-mutante`): no mutante de várias trocas, rodar também cada par sozinho com os mesmos `testes`; o mutante só vale se **todo** par sozinho sobrevive (é o que "se cobrem uma à outra" significa) e o conjunto morre. Par que morre sozinho: `inválido · o par <n> morre sozinho: vira mutante próprio` (rc 2). Teste de abuso: as sondas S2 e S3 como teste em `Execucao` (isca morta sozinha → rc 2), e a guarda nova ganha mutante na spec do PR. Custo: N+1 rodadas por mutante de lista, limitado por `MAXIMO_DE_TROCAS` (8) e `MAXIMO_DE_MUTANTES` (16); se o custo pesar, a alternativa é a `--cobertura` não creditar par cujo mutante não provou a sobrevivência individual, mas a rodada do QA segue falsa sem a primeira correção. Esforço: P/M.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Testes do arquivo tocado: `python3 -m unittest tests.test_forge_mutante` no head, 151 testes, OK (local; a suíte inteira é do CI do PR #846). Sondas S1 a S3 em repositório descartável no diretório temporário da sessão, só a ferramenta local. Sem segredo no diff (revisão manual; o diff não toca configuração nem credencial).
