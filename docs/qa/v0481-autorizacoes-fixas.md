---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-autorizacoes-fixas
commit: 39b5b066122f8f6c1883aef2bd692b147d05d8a1
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-26
---
# QA: v0481 AUTORIZACOES-FIXAS (#901, E14.52; 1ª rodada no 4c88ca81, revalidação no 39b5b066)

Diff lido contra o merge-base com a `develop` (34ab6714): `bin/forge_autorizacao.py`, `bin/forge-fechar` (relógio do corte), `bin/forge-testes` (mapa), emenda da ADR 0018, changelog e os três testes. O plano nasce das decisões F1 a F5 da emenda e da ordem do dono de 25/11 07:52 (não há UX nem API). Não escrevi teste novo: os testes do autor cobrem a emenda e conferi o que eles provam.

## Revalidação por delta (head 39b5b066, E14.76)
Delta lido: `git diff 4c88ca81..39b5b066`. Código: uma linha de `bin/forge-fechar` (:674, `comum=` em `limpar_clones`), de `cd "$(git rev-parse --git-common-dir)" && pwd -P || true` para `if cd ...; then pwd -P || true; else :; fi` (SC2015 do shellcheck 0.9.0). O resto do delta são os pareceres do review e da segurança. Escopo, critérios e mutantes da 1ª rodada não mudaram.
- Equivalência: sonda em arquivo (bash): dentro de um repositório dá o caminho físico do `.git` (`/workspaces/Forge/.git`); fora dele `git rev-parse` sai vazio, `cd ""` fica no lugar e dá o diretório atual, igual ao código antigo; o `else :` só cobre o `cd` falho, que antes caía no `|| true` e dava vazio. Mesmo resultado nos dois casos.
- `shellcheck -S style bin/forge-fechar` (0.9.0 local): limpo, rc 0.
- Módulos tocados: `python3 -m unittest tests.test_fechar` 115 testes OK (140 s); `tests.test_fechar_limpar_clone tests.test_fechar_corte` 46 testes OK (54 s). Os mutantes da lista não tocam essa linha (nenhuma guarda do `corte_diario` mudou); não rerrodados.
- ci (leitura): `gh pr checks 901` e `gh run view 45751838425` (run do head 39b5b066). Verdes: suíte 3.12 e 3.14 (partes 1 a 5), teto de pulados 3.12, `bateria (passos)`, `bateria (verificações longas)`, instalação 3.14, árvore já provada, `catraca`. Fora dos que contam: `bateria (pareceres)` e `bateria` (esperam os pareceres). `teto de pulados (python 3.14)` saiu `cancelled`: o push do parecer da segurança (6a9b5955, só docs) abriu um run novo e cancelou o anterior; não é falha. Por isso não gravo a linha `- ci: <sha> verde` ainda: falta o teto 3.14 verde no mesmo sha.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| F1 atos fixos, alvo `fixo` e validade `fixa` só entre si; sem teto da D1 | `test_autorizacao`; mutantes M1, M2, M3, M19, M20 | `fixa` em ato com prazo, prazo em ato fixo, alvo cruzado | passou |
| F2 leitura do texto: ativa só sem alvo marcado nem termo; vocabulário só para os fixos | `test_autorizacao_gravar`; M4, M5, M6, M21, M22 | termo de validade em ato fixo, palavra fora do vocabulário, vocabulário fixo vazando para os outros atos | passou |
| F3 corte abaixo do teto: item, 06:00 locais, um por dia, `corte-diario` ativa, forma da saída, id no corpo da marca | `test_fechar_corte.CorteDiario` (5 casos); M10 a M18 | 0 item, antes das 06:00, relógio ilegível, CHANGELOG ilegível, versão de hoje, saída fora da forma | passou |
| F3 leitura `ler --ato corte-diario` (a mais nova ativa; rc 1 sem ela) | `test_autorizacao`; M7, M8, M9 | nenhuma ativa, retirada, ato errado | passou |
| F4 `so-aperta-com-seguranca` só gravada e lida | leitura do diff: nenhum outro código lê `.forge/autorizacoes` além de `bin/forge_autorizacao.py` e do despacho do `bin/forge-check` | n/a | passou |
| F5 sha do gravador muda, a concessão lê `adulterada` | caminho existente (`problemas`, `Gravado-por`), sem código novo | n/a | passou |
| `rotulo-afrouxa-regra` e `merge-main` não mudam | testes antigos do módulo verdes; alvo `fixo` ou validade `fixa` neles lê `adulterada` (M1, M3) | validade e alvo cruzados | passou |
| ESCOPO+ E14.64: `test_fechar_corte` no mapa `FORGE_CHECK` | diff de `bin/forge-testes` | n/a | passou |

## Cenários e resultado real
- Módulos tocados: `python3 -m unittest tests.test_autorizacao tests.test_autorizacao_gravar tests.test_fechar_corte` rodou 92 testes, OK, em 122 s. A suíte inteira ficou com o CI (G3). O D2 do autor, que falha em `test_oraculo_sempre_atual` por falta de `/proc` no sandbox, está fora do diff e não o reproduzi.
- Vermelho antes do verde: `bin/forge-testes --vermelho 34ab6714cbc13e41c35907b13cb3a6b2b71d9688 --modulos test_autorizacao,test_autorizacao_gravar,test_fechar_corte`, saída 0. Contagem final: `não prova (passa na base)=80; prova (API ausente)=3; prova (asserção)=9`. Os testes novos do corte diário caem na base com asserção (abaixo do teto às 06h, antes das 06h, CHANGELOG ilegível, sem autorização ativa ou saída fora da forma, sem item). `test_no_teto_o_corpo_nao_cita_autorizacao` passa na base de propósito: guarda o comportamento que não mudou.
- Mutantes: `bin/forge-mutante` nas três specs (`v0481-autorizacoes-fixas.json`, `-2`, `-3`, 22 mutantes), `--processos 4`, saída 0, M1 a M22 todos `morreu`. O M7 morreu por erro do teste declarado sob o mutante (que passa sem ele), forma aceita pela regra.
- Lista contra o diff: `bin/forge-mutante --cobertura --base 34ab6714` dá como coberta cada linha de Python mudada em `bin/forge_autorizacao.py` (121, 122, 124, 149, 343, 344, 347, 349, 355, 447, 448, 457). O `bin/forge-fechar` sai `não coberto` por ser shell; conferi à mão as guardas do `corte_diario` e do `corte_da_versao` (linhas 1582 a 1594, 1637 e 1638) contra M10 a M18, uma por guarda, sem lacuna. O resto do diff dele é a passagem do argumento da autorização ao corpo da marca, coberta por `test_abaixo_do_teto_as_06h_corta_e_grava_a_autorizacao_no_corpo`.
- Sondas de leitura: `concessoes` ordena por número (A-10 depois de A-2), então a última ativa é a mais nova; o `datetime.max` do ato fixo só entra em comparação, nunca em formatação.

## Coerência com a ordem do dono de 25/11 21:52 e o cartão ROTULO-SO-APERTA-PELO-TIME
O desenho deixa o rótulo como ato do dono. A F4 diz que `so-aperta-com-seguranca` só é gravada e lida, que nenhuma ferramenta a consome e que não libera rótulo, merge na `main` nem `R-CUSTO`; `rotulo-afrouxa-regra` e `merge-main` seguem com alvo, validade e teto de antes. Nada no diff aplica rótulo. Isso é mais estrito que a frase de 21:52 (o rótulo onde a segurança escreveu só aperta é do time): a emenda não implementa essa parte, e o cartão ROTULO-SO-APERTA-PELO-TIME segue aberto até decisão do dono ou autorização gravada (R-CONFORMIDADE, ADR 0018). Não é defeito deste PR e não bloqueia.

## Resultado
Aprovado no head 39b5b066 (delta correto e equivalente; o resto vale da 1ª rodada, 4c88ca81), sem bug aberto: F1 a F5 e o ESCOPO+ cobertos, vermelho visto, 22 mutantes mortos, módulos tocados verdes e CI verde nas partes que contam.
- ci: 39b5b066122f8f6c1883aef2bd692b147d05d8a1 verde
