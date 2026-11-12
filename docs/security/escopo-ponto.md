---
tipo: revisao-seguranca
contrato: 1
pedido: v0457
branch: melhoria/escopo-ponto
commit: c51ecb4847bcac295a72bf42f0dec8ab44f1538e
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-12
---
# Review de segurança: escopo-ponto (E23.42, volta por delta)

Revalidação por delta `ba359573..c51ecb48` (E23.40) do parecer da E23.34. A1 a A4 estão corrigidos e as sondas S1 e S2 da rodada anterior agora reprovam pelo motivo certo. A âncora do anexo do portão resiste à forja (brief sem selo, brief selado e adulterado, Revisar-sha de outro portão ou de outra branch). Sobra um bloqueante no próprio A1: a recusa do veredito trocado olha só o arquivo do parecer, e um parecer novo noutro nome, com o mesmo `commit:` ancorado, passa como anexo (S3). O furo antigo dos filtros L08/G2 vem da develop, não desta branch, e vira cartão.

## Gatilhos
`R-SEGURANCA`: controle do Forge (a conferência de entrega decide o que é escopo da entrega e o que é anexo de portão).

## Achados
- A5 (bloqueante) bin/forge-check:2335 · veredito_trocado olha só as versões do mesmo nome: o autor grava docs/reviews/y.md aprovado com o commit: ancorado do review reprovado em x.md e a etapa codigo dá anexo do portão (S3); o pr escolhe por (data, nome) em :1610 e pode tomar o forjado
- A6 (recomendado) bin/forge-check:2240 · cartão para a versão seguinte, furo anterior a esta branch: os filtros L08 e G2 (:2470) confiam na origin/develop local na etapa codigo; reescrita por git update-ref, escondem do escopo o arquivo fora do declarado (S4, S5); a develop no Base-sha também dá rc 0

## Sondas
- S3 · tests: review reprovado em docs/reviews/x.md com brief do portão selado; autor commita docs/reviews/y.md parecer: aprovado com o mesmo commit:; entrega --etapa codigo · espera: rc 1, y.md fora do declarado · obtido: rc 0, escopo: ok (anexo do portão) "docs/reviews/y.md"

## Detalhe dos achados
**A1 a A4, corrigidos.**
- A1: `parecer_de_portao_da_branch` (`:2350-2364`) exige o `commit:` em `revisados_selados` (`:2324`), os `Revisar-sha:` de briefs selados com `Branch:` igual, `Etapa:` do portão da pasta (`ETAPA_DO_PORTAO`) e o mesmo pedido; e recusa o veredito trocado no mesmo arquivo (`:2335`), com o `rev-list` que falha contando como trocado. S1 refeita no head: parecer novo sem brief do portão, rc 1, fora do declarado; veredito trocado no mesmo `commit:`, rc 1, fora do declarado.
- A2: `ponto_da_integracao` (`:8718`) só move o intervalo quando o merge-base é ancestral ou igual a um `Base-sha` de brief selado mais novo que o da entrega (`bases_seladas_depois`, `:8696`). S2 refeita no head: a linha `base:` fica no Base-sha do brief (o merge-base não move). Mas a S2 original (fora.txt mudado uma vez) continua com rc 0, por causa do L08 (A6), não do merge-base; o teste do autor muda o fora.txt duas vezes para isolar a guarda nova e diz isso no docstring.
- A3: `caminhos_do_entregar` usa `item_do_entregar` (`:8565`), o mesmo do escopo declarado; o VV-3 confere `.github/...`.
- A4: com a âncora, o `commit:` é um Revisar-sha do Jarvis, não qualquer ancestral.
- `pedido_dos_pareceres` (`:2273`) agora exige `branch:` igual: aperta, não afrouxa.

**Tentativas de forjar a âncora (todas recusadas, rc 1, fora do declarado):** brief do portão escrito pelo autor sem linha de selo no pedido; brief do portão selado e depois adulterado (o sha256 do selo não bate); Revisar-sha igual ao head num brief selado de `Etapa: seguranca` usado para um parecer de review; brief de review selado para `melhoria/y`. A raiz de confiança continua sendo o arquivo do pedido, que o autor não grava.

**A5, média (bloqueante: defeito provado na correção do A1, com gatilho).** Evidência: `bin/forge-check:2335-2346` lê só `rev-list de..head -- <nome>` e `show <sha>:<nome>`; o mesmo `commit:` com outro veredito em outro arquivo da pasta não é visto. Caminho de ataque: o revisor reprova o head X em `docs/reviews/escopo-ponto.md`, e o Jarvis selou o brief do portão com `Revisar-sha: X`. O autor (tech-lead, com escrita em `docs/reviews/`) não muda código e commita `docs/reviews/v0457.md` com `pedido` e `branch` iguais, `commit: X` e `parecer: aprovado`. A conferência da etapa codigo diz `ok (anexo do portão)` (S3; na develop, o mesmo arquivo dá fora do declarado, então é regressão desta branch). O `forge-check pr` toma entre os pareceres da branch o último por `(data, nome)` (`:1610`): com `v0457.md` depois de `escopo-ponto.md`, ou `data` mais nova, vale o forjado; sem mudança de código no domínio desde X e sem linha `parecer conferido` no Histórico (é o caso do v0457), o portão passa. Correção mínima: em `veredito_trocado`, procurar o `commit:` revisado em todas as versões de todos os arquivos da pasta do portão no intervalo e em `de` (`rev-list de..head -- docs/<pasta>/` e o `ls-tree` de cada uma), com `branch:` igual; qualquer uma com o mesmo `commit:` e outro `parecer:` recusa o anexo. Falha do git continua contando como trocado. Testes: S3; e a variante em que o autor apaga `x.md` e cria `y.md` aprovado no mesmo commit. Mutante: a busca restrita de volta ao nome. Esforço P. Dono: tech-lead.

**A6, média, mas anterior a esta branch (cartão, não bloqueia).** Evidência: `escopo_pelo_primeiro_pai` (`:2222`), chamado em `:2470` em toda etapa, com `base_ref = ref_da_base` (`:1988`), que prefere `refs/remotes/origin/<base>`. L08 (`:2240`): um commit do autor que é ancestral da ref e tem o arquivo igual nela sai do escopo. G2 (`:2243`): o merge cujo segundo pai é ancestral da ref conta só a resolução. Caminhos de ataque: (S4) commit de `fora.txt`, commit em `bin/app`, `git update-ref refs/remotes/origin/develop HEAD~1`, rc 0 e `fora.txt` some; (S5) `fora.txt` num ramo lateral mesclado na branch, com a ref apontada para a ponta do ramo, rc 0. As duas dão rc 0 também com o `bin/forge-check` do Base-sha `8b5a44d5` (develop), por isso não é regressão desta branch e não bloqueia este PR (`R-REVIEW`: o bloqueio é do que a entrega muda). É o mesmo motivo de o E4 (`:2480`) ficar só nas etapas de merge. Correção mínima, na versão seguinte: nas etapas que não são de merge, os filtros L08 e G2 usam a mesma âncora do A2 (o merge-base ancorado em `Base-sha` de brief selado) no lugar da ref local, ou não rodam; testes S4 e S5. Dono: tech-lead. Cartão: "L08/G2 confiam na origin/develop local na etapa codigo".

## Riscos aceitos e ferramentas
Nenhum risco aceito. Lido: `forge-check parecer delta` (só `bin/forge-check` no domínio) e o diff dos testes tocados. Rodados no head: `tests.test_conf_escopo` (OK) e as classes `ParecerDoPortao`, `MergeDaBaseDepoisDoBrief` e `PontoInicial` de `tests.test_selo_e_entrega` (OK); as sondas S1 a S5 e as quatro tentativas de forja numa cópia fora da árvore, e S3 a S5 também contra o `bin/forge-check` do Base-sha. Os mutantes M1 a M28 estão nos quatro arquivos de `tests/mutantes/v0457-escopo-ponto*.json`; a execução deles é do QA. Varreduras de segredos e de workflow não se aplicam (sem segredo nem workflow no diff).
