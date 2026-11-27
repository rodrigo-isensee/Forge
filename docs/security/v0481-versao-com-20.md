---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-versao-com-20
commit: 6e77f72a3a6a38e3dbdcc12b43e0525f5cb26113
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-27
---
# Review de segurança: v0481 E36.3, #928 (VERSAO-COM-20), 1ª rodada completa

Diff lido: `346a7860..6e77f72a` inteiro (19 arquivos). CI do head 6e77f72a verde fora os pareceres (histórico do pedido, 26/11 22:54 e 23:53); no run do 108b8095 (só o parecer de QA a mais), as 10 partes da suíte, a catraca e a instalação passaram, e o `bateria (pareceres)` falha só pelos pareceres (QA reprovado, review e segurança ausentes).

## Gatilhos
Gatilhos: autorização do dono gravada (ADR 0018, `bin/forge_autorizacao.py`), ferramenta de corte de versão a caminho da `main` (`bin/forge-fechar --corte`), invariantes trocados em `tests/config.json`.

## O que aperta, o neutro e o que afrouxa
- **Aperta.** Sai o único caminho que fechava versão abaixo do teto do contador: `bin/forge-fechar:1636` volta a cortar só com `N >= teto`, sem ler autorização (S2: nenhuma chamada ao forge-check; M1 de `v0481-versao-com-20.json` e M25 ajustado guardam a linha). `corte-diario` sai de `FIXOS` (`bin/forge_autorizacao.py:24`) e o termo `corte` sai de `ATO_DO_TERMO` (`:316`); as palavras `corte diario todo dia` saem do `VOCABULARIO_FIXO` (`:41`), então mensagem com elas nasce pendente. Concessão `corte-diario` já gravada lê `adulterada` ("Ato fora da lista") e nunca ativa (S3); `ler --ato corte-diario` cai na listagem com rc 1, sem a linha positiva que o forge-fechar antigo exigia: falha fechada.
- **Neutro.** Os textos do time e o fragmento de changelog; a troca dos invariantes `diretriz 34` e da seção do `ritmo-e-corte.md` em `tests/config.json` e `tests/fixtures/diretrizes-do-dono.json` (ordem do dono de 26/11 21:57, PR com o rótulo `afrouxa-regra` e o título que o destaca); a saída dos testes `CorteDiario` e dos mutantes M10 a M18, que guardavam só o código removido; `cmd_corte` agora exige o ato (`:477`); `test_fechar_corte` sai da tupla `FORGE_CHECK` de `bin/forge-testes:153` (seleção local; o CI roda tudo).
- **Os outros atos fixos seguem intactos.** `so-aperta-com-seguranca` ativa e lida por `ler` e `ler --ato` com uma `corte-diario` adulterada na mesma pasta (S3: a adulterada não derruba a vizinha; só erro de leitura deixa todas inativas); `rotulo-pelo-time` e o filtro pelo ato pedido cobertos por `test_ler_ato_fixo_diz_a_ativa_mais_nova_e_sem_ela_rc_1`; `merge-main` e `rotulo-afrouxa-regra` sem mudança de código. Na raiz do Forge, `.forge/autorizacoes` não tem `corte-diario` gravada.
- **Afrouxa (sem ordem do dono).** A guarda que separa o vocabulário dos atos fixos do vocabulário dos atos com prazo (`bin/forge_autorizacao.py:378`, M6) perdeu o único teste que a matava: A1.

## Achados
- A1 (bloqueante) tests/test_autorizacao_gravar.py:529 · o teste do M6 usa "todo dia", que o diff tirou do VOCABULARIO_FIXO; o M6 (VOCABULARIO_FIXO para todo ato) sobrevive e um merge-main com "o time decide" nasceria ativo sem que a suíte veja (S1, S4). Trocar o texto por palavra que só o fixo tem.

## Sondas
- S1 · bin/forge-mutante --rev 6e77f72a --ids M6 tests/mutantes/v0481-autorizacoes-fixas.json · espera: M6 morto · obtido: M6 sobreviveu em bin/forge_autorizacao.py:378
- S2 · forge-fechar --corte com 1 item abaixo do teto às 06:00 (test_abaixo_do_teto_nao_ha_corte_diario, CI do 6e77f72a) · espera: ainda não fecha, sem chamada ao forge-check · obtido: ainda não fecha, nenhuma chamada
- S3 · python3 -I _sec122-v0481-v20-sonda2.py (A-1 corte-diario e A-2 so-aperta gravadas; forge-check autorizacao ler e ler --ato) · espera: A-1 adulterada, A-2 ativa · obtido: A-1 adulterada (Ato fora da lista), A-2 ativa, ler --ato so-aperta rc 0
- S4 · fora_do_vocabulario("pode mesclar a main 0.47.3, o time decide") com VOCABULARIO e com VOCABULARIO_FIXO · espera: decide e time fora nos dois · obtido: fora só com VOCABULARIO; com o do M6, nenhuma palavra fora

## Detalhe dos achados
**A1.** Evidência: `tests/test_autorizacao_gravar.py:529` e `:531` (texto "pode mesclar a main 0.47.3 todo dia", motivo esperado "dia, todo"); guarda em `bin/forge_autorizacao.py:378`; o diff tirou `corte diario todo dia` do `VOCABULARIO_FIXO` em `:41`, e o texto do teste ficou fora dos dois vocabulários, com ou sem a guarda. Caminho de ataque: não há exploração hoje (o código está certo); o risco é de regressão sem alarme numa guarda de consentimento: uma troca que passe o `VOCABULARIO_FIXO` aos atos com prazo faz uma mensagem de `merge-main` ou `rotulo-afrouxa-regra` com ressalva ou delegação ("o time decide", "registra", "por escrito") nascer `ativa` em vez de pendente, e a suíte segue verde (S1, S4). É uma guarda de segurança da ADR 0018 (item 5, F2) que este diff deixou sem teste, sem ordem do dono para isso. Severidade: média. Correção mínima: no `test_vocabulario_novo_so_nos_atos_fixos_e_sem_marca`, trocar o texto por um com palavras que só o `VOCABULARIO_FIXO` tem, por exemplo "pode mesclar a main 0.47.3, o time decide", com o motivo esperado "palavra fora do vocabulário: decide, time"; conferir com o S1 (M6 morto). Esforço: P. Dono: `tech-lead` (autor do #928). Converge com o A1 do parecer de QA.

Fora do meu bloqueio: o A2 de QA (texto "até 2 por dia" em `agents/tech-lead.md:44`, `skills/falar-com-o-dono/nao-trava.md:19`, `templates/projeto/CLAUDE.md:15`) é de fluxo, não de segurança. O corpo da ADR 0018 (`docs/adr/0018-autorizacao-do-dono-gravada.md:182` e `:184`) ainda descreve F1 com dois atos e o F3; a retirada no fim (`:227`) o supera e a ferramenta recusa o ato, então fica sem achado.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do diff, `forge-mutante` (S1), as sondas S3 e S4 em `/root/.forge-contrib/wt/_sec122-v0481-v20-sonda.py` e `_sec122-v0481-v20-sonda2.py` (forge-check real, pasta temporária). Ausentes no ambiente (lacuna, não instaladas): gitleaks, semgrep, osv-scanner, zizmor; o diff não toca workflow, dependência nem configuração com segredo.
