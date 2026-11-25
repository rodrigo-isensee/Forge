---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-corte-completo
commit: 036a78a16d09a3abf29ae94c02d4e6665e2b5227
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-25
---
# Review: v0481 (E13.16, #887, forge-fechar --corte: marca pronta para a promoção; classe C)

## Lido
`git diff 5fb8e328..036a78a1`: `bin/forge-fechar` (`medir_a_marca`, `corpo_da_marca`, `fragmentos_em`, `anexar_na_marca`, `rotulo_da_promocao` e as chamadas no `corte_da_versao`), `tests/test_fechar_corte.py`, `tests/mutantes/v0481-corte-completo{,-2}.json`, `tests/mutantes/v0480-d4-corte-contador-4.json`, `tests/pesos-d4.json`, `docs/fechamento-integrador.md` e o fragmento. Sem parecer de review anterior; li o de segurança (`docs/security/v0481-corte-completo.md`, reprovado pelo A1 dele, que reproduzi).

## Achados
- A1 (bloqueante) tests/test_fechar_corte.py:369 · CI vermelho no Revisar-sha, reproduzido: `python3 -I tests/test_reval_delta.py` falha (README.md citado 3 vezes em test_fechar_corte.py, CITACOES_CONHECIDAS diz 2). Mesmo achado do A1 da segurança; atualize a contagem ou reaproveite a citação.
- A2 (bloqueante) bin/forge-fechar:1615 · O ramo de falha da guarda `[ "$r" != erro ]` (leitura do origin em erro não anexa) não tem teste: a sonda S1 troca a guarda por `true` e os 28 testes de test_fechar_corte passam. Teste: ls-remote do ramo em erro, fragmento novo, rc 0, sem fetch do ramo nem pr edit; mutante na spec.
- A3 (recomendado) bin/forge-fechar:1556 · "rode o mesmo comando" não refaz o corpo: depois do envio a base comum vira a ponta da develop, `novos` fica vazio e a volta seguinte sai em 0 sem `pr edit` (o próprio test_fragmento_depois_do_corte confirma). Diga só "ajuste o corpo à mão", com o teto medido.
- A4 (recomendado) bin/forge-fechar:1538 · O anexo só roda se o --corte rodar entre o fragmento novo e o merge da marca; o --laco roda o --corte no fim da volta, e item e marca mesclados na mesma volta deixam o fragmento para a versão seguinte. Registre o limite no fechamento-integrador.md.

## Sondas
- S1 · spec com `if [ "$r" != erro ]; then anexar_na_marca` → `if true; then anexar_na_marca`, forge-mutante --processos 1 sobre tests.test_fechar_corte · espera: morreu · obtido: S1 · sobreviveu · bin/forge-fechar:1615

## Ferramentas
- `bin/forge-mutante --conferir --todas`: rc 1 com 26 trechos repetidos, saída idêntica à da base 5fb8e328 (nenhum de `bin/forge-fechar` nem das specs do diff): os trechos deste item conferem.
- `bin/forge-mutante` nas duas specs do item: M1 a M16 morreram; o M26, M28, M30 e M32 da spec v0480-d4 foram reescritos para os trechos novos sem afrouxar o que matam.
- `--cobertura --base 5fb8e328`: `não coberto: bin/forge-fechar` (shell não é analisado); as guardas li à mão: cada uma tem mutante declarado, e só a S1 mostra o ramo de falha sem teste.
- `python3 -I tests/test_fechar_corte.py`: 28 testes, OK. `shellcheck` ausente no PATH: fica para o CI. CI do PR #887: suíte parte 3/5 vermelha (A1).

## Parecer
Reprovado por A1 (CI vermelho) e A2 (guarda sem teste do ramo de falha). O resto confere com o pedido: nenhum passo novo mescla (o único `git merge` é local, na cópia do ramo da marca, enviado só por avanço, e o head novo invalida os pareceres); o anexo leva só fragmento ausente da base comum da develop com o ramo, o fragmento cortado e editado depois conflita e para (S1 da segurança), e o ramo de outra versão não é tocado porque o nome sai da versão do contador; o que barrava segue barrando (a medida que falha para antes do envio, a leitura em erro segue saindo em 0 sem anexar). `medir_a_marca` usa as funções do próprio forge-check com a base `origin/develop`, e o rótulo só é lido e impresso (R-CONTRIB). A data local, o corpo com o teto e os três pareceres e a classe na tela estão cobertos por teste com mutante. Revalidação: com A1 e A2 corrigidos, leio só o delta (`forge-check parecer delta`).
