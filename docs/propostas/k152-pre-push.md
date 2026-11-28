# K152: cópia nova sem dependências no pre-push do projeto

Propósito: correção do `templates/projeto/.githooks/pre-push.local` pronta para o dono aplicar (a pasta `.githooks/` do modelo é travada para os agentes). Público: o dono, `tech-lead`, `security-engineer`, `qa-engineer`. Revisão: 2026-12-21.

Estado: proposta (v0478 E81.1; cartão K152, sugestão F21 do projeto de métricas: "worktree nova sem dependências não quebra o pre-push"). Só aperta: o envio com código continua barrado sem o pronto rápido; o que muda é a mensagem, que diz o que falta e o comando de instalar.

## 1. O que a sonda mostrou
- **Modelo do projeto: reproduz.** Numa cópia nova (`git worktree add`) de um projeto do `bin/forge-init`, sem as ferramentas da stack, o envio com código é barrado (certo), mas a saída é o `command not found` do bash e a frase genérica "o pronto rápido reprovou (ou falta a ferramenta no PATH)": não diz que a cópia está sem as dependências nem como instalá-las.
- **Hook do Forge: não reproduz.** O `.githooks/pre-push` do Forge só precisa do `python3` e do `git` (os testes são da biblioteca padrão; o `shellcheck` ausente vira aviso, como antes). Numa cópia nova sem nada instalado, o envio leve passa (`rc=0`); com `FORGE_PREPUSH_SUITE=afetados`, as 40 falhas são as mesmas de `tests.test_oraculo_sempre_atual` rodado na cópia antiga, no mesmo sandbox (59 testes, 39 falhas e 1 erro nas duas), então são do ambiente, não da cópia nova. Nada muda no hook do Forge.

## 2. A correção
- `bin/forge-init` (já na branch, fora dos arquivos travados): grava no marcador `{{INSTALAR}}` o comando de instalação da stack, os argv de `stacks/<stack>/instalar.json` unidos por `&&` (o mesmo que o `forge-copia --instalar` roda). Sem o arquivo, ilegível ou com aspa simples (o comando fica entre aspas simples no arquivo gerado): vazio. Sem o patch abaixo, o modelo não tem o marcador e nada muda.
- `templates/projeto/.githooks/pre-push.local` (este patch): antes do pronto rápido, o programa de cada trecho dele (separado por `&&`, `||`, `|` ou `;`) precisa estar no PATH. O que falta barra o envio com `falta no PATH: <programas>`, o comando de instalar e o lembrete da chave `caminhos_extra` (para a ferramenta instalada fora do PATH). O pronto rápido reprovado também lembra o comando. Nunca pula a checagem: com tudo instalado, o pronto rápido roda como hoje.
- Fica como estava: a detecção (`deteccao`, sem código da stack o pronto é pulado), o pre-push que chama o pre-push.local e o hook do Forge.

## 3. Aplicar
Da raiz do Forge, numa branch a partir da `develop` (o `git apply` lê o bloco `diff` deste arquivo e ignora o texto em volta):

```bash
git apply --check docs/propostas/k152-pre-push.md && git apply docs/propostas/k152-pre-push.md
python3 -m unittest tests.test_prepush_k152 tests.test_forge.PreEnvioDoModelo
bin/forge-mutante tests/mutantes/v0479-k152-prepush-sem-deps.json
```

Projetos já criados não recebem o arquivo novo: o `pre-push.local` é do projeto (o `forge-init` não sobrescreve). Quem quiser a mensagem nova roda `forge-init --forcar` só para esse arquivo ou copia o trecho à mão.

```diff
diff --git a/templates/projeto/.githooks/pre-push.local b/templates/projeto/.githooks/pre-push.local
index 046c02a..58a82ef 100755
--- a/templates/projeto/.githooks/pre-push.local
+++ b/templates/projeto/.githooks/pre-push.local
@@ -6,6 +6,8 @@ set -euo pipefail
 cd "$(dirname "$0")/.."
 rapido='{{PRONTO_RAPIDO}}'
 deteccao='{{DETECCAO}}'  # arquivos da raiz que dizem que já há código da stack para checar
+instalar='{{INSTALAR}}'  # K152: o que instala as dependências da stack (do instalar.json dela); vazio quando não há
+como_instalar="${instalar:-instale as ferramentas do pronto rápido da stack {{STACK}}}"
 read -ra arquivos <<<"$deteccao"
 tem_codigo=0
 for arquivo in ${arquivos[@]+"${arquivos[@]}"}; do
@@ -15,5 +17,19 @@ if [ "$tem_codigo" -eq 0 ]; then
   echo "pre-push.local: nenhum de ${deteccao} na raiz ainda; pronto rápido pulado"
   exit 0
 fi
+# K152: cópia nova sem dependências. O programa de cada trecho do pronto rápido (separado por &&, ||, | ou ;) precisa estar
+# no PATH; o que falta para o envio com o comando de instalar. Nunca pula a checagem: instalado, o pronto rápido roda.
+trechos="${rapido//&&/;}"; trechos="${trechos//||/;}"; trechos="${trechos//|/;}"
+IFS=';' read -ra partes <<<"$trechos"
+faltam=""
+for parte in ${partes[@]+"${partes[@]}"}; do
+  read -r programa _ <<<"$parte"
+  case " $faltam " in *" $programa "*) continue ;; esac  # cada programa uma vez só na mensagem
+  command -v -- "$programa" >/dev/null 2>&1 || faltam="${faltam:+$faltam }$programa"
+done
+if [ -n "$faltam" ]; then
+  echo "pre-push.local: falta no PATH: ${faltam} (cópia nova, sem as dependências instaladas?); o envio foi barrado. Instale e envie de novo: ${como_instalar}; já instaladas fora do PATH, some a pasta delas em caminhos_extra" >&2
+  exit 1
+fi
 echo "pre-push.local: pronto rápido: ${rapido}"
-bash -c "$rapido" || { echo "pre-push.local: o pronto rápido reprovou (ou falta a ferramenta no PATH); corrija e envie de novo, ou ajuste \`rapido\` neste arquivo se o projeto usa outras ferramentas" >&2; exit 1; }
+bash -c "$rapido" || { echo "pre-push.local: o pronto rápido reprovou; corrija e envie de novo, ou ajuste \`rapido\` neste arquivo se o projeto usa outras ferramentas. Numa cópia nova, instale antes as dependências: ${como_instalar}" >&2; exit 1; }
```

## 4. Sondas (2026-11-21, git 2.43.0, Forge na `develop` adc52def)
A sonda cria um projeto pelo `bin/forge-init` da cópia do Forge dada, com o arquivo de detecção e código da stack, um remoto nu, uma cópia nova por `git worktree add` e envia a branch com código com `env -i` e o PATH do sistema (sem as ferramentas do pronto rápido de nenhuma stack). Uso: `bash sonda.sh <raiz do Forge> <python|node-react> <pasta vazia>`; o "depois" usa uma cópia do Forge com o patch aplicado. Pela neutralidade do núcleo (`R-NEUTRO`), nas saídas abaixo o nome de cada ferramenta da stack aparece como `<lint>` (o primeiro programa do pronto rápido) ou `<pacotes>` (o gerenciador de pacotes); o resto é a saída real.

```bash
set -u
FORGE="$1"; STACK="$2"; W="$3"
rm -rf "$W"; mkdir -p "$W"
git init -q --bare "$W/remoto.git"
mkdir "$W/proj" && cd "$W/proj" && git init -q -b develop
git config user.email t@t; git config user.name t; git config commit.gpgsign false
"$FORGE/bin/forge-init" --stack "$STACK" --sem-sandbox . >/dev/null 2>&1 || echo "forge-init rc=$?"
case "$STACK" in
  python) printf '[project]\nname="x"\n' > pyproject.toml; mkdir -p src; echo 'x = 1' > src/a.py ;;
  node-react) echo '{"name":"x"}' > package.json; mkdir -p src; echo 'export const x = 1' > src/a.ts ;;
esac
git add -A && git commit -q -m base
git remote add origin "$W/remoto.git"
git worktree add -q --no-track -b feature/x "$W/copia" develop
cd "$W/copia"
echo 'y = 2' >> src/a.py 2>/dev/null; echo 'export const y = 2' >> src/a.ts 2>/dev/null
git add -A && git commit -q -m codigo
echo "--- envio da cópia nova ($STACK)"
env -i PATH="/usr/bin:/bin" HOME="$W" git push origin feature/x 2>&1 | grep -v '^To \|^ \* \[new\|^remote:'
echo "rc_envio=${PIPESTATUS[0]}"
```

Saída real, modelo de hoje (barra, sem dizer o que instalar):

```text
--- envio da cópia nova (python)
pre-push.local: pronto rápido: <lint> check . && <lint> format --check . && mypy src
bash: line 1: <lint>: command not found
pre-push.local: o pronto rápido reprovou (ou falta a ferramenta no PATH); corrija e envie de novo, ou ajuste `rapido` neste arquivo se o projeto usa outras ferramentas
error: failed to push some refs to '<pasta>/remoto.git'
rc_envio=1
--- envio da cópia nova (node-react)
pre-push.local: pronto rápido: <pacotes> exec <lint> . && <pacotes> exec <formatador> --check . && <pacotes> exec <tipos> --noEmit
bash: line 1: <pacotes>: command not found
pre-push.local: o pronto rápido reprovou (ou falta a ferramenta no PATH); corrija e envie de novo, ou ajuste `rapido` neste arquivo se o projeto usa outras ferramentas
error: failed to push some refs to '<pasta>/remoto.git'
rc_envio=1
```

Saída real, com o `bin/forge-init` da branch e o patch aplicado (barra, diz o que falta e o comando):

```text
--- envio da cópia nova (python)
pre-push.local: falta no PATH: <lint> mypy (cópia nova, sem as dependências instaladas?); o envio foi barrado. Instale e envie de novo: python3 -m venv .venv && .venv/bin/python -m pip install --require-hashes --no-deps -r requirements.lock && .venv/bin/python -m pip install --no-deps -e .; já instaladas fora do PATH, some a pasta delas em caminhos_extra
rc_envio=1
--- envio da cópia nova (node-react)
pre-push.local: falta no PATH: <pacotes> (cópia nova, sem as dependências instaladas?); o envio foi barrado. Instale e envie de novo: <pacotes> install --frozen-lockfile; já instaladas fora do PATH, some a pasta delas em caminhos_extra
rc_envio=1
```

Hook do Forge, mesma ideia (clone do Forge, cópia nova por `git worktree add`, `melhoria/k152-sonda` com uma linha num `bin/` e o fragmento do changelog, `env -i` com `TMPDIR` em `/dev/shm`):

```text
--- envio da cópia nova do Forge (FORGE_PREPUSH_SUITE=vazio)
pre-push: checagens baratas ok em 0s (2 arquivos)
pre-push: envio leve: sem testes locais; a bateria completa roda no CI do PR (opt-in: FORGE_PREPUSH_SUITE=afetados ou 1).
rc_envio=0
```

## 5. Testes e mutantes
- `tests/test_prepush_k152.py` aplica o bloco `diff` acima numa cópia temporária do Forge (`bin/forge-init`, `templates/projeto`, `stacks`, o manifesto) e roda o `forge-init` e o `pre-push.local` gerado. Com o patch já aplicado no modelo, usa a cópia como está. Classes: `ForgeInitGravaOComandoDeInstalar` (o comando de cada stack, a stack sem `instalar.json`, o comando com aspa simples), `PrePushLocalSemDependencias` (nada instalado, só uma ferramenta faltando, tudo instalado, pronto reprovado) e `EnvioDaCopiaNova` (ponta a ponta com `git worktree add` e `git push`; pula se a máquina tem as ferramentas da stack python).
- `tests/mutantes/v0479-k152-prepush-sem-deps.json`: um mutante por guarda mudada, no `bin/forge-init` e nas linhas `+` deste arquivo (o teste lê o patch daqui, então mutar a linha do patch muta o hook aplicado).

## Critério de reversão
Se a conferência barrar um projeto cujo pronto rápido começa por algo que não é programa no PATH (função do shell, `VAR=valor` antes do comando), o projeto ajusta `rapido` no próprio `pre-push.local` (o arquivo é dele) ou o dono reverte o patch; o hook não ganha variável nem opção que pule.
