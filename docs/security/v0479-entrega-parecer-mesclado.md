---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-entrega-parecer-mesclado
commit: 481537335abefb88ae3b221960890585884a4ef1
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: E50.1, parecer mesclado na volta (v0478 E50.3)

Escopo: `git diff 8a503799..48153733`: `bin/forge-check` (`commit_so_de_parecer`, `parecer_mesclado_na_volta` e o ramo novo em `linhas_de_entrega`), testes, mutantes e fragmento do changelog.

Gatilhos: controle do Forge (`forge-check entrega`, conferência de escopo do autor), afrouxa-regra pendente de decisão do dono (PERGUNTA AO DONO de 10:40).

## Achados
- A1 (bloqueante) bin/forge-check:3017 · o `commit:` aceita qualquer sha entre o Desde e o head: o autor commita só o parecer, aprovado e citando o próprio código novo, e passa como anexo do portão; troca até um reprovado do portão (S1, S3). O caso real cita o Desde: exija `commit:` igual ao Desde.
- A2 (recomendado) bin/forge-check:3001 · `commit_so_de_parecer` aceita commit que muda as quatro pastas de parecer (e `docs/security/aceites/`) de uma vez: um commit só forja review, segurança e QA juntos (S2). Restrinja à pasta do `tipo` do arquivo, fora `docs/security/aceites/`.

## Sondas
- S1 · volta: autor commita `bin/app` (N) e depois só `docs/reviews/x.md` com `commit: N`, `parecer: aprovado`; `forge-check entrega --etapa codigo` · espera: rc 1, fora do declarado · obtido: rc 0, `escopo: ok (anexo do portão: parecer de tech-lead commitado na volta só com parecer)`
- S3 · portão mescla `docs/reviews/x.md` reprovado com `commit:` = Desde; autor commita código N e depois só o parecer trocado para aprovado com `commit: N` · espera: rc 1, fora · obtido: rc 0, `escopo: ok (anexo do portão ...)`
- S2 · autor commita código N e depois um commit só com `docs/reviews/x.md`, `docs/security/x.md` e `docs/qa/x.md` aprovados, `commit: N` · espera: rc 1 · obtido: rc 0, os três `escopo: ok (anexo do portão ...)`

## Detalhe dos achados
Contexto: o defeito real (`melhoria/v0479-bp1-q1-leitor`, `df0251ca..eec2c1c1`) é o portão que revalida por mensagem, sem brief selado novo, e commita ou mescla o parecer depois da conferida: os caminhos ancorados em registro do Jarvis (`parecer_de_portao_da_branch`, `parecer_mandado_pelo_portao`) e a autoria não o cobrem. Conferi no git: os dois pareceres desse caso (`2a11a457` review, `7a8405d4` segurança) têm `commit: df0251cab7badbc83f17f494a457bad66e2f263f`, o próprio Desde. A sonda S5 (o caso do teste, `commit:` = Desde) segue ok.

**Tamanho do afrouxamento.** Antes, um parecer no intervalo só saía `ok` ancorado em algo que o autor não grava: registro de autoria do hook, `Revisar-sha:` de brief selado ou brief selado que o manda gravar. Fora disso, com o brief declarado, era `fora do declarado` (reprova). Agora basta a forma do git: um commit que só muda pastas de parecer (ou merge sem resolução à mão), frontmatter da pasta, branch e pedido, e `commit:` entre o Desde e o head. O git não prova quem fez o commit; então qualquer agente que consiga commitar na branch tira da conferência um parecer forjado, desde que o faça num commit separado do código. O que segue recusado: parecer mexido junto com código (teste `test_autor_que_edita_o_parecer_no_commit_do_codigo_segue_fora`), merge com o parecer resolvido à mão (`test_merge_com_o_parecer_resolvido_a_mao_segue_fora`), parecer de outra branch, pedido ou pasta, sem veredito, `commit:` fora do intervalo ou abreviado, o mesmo `commit:` com veredito trocado (S4, `veredito_trocado`), e a primeira entrega (sem Desde).

**Caminho de ataque (A1).** Quem: o agente autor da volta (alucinação ou atalho para destravar a entrega, o risco que o pedido anti-alucinação mede). De onde: a própria branch de trabalho. O que ganha: a conferência passa com um aprovado que nenhum portão emitiu, citando o head do autor; o `forge-check pr` então não acusa desatualizado (`commit_vale` vê o domínio igual desde o `commit:`), e o `forge-check proximo` mostra o veredito como aprovado. S3 mostra o pior caso: o reprovado do portão some sob um aprovado com outro `commit:`, e `veredito_trocado` não pega porque compara só o mesmo `commit:`. Severidade: média (controle de processo interno, sem segredo nem dado pessoal; depende de o autor conseguir gravar na pasta do parecer). Correção mínima: em `parecer_mesclado_na_volta`, trocar a condição do intervalo por `revisado == de` (o Desde, que é conferida ou Revisar-sha, ambos registro do Jarvis), e acrescentar S1 e S3 como testes de abuso. Mantém o conserto do caso real. Esforço P. Dono: tech-lead.

**A2.** Com A1 corrigido, um commit forjado só pode citar o Desde, e um aprovado no Desde fica desatualizado no `forge-check pr` se houver código depois dele; ainda assim, o commit do portão só grava a própria pasta (a segurança grava parecer e modelo de ameaças, ambos em `docs/security/`), e aceitar as quatro pastas mais `docs/security/aceites/` (que nenhum agente grava) num commit "do portão" é largo sem motivo. Correção: `commit_so_de_parecer` recebe a pasta do `tipo` e exige todos os nomes sob ela e fora de `docs/security/aceites/`. Esforço P. Dono: tech-lead. Converge com A2 do review (`docs/reviews/v0479-entrega-parecer-mesclado.md`).

**Mitigações que já existem (fora desta mudança).**
- Hook `conformidade`: escrita em `docs/reviews/`, `docs/qa/`, `docs/devops/` e `docs/security/` só pelo papel dono (`hooks/conformidade.json:69-73`); `docs/security/aceites/` por nenhum agente. É a barreira principal contra o autor gravar o parecer; a leitura de comandos do Bash é de melhor esforço.
- `forge-check pr` (hook `parecer` antes de PR e merge, e a catraca do CI): `pareceres_divergentes` (`bin/forge-check:2071`) recusa aprovado forjado em outro arquivo ao lado do reprovado; com `parecer conferido` no Histórico, o blob precisa ser o conferido (`bin/forge-check:1991`); autoria por sha256 e papel (`bin/forge-check:2021`), mas só quando `.forge/run/autoria.jsonl` existe, e na cópia principal do Forge ele não existe: aqui essa camada está desligada.
- `veredito_trocado` (`bin/forge-check:2911`): o mesmo `commit:` com outro veredito, desde o Base-sha.
- Catraca do CI com o rótulo `afrouxa-regra`, os três portões que revisam a branch, o merge na `develop` pelo tech-lead e o merge da `main` pelo dono.

**Como apertar sem perder o conserto.** (1) A1: `commit:` igual ao Desde; resíduo: um aprovado forjado no Desde antes de o portão escrever, que o `forge-check pr` acusa como desatualizado quando a volta tem código depois do Desde, e que `veredito_trocado` ou `pareceres_divergentes` pegam quando o portão já gravou o reprovado. (2) A2: só a pasta do tipo. (3) Mais forte, de processo: o Jarvis registra no Histórico a revalidação por mensagem (uma linha com papel e sha do parecer, como o `parecer conferido`), e a ferramenta ancora nela em vez da forma do git; fecha também o resíduo, mas pede mudança no fluxo do Jarvis.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Com A1 e A2 corrigidos, o resíduo descrito acima ainda é afrouxamento e segue dependendo da decisão do dono sobre o rótulo `afrouxa-regra` (`R-DECISAO`). Sondas rodadas como teste temporário fora da branch, sobre o harness `ParecerMescladoNaVolta` (S1, S2, S3: rc 0; S4: rc 1; S5: rc 0; os 9 testes da classe verdes). Suíte inteira: do CI do PR; o estado do CI neste head não foi conferido (o `gh` não lê credenciais no sandbox). Lacuna: gitleaks, semgrep, zizmor e actionlint fora do PATH; a mudança não toca workflow nem dependência.
