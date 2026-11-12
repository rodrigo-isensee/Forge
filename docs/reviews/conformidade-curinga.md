---
tipo: review
contrato: 1
pedido: v046
branch: melhoria/conformidade-curinga
commit: 9bd8340486854e946ad2bd810074a6dfaaf8e778
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-12
---
# Review: v046 (E20.36, volta 4 do curinga na origem de link vinda de rev-parse)

Diff lido: `c340c322..9bd83404` (3 commits: 3f9ed613, c46a684a, 9bd83404), numa worktree destacada do revisor. Instância que não fez a correção.

## Achados
- A1 (bloqueante) hooks/conformidade.py:1095 · o glob do Python não lê `[^x]` (negação no bash) nem classe POSIX `[[:alpha:]]`: casa nada e a origem se libera; no bash casam config e hooks. Sugestão: com `[` no resto, falha fechada (só `?` e `*` liberam) ou traduzir `[^`→`[!` e recusar `[:`, `[=`, `[.`; fixture para cada.
- A2 (recomendado) docs/engineering/achados-recorrentes.md:21 · a classe "leitura do hook difere da do bash" volta neste pedido (agora no curinga); gravar a linha AR no PR que fechar o A1 (o brief desta etapa limita os arquivos ao parecer).

## Sondas
- S1 · ln "$(git rev-parse --git-dir)"/[^x]onfig h · espera: código 2 (link com caminho protegido) · obtido: código 0 (fixture gitcomum-zsonda-s1 falhou)
- S2 · ln "$(git rev-parse --git-dir)"/[[:alpha:]]onfig h · espera: código 2 · obtido: código 0 (fixture gitcomum-zsonda-s2 falhou)
- S3 · cp -s "$(git rev-parse --git-dir)"/hook[^x]/pre-push h · espera: código 2 · obtido: código 0 (fixture gitcomum-zsonda-s3 falhou)
- S4 · bash -c 'echo .git/[^x]onfig .git/[[:alpha:]]onfig .git/hook[^x]/pre-push' num .git com config e hooks/pre-push · espera: os três expandem · obtido: .git/config .git/config .git/hooks/pre-push; glob.glob dos dois primeiros: [] []

## Parecer
Reprovado pelo A1. O resto da volta 4 está correto e no escopo: chaves depois do `DIR_DO_GIT` não liberam (falha fechada), o curinga só libera se o glob de cada prefixo não cair em regra específica, o `livres` passou para dentro do `try` (papel `-`) e o `caminhos[:-1]` segue cortando o destino. As 8 fixtures `gitcomum-v3` cobrem os dois lados (7 recusam, `HEA?` libera); `[!x]onfig` também recusa (sonda extra, passou). Nada além da volta 4 mudou: o G22 da spec `-4` acompanha a linha nova, o índice `docs/hooks-fixtures.md` foi regenerado e o fragmento do changelog é próprio. A spec `-5` declara G27 a G33, um por guarda nova.

O defeito do A1 é a mesma classe que esta volta fecha (o curinga escapa da regra específica), por outra porta: `origem_so_generica` decide pelo `fnmatch` do Python, que trata `^` no início do colchete como literal e não conhece `[:classe:]`, enquanto o bash nega e expande a classe. Com a sugestão de falha fechada para `[`, as fixtures `[c]onfig` e `hook[s]` seguem recusando e `HEA?` segue livre.

Testes rodados (R-TETO, só os do brief): `python3 -m unittest tests.test_hook_git_comum tests.test_conformidade_verde` · 12 testes, OK, 55,6 s. As sondas S1 a S3 foram fixtures temporárias na worktree do revisor, apagadas depois.
