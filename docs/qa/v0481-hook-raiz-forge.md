---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-hook-raiz-forge
commit: baffa052cf425f0bc0eaed636e681c52b299b372
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-26
---
# QA: v0481 hook-raiz-forge (E37.4, PR #930)

CI do head baffa052 vermelho, sem aprovação: `gh pr checks 930` mostra `suíte (python 3.12 e 3.14, partes 1 e 2/5)`, `bateria (python 3.14)` e `bateria (pareceres)` em fail; partes 3, 4 e 5, `catraca`, `instalação` e `bateria (passos)` em pass.

## Achados
- A1 (bloqueante) tests/test_hooks.py:913 · a fixture conformidade/estadoclone-rm-git-bloqueia espera "marca de sessão dos hooks (.git/forge/)" e recebe "o .git da raiz ... liga o repositório às marcas": o novo na_raiz_em_vigor dispara antes de recusa_do_estado e troca a mensagem. Ajustar fixture ou a ordem das guardas; volta única
- A2 (bloqueante) docs/hooks-fixtures.md:1 · índice desatualizado: as 19 fixtures raiz-forge-* criaram o prefixo raiz-*; test_indice_fixtures.py:157 (conferir rc 0), :31 e :42 falham. Rodar scripts/indice-fixtures.py e commitar; volta única
- A3 (recomendado) tests/mutantes/v0481-hook-raiz-forge.json:1 · as 3 entradas de EM_VIGOR_NA_RAIZ e a guarda "r is not None" não têm mutante; apagar ".git/hooks/" ou ".devcontainer/devcontainer.json" da tupla pode sobreviver; considerar um mutante por entrada

## Critério → teste → resultado
Sem docs/ux nem contrato de API (conserto de trava); os critérios vêm da etapa E37.1 do pedido e do corpo do PR.

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| CA-1 Write, Edit e MultiEdit em .githooks/ e .git/hooks/ da raiz barram | fixtures raiz-forge-s0-write-githooks, raiz-forge-write-git-hooks, raiz-forge-multiedit-commit-msg, raiz-forge-jarvis-edit-devcontainer | papel jarvis incluído; MultiEdit | Hooks.test_fixtures_da_raiz_do_forge passou (local, 1 teste, 19 fixtures) |
| CA-2 Write em .devcontainer/devcontainer.json da raiz barra | raiz-forge-s2-write-devcontainer, raiz-forge-s4-projeto-devcontainer | sonda s2 (antes passava) | passou |
| CA-3 escrita e remoção pelo Bash barram | raiz-forge-bash-redireciona-githooks, raiz-forge-bash-cp-devcontainer, raiz-forge-bash-rm-devcontainer | remover a pasta que contém a entrada | passou |
| CA-4 alvo na raiz barra mesmo com a pasta corrente em wt/* | raiz-forge-wt-bash-devcontainer-da-raiz, raiz-forge-wt-write-githooks-da-raiz, raiz-forge-sessao-em-worktree-copia-principal | cópia principal x pasta corrente | passou |
| CA-5 leitura e cópia de wt/ seguem livres | raiz-forge-leitura-githooks-libera, raiz-forge-wt-*-da-copia-libera | leitura; cópia de trabalho | passou |
| CA-6 vizinho, scripts/ e repositório fora do Forge livres | raiz-forge-vizinho-devcontainer-libera, raiz-forge-sonda-s1-scripts-libera, raiz-forge-outro-repo-libera | arquivo vizinho; outro repositório | passou |
| CA-7 comportamento anterior preservado (mensagens das recusas existentes) | suíte do CI, fixture estadoclone-rm-git-bloqueia | mensagem da recusa | falhou (A1) |
| CA-8 índice de fixtures em dia | test_indice_fixtures | índice gerado | falhou (A2) |

## Cenários e resultado real
- Local, no head baffa052: `python3 -m unittest tests.test_hooks.Hooks.test_fixtures_da_raiz_do_forge` deu `Ran 1 test ... OK`. O teste afirma mínimos de 7 liberações e 12 recusas (guarda contra suíte vazia). Rodou sem o flock, porque o classificador do sandbox negou o flock; foi só 1,6 s.
- Falhas do CI lidas nas anotações do check-run, sem rerrodar a suíte (G3): A1 e A2, as mesmas do brief.
- Vermelho antes do verde (`bin/forge-testes --vermelho <base>`): não cumprido; não o rodei sem a trava de teste (R-TETO). Fica à volta.
- Mutantes RF1 a RF4 (`bin/forge-mutante tests/mutantes/v0481-hook-raiz-forge.json`): não rodados, mesmo motivo. Conferência da lista contra o diff: RF1 (chamada), RF2 (no_clone), RF3 (startswith) e RF4 (cópia principal) cobrem as decisões; sobra A3.
- Acessibilidade e E2E: n/a (hook sem interface).
