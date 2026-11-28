---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-hook-agente-prazo
commit: fda308676fa86cd79217b7c2fe725889375ace04
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-27
---
# Review de segurança: v0481 (#950, HOOK-AGENTE-PEDIDO-GRANDE, E50.3)

1ª rodada completa sobre `319a968d..fda30867` (`hooks/agentes.py`, `tests/test_hooks_agentes_autor.py`, `tests/mutantes/v0481-hook-agente-prazo*.json`, fragmento do changelog).

## Gatilhos
Gatilhos: hook de controle (classe C), execução de processo externo (git) a partir do hook, troca temporária de funções de outro módulo.

## Sondas

## Detalhe dos achados
Sem achado bloqueante nem recomendado. O que foi conferido, com evidência:

- **Nenhuma recusa saiu.** O diff de `hooks/agentes.py` só toca `avisos_de_brief_vencido` (hooks/agentes.py:1117-1127) e acrescenta `GitEmLote` (hooks/agentes.py:1073-1114); selo, tipo do brief, hash e R-TETO ficam intocados. O aviso D3 segue só avisando (`except Exception` → `[]`). Teste: `PedidoGrande.test_disparo_com_o_pedido_grande_sai_no_prazo_e_as_recusas_seguem` (tipo errado e brief editado depois do selo continuam com código 2).
- **A troca de funções não vaza.** `forge_check()` é cache único do processo (hooks/_comum.py:2487), então a troca afetaria qualquer uso posterior; ela é feita por `with` e o `__exit__` (hooks/agentes.py:1088-1092) devolve as originais antes de matar o lote. Sonda local: exceção comum e `BaseException` (o caso do `PrazoVencido` do vigia) no meio do `with` devolvem as duas originais (`restaura-apos-excecao True`, `restaura-apos-baseexception True`). Teste: `test_mesma_resposta_em_toda_forma_de_pergunta` (assertIs nas originais).
- **Entrada forjada cai na chamada de sempre.** `SHA_COMPLETO.fullmatch` (hooks/agentes.py:1070, 1095, 1104) só aceita 40 hexadecimais minúsculos, sem quebra de linha no fim. Sonda com espião nas originais: sha40 + `\n` + sha40, sha em maiúsculas, `sha..HEAD`, `--all`, sha de 39 e sha com espaço no fim chamaram as duas originais e deram a mesma resposta delas. Como o lote só recebe sha40, nada injeta linha nem opção no `cat-file --batch-check`; o `rev-list` vai com `--end-of-options`.
- **Mesmas respostas.** Fora do `rev-list`, o objeto que não é o próprio commit (tag anotada) volta ao `merge-base --is-ancestor`; árvore e objeto ausente dão `None`/falso como antes. Teste: `test_mesma_resposta_em_toda_forma_de_pergunta` (ancestral, não ancestral, tag anotada, árvore, ausente, nome, faixa, quebra de linha).
- **Nada da cópia de trabalho roda com privilégio.** O lote roda `git -C <raiz>` com o ambiente sem `GIT_*` (hooks/agentes.py:1107), igual ao `git` do forge-check (bin/forge-check:606-608); `rev-list` e `cat-file` não executam hook, fsmonitor nem comando de config do repositório, e o forge-check segue carregado da pasta do plugin, não da cópia. Exposição igual à das chamadas que ele substitui. Teste: `test_o_lote_ignora_o_git_do_ambiente`.
- **Travamento e falha do lote fecham.** O `readline` do lote não tem prazo próprio, mas roda sob o vigia de 8 s do hook (hooks/agentes.py:1475-1478): o alarme interrompe a leitura e o prazo vencido recusa (falha fechada), e o `with` mata o processo. Lote morto (raiz que não é repositório) dá `BrokenPipeError`, que o `except` do aviso registra e engole: perde-se só o aviso, nunca uma recusa.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do diff, os 4 testes da classe `PedidoGrande` rodados localmente (OK, 18 s) e uma sonda de restauração e de entrada forjada. Suíte inteira: CI do head `fda30867` (run 46075222405), cinco partes da suíte, instalação, passos e verificações longas verdes; `bateria (pareceres)` vermelho só pela falta dos pareceres (R-REVIEW). Sem gitleaks e sem SAST da stack no PATH desta estação (lacuna registrada; o diff não traz segredo nem dependência nova).
