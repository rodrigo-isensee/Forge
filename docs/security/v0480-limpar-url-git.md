---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-limpar-url-git
commit: da8e0173362e50b465f2d8485def99f19ccb2f5b
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-24
---
# Review de segurança: v0478 (E166.5, PR #851)

Escopo: diff `f9487606..da8e0173` (E166.1): `bin/forge-fechar` (`url_normal` e o ramo de outro origin em `limpar_clones`), `tests/test_fechar_limpar_clone.py`, `tests/test_forge_fechar.py`, mutantes e fragmento de changelog.

## Gatilhos
Gatilhos: comando que apaga cópia local (`rm -rf` em `limpar_clones`) e saída que poderia levar credencial (URL do origin)

## Detalhe
Conclusão por escrito: a mudança **só aperta ou é neutra** para a perda de trabalho, e a URL não aparece na tela.

- **Normalização (`bin/forge-fechar:615`).** Tira uma `/` final e depois um `.git` final; não mexe em esquema, credencial, host, dono, caixa nem no meio do caminho. Sondas no head (mesma função): `github.com/a/r.git` × `github.com/b/r.git` difere; `github.com/a/r` × `gitlab.com/a/r` difere; `r.git` × `r.gitx`, `r.git.git` × `r`, `r//` × `r`, `a/r` × `A/r`, `tok@host/a/r` × `host/a/r`, `git@github.com:a/r.git` × `https://github.com/a/r`, `r/.git` × `r`, `r-git` × `r`: todos diferem (a função não junta outro dono, outro host nem sufixo parecido). O único par de repositórios distintos que ela iguala é `/srv/r` × `/srv/r.git` (ou o mesmo par num servidor git genérico que aceite os dois nomes); no GitHub o nome com `.git` final não existe como repositório próprio.
- **Mesmo nesse par, o `rm -rf` segue preso às travas que não dependem da URL** (`bin/forge-fechar:638-653`): clone limpo, uma worktree só, nada fora das refs remotas dele, o que sobra alcançado pelas pontas lidas agora desta origin (commit que esta cópia não lê faz o `rev-list` falhar e fica pendente) e o HEAD mesclado aqui (`merge-base --is-ancestor` ou `sha_confere`). O pior caso exige dois repositórios irmãos com a mesma branch, o clone limpo, com o HEAD mesclado nesta origin e o resto nas refs remotas dele: nada se perde que não esteja num remoto. Sem caminho de ataque realista (quem planta o par já escreve em `~/.forge-contrib/wt`): neutro.
- **Outro origin (`bin/forge-fechar:629-637`).** Antes saía em silêncio (`continue`); agora fica `clone=pendente`, código 3, aviso no stderr e só a leitura `git -C <clone> remote -v` escapada com `printf '%q'`, sem `rm`. Clone sem origin (`url_dela` vazia) e cópia sem origin (`url_aqui` vazia) caem no mesmo ramo pendente. Aperta.
- **URL na tela.** O aviso leva só `$d` e `$ref`; `remote get-url` roda com `2>/dev/null`; nenhum `echo` com `url_aqui`/`url_dela`. O teste `test_clone_de_outro_origin_fica_pendente_e_avisa` confere que `outro.git` não sai em stdout nem stderr. A leitura sugerida (`remote -v`) mostra a URL só se quem decide a rodar, por escolha; quem a roda é o dono da cópia.
- **Fora do diff, sem efeito na segurança:** `limpar_copias_sem_merge` (`bin/forge-fechar:875`) segue com igualdade exata; é mais estrita, então só deixa de listar um clone (fica, não some).
- **Testes dos arquivos tocados:** `python3 -m unittest tests.test_fechar_limpar_clone tests.test_forge_fechar` no head: 43 testes, OK. Suíte inteira: no CI do PR #851.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática e sondas locais da função; gitleaks/semgrep fora do escopo deste diff (sem segredo nem dependência nova).
