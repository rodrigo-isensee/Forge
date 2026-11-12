---
tipo: revisao-seguranca
contrato: 1
pedido: v0457
branch: melhoria/escopo-ponto
commit: 73e4848c3d431b8ac2e99beff0d0b63f2d054284
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-12
---
# Review de segurança: escopo-ponto (E23.50, volta por delta)

Revalidação por delta `c51ecb48..73e4848c` (E23.47) do parecer da E23.42. O A4 do review está corrigido sem afrouxar nada: o portão do devops casa a `Etapa: review` real e o `Agente destino:` separa os papéis. O A5 está corrigido no caso provado (S3 virou teste e reprova) e nas variantes de mesmo commit, `git mv` e `branch:` com maiúscula ou espaço. Sobram duas variantes da mesma família que a busca nova não cobre: o merge lateral que poda o commit do revisor do `rev-list` (A7, o forjado passa na entrega e o `forge-check pr` o escolhe) e a subpasta da pasta do portão (A8). As duas regridem em relação à develop e bloqueiam esta branch.

## Gatilhos
`R-SEGURANCA`: controle do Forge (a conferência de entrega decide o que é escopo da entrega e o que é anexo de portão).

## Achados
- A7 (bloqueante) bin/forge-check:2343 · rev-list sem --full-history poda o commit do revisor: forjado y.md num ramo lateral, merge que apaga o x.md reprovado; a entrega dá anexo do portão (rc 0) e o pr (:1610) só vê y.md aprovado (S6)
- A8 (bloqueante) bin/forge-check:2342 · a busca usa a pasta do arquivo, não a do portão: docs/reviews/sub/y.md aprovado com o commit: do x.md reprovado sai anexo do portão; com o x.md apagado num commit anterior, rc 0 (S7)
- A6 (recomendado) bin/forge-check:2240 · cartão para a versão seguinte, furo anterior a esta branch: os filtros L08 e G2 (:2470) confiam na origin/develop local na etapa codigo; reescrita por git update-ref, escondem do escopo o arquivo fora do declarado (S4, S5)
- A9 (recomendado) bin/forge-check:1610 · cartão: o pr escolhe o parecer por (data, nome) e confia que a entrega recusou o forjado; defesa em profundidade: recusar o parecer cujo commit: tem outro veredito noutro arquivo da pasta na história da branch

## Sondas
- S6 · tests: x.md reprovado (commit R); ramo lateral do head revisado com y.md aprovado e o mesmo commit:; merge --no-ff com git rm x.md; entrega --etapa codigo · espera: rc 1, y.md fora do declarado · obtido: rc 0, escopo: ok (anexo do portão) "docs/reviews/y.md"
- S7 · tests: x.md reprovado; commit que apaga x.md; docs/reviews/sub/y.md aprovado com o mesmo commit:; entrega --etapa codigo · espera: rc 1, sub/y.md fora do declarado · obtido: rc 0, escopo: ok (anexo do portão) "docs/reviews/sub/y.md"

## Detalhe dos achados
**Corrigidos nesta volta.**
- Review A4: `ETAPA_DO_PORTAO["revisao-devops"]` é `review` (`:2321`) e `revisados_selados` (`:2331`) pula o brief cujo `Agente destino:` não é o papel do tipo (`PAPEL_DO_BRIEF_DO_PARECER`, `:2100`); sem a linha, `nome_do_papel(None)` não casa e o brief não ancora (falha fechada). Testes `test_brief_do_review_nao_ancora_o_devops` e o inverso.
- A5 (S3): `veredito_trocado` (`:2338`) lê todos os arquivos da pasta em `de` e em cada commit do intervalo que toca a pasta, com `branch:` igual; `rev-list` e `ls-tree` que falham contam como trocado. S3 refeita no head: rc 1, x.md e y.md fora do declarado.
- Variantes refeitas no head, todas rc 1: `git mv x.md y.md` com o veredito trocado no mesmo commit (a versão de x.md no commit do revisor conta); o autor reescreve o x.md com `branch: Melhoria/x` e cria y.md (a versão do revisor, com a branch exata, conta); y.md com `branch: melhoria/x` seguido de espaços (o frontmatter não casa a branch e y.md sai fora).

**A7, média (bloqueante: defeito provado na correção do A5, com gatilho; regressão, a develop não tem o anexo do portão).** Evidência: `bin/forge-check:2343` chama `rev-list de..head -- <pasta>` com a simplificação de história padrão do git: num merge cujo resultado na pasta é igual ao de um dos pais, o git segue só esse pai e não lista os commits do outro. Caminho de ataque: o revisor commita `docs/reviews/x.md` reprovado (`commit: C`, o Revisar-sha selado). O autor (tech-lead, que escreve em `docs/reviews/`) cria um ramo em C, commita `docs/reviews/y.md` com `branch:` e `pedido:` iguais, `commit: C` e `parecer: aprovado`, e mescla esse ramo na branch com `--no-ff`, apagando o x.md na resolução. O envio é rápido (o commit do revisor é ancestral), sem `--force`. O `rev-list` lista só o commit do forjado, o `ls-tree` de `de` não tem o x.md, e a entrega diz `ok (anexo do portão)` com rc 0 (S6); o x.md não aparece no escopo (não existe em `de` nem no head). No `forge-check pr`, `documentos` (`:344`) só vê o y.md na pasta e o escolhe em `:1610`; sem código novo desde C, o portão do review passa com o parecer forjado. Correção mínima: `rev-list --full-history de..head -- <pasta>` em `veredito_trocado` (provado numa sonda com o git trocado: a função passa a dar trocado no S6); falha do git segue contando como trocado. Testes: S6 e a variante com o merge na ordem inversa dos pais. Mutante: tirar o `--full-history`. Esforço P. Dono: tech-lead.

**A8, baixa (bloqueante: defeito provado no controle desta branch, com gatilho).** Evidência: `bin/forge-check:2342` toma `Path(nome).parent`, mas o tipo do arquivo vem do prefixo da pasta do portão (`PASTA_E_REGRA`, `:857`, por `startswith` em `:2539`), então `docs/reviews/sub/y.md` é parecer de review e a busca fica só em `docs/reviews/sub/`. Caminho de ataque: com o x.md reprovado, o autor cria `docs/reviews/sub/y.md` aprovado com o mesmo `commit:`: o sub/y.md sai anexo do portão (o x.md sai fora, então rc 1); apagando o x.md num commit anterior, rc 0 (S7). O `forge-check pr` lista só o primeiro nível da pasta (`:344`), então o portão acusa a falta de parecer e o ganho do atacante é só o escopo da entrega: por isso baixa. Correção mínima: em `veredito_trocado`, a pasta é a do portão do `tipo` (`PASTA_E_REGRA[tipo][0]`, com `ls-tree -r`), não a do arquivo; ou o anexo do portão só aceita o primeiro nível da pasta, como o `pr`. Teste: S7. Esforço P. Dono: tech-lead.

**A6 (sem mudança, cartão).** O texto da E23.42 vale: L08 e G2 confiam na `origin/develop` local na etapa codigo; anterior a esta branch (S4 e S5 dão rc 0 também com o `bin/forge-check` do Base-sha). Cartão: "L08/G2 confiam na origin/develop local na etapa codigo". Dono: tech-lead.

**A9 (cartão).** O `forge-check pr` não mudou nesta branch e só é seguro porque a entrega recusa o forjado; A7 mostra que basta um furo na entrega para o `pr` tomar o forjado. Defesa em profundidade, na versão seguinte: o `pr` recusa o parecer vigente quando outro arquivo da pasta, em qualquer commit da branch (`rev-list --full-history`), tem o mesmo `commit:` e `branch:` com outro `parecer:`. Dono: tech-lead.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Lido: `forge-check parecer delta` (só `bin/forge-check` no domínio) e o diff de `tests/test_selo_e_entrega.py`. Rodado no head, numa worktree destacada própria: `tests.test_selo_e_entrega` inteiro (70 testes, OK) e as sondas S3, S6, S7 e as três variantes acima, numa subclasse de `ParecerDoPortao` fora da árvore. Os mutantes M1 a M33 e a cobertura são do QA. Varreduras de segredos e de workflow não se aplicam (sem segredo nem workflow no diff).
