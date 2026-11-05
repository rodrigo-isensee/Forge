---
tipo: review
contrato: 1
pedido: versao-033
branch: melhoria/lote-l09
commit: 8c889ce5e9d57f4657a86c6608444ac0ae596f74
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-05
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
- A4 (recomendado) bin/forge-testes:102 · o test_qa_lote_l09 roda hooks/agentes.py, mas não está na lista de hooks/.*; mudança só no hook não o roda no pre-push

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

## Revalidação (volta 2: teste do QA e mapa do forge-testes)
Revisado: d4d1ca7. O parecer da volta 1 (51ef12d) foi trazido para a branch por cherry-pick. Li só o que entrou na branch depois de 51ef12d e não é do L08:
- a6eee8b: `tests/test_qa_lote_l09.py`, do QA, lido inteiro.
- d4d1ca7: `bin/forge-testes` e `tests/test_testes_tocados.py`.

Os merges do L08 (f37be88 e d6c9ac7) trazem só o que foi revisado no parecer do L08. O d6c9ac7 não tem resolução manual: o `--remerge-diff` sai vazio.

Veredito: **aprovado**.
- O teste do QA liga o `forge-check brief mensagem` real ao hook `hooks/agentes.py` real. Ele cobre:
  - o caminho feliz;
  - a recusa do lembrete antes do `modo:`;
  - o hash ausente ou adulterado;
  - os dois blocos.
- O d4d1ca7 põe `test_qa_lote_l09` no `FORGE_CHECK` e no `LEITORES_DE_TEXTO`, e a contagem do mapa vai para 40.

Recomendação A4, sem bloquear: o `test_qa_lote_l09` roda o `hooks/agentes.py`, mas não está na lista de `hooks/.*` do `bin/forge-testes`. Uma mudança só no hook não o rodaria no pre-push.

Testes, em d4d1ca7:
- `python3 -I -m unittest discover -s tests -p test_testes_tocados.py`: rc=0, 86 testes.
- `python3 -I -m unittest discover -s tests -p test_fechar_forge_check_real.py`: rc=0, 2 testes.

## Revalidação (pareceres da branch: 1d50bea e 083a959)
Revisado: 8bc28d6, o merge da lote-l08 que trouxe 1d50bea e 083a959. Os merges 63ede5d e 8bc28d6 não têm resolução manual (o `--remerge-diff` sai vazio), e o patch do E15 não muda. Veredito: **aprovado**, sem achado novo.

Delta lido: 1d50bea e 083a959 do L08, nos arquivos `bin/forge-check` (+13 -2), `tests/test_forge.py` (+40 -5) e `tests/mutantes/lote-l08-pareceres-da-branch.json`.

Numa branch de trabalho, o `cmd_pr` agora conta só os pareceres cujo `branch:` é igual à branch. Se não houver nenhum, reprova com `sem parecer da branch` (falha fechada). A branch vem da ref ou, quando a ref é um sha, de `branch_do_sha`. A promoção, a biblioteca chamada sem branch (catraca do CI) e o sha ambíguo continuam lendo o parecer mais recente do pedido, como antes. Isso aperta a regra e não afrouxa nenhum portão.

O efeito no `hooks/parecer.py:419`, que usa o mesmo `cmd_pr`, também aperta: `gh pr create` e `gh pr ready` passam a exigir o parecer da própria branch.

Sonda de bypass: um parecer de outro item com `branch:` forjado para a branch de trabalho, e `commit:` na base. Resultado: rc 1, `commit: desatualizado: src/x.txt mudou depois do parecer`. O `branch:` só escolhe qual parecer é lido; a validade continua sendo a do `commit_vale`. Um parecer forjado não aprova nada que o mais recente do pedido já não aprovasse antes, então não há bypass.

Testes e mutante, num clone isolado em 083a959:
- `python3 -I -m unittest discover -s tests -p test_forge.py -k ConferenciaPresaAoHead`: rc=0 (11).
- `-k test_pr_`: rc=0 (32).
- `-p test_promover_homolog.py`: rc=0 (36).
- `bin/forge-mutante tests/mutantes/lote-l08-pareceres-da-branch.json`: rc=0, M53, M54 e M55 mortos.

Enquanto esta revalidação rodava, entrou o teste do QA 5ac531f (`tests/test_qa_lote_l08.py` +38 -1, classe `QaPareceresDaBranch`). Li o teste inteiro. Ele cobre três casos: o parecer próprio aprovado com o alheio desatualizado ou reprovado, a falta do parecer próprio com o alheio aprovado e a falta só do QA. Nenhum achado. `python3 -I -m unittest discover -s tests -p test_qa_lote_l08.py` deu rc=0 (24 testes). Ele chegou aqui pelo merge 0e3067b, sem resolução manual (o `--remerge-diff` sai vazio). O `commit:` passa a 0e3067b, o último commit de teste (E16).

## Revalidação (spec de mutantes, 988505e)
Delta lido: 988505e, só `tests/mutantes/lote-l08-e7b.json` (+13 -2). O `bin/forge-check` não mudou. Chega aqui pelo merge 871d884, sem resolução manual (o `--remerge-diff` sai vazio). Veredito: **aprovado**.

- **M36 equivalente: confere.** O `conferencia_do_head` só é chamado pelo `pr_da_cli` (bin/forge-check:667 e :681). Nos dois caminhos, antes da chamada, o `pr_da_cli` já faz `branch = branch or branch_da_ref(...) or branch_do_sha(...)` com a mesma ref. O `or branch_do_sha` do `conferencia_do_head` (bin/forge-check:757) só roda quando esse resultado é None, e aí repete a mesma busca com as mesmas entradas, que volta None. Tirar o `or branch_do_sha` não muda nada que a linha de comando produza. O motivo escrito na spec está correto. Ficam guardadas as duas buscas reais: com `--base`, pelo M55 (lote-l08-pareceres-da-branch.json); sem `--base`, pelo M56.
- **M56:** guarda a busca da branch pelo sha no `pr_da_cli` sem `--base` (:666), com `ForgeCheck.test_pr_parecer_da_branch_da_ref_vale_sobre_o_de_outra_branch`.
- **Recomendação, sem achado no bloco:** o fallback redundante de :757 pode sair do código numa próxima mudança de `bin/forge-check`, e o M36 junto. Código que nenhum mutante consegue matar é candidato a remoção.

`bin/forge-mutante tests/mutantes/lote-l08-e7b.json`, numa worktree limpa em 988505e: rc=0. M36 equivalente; M37, M50, M51, M52 e M56 mortos.

## Revalidação 0.34
Revisado: 8c889ce, a junção da develop (360186e, o #445 do L08) no L09, pedido versao-034 (E3). Veredito: **aprovado**, sem achado novo; o A2 e o A4 seguem recomendados.

Delta lido, `871d884..8c889ce` em `bin/` e `tests/`:
- 3625656, lido inteiro: `bin/forge-check` (+6 -5), `tests/apoio_conferida.py`, `tests/test_conf_escopo.py` e `tests/test_estado_da_branch.py`. O `pr_da_cli` ganha `conferir=True` por padrão; o único `conferir=False` é o do escopo da merge-integracao (bin/forge-check:1396), como no caminho do squash. O `forge-check pr` da linha de comando segue cobrando a conferência do head, e o teste novo de `test_conf_escopo` prova as duas metades. Nenhum portão afrouxa. O `bin/forge-check` do delta é exatamente o patch de 3625656.
- O resto do delta (`tests/mutantes/lote-l08-e7.json` e `lote-l08-escopo.json`) veio do #445, com os portões dele, e fica como "já lido".

Resolução dos conflitos (`git show --remerge-diff 8c889ce`):
- `bin/forge-testes` e `tests/test_testes_tocados.py`: ficou o lado do L09, com `test_qa_lote_l09` no `FORGE_CHECK` e a contagem 40. Correto, porque o lado da develop só não tinha o módulo do L09.
- `tests/mutantes/lote-l08-e7.json`: ficou o lado da develop. O `de` de M29 e M30 casa com o código (bin/forge-check:668 e :682).
- `docs/{reviews,security,qa}/lote-l08.md`: ficou o lado da develop, que são os pareceres finais do L08 mesclados no #445.

O patch próprio do L09 sobre a develop atual (`360186e...8c889ce`) é só o E15: 120 linhas de código e teste, dentro do teto da M14, e `hooks/` igual à develop.

Testes: `bin/forge-testes bin/forge-check`, em modo dirigido com 40 módulos. Eles cobrem `test_conf_escopo`, `test_estado_da_branch` e os importadores de `apoio_conferida` (`test_forge`, `test_isencoes`). Resultado: rc=1, `Ran 1560 tests`, `FAILED (failures=10, skipped=27)`. As 10 falhas são todas de orçamento de tempo do hook:
- `test_hooks.Hooks.test_muitos_heredocs_recusam_dentro_do_orcamento`, 9 formas, com 6,0 a 6,5 s contra o limite de 5,0 s;
- `test_hooks_volta_lancador...test_tempo_do_teto_das_leituras_do_lancador`, com 28,6 ms contra 24,5 ms.

Repetidas sozinhas, as falhas voltam com a máquina em carga 18 sobre 12 núcleos. Nem o `hooks/` nem esses testes estão no delta ou no patch do L09, então as falhas não vêm do que foi revisado. A confirmação fica com a suíte do QA e o CI do PR.
