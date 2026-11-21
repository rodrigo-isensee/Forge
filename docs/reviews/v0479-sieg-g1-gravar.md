---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-sieg-g1-gravar
commit: 2a0e46204eb6e731fec268e2d01fa32d142479eb
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-21
---
# Review: v0478 E90.3 (SIEG-G1 G1.2a, `forge-check autorizacao gravar`, com PV-A2)

## Achados
- A1 (bloqueante) bin/forge_autorizacao.py:291 · O classificador aceita o resumo de compactação (registro real: type user, isCompactSummary e isVisibleInTranscriptOnly, sem isMeta), texto do modelo, como fala do dono, e grava o corpo (S1, ativa). A ADR 0018 item 4 o exclui. Recuse-o e faça o classificador positivo, com fixture real
- A2 (recomendado) bin/forge_autorizacao.py:309 · `(?![\w.])` não aceita ponto final logo depois do alvo: "pode aplicar o rótulo no PR 5." nasce pendente ("palavra fora do vocabulário: 5"); o mesmo com "main 0.47.3.". Falha fechada, mas é a forma comum da fala; alinhe com o `do_item`, que aceita o ponto
- A3 (recomendado) docs/adr/0018-autorizacao-do-dono-gravada.md:44 · O G1.2a adia a conferência do transcript_path no hook, mas não diz que o próprio forge-check (item 3, "repete as duas conferências") aceita até lá qualquer .jsonl: uma transcrição escrita por agente gera concessão ativa. Diga que o registro não prova origem até o corte do hook
- A4 (recomendado) bin/forge_autorizacao.py:279 · `mensagem_do_dono` repete o filtro de `texto_do_dono` (hooks/vigia.py:301), que tem a mesma falta do A1. Duas cópias do classificador divergem; uma fonte única fecha o A1 nas duas

## Sondas
- S1 · registro {"type":"user","isCompactSummary":true,"isVisibleInTranscriptOnly":true,"message":{"content":"pode aplicar o rótulo no pr 5"}} e gravar --alvos pr:5 · espera: autorizacao: recusada · obtido: rc 0, A-1 gravada · ativa (nenhum)

## Conferido
- **Comportamento (leitura):** o corpo é a mensagem lida da transcrição, nenhuma opção traz texto (`--mensagem`, `--transcricao`, `--ato`, `--alvos`, `--ramo`, `--pedido`); registro único por uuid, `sessionId` igual ao nome do arquivo, sem link, até 64 KiB; o gravar confere com `problemas` do leitor antes de gravar e usa o `fora_do_vocabulario` dele; `M-<uuid>` e `A-<n>` abertos com `x` e sem seguir link. Sondas extras (sem bloqueio): negação ("nao pode ...") e alvo a mais ("pr 5 e no pr 6") nascem pendentes; "[Request interrupted by user] ..." nasce pendente.
- **PV-A2:** o `Commit` do alvo `item:` sai do parecer de review do `Ramo`, só sha hexadecimal vira argumento do `git`, e passa pelo `fora_do_revisado`; sem pareceres, sha fora do head ou ressalva, recusa ou nasce pendente (testes `ItemPresoAoCommit` do gravar). A M24 de `tests/mutantes/v0479-pv-a2-concessao-3.json` aponta a linha nova de `ponta_do_ramo`.
- **ADR 0018 e o corte:** o G1.2a registra o que entra e o que fica (fuso em `/etc/localtime` e prazo local, `confirmar`, `retirar`, forma literal no hook, `transcript_path` e as três grafias); a regra "sem fuso legível vale uso único" do item 6 é a que o código aplica, e "fim deste pedido" e as 48 h seguem em tempo absoluto. Coerente, com a ressalva do A3.
- **Tamanho (H1):** cerca de 145 linhas de código em `bin/`, dentro do teto; 46 mutantes declarados em seis arquivos de até 8.
- **Testes:** `python3 -m unittest tests.test_autorizacao_gravar tests.test_autorizacao`: 37 testes, OK. Suíte inteira: no CI.

## Parecer
Reprovado pelo A1 (`R-REVIEW`): o pedido é que o gravar nunca aceite texto que não seja a fala do dono, e a ADR 0018 item 4 exclui o resumo de compactação, que passa e é gravado como mensagem do dono (S1, forma tirada de um registro real). Correção: recusar `isCompactSummary` e `isVisibleInTranscriptOnly` (melhor ainda, aceitar só a forma conhecida, como pede o "classificador positivo"), com teste do ramo de falha e mutante declarado. A2 a A4 não bloqueiam e viram cartão depois do merge.
