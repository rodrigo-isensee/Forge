---
tipo: revisao-seguranca
contrato: 1
pedido: v0457
branch: melhoria/escopo-ponto
commit: ba35957368421e2e1803e48011839eaa83454463
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-12
---
# Review de segurança: escopo-ponto (E23.34)

Diff `8b5a44d5..ba359573` (E23.17 a, b, c e E23.36 d, e) na conferência de entrega do `bin/forge-check`. Duas das cinco mudanças afrouxam a conferência da etapa codigo com entrada que o próprio autor controla, e as sondas provam as duas. As outras três não afrouxam.

## Gatilhos
`R-SEGURANCA`: controle do Forge (a conferência de entrega decide o que é escopo da entrega e o que é anexo de portão).

## Achados
- A1 (bloqueante) bin/forge-check:2318 · (d) o anexo do portão vale só pelo frontmatter, que o autor escreve: o tech-lead autor grava em docs/reviews/ (o hook deixa) ou troca reprovado por aprovado no parecer do portão, e a etapa codigo diz ok em vez de fora do declarado (S1)
- A2 (bloqueante) bin/forge-check:8697 · (e) na etapa codigo o intervalo passa a partir do merge-base com a origin/develop, ref local que o autor reescreve (git update-ref); apontada para um commit dele, o código anterior some do escopo e a conferência cumpre (S2), o que o E4 (linha 2444) evitava
- A3 (recomendado) bin/forge-check:7080 · gêmeo de (a) sem a correção: caminhos_do_entregar ainda tira o ponto inicial, e o VV-3 do brief selar confere a escrita de github/... e não de .github/...
- A4 (recomendado) bin/forge-check:2327 · a docstring diz commit da própria branch, mas e_ancestral aceita qualquer commit da develop anterior ao head; a âncora do A1 resolve os dois

## Sondas
- S1 · tests: parecer review reprovado commitado em melhoria/x, depois o mesmo arquivo com parecer: aprovado e o mesmo commit:; entrega --etapa codigo · espera: rc 1, fora do declarado no brief docs/reviews/x.md · obtido: rc 0, escopo: ok (anexo do portão: parecer de tech-lead da própria branch)
- S2 · tests: entrega, commit de fora.txt (fora do declarado), commit em bin/app; git update-ref refs/remotes/origin/develop HEAD~1; entrega --etapa codigo · espera: rc 1, fora.txt fora do declarado · obtido: rc 0, base: merge-base, fora.txt ausente, resultado: cumpriu

## Detalhe dos achados
**A1 (d), média.** Evidência: `bin/forge-check:2318-2327` (`parecer_de_portao_da_branch`) e `:2513` (o `elif` depois do ramo de autoria). Os campos conferidos (`tipo`, `parecer`, `branch`, `pedido`, `commit:` ancestral do head) são todos texto do arquivo, e o arquivo está no diff do autor. Caminho de ataque: o autor da etapa codigo é tech-lead e o hook `conformidade` lhe dá escrita em `docs/reviews/`; ele grava um parecer de review aprovado (ou, na volta, troca `parecer: reprovado` por `aprovado` no parecer que o revisor commitou, sem mudar o `commit:`) e a conferência, que antes reprovava como fora do declarado, passa a rotular o arquivo como anexo do portão. O ramo também fica depois do `autoria_do_parecer`: no projeto com `autoria.jsonl`, o parecer editado perde o hash do registro e cai justamente aqui. Remoções também passam (o `anexo_implicito` exige `removidas == "0"`; este não). O ganho: um parecer de portão falso ou adulterado chega aos portões e ao `forge-check pr` sem que a conferência o aponte (no Forge, sem registro de autoria e sem linhas `parecer conferido` no v0457, o `pr` não tem outra âncora). Correção mínima: ancorar o anexo em registro que o autor não grava: o `commit:` do parecer é o `Revisar-sha` de um brief selado da mesma branch e pedido com `Etapa:` do portão daquela pasta (review, seguranca, qa, devops), lido por `briefs_selados_da_entrega`; e recusar quando uma versão anterior do arquivo no intervalo tem o mesmo `commit:` com outro `parecer:` (veredito trocado sem nova revisão). Sem âncora, a linha volta a ser a de antes (fora do declarado) ou, se o dono preferir não bloquear, um `confira` que mostra `parecer:` e `commit:`, nunca `ok`. Teste: as duas formas da S1 (parecer novo sem brief do portão; veredito trocado). Esforço P. Dono: tech-lead.

**A2 (e), média.** Evidência: `bin/forge-check:8648-8657` (`ponto_da_integracao`, via `ref_da_base`, que prefere `refs/remotes/origin/<base>`) e `:8697-8699` (troca o `base_sha`). O comentário do E4 em `:2444-2447` registra que essa ref é reescrita pelo agente e por isso o filtro por ela ficou só nas etapas de merge; (e) o traz para a etapa codigo. Caminho de ataque: na worktree do autor, `git update-ref refs/remotes/origin/develop <commit dele>` (ou um `fetch` para essa ref) põe o merge-base adiante do código que ele quer esconder; o intervalo passa a começar ali e o arquivo fora do declarado não aparece (S2). Variante: o autor faz merge de um ramo lateral próprio e aponta a ref para ele. Correção mínima: só mover o intervalo quando o merge-base estiver ancorado em registro do Jarvis, por exemplo ancestral ou igual ao `Base-sha` de um brief selado do pedido mais novo que o da entrega, ou a um sha de `entrega conferida` de merge-integracao no Histórico; sem âncora, fica o `Base-sha` (ou o Jarvis sela a volta com o `Base-sha` novo, caminho que a união de (b) já cobre). Teste: a S2 e a variante do ramo lateral. Esforço P/M. Dono: tech-lead.

**A3, baixa.** `caminhos_do_entregar` (`:7080`) usa o mesmo `strip` que (a) corrigiu em `escopo_declarado`: para `.github/workflows/ci.yml` o VV-3 confere a escrita de `github/workflows/ci.yml`. O hook barra a escrita real de qualquer forma; o defeito é a pré-checagem dizer ok sobre outro caminho. Correção: a mesma expressão de `:8531`. Dono: tech-lead.

**A4, informativa.** `e_ancestral(raiz, revisado, head)` aceita qualquer commit da develop; com a âncora do A1 fica coberto.

**O que não afrouxa.**
- (a) `:8531`: só a pontuação final sai; o ponto inicial fica. A comparação continua exata pelo `declarado`, e `./` ainda sai. Nada passa que antes não passasse com o caminho certo.
- (b) `:8512`: a união pega só briefs selados (o selo é do Jarvis), com `Branch:` igual, `Etapa: codigo` e `Pedido:` deste pedido (`mesmo_pedido`); um brief de outra branch ou outro pedido fica fora (testes `test_brief_de_outra_branch_nao_entra_na_uniao` e `test_brief_de_outro_pedido_nao_entra_na_uniao`). Um brief de outra entrega só amplia o escopo se o Jarvis o selou para esta branch, que é a decisão 1a e 2a (a volta herda). O `break` em `:8504` só vale depois do sha bater.
- (c) `:2268` e `:2273`: o `id:` vem do arquivo do pedido (do Jarvis), com a mesma expressão que a função já usava em `:2480`. Escolher entre o id e o slug não baixa a régua: as duas vão ao mesmo `pareceres_da_integracao`, que exige parecer aprovado no head com `branch:` igual (E11). Forjar o `id:` exige escrever o pedido, que já é a raiz de confiança de todo o resto.
- (e), merge "maligno": com o merge-base legítimo, o intervalo de dois pontos até o head mostra tudo o que difere da develop, inclusive o que o autor pôs na resolução do merge. O problema é só a ref local (A2).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Lidos: o diff, o E4 e o ramo de autoria. Rodados: `tests.test_conf_escopo` (14 ok) e as classes `ParecerDoPortao` mais as sondas S1 e S2 numa cópia de rascunho fora da árvore (7 ok, saídas acima). A suíte inteira roda no CI. Varreduras de segredos e de workflow não se aplicam (sem segredo nem workflow no diff).
