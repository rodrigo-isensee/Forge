---
tipo: review
contrato: 1
pedido: bateria-shellcheck-prepush
branch: melhoria/bateria-shellcheck-prepush
commit: c6fc94683001f5f8db2e94b2fa2152f0c34da167
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-22
---
# Review: bateria-shellcheck-prepush

Cartão BATERIA-SHELLCHECK-PREPUSH (E1.2). Escopo lido: `git diff a3dbe22 c6fc946` (8afd7b3 e c6fc946): `.githooks/pre-push` (2 linhas), `tests/test_pre_push_shellcheck.py` (novo), `changelog.d/bateria-shellcheck-prepush.md` (novo). Nada em `.github/workflows/ci.yml` nem em `templates/projeto/.githooks/pre-push` (`git diff --name-only`). Sem `.shellcheckrc` novo.

## Achados

## Parecer
Aprovado.

Evidência de ferramenta (shellcheck 0.10.0, binário oficial baixado em `$TMPDIR`, sem custo):
- a3dbe22 `.githooks/pre-push`: rc=1, SC2015 na linha 58 e SC2317 nas linhas 243 a 246 (as mesmas do CI).
- c6fc946 `.githooks/pre-push`: rc=0. A lista inteira do passo "shellcheck (scripts e hooks)" do `ci.yml` no HEAD: rc=0.
- `tests/test_pre_push_shellcheck.py` contra o hook de a3dbe22: com shellcheck no PATH, 3 falhas; sem shellcheck, 2 falhas e 1 pulado com o aviso. Contra o de c6fc946: com shellcheck, OK (3); sem, OK com 1 pulado e o aviso `AVISO: shellcheck fora do PATH; o CI roda este passo`. Vermelho antes, verde depois, sem rede (R-CUSTO).

Leitura:
- `fila_vivas` (linha 58): `[ -e f ] && [ ! -L f ] || continue` continua quando `!(-e && !-L)`, isto é `! -e || -L`; o `if [ ! -e "$f" ] || [ -L "$f" ]; then continue; fi` é a mesma condição (De Morgan) e nenhum dos testes tem efeito colateral. Comportamento igual; fila, trava, sinais e suíte intocados.
- SC2317 (linha 242): diretiva local, acima da definição de `parar` (alcança só a função), um único código, com motivo na mesma linha. É falso positivo real: `parar` só é chamada pelo `trap parar TERM INT HUP`. Procurei forma sem diretiva e não achei: com o trap entre aspas (`trap 'parar' ...`), com a função movida para o topo do arquivo, sem o `trap -` final e sem os `exec` do modo `--suite`, o shellcheck segue acusando SC2317 no corpo; num script mínimo com o mesmo padrão ele não acusa, então o gatilho está no fluxo do arquivo inteiro e não vale reescrever o hook (fora do escopo, que proíbe mudar comportamento) só para calar uma nota de severidade info. A diretiva é a forma certa.
- O teste é sem rede, determinístico e cobre os dois achados também quando o shellcheck falta (leitura estrutural), e exige ao menos uma diretiva (mínimo de itens, item 11 do checklist).
- Fragmento do changelog no formato dos demais (`### Corrigido`). Commits em Conventional Commits, um por mudança coerente.
- Segurança: parecer próprio em `docs/security/bateria-shellcheck-prepush.md` (59625b9, aprovado); não refeito aqui.

Recomendações (não bloqueiam):
- `tests/test_pre_push_shellcheck.py:31`: a regex `&&.*\|\|\s*continue` só pega a forma numa linha; basta para o que o shellcheck acusa, mas outra forma `A && B || C` em `fila_vivas` (com `return`, por exemplo) passaria. Se voltar, ampliar para `&&.*\|\|`.
- `tests/test_pre_push_shellcheck.py:24`: no ambiente local sem shellcheck o teste principal se pula; a garantia real fica no CI, como o aviso diz. Vale lembrar que o `scripts/preparar-estacao.sh` poderia sugerir o shellcheck (cartão à parte, se o dono quiser).
