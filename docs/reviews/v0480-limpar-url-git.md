---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-limpar-url-git
commit: da8e0173362e50b465f2d8485def99f19ccb2f5b
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0478 E166.3 (PR #851, FECHAR-LIMPAR-URL-GIT)

## Escopo lido
Diff `f9487606..da8e0173`: `bin/forge-fechar` (+12/-1, dentro do teto H1), `tests/test_fechar_limpar_clone.py` (4 testes novos), `tests/test_forge_fechar.py` (teste antigo trocado), `tests/mutantes/v0480-limpar-url-git.json` (U1-U7), `changelog.d/v0480-limpar-url-git.md`.

## Conferência
- Pedido E166.1: `url_normal` tira a barra final e depois o `.git` final (`x`, `x/`, `x.git`, `x.git/` casam); o clone da branch com outro origin sai `clone=pendente`, com aviso na saída de erro e a leitura `git -C <clone> remote -v`, nunca comando que apaga; a URL não sai na tela. O `continue` mantém o clone fora das checagens que apagam: nada com trabalho fora da origem passa a ser apagado.
- Teste antigo trocado (E166.2): `test_clone_de_outra_branch_nao_e_tocado` segue exigindo a pasta da outra branch intacta e `clone=nenhum`; a parte do outro origin foi para `test_clone_de_outro_origin_fica_pendente_e_avisa`, que exige a pasta intacta, código 3, `clone=pendente`, o aviso, a leitura, nenhum `rm -rf` e a URL fora da saída. É mais estrito que o antigo (antes só a pasta intacta era exigida); não afrouxa.
- Falha antes: com o `bin/forge-fechar` do pai (`f9487606`) os 4 testes novos falham (FAIL 4 de 9 em `tests.test_fechar_limpar_clone`); no head, `tests.test_fechar_limpar_clone` e `tests.test_forge_fechar` passam (43 testes, OK).
- Guardas: as linhas mudadas (`if` do origin, `copia_st=pendente`, aviso, `continue`, os dois cortes do `url_normal`) têm mutante declarado (U1-U7), cada um com teste de comportamento do ramo de falha; nenhum lê o texto da fonte.
- Título do PR: `fix(fechar): limpar acha o clone pela URL normalizada e avisa o de outro origin (v0478 E166.1)`, Conventional Commits, sem marca de afrouxamento (nada afrouxa); serve à catraca.
- Ferramentas: `shellcheck` não está instalado neste ambiente; fica com o CI do PR (catraca pendente na leitura, `gh pr checks 851`). Suíte inteira não rerrodada (só no CI).

## Achados
- A1 (recomendado) bin/forge-fechar:629 · com esta cópia sem origin (`-z "$url_aqui"`), todo clone da branch sai pendente com o aviso "o origin dele não é o desta cópia", texto impreciso, e nenhum teste nem mutante isola esse ramo (U2 troca o `if` inteiro); cartão: aviso próprio e teste do ramo.

## Parecer
Aprovado. Faz o que a E166.1 pede, sem mais: normaliza a URL, tira o pulo silencioso e mantém a proteção do clone de outra branch e do trabalho fora da origem. O A1 é recomendado (o comportamento é o seguro, pendente; só o texto e a cobertura do ramo faltam) e vira cartão depois do merge.
