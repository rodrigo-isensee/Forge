---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-espera-amarela
commit: 054d4103ddb0c0364136575a4b36bbd3a2708164
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-27
---
# Review de segurança: v0481 (espera amarela, #948, volta 1, E47.8)

- ci: 054d4103ddb0c0364136575a4b36bbd3a2708164 verde nas 5 partes da suíte, verificações longas, passos, teto de pulados, instalação e `bateria (python 3.14)`; vermelhos por construção `bateria (pareceres)`, `bateria`, `catraca` e `catraca (conferência)` (log: só `R-CONFORMIDADE: mudança em` `.github/workflows/catraca.yml`, `.github/workflows/ci.yml` e `tests/catraca.py`, liberável pelo rótulo do dono; o script roda da base)

Gatilhos: workflow de CI (nome do check exigido, guarda do verde velho), controle de conformidade (`tests/catraca.py`, rc da catraca), regra afrouxada com `[afrouxa-regra` no título.

Aprovado. Revalidação por delta (`forge-check parecer delta`, 517557ab..054d4103; no domínio: `.github/workflows/catraca.yml`, `.github/workflows/ci.yml`, `docs/protecao-de-branch.md`, `scripts/ci-local`, `tests/catraca.py`, `tests/test_catraca.py`). Os quatro recomendados da rodada anterior fecharam; nenhum caminho do delta faz um vermelho por defeito virar amarelo, e o check exigido de nome exato segue sem run novo em toda espera.

## Estado dos achados anteriores
- A1 fechado. `.github/workflows/ci.yml:681`: o sufixo só entra com `bateria`, `pareceres`, `verificacoes`, `partes-doze` e `pulados-doze` em `success` (a lista inteira do `needs:` da linha 687); `.github/workflows/catraca.yml:70`: só com `conferencia` em `success`, que inclui o passo do T1. Teste vermelho ou T1 vermelho deixa o vermelho no nome exato.
- A2 fechado. `tests/catraca.py:156` ancora o padrão em `^` e separa o caminho; `linha_de_espera` (`:2099`) exige que o caminho separado seja o mais longo dos caminhos conhecidos (`caminhos_de_pareceres`, `:2107`, o mesmo `documentos` + `caminho_impresso` que o `cmd_pr` imprime) que abre a linha. Um parecer real cujo nome contém `: commit: desatualizado` é sempre o prefixo mais longo, então a espera não se forja. `_main` (`:2313`) decide pelo booleano `so_espera`, não pela marca no texto; e `so_espera and not outros` (`:2172`) tira a espera quando há parecer não exigido que não aprova.
- A3 fechado. `tests/catraca.py:2292-2308`: execuções em None, `fonte` em None, `pr_atual()` em None ou o git que não termina (`:1928`) entram em `falhas`, e o título `[afrouxa-regra` sai 1 com "não respondeu". Eventos em None continuam fora da espera.
- A4 fechado. `.github/workflows/ci.yml:620` e `.github/workflows/catraca.yml:60`: lista de permitidos `nenhum|failure|cancelled|timed_out|action_required|stale`; `success`, `skipped`, `neutral` e `null` (run em andamento) saem 1.

## Revalidação das sondas no 054d4103
- S1: `test_sonda_s1_arquivo_com_a_marca_e_parecer_reprovado_sai_1` (arquivo `hooks/espera: só falta o parecer` + review reprovado) · espera: rc 1 · obtido: rc 1.
- S2: `LINHA_DE_ESPERA.search` na linha literal da rodada anterior · espera: None · obtido: None; `linha_de_espera` com o parecer forjado `docs/reviews/x.md: commit: desatualizado-y.md` e um `docs/reviews/x.md` real ao lado · espera: False · obtido: False; linhas legítimas de ausente e de desatualizado · espera: True · obtido: True (sonda local na sessão, só funções do módulo).
- S3: `test_sonda_s3_execucoes_e_fonte_em_none_sai_1` e `test_cada_consulta_que_falha_sai_1` (execuções, fonte, PR, git) · espera: rc 1 · obtido: rc 1.
- Rodados: `test_catraca.EsperaNaoEVermelho` e `test_catraca.EsperaDoRotuloSoComAApiRespondendo`, 16 testes OK. A suíte inteira vale pelo CI acima.

## Plano em cartões
- Cartão (fora do delta, `tech-lead`, baixa, esforço P): `tests/catraca.py:1836-1857`, `sha_rotulado_do_mesclado`, no caminho da promoção com `[afrouxa-regra` no título: a API que não devolve o PR candidato, os eventos ou as execuções dele vira `sem(...)` e o resultado é a espera "falta o rótulo" em vez de vermelho. Sem atacante: falha de infraestrutura, o check exigido segue pendente e o dono só rotularia a promoção de novo. Correção mínima: `liberado_por_pr_mesclado_ou_none` conta esses três "a API não devolveu" como falha (anexar a `falhas`). O código não mudou no delta; vai como cartão (G1.2).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do delta, os testes novos de abuso e uma sonda local com o interpretador isolado sobre o `tests/catraca.py` do head, `gh api` de leitura dos check runs e do log. Ausentes na estação, sem instalar (lacuna, `R-CUSTO`): `gitleaks`, `actionlint`, `zizmor`, `semgrep`.
