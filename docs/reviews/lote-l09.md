---
tipo: review
contrato: 1
pedido: versao-033
branch: melhoria/lote-l09
commit: 51ef12d27a999df2a830c4971ffd2f265523ac44
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-04
---
# Review: L09 da 0.33, E15 BRIEF-MENSAGEM-LIMPA

Escopo: só o delta `103247e..bc6d081` (1 commit, `bc6d081`, 7 arquivos); os commits do L08 (`7f66d28..874c89e`) têm review próprio e ficam fora. Origem do escopo: item E15 do pedido e as DECISÕES TÉCNICAS de 04:00, 04:10 e 04:17 no Histórico de `docs/pedidos/versao-033.md`, que mandam ao E15 o A1 e o A2 do review do L07 e o A1 e o A2 da segurança do L07 (`docs/reviews/tempo-b1.md`, `docs/security/tempo-b1.md`).

Rodada 1 (bc6d081): **reprovado**, um bloqueante (A1): o commit troca a linha dos dois blocos de `agents/conferente.md:16`, mas não o teste que a exige, e `tests/test_forge.py` quebra.

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
- A2 (recomendado) tests/config.json:610 · o PR muda um invariante protegido de R-BRIEF; o título do PR leva o destaque, como a DECISÃO TÉCNICA de 04:17 do pedido manda

## Parecer
Rodada 1 (bc6d081): reprovado pelo A1 (tests/test_forge.py:5512, StopIteration), defeito provado, e com o A3 recomendado; os dois foram resolvidos na volta 1 (ver "Revalidação (volta 1)"). Passo usado para reproduzir: na worktree da branch, `python3 -I -m unittest discover -s tests -p test_forge.py -k TextoDoConferenteNoLote` dá rc 1 com `StopIteration` em `test_dois_blocos_so_depois_do_brief_e_modo_dentro_do_brief_nao_abre_bloco`; em `103247e` dá rc 0. Correção esperada: reescrever esse teste para a linha nova (`Cada mensagem traz um bloco só`, "mensagens separadas", `forma: instrução ao conferente`, "responda só ao primeiro bloco") e, de preferência, cobrir a `forma: mensagem sem Brief-sha256` (A3). O resto do delta está correto e pode seguir sem nova leitura na volta.

## Revalidação (volta 1)
Revisado: 51ef12d. A branch foi reempilhada sobre 7925640 (o L08 da volta 1) com o merge da develop 3a09c5a. Por isso o `forge-check delta --parecer` não roda direto a partir de bc6d081, que não é ancestral do head novo. O delta foi lido assim:
- `git range-diff`: 882a7dd tem o mesmo patch de bc6d081 (`=`), então fica como "já lido".
- 882a7dd..51ef12d: `agents/conferente.md` (+1) e `tests/test_forge.py` (+12 -5), lidos inteiros.
- O L08 (7925640) tem review próprio e ficou fora. Do merge 3a09c5a, conferi só o conflito em `skills/briefs-e-conferencia/SKILL.md:10`: os dois lados foram preservados.
- Nesta branch de review, o parecer da rodada 1 foi reaplicado sobre 51ef12d sem mudar o texto.

Veredito: **aprovado**. O A1 e o A3 da rodada 1 foram resolvidos; o A2 segue recomendado.
- A1: `test_um_bloco_por_mensagem_e_o_segundo_modo_e_instrucao_ao_conferente` substitui o teste antigo. Ele afirma que existe exatamente uma linha `- Cada mensagem traz um bloco só` com as cinco frases, e que a regra antiga dos dois blocos não volta.
- A3: `test_mensagem_sem_brief_sha256_reprova` afirma a `forma: mensagem sem Brief-sha256` (reprova).
- A1 da segurança: o exemplo da Entrada ganhou `Brief-sha256: <64 hex>   Bytes: <n>`, a mesma forma que o `brief mensagem` imprime (bin/forge-check:5683). O teste o procura só no trecho da Entrada.
- Teto M14 do E15: 36 linhas de código e teste (19 + 17); um comportamento só.

Fora do E15, mas registrado: o L09 está empilhado sobre o L08, que segue reprovado pelo A9 do parecer dele (`docs/reviews/lote-l08.md`: a conferência do head trava o `scripts/promover-homolog.py`). O L09 só se fecha depois do L08 e herda a correção dele.

Testes desta rodada, em 51ef12d, um módulo por vez (`python3 -I -m unittest discover -s tests -p <arq>`):
- test_erros_no_brief: rc=0, 42 testes
- test_mensagem_conferente: rc=0, 15
- test_comportamento: rc=0, 6
- test_forge: rc=0, 510
- `bin/forge-mutante tests/mutantes/lote-l09.json`: rc=0, `M1 · morreu · bin/forge-check:5673`
