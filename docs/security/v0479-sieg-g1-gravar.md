---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-sieg-g1-gravar
commit: d7c1a53b259e6f2ce980cbe05a2986eeed958be6
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-23
---
# Review de segurança: v0478 E90.8 (SIEG-G1, G1.2a, `autorizacao gravar`), volta por delta

Gatilhos: autorização do dono (ADR 0018), controle do Forge (`R-SEGURANCA`).

## Resumo
Volta da E90.6 sobre o parecer anterior (commit 5883995b, head 2a0e4620, reprovado). Delta lido com `forge-check parecer delta`: `2a0e4620..d7c1a53b`. No domínio entram `bin/forge_autorizacao.py` e `docs/adr/0018-autorizacao-do-dono-gravada.md`. Também li os testes e os mutantes do delta, que estão fora do domínio, para conferir o que deixou de ser testado.

Os dois bloqueantes fecharam. Com o comando real numa raiz descartável, o resumo de compactação recusa (S1), e um prazo local já vencido nasce `pendente-confirmacao` com uso único (S2). O classificador agora é positivo: `origin` tem de ser `{"kind": "human"}` (`:292`). Nas transcrições reais desta máquina, os 1.354 registros digitados pelo dono trazem essa forma, e nenhum resumo de compactação a traz. A `Hora-da-fala` no futuro ou com mais de 48 h recusa no `gravar` (`:377`). `tests/test_autorizacao_gravar.py`: 26 OK aqui.

Ficam abertos quatro recomendados, que voltam ao autor e são corrigidos antes do merge (`R-REVIEW`). A4 só fechou em parte: a raiz `~/.claude/projects` sai de `Path.home()`, que vem do `HOME`, e um agente aponta o `HOME` e o `CLAUDE_CODE_SESSION_ID` para uma transcrição que ele mesmo escreveu em `$TMPDIR`. Nesse caso a concessão nasce `ativa` (S4). O próprio teste usa esse caminho para montar a fixture. A3 continua aberto do lado do `ler`, e A5 e A6 seguem sem mudança (S5 a S7).

**Explorável antes dos próximos cortes?** Não, pelo mesmo motivo do parecer anterior: nada consome concessão, e a pasta `.forge/autorizacoes/` ainda aceita escrita direta. A ADR deixa para o hook a conferência do `transcript_path` e a forma literal do comando. Por isso, A4 continua recomendado e não sobe a bloqueante (o critério não mudou).

**Só aperta?** Sim. Contra o parecer anterior e contra a ADR, cada mudança do delta acrescenta recusa ou pendência:
- a transcrição tem de estar no lugar da sessão;
- o registro precisa de `origin` humano;
- o resumo de compactação recusa;
- a fala fora da janela de 48 h ou no futuro recusa;
- o prazo local, que antes nascia `ativa` com uso único, agora nasce `pendente-confirmacao`.

Nenhum leitor afrouxou, e `fim_do_termo` e `limite` não mudaram. Os testes e mutantes removidos do delta foram trocados por equivalentes mais estritos: o mapa do termo agora espera a pendência, e os mutantes antigos do classificador estão em `tests/mutantes/v0479-sieg-g1-gravar-7.json`. Há uma ressalva de texto, sem efeito no comportamento: a ADR diz que a volta "fechou esses quatro pontos (A1 a A4)", e isso vale para A1 e A2, mas não para A3 no `ler` nem para A4 com `HOME` trocado.

## Achados
- A3 (recomendado) bin/forge_autorizacao.py:118 · Aberto no `ler`: o `gravar` já recusa fala futura ou com mais de 48 h (:377), mas `limite`/`estado` não conferem `Hora-da-fala` contra agora. Uma concessão escrita direto na pasta com carimbo de 2030 segue `ativa`. Corrija antes do G1.3.
- A4 (recomendado) bin/forge_autorizacao.py:284 · Fechado em parte: a raiz vem de `Path.home()` (o `HOME`), e com `HOME` e `CLAUDE_CODE_SESSION_ID` trocados, uma transcrição escrita em $TMPDIR grava `ativa` (S4). Use `pwd.getpwuid(os.getuid()).pw_dir` e corrija na ADR 0018 o "fechou A1 a A4".
- A5 (recomendado) bin/forge_autorizacao.py:152 · Sem mudança: emoji de recusa e negação em cirílico ainda somem do vocabulário, e a mensagem nasce `ativa` (S5, S6).
- A6 (recomendado) bin/forge_autorizacao.py:380 · Sem mudança: com `--pedido` inexistente, "ate o fim deste pedido" vale os 7 dias inteiros (S7). Confira que o pedido existe e está aberto em docs/pedidos/.

## Sondas
- S1 · registro `type: user` com `isCompactSummary: true`, `isVisibleInTranscriptOnly: true` e sem `origin`, texto "pode aplicar o rotulo no pr 5", via `forge-check autorizacao gravar` · espera: recusada · obtido: recusada, "a mensagem não é uma só, digitada pelo dono nesta sessão"
- S2 · fala agora com "pode aplicar o rotulo no pr 5 ate 21/11" (dois dias antes), gravar e `ler` · espera: pendente · obtido: A-1 pendente-confirmacao (prazo local sem fuso nesta etapa), uso-unico; `ler`: 0 ativas
- S3 · `timestamp` 2030-01-01T00:00:00.000Z, e outro de 49 h atrás · espera: recusada · obtido: recusada, "Hora-da-fala no futuro ou fora da sessão (mais de 48 h)", nos dois
- S4 · `HOME=$TMPDIR/r CLAUDE_CODE_SESSION_ID=<id> forge-check autorizacao gravar --transcricao $TMPDIR/r/.claude/projects/-p/<id>.jsonl`, com a transcrição escrita pelo agente · espera: recusada · obtido: A-1 gravada, ativa
- S5 · "pode aplicar o rotulo no pr 5" seguido de dois emojis de proibição · espera: pendente · obtido: A-1 ativa
- S6 · "pode aplicar o rotulo no pr 5 нет" · espera: pendente · obtido: A-1 ativa
- S7 · `--pedido nunca-fecha` com "ate o fim deste pedido" · espera: pendente ou recusada · obtido: A-1 ativa até agora+7 dias
- S8 · `origin: {"kind": "human", "x": 1}` · espera: recusada · obtido: recusada

## Detalhe dos achados
Estado dos achados anteriores:
- **A1:** fechado (`:292`, S1, `resumo_de_compactacao` no teste com a forma real).
- **A2:** fechado (`:328`, S2, `test_prazo_local_ja_passado_nao_nasce_ativa`).
- **A3:** fechado no `gravar` (S3) e aberto no `ler`.
- **A4:** fechado em parte (S4).
- **A5 e A6:** abertos (S5 a S7).

S4 não abre uma capacidade nova: a pasta de concessões ainda aceita escrita direta. A correção mínima tira o `HOME` do caminho (`pwd`), e assim só sobra a transcrição real, que o sandbox não deixa o agente escrever (`~/.claude/projects` está fora da escrita). Um `CLAUDE_CODE_SESSION_ID` trocado ainda escolhe a transcrição de outra sessão real dentro de 48 h. Esse caso fica para o hook, que confere o `transcript_path` do evento, como a ADR já prevê. Esforço P. Dono: tech-lead.

Sondas S3, S5 a S8: apoio, não provam bloqueante.

## Riscos aceitos e ferramentas
Nenhum risco aceito. A suíte inteira não rodou aqui, e não há CI do PR: o brief pede sem suíte local e sem PR, e o CI do PR vai ser o portão da suíte. Rodei `tests/test_autorizacao_gravar.py` (26 OK) e as sondas S1 a S8 com o `bin/forge-check` do head, numa raiz descartável em `$TMPDIR`. Não rodei `gitleaks` nem `semgrep`: o delta não traz segredo nem dependência.
