# Lote PP1: cinco consertos do envio local do Forge

Propósito: correção do `.githooks/pre-push` do Forge pronta para o dono aplicar (o arquivo é travado para os agentes). Público: o dono, `tech-lead`, `security-engineer`, `qa-engineer`. Revisão: 2026-12-21.

Estado: substituída (v0478 E174.9, decisão do dono de 2026-11-24 17:08) pelo ajuste único `patches/prepush-unico.patch`. **Não aplique o bloco `diff` abaixo**: ele não aplica por cima do ajuste único e nenhum teste o prova mais (o `tests/test_prepush_lote_pp1.py` saiu). Era: proposta (v0478 E94.1; cartões PREPUSH-INDICE-E-PULOS, PREPUSH-LEVE-COBERTURA-CATRACA, PRE-PUSH-TEXTO-TRAVA-FD, FILA-INTERVALO-ZERO e PREPUSH-FORGE-AVISO-LISTA-VAZIA).

## 0. Por que fechou como substituída (2026-11-24)
- **O que entrou no lugar:** o ajuste único do `.githooks/pre-push`, um patch só: primeiro o do envio local (PREPUSH-ENVIO-LOCAL-PATCH, decisão 6 de 24/11: PRE-PUSH-TEXTO-TRAVA-FD, FILA-INTERVALO-ZERO e PREPUSH-INDICE-E-PULOS, linha a linha as deste lote), depois o D2 (PORTAO-D2) por cima. Provas: `tests/test_prepush_unico.py` (o envio local, com as classes que eram deste lote) e `tests/test_pre_push_d2.py` (o D2), os dois sobre o mesmo patch; roteiro do dono em `patches/prepush-unico-roteiro.md`.
- **O que deste lote não entra:** PREPUSH-LEVE-COBERTURA-CATRACA fechou sem mudança (decisão 7 de 24/11: o CI já barra e o ENVIO-LEVE tirou teste do envio local); PREPUSH-FORGE-AVISO-LISTA-VAZIA não está no patch aprovado do envio local e segue como cartão próprio.
- **Por que não manter as duas:** as duas mexem nas mesmas linhas do hook (o fd da trava e o intervalo da fila); com o ajuste único aplicado, o `git apply` deste bloco recusa, e o teste dele ficaria vermelho ou provando um hook que não existe. O dono autorizou a saída do teste (rótulo `afrouxa-regra` no PR).

## 1. O que a `develop` já cobre (fb3b670b)
| Cartão | Na `develop` hoje | Nesta proposta |
|---|---|---|
| PREPUSH-INDICE-E-PULOS | não: o hook não roda `scripts/indice-fixtures.py --conferir` nem conta pulos; só o CI pega. O `docs/devops/pp1-pre-push.patch` da `develop` não traz este cartão | sim (igual ao revisado na E14, branch `melhoria/v0478-prepush-pp1`) |
| PREPUSH-LEVE-COBERTURA-CATRACA | não no hook; o `docs/devops/pp1-pre-push.patch` da `develop` o traz como patch não aplicado, sem a guarda de link do `bin/forge-check` (A2 da segurança da E14) | sim (igual ao revisado na E14, com a guarda de link) |
| PRE-PUSH-TEXTO-TRAVA-FD | não no hook (`head -c 200 -- "$trava"`, linha 60); o patch da `develop` o traz, não aplicado | sim (igual ao revisado) |
| FILA-INTERVALO-ZERO | não no hook (o 0 passa e imprime a fila a cada 0,2 s); o patch da `develop` recusa o 0, mas lê `08` e `09` como octal | sim (igual ao revisado na E14: o 0 é recusado, a base é 10) |
| PREPUSH-FORGE-AVISO-LISTA-VAZIA | não: sem `sort` ou sem `mktemp` a lista de arquivos fica vazia e nada avisa | sim (novo) |

Os quatro primeiros são, byte a byte, o hook que o dono aplicou na E14 (commit 5fec4384 da `melhoria/v0478-prepush-pp1`, nunca integrado): conferido com `cmp` contra o patch revisado aplicado sobre a `develop`. O quinto vem da seção 5 da proposta `prepush-modelo-falha-aberta` (E82.3 da segurança).

**FILA-INTERVALO-ZERO, desvio do texto do cartão.** O cartão diz "recusar 0 e valor inválido e cair no padrão". Valor inválido hoje barra o envio, e `tests/test_pre_push_fila.py` (com o mutante da `v047-fila-suite-espera`) prova isso; cair no padrão afrouxaria essa recusa. A proposta segue o revisado na E14: o 0 (e `00`) é recusado como o inválido, e o inválido segue recusado. Se o dono preferir o padrão para os dois, é trocar as duas linhas `exit 1` do intervalo por `intervalo=60` com aviso, e o teste `IntervaloDaFila` muda junto.

## 2. A correção
- **Índice e pulos:** com o diff tocando `tests/hooks/`, `tests/config.json`, `scripts/indice-fixtures.py` ou `docs/hooks-fixtures.md`, as checagens baratas rodam `scripts/indice-fixtures.py --conferir`; índice desatualizado reprova. Com o diff tocando `tests/*.py`, contam `skip`, `skipIf`, `skipUnless`, `expectedFailure` e `skipTest` na âncora e no HEAD, só nos arquivos tocados, pela mesma conta da catraca (AST, sem rodar nada, sem a própria `tests/catraca.py`); subiu, reprova (R-VERIFY).
- **Cobertura da catraca:** com Python no diff, `bin/forge-mutante --cobertura --base <âncora>` (não roda teste); da saída, só a falta em arquivo de controle da catraca (`motivo_de_controle`) que não é teste reprova. Outra saída da ferramenta é aviso.
- **Trava por fd:** `texto_da_trava` lê `/proc/self/fd/9`, o arquivo já aberto e conferido, e não o caminho; sem o descritor, o texto sai vazio.
- **Intervalo da fila:** `FORGE_FILA_INTERVALO=0` (ou `00`) recusado como o inválido; o valor é lido em base 10 (`08` e `09` valem).
- **Lista vazia:** o `sort` que falha também marca a lista como ilegível (`wait "$!"` lê a saída da substituição de processo, como o `mktemp` e o `git` já faziam); com a base `origin/develop`, a lista ilegível ou vazia num envio de código avisa. Só avisa: o envio leve segue com `rc=0` como hoje, e com `FORGE_PREPUSH_SUITE=afetados` a lista ilegível já leva à suíte inteira. Sem a base, a varredura de segredo já avisa e nada muda.

## 3. Aplicar
Da raiz do Forge, numa branch a partir da `develop` (o `git apply` lê o bloco `diff` deste arquivo e ignora o texto em volta):

```bash
git apply --stat docs/propostas/prepush-lote-pp1.md   # tem de listar só .githooks/pre-push
git apply --check docs/propostas/prepush-lote-pp1.md && git apply docs/propostas/prepush-lote-pp1.md
bash -n .githooks/pre-push && ls -l .githooks/pre-push
python3 -m unittest tests.test_prepush_lote_pp1 tests.test_pre_push_patch tests.test_pre_push_trava tests.test_pre_push_fila tests.test_pre_push_leve
for s in tests/mutantes/v0479-prepush-lote-pp1*.json; do bin/forge-mutante "$s" || break; done
```

Ordem com as outras propostas: as do K339 (`docs/propostas/k339-pre-push.patch`), do K152 (`k152-pre-push.md`) e a `prepush-modelo-falha-aberta` (ainda na branch dela) mexem só no modelo de projeto (`templates/projeto/.githooks/pre-push` e `pre-push.local`), não neste arquivo: aplicam em qualquer ordem com esta. O `docs/devops/pp1-pre-push.patch` da `develop` fica superado: depois desta, o `--check` dele recusa (esperado) e o `tests/test_pre_push_patch.py` vê o hook já remendado e confere só o remendado.

```diff
diff --git a/.githooks/pre-push b/.githooks/pre-push
index f944360..24a28c0 100755
--- a/.githooks/pre-push
+++ b/.githooks/pre-push
@@ -56,8 +56,10 @@ trava_arquivo() {
   return 1
 }
 # Texto da trava (de outro processo): até 200 bytes, só imprimíveis, para um escape gravado nela não chegar ao terminal (C-14).
+# PRE-PUSH-TEXTO-TRAVA-FD: lê o arquivo já aberto e conferido no descritor 9 (/proc/self/fd/9), não o caminho: trocar o caminho por
+# um link depois da conferência não desvia a leitura. Sem o descritor aberto o head falha em silêncio e o texto sai vazio (falha fechada).
 texto_da_trava() {
-  head -c 200 -- "$trava" 2>/dev/null | LC_ALL=C tr -cd '[:print:]' || true
+  head -c 200 -- /proc/self/fd/9 2>/dev/null | LC_ALL=C tr -cd '[:print:]' || true
 }
 # Confere o arquivo já aberto no descritor 9 (não o caminho): do próprio usuário e não é link no caminho.
 trava_confere() {
@@ -288,10 +290,21 @@ caminhos_do_envio() {
     git -c core.quotepath=false diff --name-only --no-renames -z HEAD -- || sem_caminhos=1
     git -c core.quotepath=false ls-files -z --others --exclude-standard || sem_caminhos=1
   } > "$lista" 2>/dev/null
-  mapfile -d '' -t alterados < <(sort -zu "$lista")
+  # PREPUSH-FORGE-AVISO-LISTA-VAZIA: o sort que falha (ausente ou com erro) também é lista ilegível; o wait lê a saída dele.
+  mapfile -d '' -t alterados < <(sort -zu "$lista"); wait "$!" || sem_caminhos=1
   rm -f -- "$lista"
 }
-if [ "$modo_suite" -eq 0 ]; then caminhos_do_envio; fi
+# PREPUSH-FORGE-AVISO-LISTA-VAZIA: com a base, a lista que não pôde ser montada (mktemp, sort ou git falhou) ou que veio vazia num
+# envio de código deixa as checagens baratas sem nada a olhar; o envio avisa (sem a base, a varredura de segredo já avisou acima).
+# Só avisa: nada é liberado a mais (o CI é o portão).
+if [ "$modo_suite" -eq 0 ]; then
+  caminhos_do_envio
+  if [ -n "$base_dev" ] && [ "$sem_caminhos" = 1 ]; then
+    echo "pre-push: aviso: a lista de arquivos do envio falhou (mktemp, sort ou git); as checagens baratas podem não ter olhado tudo (o CI confere)." >&2
+  elif [ -n "$base_dev" ] && [ "${#alterados[@]}" -eq 0 ]; then
+    echo "pre-push: aviso: a lista de arquivos do envio veio vazia; as checagens baratas não olharam nada (o CI confere)." >&2
+  fi
+fi
 # PREPUSH-BARATAS (P4 do estudo de 2026-11-08): o vermelho de forma sai em segundos, antes da fila e da trava. Sintaxe
 # (bash -n e ast do Python) de todo script alterado, shellcheck dos scripts shell que o envio alterou, a neutralidade e o
 # scripts/verificar-contribuicao.sh nos arquivos tocados (0.43.3) e `bin/forge-changelog conferir` do HEAD (o fragmento com o
@@ -329,6 +342,57 @@ for rel in sys.argv[1:]:
                 falhas = 1
 sys.exit(falhas)
 '
+# PREPUSH-LEVE-COBERTURA-CATRACA: filtra a saída do `forge-mutante --cobertura` (stdin) pela lista da catraca: só a falta (sem mutante,
+# só equivalente, apagada) em arquivo de controle (classe C, `motivo_de_controle`) e que não é teste (`TESTE`) conta. Saída 0 = nenhuma,
+# 1 = há (impressas), 2 = não consegui carregar a catraca (aviso; o CI confere).
+COBERTURA_FILTRO_PY='import argparse, re, sys
+sys.path.insert(0, "tests")
+try:
+    import catraca
+    fc = catraca.forge_check()
+    listas = argparse.Namespace(PROTEGIDOS=catraca.PROTEGIDOS, SENSIVEIS=catraca.SENSIVEIS, FORMA_COMPILADA=catraca.FORMA_COMPILADA)
+    faltas = catraca.FALTAS_DE_MUTANTE
+except Exception:
+    sys.exit(2)
+conta = []
+for linha in sys.stdin.read().splitlines():
+    if not linha.startswith(faltas):
+        continue
+    m = re.match(r"[^·]*· (.+?):\d+", linha)
+    if m is None:
+        sys.exit(2)
+    arq = m.group(1)
+    if fc.motivo_de_controle(arq, listas) and not fc.TESTE.search(arq):
+        conta.append(linha)
+print("\n".join(conta))
+sys.exit(1 if conta else 0)
+'
+# PREPUSH-INDICE-E-PULOS: skip novo em tests/ (R-VERIFY). Argumentos: a âncora e os arquivos alterados; conta os pulos (skip, skipIf,
+# skipUnless, expectedFailure, skipTest: a mesma conta da catraca, AST, sem executar nada) só nos arquivos de teste tocados, na âncora
+# e no HEAD. Saída 0 = não subiram, 1 = subiram (impresso), 2 = não consegui contar (aviso; o CI confere).
+PULOS_FILTRO_PY='import ast, sys
+sys.path.insert(0, "tests")
+try:
+    import catraca
+    arqs = [a for a in sys.argv[2:] if a.startswith("tests/") and a.endswith(".py") and a != "tests/catraca.py"]
+    def pulos(ref):
+        arvores = []
+        for a in arqs:
+            texto = catraca.ler(".", ref, a)
+            if texto is None:
+                continue
+            try:
+                arvores.append(ast.parse(texto))
+            except SyntaxError:
+                pass
+        return catraca._forca_das_arvores(arvores)[1]
+    antes, depois = pulos(sys.argv[1]), pulos("HEAD")
+except Exception:
+    sys.exit(2)
+if depois > antes:
+    print(f"skip/skipIf/skipUnless/expectedFailure/skipTest em tests/ subiram de {antes} para {depois}")
+    sys.exit(1)
+'
 tipo_de_script() {
   local primeira
   case "$1" in *.py) echo python; return ;; *.sh) echo shell; return ;; esac
@@ -336,7 +400,7 @@ tipo_de_script() {
   case "$primeira" in '#!'*python*) echo python ;; '#!'*bash*|'#!'*/sh|'#!'*' sh') echo shell ;; esac
 }
 checagens_baratas() {
-  local arquivo falhas=0 shell=() ancora branch envio ponta ref saida rc
+  local arquivo falhas=0 shell=() ancora branch envio ponta ref saida rc controle faltas
   for arquivo in "${alterados[@]}"; do
     if [ ! -f "$arquivo" ] || [ -L "$arquivo" ]; then continue; fi
     n_baratas=$((n_baratas + 1))
@@ -370,6 +434,64 @@ checagens_baratas() {
       echo "pre-push: aviso: scripts/verificar-contribuicao.sh não conferiu o delta (saída ${rc}); o CI confere." >&2
     fi
   fi
+  # PREPUSH-LEVE-COBERTURA-CATRACA: diff com Python de controle pede mutante declarado; o CI reprova sem ele (regra_guardas_dos_hooks).
+  # `bin/forge-mutante --cobertura` não roda teste (menos de 1 s), mas julga todo o Python do diff; o filtro abaixo fica só com as
+  # faltas em arquivo da classe C sem teste, a mesma lista da catraca (motivo_de_controle e TESTE). 1 reprova; outra saída é aviso.
+  if [ -n "$base_dev" ] && [ -f bin/forge-mutante ] && [ ! -L bin/forge-mutante ] && [ -f bin/forge-check ] && [ ! -L bin/forge-check ] && [ -f tests/catraca.py ]; then
+    controle=0
+    for arquivo in "${alterados[@]}"; do
+      if [ -f "$arquivo" ] && [ ! -L "$arquivo" ] && [ "$(tipo_de_script "$arquivo")" = python ]; then controle=1; break; fi
+    done
+    if [ "$controle" = 1 ] && ancora="$(git merge-base "$base_dev" HEAD 2>/dev/null)"; then
+      rc=0; saida="$(python3 -I bin/forge-mutante --cobertura --base "$ancora" 2>&1)" || rc=$?
+      if [ "$rc" -eq 1 ]; then
+        faltas="$(printf '%s\n' "$saida" | python3 -I -c "$COBERTURA_FILTRO_PY")" && rc=0 || rc=$?
+        if [ "$rc" -eq 1 ]; then
+          printf '%s\n' "$faltas" | LC_ALL=C tr -d '\000-\011\013-\037\177' >&2
+          echo "pre-push: bin/forge-mutante --cobertura reprovou: condição mudada em código de controle sem mutante declarado (o CI reprova igual); declare em tests/mutantes/<pedido>.json." >&2
+          falhas=1
+        fi
+      fi
+      if [ "$rc" -gt 1 ]; then
+        echo "pre-push: aviso: bin/forge-mutante --cobertura não conferiu o delta (saída ${rc}); o CI confere." >&2
+      fi
+    fi
+  fi
+  # PREPUSH-INDICE-E-PULOS: (1) o índice das fixtures (docs/hooks-fixtures.md) em dia quando o envio toca o corpus, o gerador ou a
+  # config de neutralidade (`scripts/indice-fixtures.py --conferir`, sem teste, segundos); (2) teste pulado novo em tests/ reprova
+  # (R-VERIFY; o CI reprova igual em regra_testes_enfraquecidos). Ferramenta que não roda: aviso, o CI confere.
+  if [ -f scripts/indice-fixtures.py ] && [ ! -L scripts/indice-fixtures.py ]; then
+    controle=0
+    for arquivo in "${alterados[@]}"; do
+      case "$arquivo" in tests/hooks/*|scripts/indice-fixtures.py|docs/hooks-fixtures.md|tests/config.json) controle=1; break ;; esac
+    done
+    if [ "$controle" = 1 ]; then
+      rc=0; saida="$(python3 -I scripts/indice-fixtures.py --conferir 2>&1)" || rc=$?
+      if [ "$rc" -eq 1 ]; then
+        printf '%s\n' "$saida" | LC_ALL=C tr -d '\000-\011\013-\037\177' >&2
+        echo "pre-push: docs/hooks-fixtures.md desatualizado (o CI reprova igual); rode scripts/indice-fixtures.py e inclua o arquivo." >&2
+        falhas=1
+      elif [ "$rc" -ne 0 ]; then
+        echo "pre-push: aviso: scripts/indice-fixtures.py --conferir não conferiu o índice (saída ${rc}); o CI confere." >&2
+      fi
+    fi
+  fi
+  if [ -n "$base_dev" ] && [ -f tests/catraca.py ] && [ ! -L tests/catraca.py ]; then
+    controle=0
+    for arquivo in "${alterados[@]}"; do
+      case "$arquivo" in tests/*.py) [ -f "$arquivo" ] && [ ! -L "$arquivo" ] && controle=1 ;; esac
+    done
+    if [ "$controle" = 1 ] && ancora="$(git merge-base "$base_dev" HEAD 2>/dev/null)"; then
+      rc=0; saida="$(python3 -I -c "$PULOS_FILTRO_PY" "$ancora" "${alterados[@]}" 2>&1)" || rc=$?
+      if [ "$rc" -eq 1 ]; then
+        printf '%s\n' "$saida" | LC_ALL=C tr -d '\000-\011\013-\037\177' >&2
+        echo "pre-push: teste pulado novo em tests/ (R-VERIFY; o CI reprova igual); conserte o teste em vez de pular." >&2
+        falhas=1
+      elif [ "$rc" -ne 0 ]; then
+        echo "pre-push: aviso: a contagem de testes pulados não rodou (saída ${rc}); o CI confere." >&2
+      fi
+    fi
+  fi
   # O changelog é o do HEAD: confere quando o HEAD é a ponta de uma branch enviada (o nome da branch decide o fragmento).
   if [ -n "$base_dev" ] && [ -f bin/forge-changelog ] && [ ! -L bin/forge-changelog ] && [ -f .claude-plugin/plugin.json ]; then
     for envio in "${envios[@]}"; do
@@ -406,7 +528,12 @@ fi
 espera="${FORGE_TRAVA_ESPERA:-1200}"
 case "$espera" in ''|*[!0-9]*) echo "pre-push: FORGE_TRAVA_ESPERA deve ser um número de segundos inteiro (veio '${espera}')." >&2; exit 1 ;; esac
 intervalo="${FORGE_FILA_INTERVALO:-60}"
-case "$intervalo" in ''|*[!0-9]*) echo "pre-push: FORGE_FILA_INTERVALO deve ser um número de segundos inteiro (veio '${intervalo}')." >&2; exit 1 ;; esac
+# FILA-INTERVALO-ZERO: 0 (ou 00...) imprimiria a fila a cada 0,2 s; recusado como o valor inválido.
+case "$intervalo" in ''|*[!0-9]*) echo "pre-push: FORGE_FILA_INTERVALO deve ser um número de segundos inteiro maior que zero (veio '${intervalo}')." >&2; exit 1 ;; esac
+# O 10# lê em base 10 ("08" e "09" não são octal inválido); o valor decimal segue para a conta da espera (a_cada_intervalo).
+intervalo_dec=$((10#$intervalo))
+[ "$intervalo_dec" -gt 0 ] || { echo "pre-push: FORGE_FILA_INTERVALO deve ser um número de segundos inteiro maior que zero (veio '${intervalo}')." >&2; exit 1; }
+intervalo="$intervalo_dec"
 trava="$(trava_arquivo criar)" || exit 1
 if [ -L "$trava" ]; then
   echo "pre-push: ${trava} é link simbólico ou não é do próprio usuário; recusado. Apague-o e tente de novo." >&2
```

## 4. Custo do envio leve (2026-11-21, `/dev/shm`, 3 rodadas, clone do Forge na `develop` fb3b670b, branch nova com o fragmento do changelog)
| Envio | Antes | Depois |
|---|---|---|
| só texto (`docs/hooks.md` e o fragmento) | 446 a 465 ms | 454 a 483 ms |
| Python de controle, teste e fixture (`hooks/_comum.py`, `tests/test_pre_push_leve.py`, uma fixture nova com o índice regerado) | 1221 a 1314 ms | 1640 a 1776 ms |

O envio leve segue leve: o pior caso medido soma meio segundo (cobertura, índice e pulos), sem teste nenhum, e o envio só de texto não muda.

## 5. Sondas (2026-11-21, git 2.43.0, bash 5.2, contra o hook da `develop` fb3b670b e com o patch aplicado)
A sonda clona o Forge dado, põe `origin/develop` no HEAD e envia uma branch nova com uma mudança por caso, chamando o hook direto com a linha de ref no stdin e `env -i`; a pasta `sem-<programa>` tem links para todos os programas do PATH menos um. Uso: `bash sonda.sh <raiz do Forge> <caminho absoluto do hook>`.

```bash
set -u
FORGE="$1"; HOOK="$2"
W=$(mktemp -d "${TMPDIR:-/tmp}/pp1-sonda.XXXXXX")
git clone -q --no-hardlinks "$FORGE" "$W/f" && cd "$W/f" || exit 1
git update-ref refs/remotes/origin/develop HEAD
Z=0000000000000000000000000000000000000000
envia() {  # $1 = rótulo; $2 = PATH; o resto: variáveis extras do ambiente
  local r="$1" p="$2"; shift 2
  git add -A && git -c user.email=t@t -c user.name=t -c commit.gpgsign=false commit -qm sonda
  echo "--- $r"
  printf 'refs/heads/x %s refs/heads/melhoria/sonda %s\n' "$(git rev-parse HEAD)" "$Z" |
    env -i PATH="$p" HOME="$W" TMPDIR="$W" LANG=C.UTF-8 "$@" bash "$HOOK" origin /nao/existe 2>&1 |
    grep -v -e '^pre-push: duracao' -e '^arquivos da fábrica'
  echo "rc=${PIPESTATUS[1]}"
  git reset -q --hard refs/remotes/origin/develop
}
sem() {  # pasta de links para todo programa do PATH, menos $1
  local d="$W/sem-$1" p f
  mkdir -p "$d"
  IFS=: read -ra p <<< "$PATH"
  for f in $(for x in "${p[@]}"; do ls "$x" 2>/dev/null; done | sort -u); do
    [ "$f" = "$1" ] || ln -sf "$(command -v "$f")" "$d/$f" 2>/dev/null
  done
  echo "$d"
}
git switch -q --no-track -c melhoria/sonda
frag() { printf '### Corrigido\n- Sonda.\n' > changelog.d/sonda.md; }
frag; f=$(ls tests/hooks/*/*.json | head -1); cp "$f" "${f%.json}-sonda.json"
envia "S1 fixture nova sem regerar docs/hooks-fixtures.md" "$PATH"
frag; sed -i '0,/^    def test_/s//    def test_sonda(self):\n        self.skipTest("depois")\n\n    def test_/' tests/test_pre_push_leve.py
envia "S2 skipTest novo em tests/" "$PATH"
frag; python3 -I -c 'import re,sys; p="hooks/_comum.py"; t=open(p).read(); open(p,"w").write(re.sub(r"^(\s+)if ", r"\1if True and ", t, count=1, flags=re.M))'
envia "S3 condição mudada em hooks/_comum.py sem mutante declarado" "$PATH"
frag; printf 'def f(:\n' > bin/forge_sonda.py
envia "S4 .py com erro de sintaxe, com tudo no PATH (controle)" "$PATH"
frag; printf 'def f(:\n' > bin/forge_sonda.py
envia "S5 .py com erro de sintaxe, sem sort" "$(sem sort)"
frag; printf 'def f(:\n' > bin/forge_sonda.py
envia "S6 .py com erro de sintaxe, sem mktemp" "$(sem mktemp)"
echo "--- S7 FORGE_FILA_INTERVALO=0, com a trava presa por 3 s de espera"
mkdir -p "$W/m/tests" "$W/run" && git init -q "$W/m"
printf 'import unittest\nclass T(unittest.TestCase):\n    def test_a(self):\n        pass\n' > "$W/m/tests/test_a.py"
python3 -I -c 'import fcntl,sys,time; f=open(sys.argv[1],"a"); fcntl.flock(f,fcntl.LOCK_EX); time.sleep(6)' "$W/run/forge-suite-$(id -u).lock" &
sleep 0.5
(cd "$W/m" && env -i PATH="$PATH" HOME="$W/m" XDG_RUNTIME_DIR="$W/run" FORGE_TRAVA_ESPERA=3 FORGE_FILA_INTERVALO=0 bash "$HOOK" --suite > "$W/s7" 2>&1; rc=$?; echo "linhas \"fila da suíte\": $(grep -c 'fila da suíte' "$W/s7")"; grep 'FORGE_FILA_INTERVALO' "$W/s7"; echo "rc=$rc")
wait
echo "--- S8 texto da trava com o caminho trocado por link depois da conferência"
printf 'pid 1 ns 2 desde dono-do-fd\n' > "$W/aberta"; printf 'TEXTO-DE-OUTRO-ARQUIVO\n' > "$W/desviada"; ln -s "$W/desviada" "$W/trava"
bash -c "trava='$W/trava'; $(sed -n '/^texto_da_trava() {/,/^}/p' "$HOOK")
exec 9<'$W/aberta'; texto_da_trava"; echo
rm -rf "$W"
```

Saída real (sem o traceback do Python de S4; `<tmp>` é a pasta temporária). Hook de hoje: S1, S2, S3 passam (só o CI pega), S5 e S6 passam sem aviso, S7 imprime a fila a cada 0,2 s, S8 lê o arquivo desviado:

```text
--- S1 fixture nova sem regerar docs/hooks-fixtures.md
pre-push: checagens baratas ok em 1s (2 arquivos)
pre-push: envio leve: sem testes locais; a bateria completa roda no CI do PR (opt-in: FORGE_PREPUSH_SUITE=afetados ou 1).
rc=0
--- S2 skipTest novo em tests/
pre-push: checagens baratas ok em 1s (2 arquivos)
pre-push: envio leve: sem testes locais; a bateria completa roda no CI do PR (opt-in: FORGE_PREPUSH_SUITE=afetados ou 1).
rc=0
--- S3 condição mudada em hooks/_comum.py sem mutante declarado
pre-push: checagens baratas ok em 1s (2 arquivos)
pre-push: envio leve: sem testes locais; a bateria completa roda no CI do PR (opt-in: FORGE_PREPUSH_SUITE=afetados ou 1).
rc=0
--- S4 .py com erro de sintaxe, com tudo no PATH (controle)
pre-push: erro de sintaxe Python em bin/forge_sonda.py.
pre-push: checagens baratas reprovadas em 0s; a suíte nem entrou na fila. Nunca --no-verify.
rc=1
--- S5 .py com erro de sintaxe, sem sort
<tmp>/orig: line 291: sort: command not found
pre-push: envio leve: sem testes locais; a bateria completa roda no CI do PR (opt-in: FORGE_PREPUSH_SUITE=afetados ou 1).
rc=0
--- S6 .py com erro de sintaxe, sem mktemp
<tmp>/orig: line 281: mktemp: command not found
pre-push: envio leve: sem testes locais; a bateria completa roda no CI do PR (opt-in: FORGE_PREPUSH_SUITE=afetados ou 1).
rc=0
--- S7 FORGE_FILA_INTERVALO=0, com a trava presa por 3 s de espera
linhas "fila da suíte": 14
rc=1
--- S8 texto da trava com o caminho trocado por link depois da conferência
TEXTO-DE-OUTRO-ARQUIVO
```

Com o patch aplicado: S1, S2 e S3 reprovam no envio leve; S4 segue reprovando (controle); S5 e S6 avisam e seguem com `rc=0` (o CI é o portão); S7 recusa o 0 antes da fila; S8 lê o arquivo do descritor:

```text
--- S1 fixture nova sem regerar docs/hooks-fixtures.md
docs/hooks-fixtures.md: desatualizado; rode scripts/indice-fixtures.py
pre-push: docs/hooks-fixtures.md desatualizado (o CI reprova igual); rode scripts/indice-fixtures.py e inclua o arquivo.
pre-push: checagens baratas reprovadas em 1s; a suíte nem entrou na fila. Nunca --no-verify.
rc=1
--- S2 skipTest novo em tests/
skip/skipIf/skipUnless/expectedFailure/skipTest em tests/ subiram de 0 para 1
pre-push: teste pulado novo em tests/ (R-VERIFY; o CI reprova igual); conserte o teste em vez de pular.
pre-push: checagens baratas reprovadas em 1s; a suíte nem entrou na fila. Nunca --no-verify.
rc=1
--- S3 condição mudada em hooks/_comum.py sem mutante declarado
sem mutante · hooks/_comum.py:56 · True and raiz is None
pre-push: bin/forge-mutante --cobertura reprovou: condição mudada em código de controle sem mutante declarado (o CI reprova igual); declare em tests/mutantes/<pedido>.json.
pre-push: checagens baratas reprovadas em 0s; a suíte nem entrou na fila. Nunca --no-verify.
rc=1
--- S4 .py com erro de sintaxe, com tudo no PATH (controle)
pre-push: erro de sintaxe Python em bin/forge_sonda.py.
pre-push: aviso: bin/forge-mutante --cobertura não conferiu o delta (saída 2); o CI confere.
pre-push: checagens baratas reprovadas em 0s; a suíte nem entrou na fila. Nunca --no-verify.
rc=1
--- S5 .py com erro de sintaxe, sem sort
<tmp>/novo: line 294: sort: command not found
pre-push: aviso: a lista de arquivos do envio falhou (mktemp, sort ou git); as checagens baratas podem não ter olhado tudo (o CI confere).
pre-push: envio leve: sem testes locais; a bateria completa roda no CI do PR (opt-in: FORGE_PREPUSH_SUITE=afetados ou 1).
rc=0
--- S6 .py com erro de sintaxe, sem mktemp
<tmp>/novo: line 283: mktemp: command not found
pre-push: aviso: a lista de arquivos do envio falhou (mktemp, sort ou git); as checagens baratas podem não ter olhado tudo (o CI confere).
pre-push: envio leve: sem testes locais; a bateria completa roda no CI do PR (opt-in: FORGE_PREPUSH_SUITE=afetados ou 1).
rc=0
--- S7 FORGE_FILA_INTERVALO=0, com a trava presa por 3 s de espera
linhas "fila da suíte": 0
pre-push: FORGE_FILA_INTERVALO deve ser um número de segundos inteiro maior que zero (veio '0').
rc=1
--- S8 texto da trava com o caminho trocado por link depois da conferência
pid 1 ns 2 desde dono-do-fd
```

## 6. Testes e mutantes
- `tests/test_prepush_lote_pp1.py` aplica o bloco `diff` acima numa cópia temporária do hook (com o patch já aplicado, usa o hook como está e pula a comparação com o original) e roda o hook direto, num repositório descartável, com o ambiente limpo. Classes: `PatchAplica`, `TextoDaTravaPorFd`, `IntervaloDaFila`, `CoberturaDaCatraca`, `IndiceEPulos` e `ListaVazia` (sem `sort`, `sort` com erro, sem `mktemp`, lista vazia, sem base, e o controle com tudo no PATH; mais a prova de que o aviso não libera: o erro de sintaxe com tudo no PATH segue `rc=1`).
- `tests/mutantes/v0479-prepush-lote-pp1.json` a `-5.json` (36 mutantes): um mutante por guarda mudada, nas linhas `+` deste arquivo (o teste lê o patch daqui, então mutar a linha do patch muta o hook aplicado).
- Com o patch aplicado numa cópia da `develop`, os testes vizinhos do hook seguem verdes: `test_pre_push_leve`, `_fila`, `_trava`, `_afetados`, `_patch`, `_segredo`, `_ja_no_remoto`, `_parecer`, `_parecer_curto`, `_shellcheck`, `_link_apoio` e `test_prepush_refs`; e toda spec de mutante da `develop` que aponta para `.githooks/pre-push` ainda acha o seu `de` no hook remendado, o mesmo número de vezes.

## Critério de reversão
Se uma das checagens novas barrar um envio que o CI aprova (falso positivo da conta de pulos, do índice ou da cobertura), ou se o envio leve passar de 3 s no pior caso medido acima, o dono reverte o patch (`git apply -R docs/propostas/prepush-lote-pp1.md`) e o cartão volta ao quadro com a sonda do caso; o hook não ganha variável nem opção que pule a checagem.
