---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-sieg-g1-gravar
commit: 2a0e46204eb6e731fec268e2d01fa32d142479eb
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: v0478 E90.4 (SIEG-G1, G1.2a, `autorizacao gravar`, PV-A2)

Gatilhos: autorização do dono (ADR 0018), controle do Forge (`R-SEGURANCA`).

## Resumo
O corte entrega `forge-check autorizacao gravar` (`bin/forge_autorizacao.py:269-409`). Tentei forjar a autorização pelas oito vias do pedido, com o comando real numa raiz descartável. Resistem a ferramenta, o subagente, o meta, o lembrete, a mensagem acima de 64 KiB, o marcador `M-<uuid>` reaproveitado, o `item:` solto ou fora da frase do ato e o `Commit` fora do head revisado. Isso vale para a sondagem e para `tests/test_autorizacao_gravar.py` (20 testes, verdes aqui).

Duas vias passam e reprovam o corte. O resumo de compactação, texto escrito pelo modelo, é lido como fala do dono e nasce `ativa` (A1). Um prazo local já vencido vira `uso-unico` `ativa` por até 48 h (A2).

**Explorável antes dos próximos cortes?** Hoje, não. Nada consome concessão: só `ler` e os testes importam o módulo (busca por `forge_autorizacao` e `autorizacoes` no repositório). A pasta `.forge/autorizacoes/` ainda não tem proteção, então um agente já escreve nela direto, com `Sha256` e `Gravado-por` públicos (ADR 0018, Consequências). O `gravar` não abre uma capacidade nova.

A transcrição, porém, é qualquer `.jsonl` (A4). Junto com a `Hora-da-fala` futura (A3), isso planta hoje uma concessão `ativa` até 2030, e ela sobrevive à proteção da pasta e ao hook, porque esses cortes só barram escrita nova. A ordem da ADR (G1.3 depende da G1.2 inteira) segura o consumo. A limpeza ou a recusa do que foi gravado antes da proteção tem de entrar nesse corte.

**Só aperta?** Não por inteiro. Contra a ADR, o corte segue o item 6, e o teto de 48 h no `uso-unico` é menor que os 7 dias do prazo escrito. Contra a fala do dono, que é o que a ordem de 16/11 protege, A2 dá validade além do prazo escrito e A1 grava texto que não é do dono. Fora disso, o corte só acrescenta recusas: nenhum leitor afrouxou, e `fora_do_revisado` só ganhou `ponta_do_ramo`, sem mudar o comportamento.

## Achados
- A1 (bloqueante) bin/forge_autorizacao.py:291 · Resumo de compactação (`isCompactSummary`, `isVisibleInTranscriptOnly`) passa no classificador e nasce `ativa` (S1); há 65 desses registros nas transcrições reais desta máquina. Fere o item 4 da ADR 0018 e a classe fala-forjada.
- A2 (bloqueante) bin/forge_autorizacao.py:330 · Prazo local vira `uso-unico` com teto de 48 h desde a fala, mesmo já vencido no texto: "ate <anteontem>" nasce e fica `ativa` (S2). A concessão passa do prazo escrito pelo dono em qualquer fuso; afrouxa a fala.
- A3 (recomendado) bin/forge_autorizacao.py:295 · `Hora-da-fala` da transcrição não é conferida contra agora: carimbo de 2030 grava `ativa` até 2030-01-03 (S3, A13 do parecer v047 em aberto no leitor). Recuse fala futura ou mais velha que o teto, no `gravar` e no `ler`.
- A4 (recomendado) bin/forge_autorizacao.py:282 · Qualquer `<sessão>.jsonl` vale como transcrição: uma escrita pelo agente em $TMPDIR, ou de outra sessão, grava `ativa` (S4). A conferência fica para o hook; o próprio `forge-check` (item 3, duas leituras) deve exigir a pasta de transcrições da raiz.
- A5 (recomendado) bin/forge_autorizacao.py:156 · O vocabulário positivo só vê `[a-z0-9]`: emoji de recusa e negação fora do alfabeto latino somem e a mensagem nasce `ativa` (S5, S6). Conte como palavra fora do vocabulário todo caractere que não é letra latina, dígito, espaço ou pontuação.
- A6 (recomendado) bin/forge_autorizacao.py:375 · `--pedido` é livre: "ate o fim deste pedido" com um pedido que não existe nunca encontra o `F-<Pedido>` e vale os 7 dias inteiros (S7). Confira que o pedido existe em `docs/pedidos/` e está aberto.

## Sondas
- S1 · registro `type: user` com `isCompactSummary: true` e `isVisibleInTranscriptOnly: true`, texto "pode aplicar o rotulo no pr 5", via `forge-check autorizacao gravar` · espera: recusada · obtido: A-1 gravada, ativa (nenhum), pr:5
- S2 · fala agora com "pode aplicar o rotulo no pr 5 ate 19/11" (data de dois dias antes), gravar e `ler` em seguida · espera: pendente ou vencida · obtido: A-1 gravada, ativa, uso-unico, `ler` diz ativa

## Detalhe dos achados
Sondas de apoio (não provam bloqueante): S3 é o carimbo `2030-01-01T00:00:00.000Z`, gravado `ate:2030-01-03 00:00` `ativa`. S4 é uma transcrição escrita em `$TMPDIR` pelo próprio agente, que gera A-1 `ativa`. S5 é "pode aplicar o rotulo no pr 5" seguido de dois emojis de proibição, e S6 é o mesmo texto seguido de "нет" em cirílico; os dois nascem `ativa`. S7 é `--pedido nunca-fecha` com "ate o fim deste pedido", que segue `ativa` em agora+6 dias. Recusas conferidas na mesma rodada: o marcador reaproveitado ("a mensagem já gerou concessão"), a mensagem de 64 KiB+1, "ainda nao" (pendente), o `item:` sem `Commit` e o `item:` fora da frase do ato.

**A1.** A evidência está em `bin/forge_autorizacao.py:291`: a lista negativa tem `isMeta`, `isSidechain`, `toolUseResult` e `sourceToolUseID`. O resumo de compactação é `type: user`, string, sem `<` no início, e passa. Caminho: depois de uma compactação, o Jarvis aponta o uuid do resumo. Esse texto é do modelo e pode citar, fora do contexto, uma fala antiga do dono. Hoje ele nasce pendente quando é longo e `ativa` quando é curto (S1). Severidade alta. Correção mínima: classificador positivo, que recusa registro com qualquer chave booleana verdadeira fora de uma lista do que o dono digita (das transcrições reais, só `queueSkipSlashCommands`), e fixture de resumo real no teste. Esforço P. Dono: tech-lead.

**A2.** A evidência está em `:330` (`fim_do_termo` em `:298` devolve `None` para data, dia e "esta noite") e no teto de 48 h de `limite` em `:117-120`. Caminho: o dono diz "até 19/11", ou "esta noite", e o agente usa a concessão no dia seguinte ao prazo; o leitor a vê `ativa`. Severidade média, porque hoje não há consumidor e depois ela fica dentro de 48 h. Correção mínima, que só aperta e não mexe no fuso: prazo local nasce `pendente-confirmacao` com o motivo "prazo local sem fuso nesta etapa", e o Jarvis pergunta a data, como o item 6 já prevê para o termo que não se lê. Também vale limitar o fim pelo instante mais cedo possível do prazo escrito (fuso UTC+14). Esforço P. Dono: tech-lead.

**A3 a A6.** Voltam ao autor e são corrigidos antes do merge (`R-REVIEW`). A3 e A4 precisam estar fechados antes do G1.3, junto com a recusa das concessões gravadas antes da proteção da pasta. O `--ramo` livre no alvo `item:` (o cartão não está preso ao `Ramo`) e a confiança nas refs locais de `fora_do_revisado` (um agente move `refs/remotes/origin/<ramo>` no clone) seguem o desenho: a ADR os confere no `declarar` e na catraca (PV-A3, PV-A4, E1), contra o remoto. Não abro achado.

## Riscos aceitos e ferramentas
Nenhum risco aceito. A suíte inteira não rodou aqui, e não há CI do PR (o brief pede sem suíte local e sem PR). Rodei `tests/test_autorizacao_gravar.py` (20 OK) e as sondas S1 a S7 com o comando real numa raiz descartável. Não rodei `gitleaks` nem `semgrep`: o diff não traz segredo nem dependência.
