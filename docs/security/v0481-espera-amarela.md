---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-espera-amarela
commit: 517557abcd34a5605bac2c37b3d344acb953ed61
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-27
---
# Review de segurança: v0481 (espera amarela, #948, E47.3)

- ci: 517557abcd34a5605bac2c37b3d344acb953ed61 verde

Gatilhos: workflow de CI (permissões `checks: read`, `always()`, nome do check exigido), controle de conformidade (`tests/catraca.py`, rc da catraca), regra afrouxada com `[afrouxa-regra` no título.

Aprovado, com quatro recomendações que voltam ao autor antes do merge (`R-REVIEW`). Nenhum caminho achado abre a junção: em todos os casos de espera o check exigido de nome exato (`bateria`, `catraca`) fica sem run novo e a proteção da branch segue barrando. Os achados são de classificação (defeito que aparece como espera) e de uma corrida que o guarda do "verde velho" não fecha.

## Achados
- A1 (recomendado) .github/workflows/ci.yml:681 · o sufixo de espera depende só da saída de `pareceres`: teste vermelho mais parecer faltando deixa `bateria` pendente e o vermelho em `bateria (espera parecer)`; o mesmo em catraca.yml:70 com o T1 vermelho. Contradiz docs/protecao-de-branch.md:29 ("com o nome exato").
- A2 (recomendado) tests/catraca.py:2280 · a espera dos pareceres é decidida por texto: a marca em qualquer violação (ex.: arquivo sensível com "espera: só falta o parecer" no nome) e a regex sem âncora da linha 156 sobre o caminho fazem parecer reprovado, forjado ou sem autoria sair 3 em vez de 1 (S1, S2).
- A3 (recomendado) tests/catraca.py:2272 · com o título `[afrouxa-regra`, a API das execuções ou dos PRs mesclados que falha (None) ou o git que estoura o prazo viram espera "falta o rótulo" (rc 3), não vermelho; o brief e a doc dizem que falha da API segue vermelha (S3).
- A4 (recomendado) .github/workflows/ci.yml:619 · o guarda só recusa `success`: run concorrente em andamento (conclusion null) no mesmo head, comum no ci.yml sem cancelamento em PR, passa como espera e o verde dele vale depois; `skipped` e `neutral` também passam. Use lista de permitidos. Idem catraca.yml:59.

## Sondas
- S1 · `python3 -I sonda_espera.py <clone> 319a968d 517557ab`: `SO_ESPERA_PARECER in msg("R-REVIEW", "PR toca hooks/espera: só falta o parecer ... parecer: o último parecer não é aprovado)")` · espera: False · obtido: True
- S2 · `LINHA_DE_ESPERA.search("docs/reviews/a: commit: desatualizado.md: parecer: o último parecer não é aprovado (R-REVIEW)")` · espera: None · obtido: casa
- S3 · `main(["--modo","regras","--base",base,"--head",head])` com PR_TITULO `[afrouxa-regra`, rótulo antes do push e `execucoes_do_pr`/`fonte_do_github` em None · espera: 1 · obtido: 3

## Detalhe dos achados
**A1.** Evidência: `.github/workflows/ci.yml:681` (`name: bateria${{ needs.pareceres.outputs.espera }}`), `.github/workflows/catraca.yml:70`; o passo de texto do PR (catraca.yml, depois do `id: regras`) roda com `!cancelled()` e, se reprova, o job falha com a saída `espera` já gravada. Caminho: não há atacante; qualquer PR com teste vermelho e sem parecer mostra o exigido amarelo e o defeito num check irmão. O vermelho continua visível (o `forge-check` conta `bateria (espera parecer)` na linha do CI, porque o nome não está em `CHECKS_FORA_DA_LINHA_DO_CI`), mas a promessa da doc não vale. Severidade: baixa. Correção mínima: só pôr o sufixo quando o resto estiver verde, `name: bateria${{ (needs.bateria.result == 'success' && needs.verificacoes.result == 'success' && needs.partes-doze.result == 'success' && needs.pulados-doze.result == 'success') && needs.pareceres.outputs.espera || '' }}` e `name: catraca${{ needs.conferencia.result == 'success' && needs.conferencia.outputs.espera || '' }}`; ou corrigir a frase da doc. Esforço P. Dono: `devops-engineer` (workflow), `tech-lead` (doc).

**A2.** Evidência: `tests/catraca.py:156` (regex com `search`, sem âncora), `:2137` (aplica a regex à linha inteira do `cmd_pr`, que começa pelo caminho do parecer), `:2280` (procura a marca por substring em todas as violações, cujo texto inclui `tocados[0]`, o caminho escolhido pelo autor do PR). Caminho: o autor do PR (contribuidor, inclusive fork) dá a um arquivo sensível ou a um parecer um nome com a marca ou com `: commit: desatualizado`; um parecer reprovado ou forjado vira "espera" (amarelo). Não abre a junção (o exigido não ganha run), mas esconde o sinal de forja que o requisito manda manter vermelho. Severidade: baixa. Correção mínima: decidir a espera por dado, não por texto. `_violacoes_de_pareceres` devolve, junto das violações, um booleano `so_espera` calculado das linhas do `cmd_pr` com o caminho já separado (casar o sufixo depois de `<caminho conhecido>: `, como faz `PARECER_A_REVALIDAR` em `bin/forge-check:10057`, ancorado em `^`), e `_main` usa esse booleano em vez de `SO_ESPERA_PARECER in v`. Teste de abuso: arquivo `hooks/espera: só falta o parecer` mais parecer reprovado sai 1. Esforço P. Dono: autor do E47.1 (`tech-lead`).

**A3.** Evidência: `tests/catraca.py:2272`; `execucoes_do_pr` devolve None na falha da API, `fonte_do_github` devolve None sem token e `liberado_por_pr_mesclado_ou_none` devolve None no estouro do git, e os três caem na espera. Caminho: falha de infraestrutura, sem atacante. Com o rótulo do dono já posto (antes do último push), a falha mostra "falta o rótulo", e o dono pode rotular de novo sem precisar. Fecha (o exigido fica pendente), mas a classificação contradiz o brief ("falha do git ou da API" segue vermelho) e `docs/protecao-de-branch.md:29`. Severidade: baixa. Correção mínima: só esperar quando cada consulta respondeu. Guardar se `execucoes` foi None (com `eventos` vindos da API) ou se o git estourou o prazo, e nesse caso sair 1. Teste de abuso: S3 sai 1. Esforço P. Dono: `tech-lead`.

**A4.** Evidência: `.github/workflows/ci.yml:619-620`, `.github/workflows/catraca.yml:59-60` (`[ "$ultimo" != success ]`). Caminho: no ci.yml, cada run de PR tem o próprio grupo de concorrência, sem cancelamento automático (ci.yml:36-38). Run R1 no head H com a base B1 (parecer valendo) ainda em andamento. Reabrir o PR com a base B2 dispara R2 no mesmo H; o job de pareceres de R2 termina em menos de 1 minuto, lê o `bateria` de R1 com `conclusion: null` e grava a espera. R2 nunca emite `bateria`, R1 termina verde, e o exigido vale pelo verde de R1 (outra base). Antes deste PR era corrida (o `bateria` vermelho de R2 podia chegar por último); agora é certo. `skipped` e `neutral` contam como verde para a proteção da branch e também passam pelo guarda. Exige reabrir o PR com o parecer mudando de veredito só pela base, o que é raro. Severidade: baixa. Correção mínima: lista de permitidos, `case "$ultimo" in nenhum|failure|cancelled|timed_out|action_required|stale) ;; *) echo "espera: check do head em andamento ou verde; vermelho"; exit 1;; esac`, nos dois workflows. Esforço P. Dono: `devops-engineer`.

Conferido sem achado:
- `checks: read` só nos jobs `pareceres` e `conferencia`, só leitura. No ci.yml o token vai em `TOKEN_DE_LEITURA` e o script roda com `env -u`, então o código da base ou da introdução não o recebe. Na catraca.yml o script já recebia `GITHUB_TOKEN` (com `pull-requests`/`actions: read`), e `checks: read` não dá escrita.
- `PR_TITULO` e o corpo entram só por `env:` e nunca são interpolados em `run:`. O sufixo do nome vem de `echo` com texto fixo do workflow, sem dado do PR.
- `always()` no agregador novo exige `conferencia == success`, e pulado ou cancelado reprova. Sem `continue-on-error` ou `paths-ignore`. As ações seguem fixadas por SHA.
- Check `bateria`/`catraca` falso de um workflow novo trazido pelo PR (o que a espera deixaria sozinho no head): `.github/workflows/` está em `PROTEGIDOS` (tests/catraca.py:48), então a catraca só passa com o rótulo do dono depois das revisões, e a fonte do check fica fixada em GitHub Actions (docs/protecao-de-branch.md:22). Sem caminho sem o dono.
- Sem a marca no título, a regra quebrada sai 1, e custo e `NAO_LIBERAVEL` saem 1 mesmo com o título (tests/catraca.py:2256, testes `test_custo_e_defeito_mesmo_com_o_titulo`, `test_regra_sem_titulo_afrouxa_e_defeito_sai_1`). A ausência de eventos da API sai 1 (`test_sem_eventos_da_api_e_vermelho_mesmo_com_o_titulo`).
- CI do Revisar-sha: as 5 partes da suíte, os passos, as verificações longas, a instalação e o `bateria (python 3.14)` estão verdes. Ficam vermelhos por construção `bateria (pareceres)`, `bateria` e `catraca`, mais `catraca (conferência)`; o log deste lista só `R-CONFORMIDADE: mudança em` (`.github/` e `tests/catraca.py`), que o rótulo do dono libera. O script roda da base, então a espera ainda não vale neste PR.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do diff, sondas locais com `python3 -I` sobre o `tests/catraca.py` do head (S1 a S3, só funções do módulo e `main` com a API substituída) e `gh api` de leitura dos check runs e do log. Ausentes na estação, sem instalar (lacuna, `R-CUSTO`): `gitleaks`, `actionlint`, `zizmor`, `semgrep`.
