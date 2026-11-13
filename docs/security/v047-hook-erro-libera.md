---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-hook-erro-libera
commit: 4c350b2f78a2f5fc5753f74be8d5fb760c8bebbc
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-13
---
# Review de segurança: v047-hook-erro-libera

Pedido v047, etapa E3.36: segurança por delta `9e3f57c6..4c350b2f` (volta E3.28 da HOOK-ERRO-LIBERA), sobre os bloqueantes A1 e A2 da E3.17 e contra as condições C1 a C8 do modelo de ameaças da E3.6 (`/root/.forge-contrib/docs/security/v047-v2-ameacas.md`, seção 1). Lido: `forge-check parecer delta` (domínio: `hooks/conformidade.py`, `bin/forge-testes`, mutantes e fixtures), o diff inteiro de `hooks/conformidade.py` e os 14 fixtures `errointerno-*` novos. Rodados no head: `tests.test_hook_erro_libera` (11 testes, verdes, inclui todos os fixtures `errointerno-*`) e as sondas abaixo, com erro e prazo forçados pelo mesmo lançador dos fixtures (`rodar` com `forcar` em `Guarda.bash`, `tests/test_hooks.py`). Sem PR, sem CI do head: suíte inteira não rodada (carga da máquina, diretriz 15).

## Gatilhos
`R-SEGURANCA`: controle do Forge (hook `conformidade`) e analisador de comando (o marcador da falha fechada).

## Revalidação de A1 e A2 (E3.17)
- **A1 fechado.** `ESCRITORES` (`hooks/conformidade.py:2824-2825`) passa a unir `CAMINHOS_NO_GIT` (`rm`, `mv`, `checkout`, `restore`) e `GIT_GRAVA_ARQUIVO` (`apply`, `am`), a lista inteira pedida. S1 e S2 reproduzidas com erro e com prazo forçados: rc 2. Mutantes M34 a M37 tiram cada verbo da união.
- **A2 fechado.** `BASE_TROCADA` (`hooks/conformidade.py:2831-2832`) conta `cd`, `pushd`, `popd`, `-C`, `--chdir`, `--git-dir`, `--work-tree`, `GIT_DIR` e `GIT_WORK_TREE` como alvo opaco na linha que escreve (`:2878-2879`), também dentro de `sh -c '…'`, de subshell e em linhas separadas. S3 a S6 reproduzidas: rc 2 com erro e com prazo. A expressão é linear (alternância fixa, sem quantificador aninhado).
- **C1 a C8:** o delta não toca `_comum.py`, `agentes.py`, `hooks.json` nem a documentação normativa; o que a E3.17 deu como cumprido segue valendo.

## Achados
- A3 (recomendado) hooks/conformidade.py:2878 · Termo só literal, sem mudança na volta: `cp x docs//pedidos/v1.md`, `cp x docs/"pedidos"/v1.md` e `cp x ./docs/./pedidos/v1.md` passam com erro ou prazo; a guarda normal recusa. Exige ofuscação deliberada (S7 a S9).
- A4 (recomendado) hooks/_comum.py:2791 · C5 pede no corpo do PR o número de prazos vencidos que passariam a recusar; o erros.log não guarda o comando. Sem PR ainda: declarar o número medido na E3.17 (846 linhas, 0 com comando) e a limitação.
- A5 (recomendado) hooks/conformidade.py:2831 · Fora desta entrega: a guarda normal libera `env -C docs cp x pedidos/v1.md`, `git --work-tree=docs restore`, `GIT_WORK_TREE=docs git checkout`, `git -C docs apply` e `git apply --directory=docs/pedidos`; o marcador recusa. Cartão para a guarda normal.
- A6 (recomendado) hooks/conformidade.py:2874 · Regra de integração não é escrita de caminho: `git reset --hard origin/x` na develop, recusado pela guarda normal (R-REVIEW), passa com erro ou prazo. Igual antes da volta; o pre-push e a proteção do remoto seguram o envio.

## Sondas
- S1 · Bash `git restore --source=x docs/pedidos/v1.md`, tech-lead · espera: rc 2 normal, com erro e com prazo · obtido: 2 / 2 / 2
- S2 · Bash `git checkout origin/x -- docs/pedidos/v1.md`, tech-lead · espera: rc 2 nos três modos · obtido: 2 / 2 / 2
- S3 · Bash `git -C docs checkout x -- pedidos/v1.md`, tech-lead · espera: rc 2 nos três modos · obtido: 2 / 2 / 2
- S4 · Bash `cd docs && cp x pedidos/v1.md`, tech-lead · espera: rc 2 nos três modos · obtido: 2 / 2 / 2
- S5 · Bash `pushd docs; cp x pedidos/v1.md`, tech-lead · espera: rc 2 nos três modos · obtido: 2 / 2 / 2
- S6 · Bash `cd docs` e `cp x pedidos/v1.md` em linhas separadas, `(cd docs; cp …)` e `bash -c "cd docs && cp …"` · espera: rc 2 nos três modos · obtido: 2 / 2 / 2 nos três
- S7 · Bash `cp x docs//pedidos/v1.md` (A3) · espera: rc 2 nos três modos · obtido: 2 / 0 / 0
- S8 · Bash `cp x docs/"pedidos"/v1.md` (A3) · espera: rc 2 nos três modos · obtido: 2 / 0 / 0
- S9 · Bash `cp x ./docs/./pedidos/v1.md` (A3) · espera: rc 2 nos três modos · obtido: 2 / 0 / 0
- S10 · Bash `git reset --hard origin/x` na develop (A6) · espera: rc 2 nos três modos · obtido: 2 / 0 / 0

## Detalhe dos achados
Ordem dos três números nas sondas: guarda normal, erro forçado, prazo forçado. Legítimos no head: `cd build && ls`, `git -C build status` e `git checkout feature` dão 0 nos três modos; `cd build && cp x y` dá 0 / 2 / 2, o que a correção de A2 previu (só marca, recusa só em erro ou prazo, como `cp x $D`). A5, sondas no mesmo lançador: as cinco formas dão 0 / 2 / 2; o marcador é mais estrito que a guarda normal, então não é regressão da volta, é lacuna da guarda normal (família da E3.6, troca de base por opção ou variável). A6: as regras de integração (`git reset <rev>`, `git cherry-pick` na develop) não estão na política de caminhos que a C2 cobre; em erro ou prazo o marcador não as vê.

**A3, correção sugerida (P, `tech-lead`).** Buscar os termos também numa forma normalizada da linha: sem aspas dentro da palavra e com `//` e `/./` colapsados.

**A4 (`tech-lead`, corpo do PR).** Declarar no PR o número medido na E3.17 e que o log não permite a contagem pedida, ou registrar no `erros.log` um marcador sim/não por linha de prazo (sem o comando).

**A5 (cartão, `tech-lead`).** Na guarda normal, tratar a troca de base por opção ou variável como a de `cd`: `env -C`, `env --chdir`, `git --work-tree`, `git --git-dir`, `GIT_WORK_TREE`, `GIT_DIR`, `git -C <dir> apply` e `git apply --directory`.

**A6 (cartão, `tech-lead`).** Fazer o marcador consultar também as regras de integração (`git reset <rev>` e `git cherry-pick` na branch de integração), ou declarar o residual no ADR 0009, seção 7.

## Riscos aceitos e ferramentas
Nenhum risco aceito. O risco declarado na E3.17 (configuração corrompida recusa escrita na raiz, disponibilidade) segue igual e vai ao dono pelo Jarvis. Ferramentas: leitura do código, `tests.test_hook_erro_libera` e sondas pelo lançador dos testes. `gitleaks`, `zizmor` e `actionlint` não aplicáveis (nenhum segredo, workflow ou dependência no delta).
