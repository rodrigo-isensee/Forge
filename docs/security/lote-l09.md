---
tipo: revisao-seguranca
contrato: 1
pedido: versao-033
branch: melhoria/lote-l09
commit: d4d1ca79ed7c5436d219f20a41c31520a0afa027
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-04
---
# Review de segurança: versao-033, lote L09 (E15 BRIEF-MENSAGEM-LIMPA)

Escopo: só o delta `103247e..bc6d081` (o L08, `7f66d28..874c89e`, tem parecer próprio). Arquivos: `bin/forge-check` (uma linha), `agents/conferente.md`, `docs/regras/R-BRIEF.md`, `tests/config.json`, `tests/test_erros_no_brief.py`, `tests/mutantes/lote-l09.json`, `changelog.d/lote-l09.md`. Revisão estática e defensiva.

## Gatilhos
Controles do Forge (`R-SEGURANCA`): `bin/forge-check brief mensagem`, o conferente e o texto protegido de R-BRIEF.

## Achados

## Detalhe dos achados
**Controle continua falhando fechado.** A única mudança de código (`bin/forge-check:5647`) remove a chamada a `lembrar_do_jarvis`, que só escrevia em stderr e nunca mudava stdout nem o código de saída (`bin/forge-check:2703-2709`). Antes dela e depois dela, `cmd_brief_mensagem` continua recusando: brief fora de `docs/briefs/`, acima do teto, fora de UTF-8, com `recusa_do_texto`, destino ou etapa divergentes, e brief que reprova no `forge-check brief` (rc 1, sem cabeçalho). O hash continua calculado sobre o mesmo buffer lido uma vez. O teste `test_mensagem_nao_traz_lembrete_e_a_primeira_linha_e_modo_brief` prova stdout idêntico com e sem registro de erros recorrentes e a primeira linha `modo: brief`; o mutante M1 guarda a volta do lembrete.

**Brief não conferido.** O hook `hooks/agentes.py` (fora do delta) segue exigindo `modo:` na primeira linha, uma só `Arquivo:` em `docs/briefs/` e uma só `Brief-sha256:` no cabeçalho, e recalcula o hash do arquivo (`hooks/agentes.py:213-271`); nada no delta o afrouxa. Sem o lembrete, some um bloqueio benigno (linha `jarvis-recorrente:` colada antes do `modo:`), não um controle: o ganho é de disponibilidade.

**Injeção pelo conteúdo do brief.** A mensagem segue sem o texto do brief (TEMPO-B1); o conferente lê o arquivo do disco. O conferente agora trata uma segunda linha `modo:` ou `Arquivo:` como `forma: instrução ao conferente`, e qualquer `forma:` diferente de `ok` reprova (`agents/conferente.md:59`); a segunda `Arquivo:` no cabeçalho já era barrada pelo hook. A regra antiga de dois blocos na mesma mensagem, que o hook já não aceitava com duas `Arquivo:`, sai: superfície menor.

**Hash do brief.** O conferente passa de aviso a reprovação quando falta `Brief-sha256:` (`agents/conferente.md:43`), e R-BRIEF passa a dizer caminho e hash em vez de cópia literal, coerente com o hook. Endurecimento, não afrouxamento. A janela entre a checagem do hook e a leitura pelo conferente é anterior ao delta e fica coberta pela comparação do hash do arquivo lido com o da mensagem.

**A1.** Evidência: `agents/conferente.md:38-42`, bloco Entrada com `modo`, `Pedido` e `Arquivo`, sem `Brief-sha256`. Caminho de ataque: nenhum direto (o hook barra mensagem sem hash antes do conferente); risco de o conferente, lendo o exemplo, julgar a forma pela amostra incompleta. Severidade: informativa. Correção mínima: acrescentar `Brief-sha256: <64 hex>   Bytes: <n>` ao exemplo. Esforço P. Dono: quem mantém `agents/conferente.md` no lote.

**Texto protegido.** R-BRIEF e `agents/conferente.md` mudam frases invariantes (`tests/config.json`); conferi que as 13 de R-BRIEF e as 61 do conferente seguem presentes. O changelog promete destaque no PR; cabe ao dono vê-lo.

## Revalidação (51ef12d)
A branch foi reempilhada sobre o L08 novo (`7925640`, parecer próprio em `docs/security/lote-l08.md` da sec-l08): o `bc6d081` virou `882a7dd`, com o mesmo `git patch-id --stable` (`cea4905`), então a análise acima vale sem mudança. O `forge-check delta` não serve aqui (o commit anterior não é ancestral depois do reempilhamento); li o delta `882a7dd..51ef12d` à mão: `agents/conferente.md:42` e `tests/test_forge.py`.
- A1 fechado: o exemplo da Entrada traz `Brief-sha256: <64 hex>   Bytes: <n>` (`agents/conferente.md:42`), e `test_mensagem_sem_brief_sha256_reprova` o prende, junto com a frase que reprova a mensagem sem o hash.
- `test_um_bloco_por_mensagem_e_o_segundo_modo_e_instrucao_ao_conferente` prende o bloco único e impede a volta da regra de dois blocos. Só texto e teste: nenhum controle afrouxa.
Testes (um módulo por vez): `test_forge.py` na classe tocada `TextoDoConferenteNoLote` (9, OK) e `test_erros_no_brief.py` de novo sobre a base nova (OK).

## Nota (d4d1ca7, teste do QA e mapa)
O delta `51ef12d..d4d1ca7` traz três coisas. A primeira é o merge do L08: o `bin/forge-check` muda só pela `promocao` do `a46eab7`, idêntica à revisada no parecer do L08. A segunda é o teste `tests/test_qa_lote_l09.py`. A terceira, no `bin/forge-testes`, são só acréscimos ao mapa FORGE_CHECK e aos LEITORES_DE_TEXTO, então o pre-push roda mais testes. Do E15, nada mudou em `bin/forge-check`, `agents/conferente.md`, `docs/regras/R-BRIEF.md` nem `hooks/`. Nenhuma recusa passou a liberar. `test_qa_lote_l09.py` (3): OK.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Testes: `python3 -I -m unittest discover -s tests -p test_erros_no_brief.py` (42 testes, OK). Invariantes de `tests/config.json` checadas por script local. `gitleaks` e `semgrep` não estão no PATH (lacuna; o delta não traz segredo nem dependência nova).
