---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-desenho-g1-g3-p7
commit: b25681a544f6df645bec1b3ec4215e1a3ad22067
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-23
---
# Review: v0478 (E137.10, PR #820, §7 do desenho G1 a G3)

Diff `0e59c446..b25681a5`: `docs/propostas/g1-g3-fluxo-rapido.md` (§2 item 1 e §7) e `changelog.d/v0480-desenho-g1-g3-p7.md`. Item só de texto (classe T), um parecer só. Fecha o A1 do review do desenho G1 a G3 (E137.6).

## Decisões conferidas contra o pedido v0478
- Regra de voltas (§2 item 1 e D1): DECISÃO DO DONO 2026-11-22 07:23 (2.ª volta, 3.ª sem perguntar se corrige só o apontado, não muda lógica, não afrouxa teste, métrica do item; falhou, corta e reabre menor) e ORDEM DO DONO 2026-11-23 14:24, que a reafirma. Bate. A nota de que a ferramenta e o `R-QA` ainda dizem 1 volta e de que alinhá-los é outro item é correta e fica fora do escopo.
- Rótulo (§7 item 1): DECISÃO DO DONO 2026-11-22 05:21 ("até segunda"; 23/11/2026 é segunda, e a PERGUNTA AO DONO de 23/11 15:02 registra o vencimento às 09:00); DECISÃO DO DONO 2026-11-23 15:25, opção 2a (G1.2/G1.3 entre os três itens, rótulo depois do último envio, checks verdes, merge nunca automático); regra até 2026-11-27 23:59 (só aperta por escrito da segurança, listado no aviso de marco; afrouxa continua indo ao dono). Bate.
- D2: DECISÃO DO TIME 2026-11-22 08:49 (reversível, aperta em relação à ordem de 21/11 22:13; `docs/regras/` com review e segurança, sem QA). Bate, e o texto não a apresenta como do dono.
- D3: a mesma linha de 08:49 a manda para a lista de segunda; segue aberta. Bate.
- D4: linha de 08:49 e marco de 2026-11-22 06:52 (#785, CI do PR 8m35s, dentro dos 10 min). Bate; manter a (b) como decisão do dono por afrouxar está de acordo com a regra de 22/11 07:23 ("só me traga o que afrouxa regra").
- D5: registro de 2026-11-23 14:36 ("o time segue a recomendação do desenho (G2 no Forge primeiro)"). Bate.

## Verificação
- Testes dos arquivos tocados: `tests.test_changelog` (89 OK) e o `Neutralidade` de `tests.test_forge` (6 OK). `tests.test_citacao` deu 2 falhas em `test_fonte_fora_da_raiz_nao_e_lida`, que exercita `bin/forge-check`, fora do diff; isso vem do ambiente do sandbox, não do diff. A suíte inteira fica com o CI do PR.
- Commit único, Conventional Commits em português, com o fragmento de changelog e sem edição do `CHANGELOG.md`.

## Achados
- A1 (recomendado) docs/propostas/g1-g3-fluxo-rapido.md:144 · §6 ainda diz que o rótulo `afrouxa-regra` é "aplicado pelo dono"; o §7 item 1 agora registra o time aplicando pelas decisões de 23/11 15:25. Ajustar a frase do §6 para remeter ao §7 (cartão depois do merge).

## Parecer
Aprovado. O §7 e o teto de voltas do §2 refletem fielmente as decisões do pedido v0478. Cada data e hora citada foi achada na fonte com o conteúdo descrito, e decisão do time não aparece como decisão do dono. O A1 é recomendado: é texto fora do trecho mudado, sem efeito em ferramenta.
