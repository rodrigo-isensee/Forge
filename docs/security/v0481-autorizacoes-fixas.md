---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-autorizacoes-fixas
commit: 4c88ca81803e166767b3e3da3f3d4269e01ee305
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-26
---
# Review de segurança: v0481 (E14.67, #901, AUTORIZACOES-FIXAS, 1ª rodada completa)

Diff lido: `34ab6714..4c88ca81` (merge-base com a `develop`): emenda AUTORIZACOES-FIXAS da ADR 0018, `bin/forge_autorizacao.py`, `bin/forge-fechar` (corte diário), `bin/forge-testes` (E14.64), testes `test_autorizacao`, `test_autorizacao_gravar` e `test_fechar_corte`, specs de mutante e o fragmento do changelog. O merge da `develop` (#885) entrou sem conflito e não muda nada deste domínio.

- ci: 4c88ca81803e166767b3e3da3f3d4269e01ee305 verde

CI do head (run 45748475193): as 10 partes da suíte, `bateria (python 3.14)`, `bateria (verificações longas)`, `bateria (passos)`, os tetos de pulados, `instalação` e `catraca` estão verdes. Dois vermelhos, os dois por construção: `bateria (pareceres)` cai em R-REVIEW porque o PR toca `bin/forge-fechar` sem parecer aprovado (log do job 139670202413), e o agregador `bateria` cai porque `pareceres: failure` (job 139673358987). Os módulos tocados rodaram aqui: `python3 -m unittest tests.test_autorizacao tests.test_autorizacao_gravar tests.test_fechar_corte`, 92 testes, OK.

## Gatilhos
Gatilhos: autorização (registro e leitura das autorizações do dono, ADR 0018; R-DECISAO), controle do Forge (corte da versão no `forge-fechar`; R-CONFORMIDADE, R-MAIN).

## O que aperta, o que é neutro e o que afrouxa
**Aperta:**
- Os atos de antes rejeitam o alvo `fixo` e a validade `fixa` e leem `adulterada` (`bin/forge_autorizacao.py:122` e `:149`; teste `AtosFixos.test_alvo_fixo_e_validade_fixa_so_nos_atos_fixos_e_eles_so_com_eles`).
- `corte` e `aperta` viram termos de ato (`:282-283`): uma mensagem de rótulo ou de `main` que os traga nasce pendente ("mais de um ato"). Antes ela já nascia pendente pelo vocabulário, então na prática não muda nada que estivesse ativo.
- O ato fixo nasce pendente com alvo marcado, termo de validade, data ou hora, ressalva ou outro ato (`:343-352`; `test_alvo_validade_ressalva_ou_outro_ato_nascem_pendentes`). Nenhuma marca de negação ou condição entra no `VOCABULARIO_FIXO` (`:39`; `test_vocabulario_novo_so_nos_atos_fixos_e_sem_marca`).
- `cmd_corte` falha fechado: só lê concessão `ativa` com o ato `corte-diario`. Com retirada, sha que não bate, pendente ou qualquer evento ilegível na pasta, sai rc 1 (`:443-453`; `test_corte_diz_a_corte_diario_ativa_mais_nova_e_sem_ela_rc_1`).
- No `forge-fechar`, `corte_diario` (`bin/forge-fechar:1580-1595`) só autoriza com todas as condições valendo: ao menos 1 item, 06:00 locais ou mais, o CHANGELOG da `develop` lido e sem versão de hoje, e a saída do `forge-check` na forma positiva exata (regex ancorada, `:1594`). O relógio ilegível, a falha do `git show` e a saída fora da forma voltam ao "ainda não fecha".

**Neutro:**
- `so-aperta-com-seguranca`: a ferramenta só grava e lê esse ato. Nenhum código a consome (`grep` em `bin/`, `hooks/`, `scripts/` e `.github/`: os únicos leitores de `.forge/autorizacoes` são `cmd_ler` e `cmd_corte`). Ela não libera rótulo, merge na `main` nem custo (ADR 0018, F4).
- `bin/forge-testes:153` (test_fechar_corte no mapa FORGE_CHECK, E14.64). As specs de mutante `v0479-sieg-g1-gravar-2/3` e `v0480-d4-corte-contador-4` só acompanham o texto novo, com o mesmo efeito de antes (`-ge` virou `-lt` invertido, e o mutante segue de fronteira). O fragmento do changelog também é neutro.
- O `Gravado-por` preso ao sha do `forge-check` (F5): uma atualização do plugin deixa a fixa `adulterada`, e o corte volta ao contador. É falha fechada.

**Afrouxa (por ordem do dono de 25/11 07:52):**
- O teto da D1 (48 h ou 7 dias) não vale para os dois atos fixos (`:124-125`, `datetime.max`). Eles só param pela retirada `R-<Id>` ou pela troca do `forge-check`.
- O V4 do `--corte` deixa de parar abaixo do teto do contador quando há uma `corte-diario` ativa (`bin/forge-fechar:1637-1640`). A marca continua em rascunho para a `develop`, com os pareceres `release-<v>` e o `--laco` de sempre. O merge na `main` continua com o dono (R-MAIN).

## Coerência com a ordem de 25/11 21:5x e a recusa do classificador (ROTULO-SO-APERTA-PELO-TIME)
Com esse desenho, o rótulo `afrouxa-regra` continua sendo ato do dono: ou ele aplica, ou há uma concessão `rotulo-afrouxa-regra` gravada pela mensagem dele. Uma `so-aperta-com-seguranca` ativa não dá ao time ferramenta nenhuma para aplicar rótulo, e a catraca não a lê. Isso fica coerente com a recusa do classificador de 25/11 23:17 e com a primeira metade da decisão de 21:52 ("rótulo em item que afrouxa ... segue como ato do dono ou autorização gravada"). A segunda metade ("rótulo onde a segurança escreveu só aperta" pelo time) não é implementada aqui. Isso fica para o cartão S3, por autorização gravada, e é o lado seguro.

## Limite declarado (sem achado)
O portão `corte-diario` não é fronteira contra um agente. Com `FORGE_FECHAR_TESTE=1` e um `FORGE_CHECK` falso (`bin/forge-fechar:245-250`, mecanismo anterior a este PR), ou com o `gh` direto, um agente abre a marca sem concessão. Esse caminho já existia, e o ganho é nulo: sai só um rascunho para a `develop`, sujeito aos pareceres e ao merge do `tech-lead`, e a `main` continua com o dono. A integridade das concessões contra escrita direta na pasta depende do sandbox (só leitura em `.forge/autorizacoes`) e do sha do `forge-check`, o mesmo limite da ADR 0018. A validade sem fim faz esse limite durar mais, mas só para os dois atos fixos, que não liberam nada além do corte.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Ferramentas: leitura do diff, `grep`, os três módulos de teste locais e o `gh api` dos check-runs e dos logs dos dois jobs vermelhos. Sem varredura de segredos ou dependências, porque o diff não tem dependência nova nem configuração com credencial.
