---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0478-guardas-conformidade
commit: d67b2f4ebf91b8feba0aec94070670ce6e097dbc
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-19
---
# Review de segurança: v0478 (E1.23, revalidação no head d67b2f4e e pergunta do dono "só aperta?")

Delta lido (`forge-check parecer delta`): `40dc5f4f..d67b2f4e`; no domínio, `hooks/conformidade.py` (`:2292` a `:2295` e `:2307`), `docs/hooks.md` (a frase da troca pelo applet) e `tests/test_conformidade_verde.py` (`TrocaDeBranchAtrasDoBusybox`, `:653`). Rodada anterior (E1.19, D1 a D3, S21, S22) no git, em `40dc5f4f`.

Gatilhos: hook de conformidade (controle de escrita), estado do hook agentes (teto, R-TETO), falha fechada.

Estado dos achados anteriores: A8 fechado (`:2292` guarda `por_applet` e `:2307` não registra a troca de branch pedida ao `busybox`/`toybox`; S21 recusa no head como na base). A7 e A3 seguem recomendados, sem mudança (lacunas da base, não regressão).

## Só aperta?
**Sim**, com o P2 como única aceitação: nenhum caso das comparações abaixo passa de recusa (2) ou pergunta (`ask`) na `origin/develop` para liberado (0) no head.
- **P2, aceito pelo dono** (DECISÃO DO DONO 2026-11-19 09:44): com a sessão no clone, o limite de agentes vem só do `.forge/config.json` da raiz da sessão (protegido pela A3); o da worktree, mais estrito ou ilegível, deixa de recusar. Motivo a registrar no PR: o arquivo da cópia é gravável pelo agente e não é controle. `hooks/agentes.py` sem mudança desde `1ed45d9d`.
- **A8 fechado:** a troca pelo applet não é mais tida como feita; as cadeias com `;`, `||`, `&&` e quebra de linha recusam como na base.

Método: hooks da `origin/develop` (`c720891e`, sem mudança em `hooks/` desde o merge-base `4182a6b9`) e do head, por `git archive`, rodados pelo executor de fixtures do head (`tests/test_hooks.py`, `HOOKS` trocado pela árvore), 4 trabalhadores; conta a transição do código de saída base→head (2 recusa, `ask` pergunta, 0 libera). 11 245 entradas por lado, zero erro de execução.
- D1, corpus do head (2271 fixtures do `conformidade`): 2→2 1683, 0→0 565, ask→ask 19, 0→2 4; **2→0, 2→ask e ask→0: zero**.
- D2, prefixo `busybox `/`toybox ` em cada fixture Bash sem passos (4120): 0→2 1606, 0→0 964, 2→2 1506, 0→ask 34, ask→ask 10; **2→0 zero** (eram 2 na E1.19: `dir36-branch-no-proprio-projeto-libera` com `busybox` e `toybox`, agora 2→2).
- D3, os 54 applets de `APPLETS_QUE_RODAM_PROGRAMA` × 10 cargas recusadas (`forge-atualizar`, `forge atualizar`, `forge voltar-versao`, `git push --no-verify`, `rm -rf .githooks`, `gh pr merge --admin`, `git push --force`, `git commit --no-verify`, `rm -rf .forge`, `git push origin main`) × 3 prefixos (`busybox`, `/bin/busybox`, `toybox`) × 2 papéis (3240): 2→2 828, 0→2 588, 0→0 1824 (o 0→0 é a lacuna A7 da base), **2→0 zero**.
- Família do A6 (as cargas de atualização, mais `'forge atualizar'` entre aspas, 1296 entradas; contém os 196 da E1.17, regenerados pelo mesmo gerador, não pelos arquivos de então): 864 2→2, 432 0→2, **2→0 zero**.
- A8, 6 trocas pelo applet (`busybox git switch -c`, `toybox git checkout -b`, `/bin/busybox git switch -c`, `busybox git checkout develop`, `toybox git switch develop`, `busybox git -C . switch -c`) × 4 separadores (`;`, `||`, `&&`, quebra de linha) × 9 ações na `main` (`git push`, `git push origin HEAD`, `git commit`, `git commit --amend`, `git merge`, `git rebase`, `git reset --hard`, `git cherry-pick`, `git revert`) × 2 papéis (432): 432 2→2. Contraprova, troca direta `git switch -c x` com `;` e `&&` antes de `git commit` (4): 0→0.
- Formas vizinhas (18: `busybox env|nice|timeout git switch`, `busybox sh -c`, troca no meio da cadeia, `|`, `&`, subshell, grupo, aspas, barra invertida, `./busybox`, `busybox.static`): resultado igual nos dois lados em todas.
- Legítimos (41 comandos × direto/`busybox`/`toybox` × 7 papéis, 854): 854 0→0.

Testes do delta: `TrocaDeBranchAtrasDoBusybox` 2 OK (10 s). Suíte inteira: só no CI (brief sem suíte local); CI do head não citável (sem PR).

## Achados
- A7 (recomendado) hooks/conformidade.py:2295 · Lacuna anterior, não regressão: applet do busybox que roda programa e não está em LANCADORES (`chroot`, `setarch`, `nsenter`, `su -c`, `ash -c`...) esconde `git push --no-verify`, `rm -rf .githooks`, `gh pr merge --admin`: rc 0 na base e no head (D3, 1824 0→0).
- A3 (recomendado) hooks/conformidade.py:2375 · Lista negativa não fecha a família: sort -o, curl -o, wget -O, gzip, zip -m, patch -o, split, sqlite3, git -C init, dpkg-deb -x, ar x, pax -r, interpretador e destino vindo do arquivo (tar -P, 7z -spf, cpio -i absoluto, unzip -:) gravam no estado com rc 0. Saída: sandbox (dono).

## Detalhe dos achados
**A7, A3.** Sem mudança desde `1ed45d9d`; a S22 (`false && git switch -c x; git push`, rc 0 na base e no head) segue como lacuna de modelo, em cartão à parte.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum gravado em `docs/security/aceites/`; o P2 tem a aceitação do dono no pedido (09:44), a registrar no PR. Ferramentas: executor de fixtures da suíte sobre os hooks da `origin/develop` e do head (11 245 entradas por lado mais 18 formas vizinhas), teste do delta (2 OK). Lacunas: busybox e toybox fora do PATH (sondas só no analisador); suíte inteira não rodada localmente; CI do head não citável.
