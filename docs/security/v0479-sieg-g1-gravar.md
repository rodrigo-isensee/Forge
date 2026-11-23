---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-sieg-g1-gravar
commit: 3e653044fb25104f5a56198d03da6d22602c0a50
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-23
---
# Review de segurança: v0478 E90.16 (SIEG-G1, G1.2a, `autorizacao gravar`), volta por delta

Gatilhos: autorização do dono (ADR 0018), controle do Forge (`R-SEGURANCA`).

## Resumo
Esta é a volta da E90.14 (Decisão 3a do dono) sobre o parecer aprovado cbdc9782 (head 9f833cd6). A rodada anterior fica no git. Li o delta com `forge-check parecer delta`, no intervalo `9f833cd6..3e653044`. Dentro do domínio estão `bin/forge_autorizacao.py` (`:319`, só o regex `marcado`) e `docs/adr/0018-autorizacao-do-dono-gravada.md`. Fora do domínio, também li `tests/test_autorizacao_gravar.py`, o mutante 8 (M58, M59) e `changelog.d/`. `tests/test_autorizacao_gravar.py`: 32 OK aqui.

Estado dos achados anteriores:
- **A3, A4, A5, A6:** seguem fechados. O delta não toca `estado`, `casa_do_dono`, `fora_do_vocabulario` nem o contexto do pedido.
- **Afrouxamento do A2 do review (S5 da rodada anterior):** desfeito. O regex `marcado` (`bin/forge_autorizacao.py:319`) voltou a `(?![\w.])` nos dois ramos. O texto é idêntico byte a byte ao da base 2d5efbe8 (`:311`). "pr 5." e "0.47.3." voltam a nascer `pendente-confirmacao` (S1), como na base (S2). O teste `test_ponto_final_logo_depois_do_alvo_deixa_pendente` exige pendente. Os mutantes M58 e M59 recolocam a forma frouxa `(?!\w|\.\w)`, e o teste os mata: no 9f833cd6 os dois casos saíam `ativa` (S3).
- **ADR 0018 e changelog:** a frase "o ponto final logo depois do alvo não o esconde" saiu. A ADR diz agora que esses casos seguem pendentes pela decisão 3a. Nada promete mais do que o código faz.

**Só aperta? Sim, por escrito.** Medido contra a base 2d5efbe8, o item agora só acrescenta recusa ou pendência: A3 (fala no futuro, adulterada), A4 (pasta pelo banco de senhas), A5 (emoji e outra escrita fora do vocabulário) e A6 (fim do pedido só com o pedido aberto). A única mudança que afrouxava foi o A2, e ela foi desfeita. Nas sondas S1 e S2, todo caso que era pendente na base continua pendente no head. A única diferença está no motivo de "pr 5._", que agora também lista `_` como fora do vocabulário, efeito do A5, ou seja, mais um aperto. Pelo lado da segurança, o rótulo "só aperta" vale para este item no head 3e653044.

**Explorável antes dos próximos cortes?** Não, e isso não mudou: nada consome concessão ainda, e a origem da transcrição só é provada no corte do hook, como a ADR registra.

## Sondas
- S1 · `leitura` do head com "pode aplicar o rótulo no PR 5.", "pode mesclar a main 0.47.3.", "pr 5.1", "pr 5._" e "pr 5" · espera: pendente nos quatro primeiros, ativa no último · obtido: pendente-confirmacao ("fora do vocabulário: 5"; "0, 3, 47"; "alvos do texto diferentes"; idem) e ativa
- S2 · as mesmas entradas na base 2d5efbe8 · espera: o mesmo estado do head · obtido: os mesmos estados; "pr 5._" lista só "5" no motivo
- S3 · as mesmas entradas no 9f833cd6 · espera: o afrouxamento que foi desfeito · obtido: "PR 5." e "0.47.3." ativa

## Riscos aceitos e ferramentas
Nenhum risco aceito. A suíte inteira não rodou aqui e não há CI do PR: o brief pede para não rodar a suíte local nem abrir PR, e o CI do PR será o portão. Rodei `tests/test_autorizacao_gravar.py` (32 OK) e as sondas S1 a S3. Não rodei `gitleaks` nem `semgrep`: o delta é uma linha de regex, sem segredo nem dependência.
