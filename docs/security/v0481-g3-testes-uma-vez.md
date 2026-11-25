---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-g3-testes-uma-vez
commit: ef45eec579f148d70ee8b885b183087351817fbc
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-25
---
# Review de segurança: v0481 (E8.4, #893, G3 primeira fatia: review e QA leem o CI do head; classe C)

## Achados
- A1 (bloqueante) bin/forge-check:9637 · A linha G3 (e skills engineering-practices:54, qa-testing:46, CI_NO_ESQUELETO :3716) exige `gh pr checks` todo verde no Revisar-sha, mas nele `bateria (pareceres)`, `bateria` e a catraca de controle ficam vermelhos por construção (S1): só se grava `- ci:` mentindo

## Sondas
- S1 · `gh pr checks 893` (head do PR = ef45eec5, o Revisar-sha) · espera: todos verdes possíveis antes do parecer · obtido: `bateria (pareceres)` fail (pareceres ausentes), `catraca` fail (R-CONFORMIDADE: bin/forge-check pede o rótulo `afrouxa-regra`), suíte pending
- S2 · `bin/forge-mutante tests/mutantes/mp1311-pre-envio-fabrica.json --ids M6,M7` · espera: morrem · obtido: M6 e M7 morreram
- S3 · `bin/forge-mutante tests/mutantes/v0479-forge-check-ci-verde-2.json tests/mutantes/v0479-forge-check-ci-verde-3.json --ids M13,M16,M17` · espera: morrem · obtido: os três morreram
- S4 · `bin/forge-mutante tests/mutantes/v0481-g3-testes-uma-vez.json tests/mutantes/v0481-g3-testes-uma-vez-2.json` · espera: M1 a M14 morrem · obtido: todos morreram (M13 por erro do teste declarado, não por asserção)
- S5 · `python3 -m unittest tests.test_forge_check_pr tests.test_pre_envio_brief tests.test_fechar_forge_check_real` · espera: OK · obtido: 87 testes, OK
- S6 · `bash /root/.forge-contrib/wt/_sec-v0481-g3-sonda.sh` (review e QA aprovados nas branches v0481 com PR aberto) · espera: inventário · obtido: 14 pareceres sem `- ci:` em 8 branches; catraca-ajudante não lida

## Gatilhos
Gatilhos: controle do portão de merge (`forge-check pr`, `--previo`, passo 1 do `forge-fechar`; R-REVIEW, R-QA, R-CONFORMIDADE), texto dos briefs de parecer e skills de portão.

## Detalhe dos achados
**A1 (bloqueante, dono: autor do #893, dono de `bin/forge-check`).** Caminho: o revisor de review ou QA recebe o brief com a `LINHA_LE_O_CI` (bin/forge-check:9637-9639), que manda ler `gh pr checks` "todos concluídos e verdes no `Revisar-sha`" e gravar `- ci: <sha40 do Revisar-sha> verde`; o `leu_o_ci` (:2173-2176) só aceita a linha com o sha do `commit:`, que é o Revisar-sha. Nesse sha, em toda 1ª rodada, o job `bateria (pareceres)` é vermelho porque os pareceres ainda não existem (.github/workflows/ci.yml:739-777), o agregador `bateria` herda o vermelho e, em entrega que toca controle, a `catraca` é vermelha até o rótulo do dono, aplicado depois do último push (S1, run 45572219425; o parecer v0481-fechar-ci-topo já registra o mesmo vermelho de pareceres no Revisar-sha). O revisor honesto não aprova nunca; o que aprova grava uma linha falsa. A regra que pede a declaração a torna sistematicamente falsa, e a linha `- ci:` deixa de valer como prova, que é o que o pedido quer dela. Não abre merge indevido: o `checks_do_head` e os passos 4 e 6 do `forge-fechar` seguem lendo o CI do head real. Correção mínima: o texto da linha G3, o comentário do `CI_NO_ESQUELETO` e as duas skills dizem quais checks contam no Revisar-sha e excluem nomeadamente os que esperam o próprio parecer ou o rótulo: `bateria (pareceres)`, `bateria` (o agregador) e `catraca`. A lista sai de uma constante em `bin/forge-check`, citada pelos três textos e por um teste, para não divergir de `.github/workflows/ci.yml`. Esforço P.

**O que aperta, o que é neutro, o que afrouxa (pergunta 1).**
- Aperta: `suite_do_parecer` (:2179-2198) só soma a violação `sem_ci` aos retornos de antes. Os quatro caminhos antigos (fora do Forge, prova da suíte que vale, `adiar`, CI do head lido) devolvem o mesmo que na develop mais `sem_ci`; nenhum `return []` antigo sobrevive fora do "fora do Forge". O `test_a_linha_nao_dispensa_o_ci_verde_do_head` prova que a linha não substitui o CI verde nem a prova `- suíte:`. Também aperta: sem PR, o brief de review e QA passa de "cita o PQ do autor" a "não aprova" (`SEM_PR_NO_PORTAO`, :9640); as skills deixam de aceitar "o PQ do autor" no lugar do CI.
- Neutro: a linha `- ci:` é texto declarado e pode ser escrita sem o CI verde. Com a prova `- suíte:` válida, o `suite_do_parecer` não lê o gh, como antes; quem forjaria a linha já podia forjar a `- suíte:`. O merge exige o CI verde pelo `checks_do_head` (fora do rascunho), pelos passos 4 e 6 do `forge-fechar` e pela proteção da develop, que esta entrega não toca. A catraca do CI (`suite=None`) e a promoção não cobram a linha: o portão do CI não muda. O brief da segurança e o do autor seguem como antes (M9, M12 e `test_seguranca_e_autor_sem_a_linha`).
- Afrouxa: nada no código. No processo, "não rode a suíte inteira" troca a rodada do revisor pela leitura do CI; a suíte já era só do CI pelas skills na develop, então o efeito é neutro.

**Branches em andamento (pergunta 2).** S6 achou 14 pareceres aprovados sem a linha: docs-ok 2, limpar-clone-parecer 2, prazo-forge 2, perfil-fifo 2, g4-f1-aviso 2, g2-1-publicar 1, ae2-quadro-anda 1, pedido-arquiva 1 (catraca-ajudante: fetch falhou). Quando o `forge-check` com este diff roda numa delas (depois de trazer a develop, ou pelo `forge-fechar` da develop), esses pareceres passam a ser recusados no `pr`, no `--previo` (pre-push) e no passo 1 do fechar. O conserto descrito no PR é regravar o parecer com a linha, num commit só dele. Isso muda o blob, e o parecer com `parecer conferido` no Histórico do pedido pede o registro novo. Com A1 aberto, esse conserto também só sai com linha falsa. Corrigido A1, o custo é um commit de parecer por portão, e nada passa sem o portão regravar.

**Mutantes realinhados (pergunta 3).** mp1311 M6: o teste passou de `qa` para `seguranca`, que segue com o texto antigo; a guarda "sem PR, a suíte fica para o CI do PR" continua viva para a segurança, e o caminho novo de review e QA ganhou M11. mp1311 M7, v0479 M13, M16 e M17: só o `de`/`para` acompanha a forma nova (`saida +=`, `sem_ci +`); a troca é a mesma e os testes declarados são os mesmos. Todos morrem (S2, S3).

## Riscos aceitos e ferramentas
Nenhum risco aceito. O CI do Revisar-sha não estava verde no momento do parecer (S1: `bateria (pareceres)` e `catraca` fail, suíte pending); por isso este parecer não grava a linha `- ci:`, e a regra também não cobra o parecer de segurança. gitleaks, zizmor, actionlint, semgrep e shellcheck não estão no PATH; o diff não toca workflow nem segredo.
