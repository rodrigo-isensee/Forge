---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-mapa-testes
commit: 2263bc0d9d032d4d79d42c4e57641b073108f4dc
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-14
---
# Review: v047 (E1.284, melhoria/v047-mapa-testes)

Revalidação do code review (`R-REVIEW`) por delta, feita por uma instância que não fez a entrega. Rodada anterior (E1.271, head `477dbefe`): reprovado por A1 (o ramo dos apoios afrouxava a opção C da M8 sem decisão do dono) e A2 (o fecho não seguia teste que importa teste). A3 e A4 eram recomendados.

## Achados
- A1 (recomendado) bin/forge-testes:328 · M1 morre por erro (TypeError em achado[1] com `if False`), não por asserção. Vale como morto, mas um caso com caminho fora de hooks/ que o mutante deixe passar sem erro tornaria a morte explícita.
- A2 (recomendado) bin/forge-testes:333 · `{**lidos, **textos}` junta por stem hooks/ e tests/: um hook e um apoio com o mesmo nome se sobrescrevem e o fecho perde os imports de um deles. Hoje não há colisão (conferido); vale uma nota ou chave por pasta.

## Sondas

## Parecer
**Aprovado** no head `2263bc0d`.

Delta lido: `forge-check parecer delta docs/reviews/v047-mapa-testes.md` (rc=0), intervalo `477dbefe..2263bc0d`, commits `c808c573`, `e71680ab`, `2263bc0d`; no domínio `bin/forge-testes`, `changelog.d/v047-mapa-testes.md`, as duas specs em `tests/mutantes/` e `tests/test_testes_tocados.py`. Já lido e não relido: o restante da branch, no parecer da rodada anterior.

Achados da rodada anterior:
- A1 resolvido. O ramo `apoio` saiu (`IMPORTAVEL`, `APOIO_NA_COMPLETA`, `VARRE_TESTS` e o `fnmatch` foram apagados); `quem_importa` devolve vazio fora de `hooks/` e o `if casou is None` volta ao texto da `develop` (`c5c3a449`, linha 268). No repositório, `tests/ambiente_git.py` e `tests/apoio_jarvis.py` dão `completo`. Fica a decisão 7 do dono intacta.
- A2 resolvido no que restou (o hook). O fecho agora parte do hook e dos módulos da regra (`junto`) e segue hook, apoio e módulo de teste que importa um deles. O teste permanente `test_no_repositorio_o_plano_do_hook_traz_todo_teste_que_importa_um_modulo_do_plano` refaz a sonda S2 pela árvore sintática, independente da expressão do script, nos 9 hooks (mínimo afirmado: 9).
- A3 resolvido: `tests/apoio_volta_unica.py` voltou ao caso `completo` (`tests/test_testes_tocados.py:165`), e `test_apoio_de_tests_importado_segue_na_completa` (linha 334) trava o ramo de falha.
- A4 atendido: o PR ficou só com o hook.

Efeito medido: o plano de cada hook cresceu de 27-30 para 46-65 módulos (`_comum` 65, `agentes` e `pesado` 64, `doutor` 46, os outros 61), porque o fecho agora traz quem importa os módulos da regra (`test_hooks` e afins). É o lado seguro (só alarga) e continua dirigido; registro como medida, não como achado.

Checklist de leitura sobre o delta: `importados` e `quem_importa` são curtos e legíveis; o regex `IMPORTA` lê import também em texto que vai ao subprocesso e em comentário, o que só alarga. O ajuste do `test_oraculo_entra_no_plano_sem_mudar_a_contagem` copia os textos reais para o brinquedo, necessário porque o fecho lê os imports. Teste do ciclo em subprocesso com `-I`, ambiente limpo e prazo. Fragmento do changelog atualizado e coerente com a decisão 7. Commits em Conventional Commits, em português. Tamanho contra a base: `bin/forge-testes` 43 e `tests/test_testes_tocados.py` 81, 124 linhas, abaixo dos 150 (M14).

Mutantes (rodados por mim, 1 processo): `bin/forge-mutante tests/mutantes/v047-mapa-testes.json` M1 a M8 morreram (M1 por erro, ver A1); `tests/mutantes/v047-mapa-testes-2.json` M9 a M13 morreram. `bin/forge-mutante --cobertura --base 477dbefe` aponta só `sem mutante · bin/forge-testes:274 · casou is None`, que é a linha da `develop` restaurada, sem mudança contra a base do pedido.

Suíte: sem PR aberto, não há CI para citar. Rodei os vizinhos: `python3 -m unittest tests.test_testes_tocados.QuemImporta tests.test_testes_tocados.Mapa tests.test_testes_tocados.Oraculos` deu 26 testes OK.
