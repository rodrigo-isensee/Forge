---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-mapa-testes
commit: 477dbefe80ed35a590dc2f689eea32cd39177fcd
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-14
---
# Review: v047 (E1.271, melhoria/v047-mapa-testes)

Code review (`R-REVIEW`) do intervalo `origin/develop` (`c5c3a449`) até `477dbefe`, 3 commits da E1.253: `quem_importa` em `bin/forge-testes`, testes em `tests/test_testes_tocados.py` (classe `QuemImporta`), duas specs de mutantes e o fragmento do changelog. Feito por uma instância que não fez a entrega.

## Achados
- A1 (bloqueante) bin/forge-testes:278 · Requisito (R-DECISAO): apoio de tests/ sai da suíte completa para o dirigido. A decisão 7 do estudo-custo-suite (21:21) e o adendo 2 da 075 (linha 71) dizem que isso afrouxa a opção C da M8 e só reabre pelo fato da A13. Tire o ramo apoio ou leve ao dono.
- A2 (bloqueante) bin/forge-testes:341 · Defeito provado (S1, S2): o fecho segue apoio que cita apoio, mas não teste que importa teste. Mudar tests/ambiente_git.py deixa fora os 20 test_fechar_*, cujo setUp é base.Fechar.setUp (chama sem_manutencao). É a variante V1t da M8.
- A3 (recomendado) tests/test_testes_tocados.py:165 · O caso apoio_volta_unica completo (oráculo MP-1-fechado do adendo 2) saiu do teste da decisão 7. Se o dono reabrir, o PR leva o afrouxamento no título com o motivo (CLAUDE.md); se não, o caso volta.
- A4 (recomendado) bin/forge-testes:327 · O ramo hook só alarga: nos 9 hooks/*.py o plano novo contém o antigo (agentes 27 para 29, _comum 27 para 30, pesado 27 para 28). Ele fecha o TESTE-RITMO-SEM-MAPA sozinho e pode entrar num PR à parte, sem o ramo apoio.

## Sondas
- S1 · brinquedo: tests/apoio_a.py; test_base.py faz `from apoio_a import f`; test_filho.py faz `import test_base` e usa Base.setUp; planejar(["tests/apoio_a.py"]) · espera: test_filho no plano ou "completo" · obtido: ('dirigido', ['test_base'])
- S2 · no repo, planejar(["tests/ambiente_git.py"]) contra os imports test_* -> test_* · espera: todo módulo que importa um do plano está no plano · obtido: dirigido com 99 módulos, faltam 35, entre eles test_fechar_auto_merge e os outros 19 test_fechar_*

## Parecer
**Reprovado** por A1 e A2.

A1. O ponto que o brief pede para o review: a opção C da M8 (2026-10-24) manda todo módulo de teste do diff para a suíte completa, e a decisão 7 do estudo-custo-suite (2026-11-07 21:21, "Não, por ora") recusou até a opção A. Essa opção levava o módulo de teste ao dirigido e mesmo assim mantinha "apoios e fixtures no caminho inteiro". O adendo 2 da 075 (`docs/arquitetura/versao-075-desenho-adendo-2.md:5,71,84,136`) diz que mapear apoio para quem o importa afrouxa a opção C. Diz também que a decisão já é do dono e reabre só pelo fato registrado no estudo: mais de 2 suítes inteiras por dia cujo único gatilho foi módulo de teste, medido no log da A13. O cartão TESTE-RITMO-SEM-MAPA e a E1.253 não trazem decisão nova do dono, e o pedido v047 não tem nenhuma linha DECISÃO DO DONO sobre apoios. Ler o apoio como "não é módulo de teste" não fecha o ponto, porque a própria decisão o separou e o manteve na completa. Sugestão: tire o ramo `apoio` de `IMPORTAVEL` (`bin/forge-testes:231`) e devolva `tests/apoio_volta_unica.py` ao caso `completo` (`tests/test_testes_tocados.py:166`). Se o dono quiser reabrir, ele recebe o pedido com a medida da A13.

A2. Mesmo com decisão do dono, o fecho está incompleto. O argumento da opção C foi exatamente este: a importação entre testes é direta, transitiva ou dinâmica, e o mapa não acompanha. O `quem_importa` cobre a importação direta, a varredura por glob e a cadeia apoio → apoio. Fica de fora a cadeia apoio → teste → teste: `test_fechar` importa `ambiente_git`, e os 20 `test_fechar_*` importam `test_fechar` e rodam o `setUp` dele. Contra o grafo de imports do repositório, `ambiente_git` deixa 35 módulos fora do plano, `apoio_jarvis` e `modelo_git` 24 cada, `apoio_volta_unica` 10 e `guarda_git` 5. A conferência `MapaCobreOQueOsTestesLeem` não pega o caso porque não olha imports de apoio.

Hooks (A4): comparei `planejar` da `origin/develop` com o do head nos 9 hooks. Nenhum perde módulo, então essa parte endurece e está correta. O critério de import (`^\s*import x\b` ou `from x import`) está coberto pelos casos `agentes_x` e `'agentes'` do teste.

Checklist de leitura: legível, sem código morto, guardas com mutantes declarados em duas specs (o autor relata 14 mortos). O teste do ciclo roda em subprocesso com `-I`, ambiente limpo e prazo. Tamanho: 126 linhas de código e teste (`bin/` 50, `tests/test_testes_tocados.py` 76), abaixo da orientação de 150 (M14). Commits em Conventional Commits, em português.

Suíte: o brief não abriu PR, então não há CI para citar. O autor relata 157 testes verdes (log do pedido, 21:56). Rodei só os testes novos e os vizinhos: `python3 -m unittest tests.test_testes_tocados.QuemImporta tests.test_testes_tocados.Mapa` deu 24 testes OK. Os testes passam, e A2 mostra que o defeito fica fora do que eles medem.
