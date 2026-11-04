---
tipo: review
contrato: 1
pedido: versao-033
branch: melhoria/lote-l09
commit: bc6d081513aa0128fd035f27cc924980cc8c819f
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-04
---
# Review: L09 da 0.33, E15 BRIEF-MENSAGEM-LIMPA

Escopo: só o delta `103247e..bc6d081` (1 commit, `bc6d081`, 7 arquivos); os commits do L08 (`7f66d28..874c89e`) têm review próprio e ficam fora. Origem do escopo: item E15 do pedido e as DECISÕES TÉCNICAS de 04:00, 04:10 e 04:17 no Histórico de `docs/pedidos/versao-033.md`, que mandam ao E15 o A1 e o A2 do review do L07 e o A1 e o A2 da segurança do L07 (`docs/reviews/tempo-b1.md`, `docs/security/tempo-b1.md`).

Veredito: **reprovado**, um bloqueante (A1): o commit troca a linha dos dois blocos de `agents/conferente.md:16`, mas não o teste que a exige, e `tests/test_forge.py` quebra.

## Ferramentas (citadas, não refeitas)
- `python3 -I -m unittest discover -s tests -p test_erros_no_brief.py`: rc=0, `Ran 42 tests`, `OK`.
- `python3 -I -m unittest discover -s tests -p test_mensagem_conferente.py`: rc=0, `Ran 15 tests`, `OK`.
- `python3 -I -m unittest discover -s tests -p test_comportamento.py` (lê os invariantes de `tests/config.json`): rc=0, `Ran 6 tests`, `OK`.
- `python3 -I -m unittest discover -s tests -p test_forge.py -k TextoDoConferenteNoLote`: rc=1 em `bc6d081` (`ERROR test_dois_blocos_so_depois_do_brief_e_modo_dentro_do_brief_nao_abre_bloco`, `StopIteration`); rc=0 em `103247e` (8 testes, `OK`).
- `bin/forge-mutante tests/mutantes/lote-l09.json`: rc=0, `M1 · morreu · bin/forge-check:5647`.
- shellcheck: nenhum shell no diff. `test_agentes_hash_brief.py`: fora do delta, não rodado.

## Checklist (leitura)
1. Escopo: a mensagem do `brief mensagem` deixa de chamar `lembrar_do_jarvis` e a primeira linha passa a ser `modo: brief` (E15); R-BRIEF e o conferente passam a dizer caminho e hash e um bloco por mensagem (A1 e A2 do L07); a falta de `Brief-sha256:` vira `forma:` (A1 da segurança do L07). Nada além do que o Histórico manda. O A3 da segurança do L07 (lista fechada de campos no hook) era para o backlog e ficou fora, corretamente.
2. O hook `mensagem_sem_forma` já recusa linha antes de `modo:`, então o E15 corrige a origem e `hooks/` não precisa mudar (o plano listava o arquivo; o delta não o toca, e a M14 fica sem as restrições de `hooks/`).
3. M14: 19 linhas de código e teste (`bin/forge-check` 2, `tests/config.json` 5, `tests/test_erros_no_brief.py` 12); `tests/mutantes/` fica fora. Um comportamento: a mensagem ao conferente (origem e o texto que a descreve), com as recomendações incluídas por decisão registrada.
4. Teste novo reprova sem a mudança (o mutante M1 morre) e afirma o stdout igual antes e depois do registro, a primeira linha `modo: brief` e o lembrete ainda no `brief`.
5. Invariante protegido: `tests/config.json` troca "literal, exatamente como será enviado" (R-BRIEF); a DECISÃO TÉCNICA de 04:17 pede destaque no título do PR (A2).

## Achados
- A1 (bloqueante) tests/test_forge.py:5512 · o teste busca a linha "- A mensagem pode ter dois blocos" que bc6d081 tirou de agents/conferente.md:16 e quebra (StopIteration); rode discover -p test_forge.py -k TextoDoConferenteNoLote: rc 1, na base rc 0
- A2 (recomendado) tests/config.json:610 · o PR muda um invariante protegido de R-BRIEF; o título do PR leva o destaque, como a DECISÃO TÉCNICA de 04:17 do pedido manda
- A3 (recomendado) agents/conferente.md:43 · a nova `forma: mensagem sem Brief-sha256` (reprova) não tem teste nem invariante; a correção do A1 pode afirmá-la junto com a linha nova do bloco único

## Parecer
Reprovado pelo A1, defeito provado. Passo para reproduzir: na worktree da branch, `python3 -I -m unittest discover -s tests -p test_forge.py -k TextoDoConferenteNoLote` dá rc 1 com `StopIteration` em `test_dois_blocos_so_depois_do_brief_e_modo_dentro_do_brief_nao_abre_bloco`; em `103247e` dá rc 0. Correção esperada: reescrever esse teste para a linha nova (`Cada mensagem traz um bloco só`, "mensagens separadas", `forma: instrução ao conferente`, "responda só ao primeiro bloco") e, de preferência, cobrir a `forma: mensagem sem Brief-sha256` (A3). O resto do delta está correto e pode seguir sem nova leitura na volta.
