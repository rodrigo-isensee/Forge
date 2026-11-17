---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-maq-i9-trava-s
commit: 8bff4e7dbb0a168e55356899a00e64648c27a49f
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-17
---
# Review de segurança: v047 (E2.680, MAQ-I9 fatia 2, TRAVA_S 600 para 1.200 s)

Escopo: `git diff 73a0ab81..8bff4e7d` (f07cb1ab, 8bff4e7d): `hooks/pesado.py` (só a constante e o comentário), fixture renomeado, `tests/test_pesado_fila.py` (classe `TravaDeVinteMinutos`), `tests/test_forge_pesado.py`, mutantes e o fragmento do changelog. Só leitura da branch (Z10), sem suíte local (brief): a bateria inteira é a do CI do PR.

Gatilhos: controle do Forge (hook `pesado`, `R-TETO`), afrouxa-regra (prazo da trava de recurso compartilhado entre sessões).

## Afrouxamento
- **O que muda:** `hooks/pesado.py:33` sobe `TRAVA_S` de 600 para 1.200. O teto efetivo é `min(expira_s(), TRAVA_S)` (`hooks/pesado.py:114`), então `expiracao_horas` menor ainda limita (provado por `test_expiracao_menor_limita_os_20_min`). Os outros leitores usam a mesma constante, sem cópia do número: `bin/forge-pesado:102` e `hooks/agentes.py:329` (C9: registro de agente com escrita só sai com a trava livre).
- **Caminho de ataque:** nenhum novo. Quem prende a trava é uma sessão local do mesmo usuário, com o PID vivo (`pid_vivo`, `hooks/pesado.py:159-175`: morto, zumbi ou PID reaproveitado soltam na hora, sem mudança). O efeito é só de disponibilidade: uma trava sem o par Post (permissão negada no diálogo, outro hook bloqueou) prende as outras sessões por até 20 min em vez de 10. A própria sessão e o próprio agente nunca são barrados, a espera segue pela fila com teto `ESPERA_S` = 240 (sem mudança) e recusa com a posição, e a liberação manual (apagar `.forge/run/pesado.json`) continua. Não há fronteira de confiança cruzada, rede, segredo nem escrita nova.
- **Motivo aceito:** a suíte em série vai a 693 s; com 600 s a trava vencia no meio e outra sessão pesada entrava junto, que é o risco que o `R-TETO` contém (carga da máquina). O afrouxamento troca 10 min a mais de espera no pior caso por não perder a trava em uso legítimo. Proporcional; a decisão de afrouxar segue sendo do dono pelo rótulo do PR (`R-CONFORMIDADE`, `R-DECISAO`).
- **A frase de `docs/security/processo-pronto-develop-instancias.md:55`** (600 s / 10 min para 1.200 s / 20 min), escrita pelo tech-lead no 8bff4e7d: conferida e assumida por este parecer (ESCOPO+ E2.678). O "no máximo 20 min" vale com `expiracao_horas` padrão (2 h); com valor menor, o teto é menor, o que só reforça o limite.

## Provas
- `python3 -m unittest tests.test_pesado_fila.TravaDeVinteMinutos tests.test_forge_pesado.ForgePesado.test_trava_vencida_fica_livre` no clone, head 8bff4e7d: 4 OK.
- Mutantes do `tests/mutantes/v047-maq-i9-trava-s.json`, aplicados numa cópia por `git archive` em `$TMPDIR`: M1 (`TRAVA_S = 600`) derruba `test_pid_vivo_ha_mais_de_10_min_segue_ocupado_e_vai_para_a_fila`; M2 (`TRAVA_S = 1400`) derruba `test_pid_vivo_ha_mais_de_20_min_solta`. Os dois mortos.

## Achados
- A1 (recomendado) docs/hooks.md:122 · Doc do hook ainda diz 10 min em :14 (tabela), :72 (prazo da trava) e :122 (negação interativa "só contida pelos 10 minutos"); o prazo agora é 20 min. Trocar as três por 20 minutos (TRAVA_S = 1.200 s). Dono: tech-lead.

## Sondas

## Riscos aceitos
Nenhum por este parecer. O afrouxamento em si é decisão do dono pelo rótulo `afrouxa-regra` do PR.
