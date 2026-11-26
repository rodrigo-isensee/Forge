---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-rotulo-base-alheia
commit: 48034214f4654bf7d00788ea68f0c0790d79783e
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-26
---
# Review de segurança: v0481 (E17.4, #906, 1ª rodada completa)

Gatilhos: controle do Forge (a catraca, `tests/catraca.py`, arquivo PROTEGIDO), regra de validade do rótulo `afrouxa-regra` do dono (ADR 0008), aceite do usuário (`docs/security/aceites/`).

## Lido
Diff `22ceb2c8..48034214` (merge-base com a develop): `tests/catraca.py` (`PARECERES` +`docs/security/`, constante `ACEITES`, filtro em `pareceres_do_pedido`), 2 testes em `tests/test_catraca.py`, spec `tests/mutantes/v0481-rotulo-base-alheia.json` (RB1, RB2), fragmento. Lidos também, sem mudança: `rotulo_vale_pelo_conteudo`, `protegidos_como_no_rotulo` (`tests/catraca.py:1439-1464`) e, no `bin/forge-check`, `mesmo_diff`, `arquivos_divergentes`, `desatualiza` e `livre` (`bin/forge-check:635-643, 735-783`).

## O que aperta, o neutro e o que afrouxa
- **Afrouxa (o que o item pede, decisão do dono 24/11):** depois do rótulo, mudam sem derrubá-lo pelo caminho `mesmo_diff` os arquivos de `docs/security/` fora de `aceites/` que o PR já tocava no head rotulado e o `docs/security/<último segmento da branch>.*`. Antes, só `docs/reviews/` e `docs/qa/`. Limite: nenhum desses é lido como regra por código (busca em `bin/`, `hooks/`, `scripts/`, `.github/`: só `aceites/` é consumido como controle); a validade do próprio parecer segue no modo `pareceres` (`commit:`, domínio, autoria pelo hook `conformidade`); e `violacoes_novas` continua rodando nos dois caminhos (`tests/catraca.py:1463-1464`).
- **Neutro:** `protegidos_como_no_rotulo` e `VIGIADOS_DO_ROTULO` sem mudança; nenhum PROTEGIDO nem `hooks/conformidade.json`/`tests/config.json` mora em `docs/security/`, então nenhum arquivo de controle entra no `ignorar`. O filtro de curinga (`CURINGA`) segue. O alinhamento com `LIVRES` do `bin/forge-check:203`, que já trata `docs/security/` como pasta de parecer, é neutro.
- **Aperta / mantém fechado:** o aceite do usuário nunca entra no `ignorar`: o filtro `not a.startswith(ACEITES)` (`tests/catraca.py:1394`) o tira do conjunto do head rotulado, e o casamento por nome exige pai exatamente em `PARECERES` (`tests/catraca.py:1397`), que `docs/security/aceites/` não é. Por trás, `desatualiza` (`bin/forge-check:643`) já recusa o aceite que não esteja nomeado no `ignorar`. Apagar ou renomear aceite aparece no diff (`--no-renames`) e diverge. Provas: `test_aceite_do_usuario_ou_parecer_de_seguranca_alheio_depois_do_rotulo_invalida` (aceite tocado no head rotulado e reescrito depois, e parecer de segurança de outro pedido: rc 1) e `test_parecer_de_seguranca_do_pedido_e_merge_da_base_mantem_o_rotulo` (o caso do #875: rc 0).

## Achados
- A1 (recomendado) tests/catraca.py:45 · ACEITES copia à mão o ACEITES_DO_USUARIO do bin/forge-check:2298, sem teste de paridade; se a lista do forge-check crescer, a pasta nova tocada no head rotulado entra no ignorar do mesmo_diff e o desatualiza não a segura, pois ela vai nomeada.

## Detalhe dos achados
**A1.** Evidência: `tests/catraca.py:45` e `bin/forge-check:2298`; `desatualiza` (`bin/forge-check:643`) só segura o aceite que não está nomeado no `ignorar`, e é a catraca que o nomeia. Caminho de ataque: hoje nenhum (as duas listas são iguais, uma pasta só); o risco é a deriva silenciosa de uma fonte duplicada (ADR 0002, uma fonte só) num controle da fábrica: um PR futuro que acrescente pasta de aceite só no `forge-check` deixaria o aceite dessa pasta, tocado antes do rótulo, ser reescrito depois dele sem derrubá-lo. Severidade baixa. Correção mínima: ler a lista da fonte (`ACEITES = forge_check().ACEITES_DO_USUARIO`, dentro de `pareceres_do_pedido`, já que a catraca carrega o `forge-check` em `mesmo_diff`) ou um teste de paridade `assertEqual(catraca.ACEITES, forge_check().ACEITES_DO_USUARIO)` em `tests/test_catraca.py`. Esforço P. Dono: o autor do #906.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do diff, `python3 -m unittest tests.test_catraca` no `48034214` (419 testes, OK), `forge-mutante tests/mutantes/v0481-rotulo-base-alheia.json` (`RB1 · morreu · tests/catraca.py:1394`, `RB2 · morreu · tests/catraca.py:44`). CI do #906 no `48034214`: `bateria (passos)`, `bateria (verificações longas)`, `instalação`, `árvore já provada na develop` verdes; `catraca` vermelha por R-CONFORMIDADE (toca `tests/catraca.py` sem o rótulo `afrouxa-regra` do dono, esperado: o rótulo é do dono, depois do último push); `bateria (pareceres)` vermelha por R-REVIEW (sem parecer de review aprovado ainda, esperado); a suíte estava pendente na leitura. O merge depende da suíte verde e do rótulo.
