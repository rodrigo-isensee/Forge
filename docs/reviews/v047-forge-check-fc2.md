---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-forge-check-fc2
commit: b7a180d61469a6aed2d6accee139622ca5944eaf
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-16
---
# Review: v047-forge-check-fc2 (E2.181, revisado na E2.435)

Parecer completo, o primeiro desta branch. Diff lido: `58dfa2ab...b7a180d6` (Base-sha do brief até o head; o merge da develop b7a180d6 tira o FC1 do diff). No domínio: `bin/forge-check`, `tests/test_volta_por_delta.py`, `skills/qa-testing/SKILL.md`, `changelog.d/v047-forge-check-fc2.md` e duas specs de mutante.

## Achados
- A1 (recomendado) bin/forge-check:2989 · Depois do fetch, a linha `base:` afirma que o merge trazia o que a base não tinha sem reconferir `fora[0]` contra a base nova: merge de outra branch com a develop avançada sai como resolvido. O delta segue fechado; só o texto engana. Sugestão: reler e_ancestral contra `depois`.
- A2 (recomendado) changelog.d/v047-forge-check-fc2.md:1 · pendente: BRIEF-SELAR-LINHA-DA-ETAPA, item da E2.181, sem commit nesta branch; o Histórico do pedido (05:35) o devolve ao cartão (trava nova sob R-DECISAO). Não bloqueia este item; o cartão precisa seguir aberto.

## Sondas

## Parecer
Aprovado no head b7a180d6.

O que muda: (1) BRIEF-VOLTA-FORA-COMPACTO, `fora_do_escopo_do_pedido` escreve só os ids das outras etapas, 40 por linha (`linhas_de_ids_do_fora`); o `conferir_corte` já lia ids pelo `referencias_do_item`, e o teste do pedido de 600 etapas prova o teto de 10.000 caracteres e a conferência verde até `E4.600`; a lista vazia mantém `- (o pedido não tem outra etapa)`. (2) PARECER-DELTA-SEM-MERGE-DA-DEVELOP, `base_do_delta_em_dia` busca a base uma vez quando um merge da primeira linha traz commit fora da `origin/<base>` local. Falha fechada conferida: fetch que falha ou expira (`GIT_TIMEOUT_S`, `TimeoutExpired` capturado) deixa a base igual e o delta inteiro, com `aviso:`; rev-list que falha dá rc 2 (`FalhaDoGit`). A base vem de `BASES_DO_DELTA` (lista fechada), então o refspec do fetch não recebe texto livre; `fetch` está em `GIT_REDE`. Nenhum hook chama o `parecer delta` (grep em `hooks/`, `.githooks/`, `scripts/`), então o fetch não pesa no orçamento de 10 s dos hooks. A docstring do `cmd_parecer_delta` e a skill `qa-testing` dizem que deixou de ser só leitura.

Testes do item (`python3 -m unittest`, raiz do clone): `DeltaComBaseAtrasada` (3) e os dois testes novos de `BriefDeVolta`, 5 OK em 26 s. Os testes mudados de `BriefDeVolta` ficam para o CI (a classe inteira passa de 170 s localmente). Mutantes: `bin/forge-mutante --processos 1 tests/mutantes/v047-forge-check-fc2-2.json`, FC2-M3 a M9 morreram, rc=0; uma linha de guarda por mutante (2973, 2976, 2978, 2979, 2986, 3194, 3197), e FC2-M1 e M2 cobrem as do Fora compacto. O ramo de falha de cada guarda tem teste de comportamento (sem rede, base ausente, git falso do `DeltaGitFalha`). Suíte inteira: sem PR nesta etapa, o CI do PR é que a roda; cite o CI verde no merge. A falha de `test_reval_delta` vem do #576 na develop (brief), não deste item.

Tamanho (M14): 136 linhas de código e teste (`bin/forge-check` 47+6, `tests/test_volta_por_delta.py` 79+4), dentro do teto. São dois comportamentos no mesmo PR, os dois em `bin/forge-check` (fora de `hooks/`), do mesmo lote FC2 decidido no pedido: aceito.

AR (PA-7) conferidos no diff: AR-1 e AR-2 (mutantes e ramo de falha) ok; AR-4 os testes novos usam o `Repositorio` e o `check` existentes; AR-6 sem shell; AR-12 as specs batem com as linhas no head (o forge-mutante achou cada trecho). Nenhuma classe repetida neste pedido: `achados-recorrentes.md` sem linha nova.
