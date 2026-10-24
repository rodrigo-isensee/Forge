---
tipo: revisao-seguranca
contrato: 1
pedido: catraca-pr-mesclado
branch: melhoria/catraca-pr-mesclado
commit: 676dd62a3ae429574c961e3eebf0fb3a1b64ebc8
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-24
---
# Review de segurança: catraca-pr-mesclado

Escopo: diff `e833d3c..676dd62` (`tests/catraca.py`, `tests/test_catraca.py`, `changelog.d/catraca-pr-mesclado.md`). A correção põe a cadeia de primeiro pai da prova do squash sobre a ponta da branch promovida (`ponta_promovida`, segundo pai do merge de teste) e imprime o motivo quando a conferência do PR mesclado não libera.

## Gatilhos
`controles do Forge`: a catraca anti-piora (ADR 0008), que decide quando o rótulo `afrouxa-regra` de um PR mesclado libera a promoção.

## Achados

## Detalhe dos achados
Sem achado bloqueante nem recomendado. A conferência feita:

1. **A correção não libera mais do que a regra já liberava.** `tests/catraca.py:929` só troca a ponta quando o head tem exatamente 2 pais e o primeiro é a base resolvida; no CI a base é o próprio primeiro pai do merge de teste (`.github/workflows/catraca.yml:39`), então a ponta é a ponta da `develop` do PR de promoção, que só quem envia à `develop` controla (branch protegida). A ponta entra só na prova de que M é squash na cadeia de primeiro pai (`tests/catraca.py:944`); continuam inteiras as outras condições: PR de promoção do próprio repositório (`tests/catraca.py:858`), PR candidato mesclado na `develop`, base e head do próprio repositório (`tests/catraca.py:972`), M em base..head, último `labeled` do dono sem app, S do instante do rótulo ancestral do `head.sha` da API, a mesma violação em S e o arquivo do head com o mesmo blob e modo do de S (`tests/catraca.py:1032`, contra o `head` original, não contra a ponta). Antes, a cadeia de primeiro pai de base..merge-de-teste era só o próprio merge e a prova nunca passava no CI: a correção devolve o comportamento que a regra já previa (#242, #250), sem transitividade nova.
2. **Ponta forjada.** Sonda local em repositório descartável (`$TMPDIR/security-engineer-catraca-pr-mesclado/`), chamando `ponta_promovida` do head revisado: merge de teste (base, X) devolve X; 2 pais com o primeiro fora da base, base como segundo pai, octopus (3 pais), commit de um pai, base inexistente, head inexistente e base em forma de opção (`--all`) devolvem o próprio head (comportamento anterior, que falha fechado). Merge forjado empurrado à `develop` não ganha nada: no CI o head é o merge de teste e só um nível é desembrulhado; e mesmo com a ponta num commit arbitrário, M ainda precisa ser o `merge_commit_sha` que a API diz mesclado na `develop`, com o rótulo do dono e o arquivo idêntico ao rotulado.
3. **Fetch de `refs/pull/<n>/head` com `persist-credentials: false`.** Código inalterado (`tests/catraca.py:908`, `tests/catraca.py:913`): `n` é inteiro, o destino é só `refs/catraca/pull/<n>` (sem branch, tag nem FETCH_HEAD), o PR já foi conferido como do próprio repositório antes do fetch (`tests/catraca.py:972`, o head de fork sai aí) e o commit trazido precisa ser o `head.sha` da API (`tests/catraca.py:954`). Ref de terceiro não entra; sem credencial em repositório privado o fetch falha e vale como sem rótulo.
4. **Motivo impresso** (`tests/catraca.py:1054`). Só texto fixo, sha truncado em 12, nome do tipo da exceção (sem o conteúdo) e caminhos de arquivos protegidos que a catraca já imprime nas violações; nenhum token nem corpo de resposta da API vai ao log. Não há texto livre do autor do PR que permita injetar comando de workflow.
5. **Testes:** `tests.test_catraca.RotuloDePrSquash` (27 testes) verde no head revisado, incluindo o merge de teste das promoções #310 e #317 e o M fora da cadeia de primeiro pai da `develop`, que segue pedindo o rótulo.

Observação (sem achado): o workflow roda o `catraca.py` da base, então a correção só vale nas promoções depois que chegar à `homolog`; é o desenho já aceito (ADR 0008), não defeito.

PA-7 (`docs/engineering/achados-recorrentes.md`): sem achado recorrente registrado; nada a conferir.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Revisão manual estática e sonda local passiva. `gitleaks`, `zizmor`, `actionlint` e `semgrep` não estão no PATH (lacuna registrada; nenhum workflow mudou nesta entrega).
