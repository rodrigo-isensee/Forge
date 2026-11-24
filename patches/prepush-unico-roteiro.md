# Roteiro do dono: ajuste único do pre-push

Propósito: a sequência literal para o dono aplicar o `patches/prepush-unico.patch` no `.githooks/pre-push` (arquivo travado para os agentes), da cópia separada ao envio. Público: o dono. Pedido v0478, etapa E174.9, decisão do dono de 2026-11-24 17:08.

O que o patch faz: primeiro o envio local (PREPUSH-ENVIO-LOCAL-PATCH, decisão 6 de 24/11: texto da trava pelo descritor 9, `FORGE_FILA_INTERVALO=0` recusado e lido em base 10, índice das fixtures e teste pulado novo conferidos no envio leve), depois o D2 por cima (índice do Forge, teto H1 e texto do PR aberto). Nenhum teste local passa a rodar no envio.

**Quando rodar:** depois que o PR da branch `melhoria/v0480-prepush-ajuste-unico` estiver mesclado na `develop`, porque o patch e os testes dele moram nela.

## Ensaio (2026-11-24, tech-lead)
A sequência rodou numa cópia descartável até o commit, sem envio. A cópia saiu por `bin/forge-copia clone` da `origin/develop` (a27eab7e). Como o PR ainda não estava mesclado, o ensaio trouxe o commit dele por avanço rápido (`git merge --ff-only`, 7e86f6c4) e, para o hook ver a base como ela vai estar, apontou a `origin/develop` local da cópia para esse commit (`git update-ref`). Esses dois passos valem só para o ensaio; no seu roteiro, o `git fetch` e a cópia já trazem a `develop` com o PR mesclado. O destino do ensaio foi `/root/.forge-contrib/wt/ensaio-prepush-unico`. No seu roteiro, o destino é `/root/.forge-contrib/wt/prepush-unico-dono`, porque o `forge-copia` recusa destino já ocupado.

## 1. Cópia separada (não a principal) e a branch
```bash
cd /workspaces/Forge
git fetch origin develop
bin/forge-copia clone /root/.forge-contrib/wt/prepush-unico-dono --branch melhoria/v0480-prepush-unico-dono --origem https://github.com/rodrigo-isensee/Forge --base origin/develop
cd /root/.forge-contrib/wt/prepush-unico-dono
git config core.hooksPath .githooks
```
Saída no ensaio (o `forge-copia` cria a branch com `--no-track`):
```
Cloning into '/workspaces/.forge-contrib/wt/ensaio-prepush-unico'...
Switched to a new branch 'melhoria/v0480-prepush-unico-dono'
```
O `git config core.hooksPath .githooks` liga o pre-push na cópia. O clone novo vem sem ele, e sem ele o envio do passo 6 não roda hook nenhum. No ensaio esse passo não rodou, porque o hook dos agentes recusa mexer no `core.hooksPath` (R-VERIFY). O hook remendado rodou direto no passo 6.

## 2. Aplicar o ajuste
```bash
git apply --stat patches/prepush-unico.patch
git apply --check patches/prepush-unico.patch
git apply patches/prepush-unico.patch
bash -n .githooks/pre-push
git status --short
```
Saída no ensaio:
```
 .githooks/pre-push |  151 +++++++++++++++++++++++++++++++++++++++++++++++++++-
 1 file changed, 148 insertions(+), 3 deletions(-)
rc=0      (--stat)
rc=0      (--check)
rc=0      (apply)
rc=0      (bash -n; o modo segue -rwxr-xr-x)
 M .githooks/pre-push
```

## 3. Teste
Primeiro, a prova do ajuste (com o hook já remendado, cada teste confere o hook em vigor):
```bash
python3 -m unittest tests.test_prepush_unico tests.test_pre_push_d2 tests.test_pre_push_patch
```
Saída no ensaio:
```
Ran 54 tests in 82.808s

OK
```
Depois, todos os testes do pre-push, mais o mapa dos testes e os pesos (uns 10 min):
```bash
python3 -m unittest $(ls tests/test_pre_push_*.py tests/test_prepush_*.py | sed 's#/#.#; s#\.py$##') tests.test_testes_tocados tests.test_forge.PesosDaSuite
```
Saída no ensaio:
```
FAIL: test_texto_da_trava_sai_limitado_e_sem_controle (tests.test_pre_push_trava.PrePushTrava.test_texto_da_trava_sai_limitado_e_sem_controle)
AssertionError: 649 not less than or equal to 600
Ran 509 tests in 610.099s

FAILED (failures=1, skipped=16)
```
Essa falha não vem do ajuste. O mesmo teste falha igual na `develop` pura (a27eab7e, sem o patch, 649 > 600) dentro do sandbox dos agentes. Os 16 pulados são do sandbox (`/proc` de outro namespace e `chown` fora do namespace). Na sua máquina, fora do sandbox, espere `OK`. Se esse teste falhar lá também, ele falha igual sem o patch: confira com `git stash` e rode só ele.

## 4. Fragmento do registro de mudanças
```bash
python3 bin/forge-changelog novo Alterado 'Ajuste único do .githooks/pre-push aplicado pelo dono (v0478 E174.9): o patches/prepush-unico.patch, com o envio local (texto da trava pelo descritor 9, FORGE_FILA_INTERVALO=0 recusado e lido em base 10, índice das fixtures e teste pulado novo conferidos no envio leve) e o D2 por cima (índice do Forge, teto H1 e texto do PR aberto), sem teste local no envio.'
```
Saída no ensaio:
```
gravado em changelog.d/v0480-prepush-unico-dono.md
```
O CI não exige o fragmento quando o envio só muda o `.githooks/pre-push`. Numa sonda, a branch só com o hook deu `bin/forge-changelog conferir --base <develop>`: `arquivos da fábrica alterados: 0`, rc 0. A regra do Forge pede um fragmento por PR, para a mudança chegar ao `CHANGELOG.md` da versão; por isso o fragmento fica.

## 5. Commit (seu)
```bash
git add .githooks/pre-push changelog.d/v0480-prepush-unico-dono.md
git commit -m "feat(pre-push): ajuste único do pre-push aplicado pelo dono, envio local e D2 (v0478 E174.9)"
```
Saída no ensaio:
```
M  .githooks/pre-push
A  changelog.d/v0480-prepush-unico-dono.md
8d8024e9 feat(pre-push): ajuste único do pre-push aplicado pelo dono, envio local e D2 (v0478 E174.9)
 .githooks/pre-push                      | 151 +++++++++++++++++++++++++++++++-
 changelog.d/v0480-prepush-unico-dono.md |   2 +
 2 files changed, 150 insertions(+), 3 deletions(-)
```
Conferência do fragmento depois do commit (`python3 bin/forge-changelog conferir --base <develop>`): `arquivos da fábrica alterados: 0 | versão base: 0.47.16 | versão do PR: 0.47.16`, rc 0.

## 6. Envio
```bash
git push origin melhoria/v0480-prepush-unico-dono
```
O envio não rodou no ensaio. Para ver o que o envio mostra, o hook remendado rodou direto na cópia, com a mesma entrada que o `git push` passa a ele. Nada foi enviado. Saída:
```
pre-push: aviso: shellcheck fora do PATH; .githooks/pre-push não foi conferido (o CI confere).
pre-push: tamanho: 151 linhas de código, acima do teto de 150 por item (testes e documentação não contam; H1, decisão do dono 17/11 11:15): corte o item; passe só se cortar mais quebrar a suíte, com `teto: excedido, 151 linhas, <motivo>` no corpo do PR
pre-push: checagens baratas ok em 9s (2 arquivos)
pre-push: envio leve: sem testes locais; a bateria completa roda no CI do PR (opt-in: FORGE_PREPUSH_SUITE=afetados ou 1).
pre-push: duracao inicio=2026-11-24T20:41:55Z fim=2026-11-24T20:42:12Z plano=leve rc=0
```
O aviso do tamanho é o D2 já em ação. Sem PR aberto, ele só avisa e o envio passa (rc 0). Na sua máquina, com o `shellcheck` instalado, a primeira linha não aparece.

## 7. Depois do envio (o time)
- O time abre o PR `melhoria/v0480-prepush-unico-dono` → `develop`, com `teto: excedido, 151 linhas, o ajuste único é um patch só por decisão do dono (24/11 17:08); cortar separaria o envio local do D2` no corpo. Sem essa linha, o D2 e a catraca reprovam o texto.
- A catraca pede o seu rótulo `afrouxa-regra`, posto depois do último envio. No ensaio, `tests/catraca.py --modo regras` sobre o commit deu: `R-CONFORMIDADE: mudança em .githooks/pre-push ... só passa com o rótulo afrouxa-regra do dono, aplicado depois do último push`, rc 1.
- O Jarvis confere se o hook enviado é byte a byte o patch revisado sobre a `develop` (CONFERENCIA-PATCH-DO-DONO). Os portões revisam, e o time integra com tudo verde.

## Critério de reversão
Se uma checagem nova barrar um envio que o CI aprova (falso positivo do índice, da conta de pulos, do teto ou do texto do PR), ou se o envio leve ficar mais de 3 s mais lento que o hook de antes na mesma entrada, reverta. No ensaio, a mesma entrada levou 20 s sem o patch e 19 s com ele, dentro do sandbox; o tempo vem das checagens que já existiam. Para reverter, rode `git apply -R patches/prepush-unico.patch` numa branch nova, pelo mesmo roteiro. O cartão volta ao quadro com a sonda do caso.
