---
tipo: review
contrato: 1
pedido: pn5-esperar-estado
branch: melhoria/pn5-esperar-estado
commit: 9e4eb2a3a6b5d0684f6ac9ead3a2a441a03508f2
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-29
---
# Code review: skill esperar-estado, espera de PR pelo estado (P-N5, PR B1-1)

Escopo: diff `99315cf...9e4eb2a` (3 commits: `49e15d8` skill e tech-lead, `abf92c6` teste e mapa, `9e4eb2a` fragmento) contra o pedido PN5-ESPERAR-ESTADO e a seção 2 do lote B1 do desenho `2026-10-29-desenho-h1-b1.md`.

## Conferido
- **Regras 1 a 3 do desenho:** a skill espera pelo estado do objeto (regra 1); o laço é uma chamada em primeiro plano de 17 voltas de 30 s (510 s de espera, abaixo dos 540 s), imprime `fim=teto` e sai com código 1 no teto, sem `timeout`/`sh -c`, `--watch` nem segundo plano (regra 2); lê o estado antes dos checks, sai fora de `OPEN` e trata o código 8 como pendente (regra 3). O código 8 conferido aqui: `gh pr checks --help` traz "Additional exit codes: 8: Checks pending". O laço é o esboço do desenho, sem desvio.
- **Sem marcador dos hooks:** `test_skill_sem_palavra_de_marcador_dos_hooks` varre o texto inteiro da skill; `MERGED`/`CLOSED` não casam `\bmerge\b`/`\bclose\b`. Os blocos passam pelos hooks `parecer` e `conformidade` com papel `tech-lead`, no clone do Forge e em projeto (rc 0, `BlocosPassamPelosHooks`): é a evidência de execução pedida.
- **Casos de teste da seção 3 (parte do PR):** OPEN depois MERGED com checks 8 (sai na 2.ª leitura, o caso P-N5), CLOSED, checks 0 e 1, teto em exatamente 17 leituras com rc diferente de 0, `gh` que falha (`fim=erro`, 0 leituras); asserções de texto (proibidos e voltas × intervalo ≤ 540) e frontmatter com o tech-lead carregando a skill. O laço testado é extraído do próprio `SKILL.md`, não uma cópia.
- **Mapa do `bin/forge-testes`:** `test_esperar_estado` entra em `FORGE_CHECK` (importa `test_hooks`, que executa o `bin/forge-check`, conforme o comentário da linha 65), na regra larga de `hooks/` (roda os hooks) e numa linha própria para `skills/esperar-estado/` e `agents/tech-lead.md`, antes da regra larga de texto. A contagem do `test_testes_tocados` passa de 30 a 31, coerente com a tupla.
- **Fora do escopo respeitado:** nada da parte do envio (B1-2): `agents/tech-lead.md:21`, `docs/fechamento-integrador.md` e `tests/test_forge.py` intocados; nenhum hook, `bin/forge-fechar` nem `scripts/promover-homolog.py`. `agents/tech-lead.md` muda só no frontmatter e numa linha da seção do Forge, como o desenho pede.
- **Teto M14:** 136 linhas de código e teste (`bin/forge-testes` 5, `tests/test_esperar_estado.py` 129, `tests/test_testes_tocados.py` 2), abaixo de 150; um comportamento só; sem arquivo de `hooks/` nem de `PROTEGIDOS`.
- **`R-NEUTRO`, `R-CUSTO`:** a skill não cita projeto nem stack; os testes usam `gh` e `sleep` falsos no `PATH`, sem rede. Fragmento `changelog.d/pn5-esperar-estado.md` presente.
- **Mutação:** não há guarda de código nova (o `bin/forge-testes` muda só dados do mapa); spec de mutantes não se aplica, como o pedido prevê ("se houver guarda de código").
- **Achados recorrentes (PA-7), lidos item a item:** AR-6 (máscara do shell): `e=$(gh …) || …` preserva o código da substituição e `c=$?` vem logo depois do `gh pr checks`; sem máscara. AR-9 (limite antigo no texto): 540 e 17 × 30 consistentes na skill, no teste e no fragmento. AR-4 (teste herda o ambiente do CI): ocorre de leve, ver A1. Os demais não alcançam o diff. Sem linha AR nova nesta rodada (decisão técnica de 2026-10-29 15:28 do T1-CONF-ESCOPO-REV); a classe do A1 é a do AR-4.

## Saída das ferramentas
- `python3 -m unittest tests.test_esperar_estado tests.test_testes_tocados`: `Ran 90 tests in 16.036s` · `OK` (head `9e4eb2a`).
- `bin/forge-testes --listar --base 99315cf`: "suíte completa (bin/forge-testes altera o mapa ou a configuração)"; a suíte completa fica no pre-push e no CI do PR (decisão M8), não refeita aqui.
- `python3 -m unittest tests.test_forge -k skills`: OK (inclui a citação das skills no frontmatter).

## Achados
- A1 (recomendado) tests/test_esperar_estado.py:51 · o laço roda com `dict(os.environ, …)`: um `BASH_ENV` do ambiente seria lido pelo `bash -c` e mudaria o resultado (classe AR-4, teste herda o ambiente); sugestão: retirar `BASH_ENV` e `ENV` do `env` do subprocesso.
- A2 (recomendado) skills/esperar-estado/SKILL.md:19 · `gh pr view` com código 0 e saída vazia faz `fim` ficar vazio e imprimir `fim=teto` na 1.ª volta; caso improvável, a repetição recomendada é inofensiva; sugestão: `fim="${e:-erro}"` no ramo fora de `OPEN`.

## Parecer
**Aprovado.** A skill segue as regras 1 a 3 e o esboço do lote B1 sem desvio, os seis casos do PR da seção 3 estão cobertos com o laço extraído do próprio `SKILL.md`, os blocos passam pelos dois hooks, o mapa e a contagem 31 são coerentes, e nada da parte do envio nem de hook entrou. Os dois achados são recomendações (nenhum defeito provado em uso real) e não devolvem a entrega.
