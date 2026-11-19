---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0478-promocao-pr
commit: d836c43521f83e02e74c913e2e485a7154b8f50a
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-18
---
# Review de segurança: v0478-promocao-pr

Rodada única (E31.4) no head d836c435, diff `73842444..d836c435`: `bin/forge-check` (`promocao`, `foi_ponta_da_integracao`), `bin/forge-testes`, `tests/test_promocao_por_marca.py`, `tests/test_testes_tocados.py`, os mapas de mutantes e o fragmento do changelog. Pergunta do brief: um item de trabalho consegue se passar por promoção e escapar da conferência E7 e do teto H1?

## Gatilhos
Gatilhos: controle do Forge (portão do `forge-check pr`: quando a conferência E7 e o teto H1 deixam de valer).

## Resumo
- A ampliação (`bin/forge-check:1582`, `:1585-1592`) aceita como promoção o head que está na cadeia de primeiros pais de `origin/develop` ou `origin/homolog`. Isso só abre caminho a um estado que já foi a integração (ou ancestral dela na cadeia), e não muda o resto: `cmd_pr` (pareceres) continua valendo na promoção (`:1568`), e a main segue mesclada pelo usuário (R-MAIN).
- Branch de trabalho: no fluxo do Forge o item entra na develop por squash (`bin/forge-fechar:167`) ou, com merge commit, como segundo pai; em nenhum dos dois o head da branch fica na cadeia de primeiros pais. O teste `test_branch_mesclada_na_develop_nao_vira_promocao` prova o merge commit; o `test_item_comum_de_366_linhas_segue_medido_e_reprovado` prova E7 e H1 iguais para o item.
- Falha fechada: sem ponta ou com o git falhando, não é promoção (`:1589-1592`; `test_sem_ponta_ou_com_o_git_falhando_nao_e_promocao`). A ponta vem de `sha_do_commit` (sha40, `--end-of-options`), então não há injeção de opção no `rev-list`. O CI busca a história inteira (`fetch-depth: 0` em `.github/workflows/ci.yml`), então clone raso não abre nem fecha o caminho por acidente.
- Manipular `refs/remotes/origin/develop` no clone local já dava o mesmo efeito antes (igualdade com a ponta): o risco não muda, e o CI recalcula a partir do remoto.
- Estado antigo: qualquer commit antigo da cadeia vale como promoção, inclusive um anterior a uma reversão. É o desenho da marca (`forge-fechar --promover <sha>`); o diff contra a main não desfaz o que a main já tem, e o merge na main é do usuário. Sem achado.

## Achados
- A1 (recomendado) bin/forge-check:1591 · Com avanço rápido (ff) na integração (a develop local sem remoto, ou um projeto que mescla assim), os commits intermediários de um item entram na cadeia de primeiros pais e viram promoção sem nunca terem sido ponta: escapam de E7 e H1. A docstring diz que isso nunca acontece. Sonda S1.

## Sondas

## Detalhe dos achados
**A1** · evidência: `bin/forge-check:1585-1592` (a docstring em `:1586-1588` diz "nunca primeiro pai") e `:2433-2435` (`ref_da_base` cai na `develop` local quando não há a remota). Sonda S1, reproduzida num repositório temporário com remoto bare: `base` → item `c1` (estado intermediário) → `c2` (correção); a develop avança por ff até `c2` e é enviada; `promocao(repo, c1, "main")` dá `True` no head d836c435 e `False` no `bin/forge-check` de 73842444. Script em `scratchpad/sonda_e31.sh` da sessão, não versionado.
Caminho de ataque: quem abre o PR de promoção escolhe como head um commit intermediário do item (por exemplo, o anterior à correção que um portão pediu), que entrou na develop só como ancestral de um estado aprovado. O `forge-check pr --base main|homolog` pula E7 e H1 para ele. Ganho limitado: `cmd_pr` ainda cobra os pareceres, e no Forge a develop é mesclada por squash, então o caminho não existe aqui; aparece num projeto que usa a ferramenta com integração por ff ou sem remoto. Por isso é recomendado.
Severidade: baixa. Correção mínima (esforço P): estender só para a ponta remota (`refs/remotes/origin/<base>`, onde o merge pelo GitHub nunca é ff) e manter a igualdade estrita no fallback para a branch local. Filtrar a cadeia por `--merges` não serve, porque a própria marca da 0.47.8 (b407f8f7) é um squash. Também: corrigir a docstring de `foi_ponta_da_integracao` para dizer em qual método de merge a garantia vale, e incluir um caso de ff no `tests/test_promocao_por_marca.py`. Dono: o autor da E31.1.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Rodado no head d836c435: `tests/test_promocao_por_marca.py`, 4 testes OK em 5,2 s. Suíte inteira: não rodada (brief); nenhum CI no head d836c435 até este parecer (sem PR), então o CI do PR continua como portão. Ferramentas: o varredor de segredos e os linters de workflow não estão no PATH (lacuna); o diff não toca em workflow nem traz segredo, e foi revisto à mão.
