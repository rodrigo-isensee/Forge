---
tipo: qa
contrato: 1
pedido: mutante-casa-espaco
branch: melhoria/mutante-casa-espaco
commit: 16beca149f3b033fc6c8149d1717d727c2e45af4
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-30
---
# QA: mutante-casa-espaco

Sem UX nem API; as obrigações são E1 e E2 do pedido `MUTANTE-CASA-ESPACO` e o desvio aceito na DECISÃO TÉCNICA de 2026-10-30 03:10 (sufixo medido no `de` inteiro, soma limitada ao menor texto, aceita quando uma posição possível cai no nó). Não escrevi o diff. Rodado em `~/.forge-contrib/wt/wt-qa-mutante-casa-espaco`, em paralelo ao review (ACELERA-RODADA).

## Achados

## Critério → teste → resultado
| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1 ternário com ` and False` depois da condição conta `coberta` | `Cobertura.test_de_e_para_que_dividem_o_espaco_junto_da_condicao_casam` (1ª asserção); C1, C6 | trecho um byte além do fim do nó | passou |
| E1 `de` e `para` que dividem o espaço (fim do nó de uma comprehension) | mesmo teste (2ª asserção); C3, C5 | fim do nó | passou |
| E1 o portão não afrouxa: fora do nó segue `sem mutante` | mesmo teste (3ª e 4ª asserções); C2, C5 | desliza para fora do nó; remoção maior que o nó | passou |
| E2 mutante comum que já casava segue coberto | `Cobertura.test_casamento_pelo_intervalo_do_no_e_as_travas_do_de` (existente, passa no head); C2, C3, C5 | `de` repetido, 8 caracteres, deslocamento em bytes | passou |
| E2 spec das guardas novas | `tests/mutantes/mutante-casa-espaco.json` (C1 a C6) | uma guarda por linha mudada | passou |

## Execução (resultado real)
- `python3 -m unittest tests.test_forge_mutante` (head `16beca1`): `Ran 68 tests in 12.611s`, `OK`.
- Vermelho: `bin/forge-testes --vermelho 042e5d8f73fc659615a4313c7213a661dfc32ce0 --modulos test_forge_mutante`; abre com `vermelho: base=042e5d8f73fc head=16beca149f3b módulos=test_forge_mutante (restrito por --modulos)` e `revertidos à base: bin/forge-mutante, changelog.d/mutante-casa-espaco.md`; fecha com `contagem: não prova (passa na base)=67; prova (asserção)=1`, rc=0. O teste novo `test_de_e_para_que_dividem_o_espaco_junto_da_condicao_casam` dá `H=ok · B=falha`; nenhum teste cai no HEAD.
- Mutantes: `bin/forge-mutante tests/mutantes/mutante-casa-espaco.json` (rev `16beca149f3b`): C1, C2, C3, C5, C6 `morreu`; `equivalente: C4`; rc=0.
- Conferência da lista contra o diff: as linhas de guarda mudadas são sufixo (419, C6), `comum` (420, C4), `primeira` (423, C1 e C2), `ultima` (424, C3) e a condição do `casa` (425-426, C5); todas têm mutante ou equivalente. A condição `len(...) >= 8 and dados.count(de) == 1` não mudou.
- C4 (equivalente): rodei uma busca própria, 2.702.464 combinações de `de`, `para`, nó real (de `condicoes`) sobre sete textos, comparando `casa` com e sem o `len(para)`: toda divergência é `False` contra `SyntaxError` (`para` que não é Python válido); com `para` válido, nenhuma. A justificativa se sustenta.
- Prova independente do portão: contra um oráculo (existe edição equivalente, dentro da janela do `de` e do nó, que produz o mesmo texto, com 8 caracteres não brancos e `de` único), o `casa` novo teve 0 divergências nas mesmas 2.702.464 combinações (sem os `SyntaxError`): não aceita o que não cai no nó e aceita o que cai.
- `bin/forge-mutante --cobertura --base 042e5d8f73fc659615a4313c7213a661dfc32ce0` (chamada separada): uma linha, `coberta · bin/forge-mutante:425 · tests/mutantes/mutante-casa-espaco.json:C5 · declarado, não provado`, rc=0; nenhuma `sem mutante`.
- `scripts/verificar-contribuicao.sh origin/develop`: rc=0 (`ok: nenhum segredo nem caminho pessoal no diff`).
- Lista de PA-7 conferida: lista de mutantes completa (AR-1), ramos de falha com teste (AR-2), sem lista negativa de ambiente, sem `python` sem `-I` em caminho que decide, nada de máscara de shell; nenhuma classe AR reaparece.

## Riscos
- O mutante equivalente C4 se separa só quando o `para` é Python inválido (o `casa` sem o `len(para)` levantaria `SyntaxError` em vez de devolver `False`); num spec real esse mutante já falharia na rodada normal, então o risco é só de nome.
