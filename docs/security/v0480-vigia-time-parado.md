---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-vigia-time-parado
commit: b13b7016c1fd7dd1796ea1f84a0cab672fc44c71
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-22
---
# Review de segurança: v0478 (E105.8, VIGIA-TIME-PARADO, revalidação)

Volta por delta sobre o parecer de 4822ad8e (head 3821ad14). Delta lido (`forge-check parecer delta`, 3821ad14..b13b7016), no domínio: `hooks/vigia.py`, `docs/hooks.md`. Fora do domínio e não relidos: testes, specs de mutante, `tests/pesos-d4.json`, fragmento do changelog. Já lido na rodada anterior e sem mudança: o resto do diff 900bfdfe..3821ad14.

Gatilhos: hook de controle (o vigia decide o `Stop` da sessão e escreve texto ao modelo).

## Achados
- A1 (bloqueante) hooks/vigia.py:626 · resolvido: reason ao modelo agora coberto pelo item 7 da emenda da ADR 0003 (melhoria/v0480-ordens-adr, e7a94603); o código segue o item 7: só Stop, só sessão do Jarvis, texto fixo, ID por lista positiva, uma vez por vez
- A2 (recomendado) hooks/vigia.py:560 · resolvido: ler_quadro abre com O_NOFOLLOW e O_NONBLOCK e exige arquivo regular (fstat); link e FIFO calam e vão ao erros.log
- A3 (recomendado) hooks/vigia.py:534 · resolvido: sete marcas comparadas sem caixa e sem espaço repetido, mais Responsável usuário pelo cabeçalho; no quadro real, livres caem de 76 para 27
- A4 (recomendado) hooks/vigia.py:545 · resolvido: sessao_do_jarvis exige agent_type no papel jarvis de conformidade.json; sem agent_type ou de outro agente, cala

## Detalhe
**A1 contra o item 7**, regra por regra:
- Só a sessão principal: `aviso_time_parado` sai em `hook_event_name != "Stop"` (`hooks/vigia.py:611`) e em `sessao_do_jarvis` falso (`:616`); `agent_type` vem de `papeis.jarvis` = `["forge:jarvis"]`. Sem `agent_type`, silêncio (falha fechada).
- Texto fixo: `hooks/vigia.py:626-627`; `<N>` é `len()`; `<ID>` só com `fullmatch` de `[A-Za-z0-9.-]{1,16}`, fora disso a linha sai sem `, primeiro`. O prefixo `Forge:` saiu do `reason` (`:655`), como o item 7 fixa. Nenhum texto livre do quadro entra.
- Uma vez por vez: `stop_hook_active is True` sai antes (`:613`), e a saída segue com o `systemMessage` de sempre.
- Nunca falha a sessão: tudo dentro do `try` com `registrar_erro`; código 0.
- Determinístico: só disco (quadro, `agentes.json`), sem rede nem git novo.
- Docstring (`:24-35`) e `docs/hooks.md` alinhados ao item 7.

Condição: o item 7 só vale com a branch `melhoria/v0480-ordens-adr` mesclada antes desta, e o título do PR leva o rótulo `afrouxa-regra` (emenda da ADR 0003, "Afrouxa").

## Sondas
- S1 · reason montado com IDs de 16 e 17 letras, G1-X, dígitos arábicos, largura total, a_b, espaço de largura zero e um ponto, contra a expressão do item 7 · espera: todos casam; só os de formato entram · obtido: todos casam; entram o de 16, G1-X e o ponto
- S2 · `cartoes_livres` sobre `~/.forge-contrib/KANBAN.md` real (só leitura) · espera: menos livres que os 76 da rodada anterior, sem "depois do", "DECISÃO DO DONO", "espera", "bloqueado" na Obs. · obtido: 27 livres, nenhuma dessas marcas na Obs.
- S3 · `python3 -m unittest tests.test_vigia_parado` · espera: OK · obtido: 22 testes, OK (inclui link, FIFO, sessão do Jarvis, ID fora do formato e o `principal` com o JSON exato)

## Cartões propostos (fora do delta, não bloqueiam)
- VIGIA-FIXTURE-ITEM7 (dono: qa-engineer): o item 7 prevê mudar o laço das fixtures de `tests/test_hooks.py` (aceitar `decision`/`reason` só no `Stop`, com o `reason` casando a expressão do item 7) e quatro fixtures em `tests/hooks/vigia/` (bloqueia uma vez, `stop_hook_active` libera, ID fora do formato, subagente silencioso). Hoje o comportamento é coberto pelos testes de unidade de `tests/test_vigia_parado.py`, mas a guarda de ponta a ponta do critério de reversão ("reason com texto fora do formato fixo") não existe no laço.
- Observação funcional: com o teto de 16 caracteres, a maioria dos IDs reais (o primeiro livre hoje tem 28) sai sem `, primeiro <ID>`. É o que a ADR fixa; não é defeito de segurança.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Suíte inteira: fica para o CI do PR (por brief). Ferramentas de SAST e varredura de segredos não estão no PATH: lacuna registrada.
