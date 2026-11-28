---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-forge-check-fc2
commit: e1aff90260eba1e97fa153ddcd9b5e8127e5945f
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-16
---
# Review: v047-forge-check-fc2 (E2.181, revisado na E2.435)

Parecer completo, o primeiro desta branch. Diff lido: `58dfa2ab...b7a180d6` (Base-sha do brief até o head; o merge da develop b7a180d6 tira o FC1 do diff). No domínio: `bin/forge-check`, `tests/test_volta_por_delta.py`, `skills/qa-testing/SKILL.md`, `changelog.d/v047-forge-check-fc2.md` e duas specs de mutante.

## Achados
- A1 (recomendado) bin/forge-check:2989 · Depois do fetch, a linha `base:` afirma que o merge trazia o que a base não tinha sem reconferir `fora[0]` contra a base nova: merge de outra branch com a develop avançada sai como resolvido. O delta segue fechado; só o texto engana. Sugestão: reler e_ancestral contra `depois`.
- A3 (recomendado) skills/qa-testing/SKILL.md:47 · O encurtamento tirou a frase de que o `parecer delta` busca a base atrasada; sobrou `base:`/`aviso:: base atrasada`. Nenhuma regra saiu, mas o leitor perde o efeito do fetch. Sugestão: dizer `busca a base` em 2 palavras, se couber no teto.
- A2 (recomendado) changelog.d/v047-forge-check-fc2.md:1 · pendente: BRIEF-SELAR-LINHA-DA-ETAPA, item da E2.181, sem commit nesta branch; o Histórico do pedido (05:35) o devolve ao cartão (trava nova sob R-DECISAO). Não bloqueia este item; o cartão precisa seguir aberto.

## Sondas

## Parecer
Aprovado no head b7a180d6.

O que muda: (1) BRIEF-VOLTA-FORA-COMPACTO, `fora_do_escopo_do_pedido` escreve só os ids das outras etapas, 40 por linha (`linhas_de_ids_do_fora`); o `conferir_corte` já lia ids pelo `referencias_do_item`, e o teste do pedido de 600 etapas prova o teto de 10.000 caracteres e a conferência verde até `E4.600`; a lista vazia mantém `- (o pedido não tem outra etapa)`. (2) PARECER-DELTA-SEM-MERGE-DA-DEVELOP, `base_do_delta_em_dia` busca a base uma vez quando um merge da primeira linha traz commit fora da `origin/<base>` local. Falha fechada conferida: fetch que falha ou expira (`GIT_TIMEOUT_S`, `TimeoutExpired` capturado) deixa a base igual e o delta inteiro, com `aviso:`; rev-list que falha dá rc 2 (`FalhaDoGit`). A base vem de `BASES_DO_DELTA` (lista fechada), então o refspec do fetch não recebe texto livre; `fetch` está em `GIT_REDE`. Nenhum hook chama o `parecer delta` (grep em `hooks/`, `.githooks/`, `scripts/`), então o fetch não pesa no orçamento de 10 s dos hooks. A docstring do `cmd_parecer_delta` e a skill `qa-testing` dizem que deixou de ser só leitura.

Testes do item (`python3 -m unittest`, raiz do clone): `DeltaComBaseAtrasada` (3) e os dois testes novos de `BriefDeVolta`, 5 OK em 26 s. Os testes mudados de `BriefDeVolta` ficam para o CI (a classe inteira passa de 170 s localmente). Mutantes: `bin/forge-mutante --processos 1 tests/mutantes/v047-forge-check-fc2-2.json`, FC2-M3 a M9 morreram, rc=0; uma linha de guarda por mutante (2973, 2976, 2978, 2979, 2986, 3194, 3197), e FC2-M1 e M2 cobrem as do Fora compacto. O ramo de falha de cada guarda tem teste de comportamento (sem rede, base ausente, git falso do `DeltaGitFalha`). Suíte inteira: sem PR nesta etapa, o CI do PR é que a roda; cite o CI verde no merge. A falha de `test_reval_delta` vem do #576 na develop (brief), não deste item.

Tamanho (M14): 136 linhas de código e teste (`bin/forge-check` 47+6, `tests/test_volta_por_delta.py` 79+4), dentro do teto. São dois comportamentos no mesmo PR, os dois em `bin/forge-check` (fora de `hooks/`), do mesmo lote FC2 decidido no pedido: aceito.

AR (PA-7) conferidos no diff: AR-1 e AR-2 (mutantes e ramo de falha) ok; AR-4 os testes novos usam o `Repositorio` e o `check` existentes; AR-6 sem shell; AR-12 as specs batem com as linhas no head (o forge-mutante achou cada trecho). Nenhuma classe repetida neste pedido: `achados-recorrentes.md` sem linha nova.

## Revalidação por delta (head c2d1c60c)
Delta lido (`forge-check parecer delta`): `b7a180d6..c2d1c60c`, no domínio `bin/forge-check`, `skills/qa-testing/SKILL.md` e `tests/mutantes/v0432-integracao-2.json`; o `bin/forge-check` do delta é só o que veio da develop (`tmpdir_da_prova`, outro item), com `aviso:` de merge ainda fora da `origin/develop` local. O que o item mudou:
- Skill `qa-testing`: 3 linhas encurtadas (12067 bytes); conferi frase a frase: `sem ler o código do autor`, `R-QA`, `o QA cita o run`, `R-REVIEW`, `commit:`, `docs/ux/<demanda>/` e o resumo do `parecer delta` ficam; nenhuma regra saiu (diretriz 25). Só a explicação do fetch encolheu (A3, recomendado).
- I20 reancorado em `bin/forge-check:3200` (a `if isinstance(lido, FalhaDoGit)` do `cmd_parecer_delta`), mesma mutação (`not (...)`), trecho `de`/`para` apertado a três linhas. `bin/forge-mutante --processos 1 --prazo 900` sobre a spec só com o I20: `I20 · morreu · bin/forge-check:3199`, rc=0.
- Testes tocados: nenhum arquivo de teste mudou no delta; o I20 roda os 7 módulos da spec, e o que matou o mutante vale como teste do ramo de falha. Sem suíte inteira (CI).
Parecer segue aprovado, agora no head c2d1c60c. O QA não precisa revalidar: o delta dele é só a skill encurtada (texto, sem teste nem código do item) e a spec do I20; a lógica do item não mudou desde b7a180d6.

## Revalidação por delta (head e1aff902; clone no 7adc80d5)
Delta lido (`forge-check parecer delta`): `c2d1c60c..7adc80d5`, no domínio `bin/forge-check` (só o que veio da develop, outro item), `skills/qa-testing/SKILL.md` e `tests/test_volta_por_delta.py`. Skill: uma linha encurtada (`aponta (commit:) o commit`; `Na volta ... lista só o que mudou`); `R-QA`, `R-REVIEW`, `commit:`, `base:`/`aviso:`, `docs/ux/<demanda>/` e o resumo do `parecer delta` ficam; nenhuma regra saiu. A3 segue recomendado (o fetch não é dito). Teste: `remoto_sem_manutencao(self.origem)` no `DeltaComBaseAtrasada` (3 OK em 2 s) e o import de `ambiente_git`; `tests/test_metricas_texto` 2 OK, sem -I. Sem código do item mudado. Parecer segue aprovado.
