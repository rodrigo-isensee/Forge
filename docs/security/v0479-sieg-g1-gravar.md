---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-sieg-g1-gravar
commit: 9f833cd6d8290f0d0aeeb2306ef1f16fa56f9b67
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-23
---
# Review de segurança: v0478 E90.12 (SIEG-G1, G1.2a, `autorizacao gravar`), volta por delta

Gatilhos: autorização do dono (ADR 0018), controle do Forge (`R-SEGURANCA`).

## Resumo
Esta é a volta da E90.10 sobre o parecer aprovado f88a2a8e (head d7c1a53b, com quatro recomendados abertos). A rodada anterior fica no git. Li o delta com `forge-check parecer delta`, no intervalo `d7c1a53b..9f833cd6`. Dentro do domínio estão `bin/forge-check` (`:10713`, o `pedido_existe` no contexto), `bin/forge_autorizacao.py` e `docs/adr/0018-autorizacao-do-dono-gravada.md`. Fora do domínio, também li o delta de `tests/test_autorizacao_gravar.py` e os mutantes 8 e 9. `tests/test_autorizacao_gravar.py`: 32 OK aqui.

Estado dos achados anteriores (sondas S1 a S6, com o `bin/forge-check` do head numa raiz descartável em `$TMPDIR`):
- **A3:** fechado. `estado` (`:242`) trata `Hora-da-fala` depois de agora como adulterada. No instante da fala, a concessão vale (S1).
- **A4:** fechado no que o código alcança. `casa_do_dono` (`:282`) vem do banco de senhas. A sonda S4 da rodada anterior (`HOME` e `CLAUDE_CODE_SESSION_ID` apontados para uma transcrição escrita em `$TMPDIR`) agora é recusada (S2). Continua possível, dentro de 48 h, escolher a transcrição de outra sessão real pelo `CLAUDE_CODE_SESSION_ID`. Isso fica para o corte do hook (`transcript_path` do evento), e a ADR agora diz isso por escrito.
- **A5:** fechado. Emoji, letra cirílica e travessão contam como fora do vocabulário e deixam a concessão pendente (S3).
- **A6:** fechado. "até o fim deste pedido" nasce pendente quando o pedido não está em `docs/pedidos/`, quando há `F-<Pedido>` gravado ou quando falta `pedido_existe` (S4). `pedido_para_anotar` só aceita o id, e `--pedido` com caminho é recusado como "Pedido fora da forma".
- **Texto da ADR 0018:** corrigido. A ressalva da rodada anterior ("fechou A1 a A4") saiu. Agora o texto diz o que cada volta fechou e declara que a origem da transcrição **não** está provada até o corte do hook.

**Só aperta?** Não. A3, A4, A5 e A6 só acrescentam recusa ou pendência, mas uma mudança afrouxa: o A2 do review. O regex `marcado` (`:319`) trocou `(?![\w.])` por `(?!\w|\.\w)`. Com isso, "pr 5." e "0.47.3." deixaram de nascer `pendente-confirmacao` (na base 2d5efbe8: "palavra fora do vocabulário: 5") e passaram a nascer `ativa` (S5). Não há caminho de ataque: o ponto final não muda o alvo, e o que vem depois dele continua preso ("pr 5.1" e "pr 5._" seguem pendentes, com "alvos do texto diferentes", S6). Aprovo a mudança, mas, por escrito, ela não entra no rótulo "só aperta".

**Explorável antes dos próximos cortes?** Não. Nada consome concessão ainda, e `.forge/autorizacoes/` aceita escrita direta até o corte do hook, como a ADR registra.

## Sondas
- S1 · concessão gravada agora; `concessoes` lida 5 min antes e depois no instante da fala · espera: adulterada, depois ativa · obtido: `('A-1', 'adulterada', 'Hora-da-fala no futuro')`, depois `('A-1', 'ativa', '')`
- S2 · `forge-check autorizacao gravar` com `HOME` e `CLAUDE_CODE_SESSION_ID` trocados para uma transcrição em `$TMPDIR`, com a casa real do `pwd` · espera: recusada · obtido: recusada, "transcrição não é o .jsonl comum da sessão em curso"; no controle, com a casa do `pwd` na raiz: A-1 ativa
- S3 · "pode aplicar o rotulo no pr 5" com dois emojis de proibição, com "нет" e com "— nao" · espera: pendente · obtido: pendente-confirmacao, com "fora do vocabulário: 🚫", "е, н, т" e "nao, —"
- S4 · "ate o fim deste pedido" com `--pedido nunca-fecha` e com `--pedido v0478` e `docs/pedidos/v0478.md` presente · espera: pendente e ativa · obtido: pendente-confirmacao ("pedido inexistente ou fechado") e ativa; com `--pedido ../../x`, recusada
- S5 · "pode aplicar o rotulo no pr 5." no head e na base 2d5efbe8 · espera: o afrouxamento declarado · obtido: ativa no head, pendente-confirmacao na base
- S6 · "pr 5.1" e "pr 5._" · espera: pendente · obtido: pendente-confirmacao, com "alvos do texto diferentes dos declarados"

## Riscos aceitos e ferramentas
Nenhum risco aceito. A suíte inteira não rodou aqui e não há CI do PR: o brief pede para não rodar a suíte local nem abrir PR, e o CI do PR será o portão. Rodei `tests/test_autorizacao_gravar.py` (32 OK) e as sondas S1 a S6. Não rodei `gitleaks` nem `semgrep`: o delta não traz segredo nem dependência, e o único import novo é `pwd`, da biblioteca padrão.
