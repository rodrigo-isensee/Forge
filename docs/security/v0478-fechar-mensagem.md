---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0478-fechar-mensagem
commit: 8989baa06876e4ad25235c846aaf4926f686a1d1
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-18
---
# Review de segurança: v0478-fechar-mensagem

Escopo: diff `4182a6b9..3b1e324b` (bin/forge-fechar, teste novo, mutantes, fragmento do changelog). O `forge-fechar` é controle de merge; a pergunta do brief é se o `--subject` e o `--body` novos do passo P6 abrem injeção de argumento na chamada de merge do gh.

## Revalidação no head 8989baa0
Delta lido: `forge-check parecer delta` de `3b1e324b..8989baa0`, sem o que veio da develop: nenhum arquivo do domínio mudou; fora do domínio só `tests/mutantes/v047-integracao-em-lote-8.json` (spec IL-M63). Já lido: a análise abaixo, de `3b1e324b`, que continua valendo. Achados anteriores: nenhum.

## Gatilhos
Gatilhos: controle de merge (forge-fechar, passo P6 da promoção), argumentos montados para o gh

## Achados

## Sondas

## Detalhe dos achados
Sem achado. Análise da injeção de argumento:

- `bin/forge-fechar:783`: `mesclar_auto` repassa `"${@:3}"` entre aspas; cada argumento extra chega ao gh como uma palavra só, sem divisão nem glob. Os argumentos fixos (`$ref`, `--auto`, o método, `--match-head-commit "$2"`) vêm antes e não mudam; o único chamador que passa extras é o P6 (`:1118-1119`); o passo 6 continua sem extras.
- `bin/forge-fechar:1118-1119`: o título e o corpo são uma palavra cada, com prefixo literal (`chore(promoção): ` e `Promoção da versão `); nenhum valor interpolado chega na posição de opção, então nenhum valor pode começar com `-` e virar opção nova, e o valor de `--subject` e `--body` é consumido inteiro como texto.
- Origem dos valores interpolados: `$versao` (`:1058`) só `[0-9A-Za-z.-]{1,40}` lido do plugin.json da marca e depois exigido X.Y.Z por `par_de_promocao` (`:1060`); `$pr_n` só dígitos, pela regex `^https://.../pull/([0-9]{1,9})$` (`:1112`) ou pelo `.number` da listagem de PRs filtrada por `isCrossRepository == false` (`:1086`, `:1094`); `$sha` é `$promover_sha`, exigido `^[0-9a-f]{40}$` (`:146`) e ancestral da develop do servidor (`:1057`); `$pedido` é o posicional do operador local (sem regex no modo `--promover`), mas fica só dentro do corpo, depois de prefixo fixo, e não é dado de terceiro.
- Sem `eval` nem shell intermediário: o gh é chamado direto por `"$gh"`; o texto não passa por interpretação de shell nem de template.
- A trava contra mesclar outro commit (`--match-head-commit "$2"`, o sha da marca) continua antes dos extras e intacta; o título muda só a mensagem do commit de merge, não o que é mesclado.
- O hook `parecer` já trata `--subject` e `--body` como opções com valor (`hooks/parecer.py:84`); sem efeito aqui, porque a chamada roda dentro do script.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Teste novo rodado: `tests.test_fechar_lote.Promover.test_merge_da_promocao_leva_titulo_e_corpo_em_portugues_com_o_numero_do_pr` OK (1 teste, 5,3 s); a suíte inteira fica no CI do PR. Lacunas do ambiente: shellcheck e gitleaks fora do PATH (não instalados, `R-CUSTO`); o shellcheck roda no CI.
