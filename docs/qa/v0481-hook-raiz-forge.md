---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-hook-raiz-forge
commit: 10c1b834b6fb062bfb2f9b7d9020dbbcbe828abf
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-27
---
# QA: v0481 hook-raiz-forge (E37.8, PR #930, volta 1)

Delta baffa052..10c1b834. A1 e A2 da volta 0 (fixture estadoclone-rm-git-bloqueia e índice das fixtures) e o A3 (mutantes das entradas de EM_VIGOR_NA_RAIZ) estão resolvidos.

## Critério → teste → resultado
Sem docs/ux nem contrato de API (conserto de trava); os critérios vêm da etapa E37.1 do pedido e do corpo do PR.

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| CA-1 Write, Edit e MultiEdit em .githooks/ e .git/hooks/ da raiz barram | fixtures raiz-forge-s0-write-githooks, raiz-forge-write-git-hooks, raiz-forge-multiedit-commit-msg, raiz-forge-jarvis-edit-devcontainer | papel jarvis incluído; MultiEdit | passou |
| CA-2 Write em .devcontainer/devcontainer.json da raiz barra | raiz-forge-s2-write-devcontainer, raiz-forge-s4-projeto-devcontainer | sonda s2 | passou |
| CA-3 escrita e remoção pelo Bash barram | raiz-forge-bash-redireciona-githooks, raiz-forge-bash-cp-devcontainer, raiz-forge-bash-rm-devcontainer | remover a pasta que contém a entrada | passou |
| CA-4 alvo na raiz barra mesmo com a pasta corrente em wt/* | raiz-forge-wt-bash-devcontainer-da-raiz, raiz-forge-wt-write-githooks-da-raiz, raiz-forge-sessao-em-worktree-copia-principal | cópia principal x pasta corrente | passou |
| CA-5 leitura e cópia de wt/ seguem livres | raiz-forge-leitura-githooks-libera, raiz-forge-wt-*-da-copia-libera | leitura; cópia de trabalho | passou |
| CA-6 vizinho, scripts/ e repositório fora do Forge livres | raiz-forge-vizinho-devcontainer-libera, raiz-forge-sonda-s1-scripts-libera, raiz-forge-outro-repo-libera | arquivo vizinho; outro repositório | passou |
| CA-7 comportamento anterior preservado (mensagem das recusas existentes) | suíte do CI, fixture estadoclone-rm-git-bloqueia | mensagem da recusa | passou no CI do head |
| CA-8 índice de fixtures em dia | test_indice_fixtures | índice gerado | passou (local) |
| CA-9 (volta 1) texto de interpretador, destino em variável, linha ilegível e as entradas .devcontainer/, .devcontainer.json, .claude-plugin/ barram na raiz | fixtures raiz-forge-s1 a s6, raiz-forge-variavel-*, raiz-forge-errointerno-*, raiz-forge-python-c-*-libera | leitura e escrita fora da entrada seguem livres | passou |

## Cenários e resultado real (volta 1)
- ci: 10c1b834b6fb062bfb2f9b7d9020dbbcbe828abf verde (`gh pr checks 930`: tudo pass, fora `bateria (pareceres)`, `bateria` e `catraca`, que esperam parecer ou rótulo; suítes 3.12 e 3.14, partes 1 a 5, passaram).
- Local, sob o flock da trava A: `python3 -m unittest tests.test_hooks.Hooks.test_fixtures_da_raiz_do_forge tests.test_indice_fixtures` deu `Ran 11 tests ... OK`.
- A3 resolvido: `bin/forge-mutante` das 3 specs (22 mutantes: RF1 a RF5, RF7, RF8, RE1 a RE5 (uma entrada da tupla cada), RT1, RT2, RD1 a RD6, RX1, RX2) saiu rc=0, todos `morreu`, sem sobrevivente nem equivalente (`forge-mutante: pedido=v0481-hook-raiz-forge rev=10c1b834b6fb`). `--cobertura --base baffa052` não lista condição sem mutante; as linhas mudadas saem "declarado, não provado", e a rodada acima as provou.
- Vermelho antes do verde: `bin/forge-testes --vermelho baffa052 --modulos test_hooks` estourou o prazo (rc=124, sem veredito) no limite local de 10 min; não vale como vermelho. A prova de que as fixtures falham sem a implementação são os 22 mutantes mortos por elas e pelos testes.
- Spec M19 de v0479-entrega-parecer-mesclado-4 realinhada: confirmada pelo CI verde da suíte.
- Efeito colateral declarado (o texto de interpretador também recusa em wt/): lido no diff, coerente com a saída por Write ou Edit; sem achado.
- Acessibilidade e E2E: n/a (hook sem interface).
