---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-agentes-caiu-em-finito
commit: 814086187e3fcef8bc2280927c40ff27c6a547be
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: v0479-agentes-caiu-em-finito

Etapa E53.3 do pedido v0478, no head 81408618 (base develop 5ccac0bf). Escopo lido: `hooks/agentes.py` (diff inteiro), os três testes novos de `tests/test_agentes_interrompidos.py`, os mutantes e o fragmento do changelog.

## Gatilhos
Gatilhos: hook de controle do Forge (`hooks/agentes.py`, R-TETO e reserva de disparo), estado de controle lido de arquivo (`agentes.json`).

## Resumo
- **Defeito fechado (reproduzido na base):** em 5ccac0bf, `lapides` ou `autores` com `desde` = 10**400 fazem `agora - desde` levantar OverflowError fora do `except EstadoIlegivel` de `principal` (`hooks/agentes.py:1309`); a exceção sobe até `executar`, que chama `falhar_fechado` com `critico=None` (`hooks/_comum.py:2793`) e sai 0: o disparo passa sem reserva. Na sonda da base, as quatro combinações (lápide e autor, ±10**400) deram OverflowError sem reserva.
- **Correção:** `lapides_vigentes` (`hooks/agentes.py:563-573`) e `autores_vigentes` (`hooks/agentes.py:674-687`) passam pelo `caiu_em_finito` (`hooks/agentes.py:640`, o mesmo já usado em `interrompidos`) e levantam `EstadoIlegivel` para inteiro enorme, inf e nan; o disparo recusa e o arquivo não é regravado. Sem caminho novo de liberação: o item que não é registro, ou de `desde` não numérico, continua fora como antes.
- **Família varrida no head (sonda PreToolUse de `principal`, 5 valores: ±10**400, ±inf, nan, em 5 campos):** `lapides.desde`, `autores.desde` e `interrompidos.caiu_em` saem 2 sem regravar; `agentes[].desde` e `interrompidos[].desde` saem 0 **com** a reserva gravada (o `vigentes` mantém o registro na dúvida, `hooks/agentes.py:372-380`; o `interrompidos.desde` só é copiado). Na retomada (`SendMessage`), lápide e autor não finitos recusam; registro ativo segue o caminho de sempre. Nenhuma combinação passou sem reserva. O `espera` do registro da máquina e o `desde` da trava `pesado` estão sob `except Exception` que recusa ou mantém o registro (`hooks/agentes.py:1197-1199`, `:379`).
- **Efeito colateral aceitável:** quem grava um `desde` não finito em `agentes.json` trava os disparos (recusa por estado ilegível); é o mesmo efeito de gravar JSON inválido, já tratado como ilegível, e o arquivo é de controle.
- **Testes:** rodados no head os três novos (`test_lapide_e_autor_com_numero_nao_finito_deixam_o_estado_ilegivel`, `test_lapide_e_autor_finitos_seguem_o_prazo`, `test_disparo_com_lapide_ou_autor_enorme_e_recusado_sem_regravar_o_estado`): 3, OK. Os mutantes novos cobrem o filtro e o prazo das duas funções.

## Sondas

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Suíte inteira: não rodada (brief, "sem suíte local"); entrega E53.1 conferida pelo Jarvis no head 81408618 (pedido v0478, histórico 14:10); o CI do PR, obrigatório para o merge, fecha a bateria. Ferramentas: varredor de segredos e SAST fora do PATH (lacuna; o diff não toca segredo, dependência nem workflow). Sondas em pasta temporária, fora do repositório.
