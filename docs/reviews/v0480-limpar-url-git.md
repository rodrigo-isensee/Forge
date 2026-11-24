---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-limpar-url-git
commit: 2186affb75a57c4f74d07e10e0affac332f25be0
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0478 E166.3 e E166.7 (PR #851, FECHAR-LIMPAR-URL-GIT)

## Escopo lido
Diff `f9487606..da8e0173`: `bin/forge-fechar` (+12/-1, dentro do teto H1), `tests/test_fechar_limpar_clone.py` (4 testes novos), `tests/test_forge_fechar.py` (teste antigo trocado), `tests/mutantes/v0480-limpar-url-git.json` (U1-U7), `changelog.d/v0480-limpar-url-git.md`.

## Conferência
- Pedido E166.1: `url_normal` tira a barra final e depois o `.git` final (`x`, `x/`, `x.git`, `x.git/` casam); o clone da branch com outro origin sai `clone=pendente`, com aviso na saída de erro e a leitura `git -C <clone> remote -v`, nunca comando que apaga; a URL não sai na tela. O `continue` mantém o clone fora das checagens que apagam: nada com trabalho fora da origem passa a ser apagado.
- Teste antigo trocado (E166.2): `test_clone_de_outra_branch_nao_e_tocado` segue exigindo a pasta da outra branch intacta e `clone=nenhum`; a parte do outro origin foi para `test_clone_de_outro_origin_fica_pendente_e_avisa`, que exige a pasta intacta, código 3, `clone=pendente`, o aviso, a leitura, nenhum `rm -rf` e a URL fora da saída. É mais estrito que o antigo (antes só a pasta intacta era exigida); não afrouxa.
- Falha antes: com o `bin/forge-fechar` do pai (`f9487606`) os 4 testes novos falham (FAIL 4 de 9 em `tests.test_fechar_limpar_clone`); no head, `tests.test_fechar_limpar_clone` e `tests.test_forge_fechar` passam (43 testes, OK).
- Guardas: as linhas mudadas (`if` do origin, `copia_st=pendente`, aviso, `continue`, os dois cortes do `url_normal`) têm mutante declarado (U1-U7), cada um com teste de comportamento do ramo de falha; nenhum lê o texto da fonte.
- Título do PR: `fix(fechar): limpar acha o clone pela URL normalizada e avisa o de outro origin (v0478 E166.1)`, Conventional Commits, sem marca de afrouxamento (nada afrouxa); serve à catraca.
- Ferramentas: `shellcheck` não está instalado neste ambiente; fica com o CI do PR (catraca pendente na leitura, `gh pr checks 851`). Suíte inteira não rerrodada (só no CI).

## Revalidação (E166.7, head 2186affb)
- Delta lido: `forge-check parecer delta` no intervalo `da8e0173..2186affb`, sem o que veio da `develop` (merge de `0f4a7791`); no domínio só `tests/mutantes/v0474-mp6-disco.json` (M8: só o nome do teste) e `tests/mutantes/v0474-mp6-disco-2.json` (M9: `de`, `para` e teste).
- M8: o `de` segue em `bin/forge-fechar:627` (`symbolic-ref ... || continue`); o teste citado, `LimparClones.test_clone_de_outra_branch_nao_e_tocado`, existe (`tests/test_forge_fechar.py:169`). `forge-mutante --ids M8`: `M8 · morreu · bin/forge-fechar:627`.
- M9: o `de` novo é a guarda do origin do E166.1 (`bin/forge-fechar:629`, com `url_normal`); o teste citado, `LimparCloneNaoListado.test_clone_de_outro_origin_fica_pendente_e_avisa`, existe (`tests/test_fechar_limpar_clone.py:107`). `forge-mutante --ids M9`: `M9 · morreu · bin/forge-fechar:629`.
- Nenhum mutante saiu: ids iguais antes e depois (M1-M8; M9, M10, M12-M16). `forge-mutante --conferir --base 0f4a7791`: "o trecho de cada spec do diff está no lugar".
- Testes dos arquivos tocados no head: `tests.test_fechar_limpar_clone` e `tests.test_forge_fechar`, 43 testes, OK. Suíte inteira fica com o CI do PR.
- O A1 segue recomendado, sem mudança.

## Achados
- A1 (recomendado) bin/forge-fechar:629 · com esta cópia sem origin (`-z "$url_aqui"`), todo clone da branch sai pendente com o aviso "o origin dele não é o desta cópia", texto impreciso, e nenhum teste nem mutante isola esse ramo (U2 troca o `if` inteiro); cartão: aviso próprio e teste do ramo.

## Parecer
Aprovado no head 2186affb (a volta só realinha M8 e M9 à guarda e ao teste novos). Faz o que a E166.1 pede, sem mais: normaliza a URL, tira o pulo silencioso e mantém a proteção do clone de outra branch e do trabalho fora da origem. O A1 é recomendado (o comportamento é o seguro, pendente; só o texto e a cobertura do ramo faltam) e vira cartão depois do merge.
