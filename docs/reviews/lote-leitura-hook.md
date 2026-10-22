---
tipo: review
contrato: 1
pedido: lote-leitura-hook
branch: melhoria/lote-leitura-hook
commit: 1b0fb6bf88b73bc81d7a5d4e85164942f119b1b2
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-22
---
# Review: lote-leitura-hook (revalidação 5)

Escopo: a entrega inteira, `git diff ad6d96ce6b19663f7695d361d61f59c7545bdca6 1b0fb6bf88b73bc81d7a5d4e85164942f119b1b2`. Revalidei por delta desde o parecer anterior (7dba2e5, sobre a1a9f84). `forge-check delta --parecer docs/reviews/lote-leitura-hook.md` listou `a1a9f84..a40ad01`: `changelog.d/lote-leitura-hook.md:4`, `docs/hooks.md:94`, `hooks/_comum.py` (9, 789-834, 846-1023, 1079-1141), `hooks/conformidade.py:755-761`, `tests/test_hooks.py` e as 10 fixtures novas. O 7bdd5e0 e o a40ad01 são o parecer da segurança, que não reli como código. Li só esse delta, e os commits até a1a9f84 ficam como "já lido". A exceção é o A2 abaixo. Ele vem de código já lido, mas a sonda o achou e o `docs/hooks.md:94` do delta afirma que esse caso está coberto. Sou revisor independente, não o autor. A segurança (E1.3) aprovou o mesmo sha em `docs/security/lote-leitura-hook.md` (7bdd5e0), e não refiz o parecer dela.

## Achados
- A1 (bloqueante) hooks/_comum.py:911 · GRAVA_REDIRECAO trata `>&` como cópia de descritor, mas `>&arquivo` grava (bash): cat >&.husky/pre-commit <<'EOF' && git commit -m x com gh pr merge ou git push origin main no corpo sai 0 nos dois hooks (base: parecer 2); bash rodou o gancho
- A2 (bloqueante) hooks/_comum.py:891 · o dono olha só o comando lógico do heredoc: cat > x.sh <<'EOF'⏎corpo⏎EOF⏎./x.sh (a quebra de linha vale o `;` do A1 de 3e5d570) sai 0 nos dois hooks desde f8e00ae (base 2); a ADR N-HOOK1, corpus linha 4, espera 2

## Parecer
**Reprovado.** O A1 do review anterior (tempo) está resolvido: o custo ficou linear e abaixo da base em dobro. O A1 da segurança de e62b1b6 também está resolvido, nas formas e nas variantes. O A2 do review anterior está resolvido para `>`, `>>`, `>|`, `1<>`, `tee`, aspas no destino e `git apply`, mas não para `>&arquivo` (A1 deste parecer). O A2 deste parecer é a forma com quebra de linha do furo `; ./x.sh`, que a volta 4 fechou só dentro do comando lógico. Os dois deixam passar R-MAIN e R-REVIEW no hook. Pela decisão V1 = A do dono, não há 6.ª volta e o conteúdo vai ao N-HOOK1. O Jarvis leva isso ao dono (R-DECISAO).

### Sondas
As sondas rodaram com o hook real, em cópias por `git archive` da base (ad6d96c), de f8e00ae, do HEAD anterior (a1a9f84) e do HEAD (1b0fb6b) em `$TMPDIR`. Usei o `Fixture`, o `montar_proc` e o `rodar` do HEAD. Os modelos foram `conformidade/heredoc-outro-comando-make-push-main-bloqueia` (corpo `git push origin main`) e `parecer/forge-clone-pr-merge-no-corpo-de-heredoc-gravado-e-make-bloqueia` (corpo `gh pr merge` com review reprovado). Cada célula mostra o resultado do conformidade e o do parecer.

| Caso | base | a1a9f84 | 1b0fb6b |
|---|---|---|---|
| `&& git push --receive-pack='sh x.sh'`, `--rec=`, `GIT_SSH=./x.sh git push`, `git -C . push --exec=` | — | 0 / 0 | **2 / 2** |
| `export GIT_SSH=./x.sh; cat > x.sh <<'EOF' && git push …` | — | 2 / 2 | 2 / 2 |
| `cat > .husky/pre-push <<'EOF'; git push origin feature/x` | — | 0 / 0 | **2 / 2** |
| o mesmo com `\| tee`, `1<>`, `>\|`, `> ".husky/pre-push"` e `git apply <<'EOF' && git commit` | — | 0 / 0 | **2 / 2** |
| **A1:** `cat >&.husky/pre-push <<'EOF' && git push …`, `cat <<'EOF' >& .husky/pre-commit && git commit -m x`, `cat >&x.sh … && git add && git commit` | 0 / 2 (o 3.º: 2 / 2) | 0 / 0 | **0 / 0** |
| **A2:** `cat > x.sh <<'EOF'`⏎corpo⏎`EOF`⏎`./x.sh` e `cat > .husky/pre-push …`⏎`git push origin feature/x` | 2 / 2 e 0 / 2 | 0 / 0 (f8e00ae também) | **0 / 0** |
| `cat <<'EOF' \| git commit -F - && git push origin feature/x`, `cat <<'EOF' > /dev/null && git push …` | — | 0 / 0 | 0 / 0 |
| `git add && git commit -m "$(cat <<'EOF'` com `it's` `&& git push origin feature/x` (conformidade) | — | 0 | 0 |
| o mesmo com `git push origin main` | — | 2 | 2 |
| `cat > n.md <<'EOF' && git add n.md` com `it's` (conformidade) | 0 | 0 | **2** (recomendação abaixo) |
| `git commit -m "$(cat <<'EOF'` com `it's` e `&& git log -1` ou `&& echo feito`, `gh pr create --body … && echo ok` | 0 | 2 | 2 (recomendação de 7dba2e5, não feita) |

No bash, o A1 se confirma assim: num repositório com `core.hooksPath .husky` e `.husky/pre-commit` executável, `cat >&.husky/pre-commit <<'EOF' && git commit -q -m x`, com `echo RODOU-NO-HOOK` no corpo, imprime `RODOU-NO-HOOK` e faz o commit. Correção mínima: `>&` seguido de algo que não seja só dígitos nem `-` conta como gravação.

Para o A2, o arquivo gravado continua no disco depois do comando lógico. Por isso, os outros comandos do resto do texto, e não só os do comando lógico, precisam passar pela mesma lista positiva e pela regra do `grava_arquivo`. A seção [B] de `docs/hooks.md` aceita o script gravado e executado depois, numa chamada à parte. Este caso é diferente: é a mesma linha do Bash, que a base barrava.

Tempo do `conformidade` com `git push origin main` no fim (base → HEAD): 3000 heredocs em linhas separadas, 1,53 s → 2,06 s. Os mesmos ligados por `&&`, 1,66 s → 1,86 s. Os mesmos num pipeline, 0,39 s → 0,65 s. Com 5000, 2,71 s → 2,78 s, e a forma com `&&` é recusada pelo teto. O caso que levava 26,85 s em a1a9f84 agora leva 2,06 s.

### Delta lido, por commit
- **2af1983 (A1 de segurança):** a lista fechada de opções por subcomando, o `-C` e o `--no-pager` antes do subcomando, a recusa de atribuição antes do programa e o `MUDAM_O_AMBIENTE` seguem as letras a e b da regra 2.2 da ADR N-HOOK1. A abreviada fica fora porque toda opção fora da lista recusa. `programas_e_atribuicoes` só estende `programas_da_linha` e mantém a assinatura antiga.
- **b45f410 (A1 do review):** `limites_logicos` com cache por texto, a busca binária em `lugar_logico`, o `indice_das_partes` e o `DonosDosHeredocs`, que devolve o mesmo objeto ao mesmo dono, cumprem a regra 3.1. O `corpo_so_lido` com `lru_cache` exige um `tambem` com hash estável. O `interprete` do conformidade é uma função de módulo, e o `nenhum` substituiu a lambda pelo mesmo motivo. Os testes de tempo têm teto e medem o hook real.
- **8d59d8f (A2 do review):** a direção (nenhum `git` quando a linha grava) segue a letra c da regra 2.2. O furo está no `(?!&)` da expressão (A1 deste parecer). A busca de `-o` por prefixo pega também `-ours`, mas isso só deixa a leitura mais desconfiada.
- **1b0fb6b (refactor do nome):** é só a troca de `segmentos` por `trechos`, que o T4 pedia. Quanto à P3 = B: o 1b0fb6b se reverte sozinho no HEAD sem conflito. O 2af1983, o b45f410 e o 8d59d8f não se revertem sozinhos no HEAD. Isso já acontecia em 8d59d8f, antes do rename, porque os três mudam o mesmo parágrafo de `docs/hooks.md:94` e trechos vizinhos de `_comum.py`. Revertidos os quatro em ordem inversa, sai limpo. O segundo commit para o mesmo achado não piora a reversão. A P3 = B, porém, já não valia por commit neste lote. Fica como recomendação, sem bloquear.
- **Docs e changelog:** `docs/hooks.md:94` e o fragmento novo descrevem o delta. A frase sobre os outros comandos "noutra linha" afirma o que o A2 desmente.

### Recomendações (fora do bloco)
- **Falso positivo novo:** `cat > n.md <<'EOF' && git add n.md` com apóstrofo agora recusa, e a base e a1a9f84 liberavam. É a forma comum de gravar e adicionar um arquivo. A letra c da regra 2.2 da ADR inclui o subcomando que roda filtros ou fsmonitor, e a regra 4 manda resolver o falso positivo pela mensagem. A mensagem já dá a saída por arquivo, por isso não bloqueia. Registre o caso no corpus do N-HOOK1.
- A recomendação de 7dba2e5 (deixar o `git` quando a linha não grava) não foi feita. A regra 4 da ADR permite isso, e o falso positivo de `&& git log` continua.
- Continua valendo para o integrador (E1.5): R6 na descrição do PR, rótulo `afrouxa-regra` e o cartão HOOK-N4 no quadro.
- Os commits estão limpos, em Conventional Commits em português, com o porquê e o vermelho de antes na mensagem.

### Invariantes e ferramentas
O delta não toca em `tests/config.json`. Na cópia do HEAD, `python3 -m unittest tests.test_hooks -k heredoc -k fixture -k corpo -k tempo -k custo` deu 6 testes OK em 96,8 s. Não refiz a suíte, que o pre-push deste parecer roda.
