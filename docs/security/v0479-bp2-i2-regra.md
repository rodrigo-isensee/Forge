---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-bp2-i2-regra
commit: 0ce5173bf504d028f1a49eeb94491c9d22cdedae
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: v0479-bp2-i2-regra (BP2 I2 e I5, texto da fila e do conserto, E38.10)

Escopo lido: `git diff 004ce869..0ce5173b` (`docs/regras/R-FLUXO.md`, `skills/trabalho-em-paralelo/ritmo-e-corte.md`, `agents/tech-lead.md`, `docs/protecao-de-branch.md`, `templates/projeto/docs/engineering/protecao-de-branch.md`, `tests/config.json`, `changelog.d/`), comparado com as condições C1 a C7 do desenho (`docs/propostas/v0479-bp2-fila-de-merge.md` em 9786d4ab, linhas 43-49) e com a D2 e a D5 do dono. Só texto e invariantes: sem suíte local (brief); o CI do PR é o portão dela.

## Gatilhos
Gatilhos: controle do Forge (portão de merge da integração), afrouxa-regra (R-FLUXO, D5 do dono), fluxo de branches.

## Confirmação pedida pela D5 (por escrito)
**Preso ao commit revisado: confirmado.** O item 3 (`skills/trabalho-em-paralelo/ritmo-e-corte.md:26`) prende o merge ao head revisado e só aceita o head novo como o merge do revisado com o topo; o item 2 (`:25`) mantém a cadeia de sempre, e nela o `forge-check pr --base` recusa qualquer byte a mais no commit de merge além do que a base trouxe (`bin/forge-check:153`). Um merge com edição à mão não passa pelo item 2 mesmo que alguém o leia como "o merge do revisado com o topo". O A1 pede que o item 3 diga isso sozinho, para quem confere à mão até o I1 entrar.

**Com a mesma falha declarada: confirmado.** O item 1 (`:24`) prende o vermelho ao CI de `push` do topo, lido na hora, concluído com falha, e para se o topo andar; o item 4 (`:27`) exige que cada teste que falhou nesse run tenha passado no PR; o item 7 (`:30`) registra run, topo, PR e head; o item 5 (`:28`) é a C5 da D2. "Passou" exclui, ao pé da letra, o teste pulado e o apagado. O A2 pede que o texto nomeie as duas armadilhas que a segurança provou no I1 (`docs/security/v0479-bp2-i1-conserto.md`, A1 e A2) e a falha de passo que não é teste.

Texto avaliado como está: até o I1 e o I4 entrarem, o `tech-lead` confere à mão (`:31`). Isso não abre caminho novo, porque a confirmação acima vale pelo texto e pelo `forge-check pr`, não pelo script.

Conferido sem achado: o trecho tirado da `R-FLUXO` ("bateria completa no CI do PR, obrigatória para o merge; mescla com tudo verde") não era invariante e foi para `ritmo-e-corte.md:20`; o "Fluxo contínuo" da regra segue exigindo CI verde. Os invariantes novos só acrescentam (`tests/config.json`). O texto da fila nativa no modelo de projeto não mexe em workflow nem em ruleset; quem marca a caixa é o dono (`R-CONFORMIDADE`). O lote continua exceção declarada, com a integração verde antes (`:21`, D4).

## Achados
- A1 (recomendado) skills/trabalho-em-paralelo/ritmo-e-corte.md:26 · Item 3 sem o C3 inteiro: diga que o merge sai com `--match-head-commit` no head revisado e que o head novo tem pais (revisado, topo) e a árvore do merge automático (`git merge-tree`), sem resolução nem edição à mão.
- A2 (recomendado) skills/trabalho-em-paralelo/ritmo-e-corte.md:27 · Item 4: "passou" quer dizer rodou e passou; pulado por classe ou por módulo (setUpClass, ModuleSkipped) ou apagado não conta, e passo vermelho que não é teste (teto de pulados) também tem de ficar verde no PR. São as armadilhas A1 e A2 do I1.

## Sondas

## Detalhe dos achados
**A1.** Evidência: `skills/trabalho-em-paralelo/ritmo-e-corte.md:26` contra a C3 do desenho (linha 45 em 9786d4ab), que a D2 aceitou "como está". Caminho de ataque: o agente que confere à mão traz a base, resolve ou edita no commit de merge e lê o item 3 ao pé da letra ("é o merge do revisado com o topo"). Hoje o item 2 barra, porque o `forge-check pr --base` recusa byte a mais no merge (`bin/forge-check:153`), por isso é recomendado. Severidade: baixa. Correção mínima: no item 3, "o merge sai com `--match-head-commit <head revisado>`; com a base trazida, o head novo só vale com pais (revisado, topo) e árvore igual à do `git merge-tree` dos dois, sem resolução nem edição à mão". Esforço: P. Dono: tech-lead.

**A2.** Evidência: `skills/trabalho-em-paralelo/ritmo-e-corte.md:27`, e no I1 as sondas da segurança (`docs/security/v0479-bp2-i1-conserto.md`, S1) mostraram que o pulado por classe ou módulo não aparece pelo id do teste. O CI de `push` também tem passos vermelhos que não são teste, como o teto de pulados (`.github/workflows/ci.yml:107-130`). Caminho de ataque: quem confere à mão procura o id do teste vermelho só na lista de pulados, não o acha porque a classe ou o módulo foi pulado ou o teste foi apagado, e o conserto entra com a falha escondida. Os pareceres do item 2 veriam o pulo ou a remoção no diff, por isso é recomendado. Severidade: baixa. Correção mínima: no item 4, "cada teste que falhou no vermelho rodou e passou no PR: não vale pulado pelo id, pela classe (`setUpClass`, `tearDownClass`), pelo módulo (`setUpModule`, `tearDownModule`, `ModuleSkipped`), nem apagado; passo vermelho que não é teste fica verde no PR". Esforço: P. Dono: tech-lead.

## Riscos aceitos e ferramentas
Sem risco aceito. O item 5 aceita qualquer arquivo mudado desde o último verde: é a D2 do dono ("C1 a C7 como estão, inclusive C5"), não achado. Até o I1 e o I4 entrarem, a fila e o conserto ficam na conferência à mão do `tech-lead`, como o texto diz; o risco residual é o de leitura errada, coberto pelo item 2.
Ferramentas: leitura estática; nada a varrer (só texto e JSON de invariantes). Analisador de segredos, de workflows e lint de shell fora do PATH desta estação (lacuna registrada, sem instalação, `R-CUSTO`). Suíte: não rodada aqui (brief); o CI do PR é o portão dela.
