---
tipo: qa
contrato: 1
pedido: impl-n-tpl-a
branch: melhoria/impl-n-tpl-a2
commit: 84c53e9afc27f5aa1ec76cdb8a7c3e884e9623c5
parecer: aprovado
revisor: forge:qa-engineer
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-22
---
# QA: impl-n-tpl-a

Etapa E1.4 (`R-QA`), depois do review (6d643b3) e da segurança (7e85431), os dois aprovados. Instância que não é a autora (D-ETAPAS-INST = A). Código testado: 84c53e9 (depois dele só entraram os pareceres). Diff lido: `a3dbe22..84c53e9`, 11 arquivos, 4 commits. Base: desenho do lote N-TPL-a (`docs/propostas/discovery-0.29.0/n-tpl.md`) e adendo de ameaças (`docs/security/ameacas/n-tpl.md`). O lote não tem especificação de UX nem contrato de API: os critérios são os controles do desenho e do adendo, mais P3 = B. Todas as sondas rodaram em clone próprio em `$TMPDIR`; a worktree compartilhada não foi trocada de HEAD.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| NOME-PEDIDO-NEUTRO: modelo de pedido manda nome neutro no Forge (`R-NEUTRO`), forma do ID, sem segredo, correção é renomear | `test_clareza.TestNomeDoPedidoNeutro` e invariante em `tests/config.json` | texto sumir do modelo (invariante); sem exceção nova na neutralidade | passou |
| F8: os dois passos a passo existem e trazem os controles (ruleset sem ator de bypass, enforcement Active, fonte do check fixada, force push, deleção, branch atualizada, conferência só de leitura, custo, `R-CONFORMIDADE`) | `test_modelos_projeto` (`test_passo_a_passo_*`, `test_protecao_sem_bypass_nos_portoes`) | bypass na lista; mínimo de 2 checks citados | passou |
| F8: check citado existe como job nos workflows | `test_checks_citados_existem_nos_workflows` | nome de job mudar; guarda de suíte vazia (>= 2) | passou |
| F8: texto do projeto é neutro (sem catraca nem bateria) e nenhum agente escreve na API | `test_modelo_de_projeto_e_neutro_*`, `test_texto_diz_que_agente_nao_cola_token_*` | termo do Forge vazar para o modelo | passou |
| M9: modelo com `version: 2`, `target-branch`, cooldown, grupo de rotina sem major, um grupo só de major, sem ignore, auto-merge, registries nem execução de código externo | `test_dependabot_modelo` (`test_modelo_dependabot*`) | major no grupo de rotina; item proibido | passou |
| M9: bloco por stack e frases da skill de CI | `test_toda_stack_traz_o_ecossistema_do_dependabot`, `test_ci_cd_avisa_branch_padrao_e_pr_do_robo` | stack sem bloco (mínimo de 1 stack) | passou |
| `forge-init` em diretório novo copia o dependabot.yml e o passo a passo, sem `{{` | sonda manual + `test_cria_estrutura_completa` | marcador sobrando | passou |
| P3 = B: cada commit reverte sozinho no HEAD | sonda `git revert --no-commit` por commit | conflito de arquivo compartilhado | passou |
| Fábrica: neutralidade e regras com ID | `NeutralidadeDoNucleo`, `RegrasInviolaveis`, `scripts/validar-plugin.sh` | termo de stack no núcleo | passou |

## Cenários e resultado real
- **Revert de cada commit sobre 84c53e9** (`git revert --no-commit <sha>` e suíte `tests.test_forge` completa mais os módulos que sobram), sem conflito em nenhum dos 4:
  - 6319d21 (NOME-PEDIDO-NEUTRO): 430 testes OK.
  - 20a3127 (F8): 431 testes OK (o módulo da F8 sai junto, os outros ficam verdes).
  - 77d1856 (M9): 429 testes OK.
  - 84c53e9 (fragmento): módulos novos e `NeutralidadeDoNucleo` OK (22 testes).
  Os testes da M9 vivem em arquivo próprio, criado pelo 77d1856; o `tests/config.json` só recebe acréscimo, como o desenho permite. P3 = B cumprido.
- **Vermelho antes do verde:** restaurei os arquivos de conteúdo dos 3 itens para o estado da base (a3dbe22), mantendo os testes novos, e rodei `python3 -m unittest tests.test_clareza tests.test_modelos_projeto tests.test_dependabot_modelo tests.test_forge.RegrasInviolaveis`: 19 testes, `FAILED (failures=4, errors=10)`. Com o conteúdo do 84c53e9: 22 testes OK.
- **`forge-init` num diretório novo** (`bin/forge-init` do clone, rc=0): criou `.github/dependabot.yml` e `docs/engineering/protecao-de-branch.md`, ambos idênticos ao modelo; `grep -r '{{'` no projeto criado: 0 ocorrências.
- **Neutralidade e plugin:** `NeutralidadeDoNucleo` OK; `scripts/validar-plugin.sh` no clone: "Validation passed".
- **Suíte completa:** não rodei a suíte inteira como bateria à parte (`R-TETO`): a de `tests.test_forge` rodou três vezes inteira nas sondas de revert (todas OK, ver acima), e o pre-push deste commit roda a suíte toda. O autor relatou 1384 testes OK em 84c53e9.
- **Recomendações do review (6d643b3) e da segurança (7e85431) conferidas, nenhuma bloqueia:**
  - docstring de `tests/test_modelos_projeto.py:1` ainda cita a M9 e três linhas em branco em `tests/test_clareza.py:59`: cosmético, confirmado.
  - R1 (desvio do `main-do-dono` em conta pessoal) e R2 (conferência não confere `integration_id` nem a regra de update): texto do roteiro, confirmado que faltam; baixa.
  - R3 (`tests/test_modelos_projeto.py:43` junta `name:` de passos e de jobs; `:53` não barra "Bypass list: Repository admin"): confirmado, teste frouxo em dois pontos; um mutante com "Bypass list: Repository admin" no passo 3 sobreviveria. Informativa.
  - R4 (`--forcar` do `forge-init` sobrescreve o `dependabot.yml`): fora do lote pelo desenho; sugiro cartão.
- **Limites da sonda:** o YAML do `dependabot.yml` só é validado de fato pelo robô no primeiro uso, e a interface do GitHub não é testável aqui (sem rede). O sandbox bloqueou chamadas de saída durante o validar-plugin; o resultado não dependeu delas.

## Bugs
Nenhum aberto (`docs/qa/bugs/` não ganha arquivo).
