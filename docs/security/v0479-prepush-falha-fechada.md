---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-prepush-falha-fechada
commit: 653b44116a942dc9c8d7bfd8d7895472ce12930a
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: v0479-prepush-falha-fechada (v0478 E82.3, PREPUSH-MODELO-FALHA-ABERTA)

Escopo: diff `2097f9bf..99a4fc30` (proposta `docs/propostas/prepush-modelo-falha-aberta.md`, blob `3354881f06f29a5dcdcc2bb6efba5b44dde30be2`; `tests/test_prepush_falha_fechada.py`; mutantes; `bin/forge-testes`; `tests/test_reval_delta.py`). O patch revisado é o bloco `diff` desse blob: o dono aplica a proposta com este blob (`git rev-parse HEAD:docs/propostas/prepush-modelo-falha-aberta.md`); proposta com outro blob pede parecer novo, porque `docs/propostas/` é TEXTO e o delta não envelhece este parecer.

## Gatilhos
Gatilhos: hook de controle do envio (pre-push do modelo, via proposta), lista C-2 de citações de caminho de TEXTO (`tests/test_reval_delta.py`).

## Achados

## Sondas

## Detalhe dos achados
**Só aperta: sim.** Ramo a ramo, com o utilitário presente o comportamento é o de antes:
- `lider_vivo` (proposta, hunk `@@ -90`): `for p in $(jobs -rp)` com comparação exata equivale ao `case " … "` com `tr`; o bash não herda `IFS` do ambiente e PID é só dígitos (sem glob). Sem o `tr`, o limite e o órfão voltam a valer.
- `local_hook` (hunk `@@ -271`): com `dirname` bom, `pasta_hook` é o mesmo texto; o novo `exit 1` só sai quando o `dirname` falta, sai fora de 0 ou devolve vazio. Barra também quem não tem `pre-push.local` (sonda S4 abaixo): excesso do lado fechado, aceitável.
- `comando_de_registros` (hunk `@@ -317`): com `python3`, linha a linha igual; sem ele, a chave citada barra (`return 1` → `registros=… || exit 1` do modelo, linha 340), sem a chave segue com aviso (como antes). O texto é lido por `$(<arquivo)`, sem utilitário.
- Nenhuma variável, opção nem ramo novo que libere.

**Outras ausências e falhas tentadas** (sondas no hook com o patch, pela base do teste novo, PATH só com links):
- S1 chave escapada `{"registros": "false"}` sem `python3`: rc=0 com aviso "sem a chave". Não é achado: com `python3`, um config ilegível já segue com aviso por decisão (D3), então quem escreve o config já tinha esse caminho; o escape não dá capacidade nova. Proporcionalidade: sem ganho para o ator.
- S2 `python3` que sai 127 (shim sem versão): rc=1, barra.
- S3 `python3` falso que sai 0 sem imprimir: rc=0. Fora do modelo (binário adulterado no PATH do próprio usuário já executa o que quiser).
- S4 sem `dirname` e sem `pre-push.local`: rc=1 (barra a mais, lado fechado).
- S5 sem `tr` e sem `ps` juntos, checagem de 20 s com limite de 1 s: rc=1, limite vale (o `tr` das linhas 155 e 158 do modelo só suja o stderr; o PGID cai no `kill -0`, builtin).
- S6 sem `bash` no PATH: rc=1 (o `env bash` do shebang falha e o git aborta o envio).
- Revisto sem sonda: `timeout` com sintaxe diferente sai fora de 0 e barra; `cd ""` no registros é no-op dentro da raiz; `mktemp`/`git diff` falhos em `so_docs` e `arquivos_enviados` levam a "olhar tudo".

**C-2 (`tests/test_reval_delta.py:134-136`):** as duas entradas conferem. `("tests/test_prepush_falha_fechada.py", "docs/propostas/"): (1, "teste-le")`: uma linha (docstring, linha 4); o teste lê a proposta (`PROPOSTA`, linha 25, montada por partes) e aplica o bloco `diff` numa cópia temporária, mesmo padrão já aceito para `tests/test_forge.py` e `tests/test_hooks.py`; teste pode ler (a guarda (d) só barra fora de `tests/`). `("bin/forge-testes", "docs/propostas/"): (1, "nome")`: a linha 250 é só a regex do mapa de afetados, não lê conteúdo. Nenhuma das duas é normativa para o Forge em produção. O risco residual (a proposta editada depois deste parecer não o envelhece) fica coberto pelo blob preso no Escopo acima e pelo review do PR do dono que aplicar o patch no hook (código, com gatilho).

**Seção 5 da proposta (`.githooks/pre-push` do Forge):** reproduzido por leitura: sem `sort` (linha 291, `mapfile … < <(sort -zu …)`) a lista fica vazia com `sem_caminhos=0`; sem `mktemp` (linha 281) vai a `sem_caminhos=1`, mas as checagens baratas iteram só `alterados`, vazio. Gravidade **baixa**: as checagens baratas são adiantamento do CI (ENVIO-LEVE, decisão do dono; o próprio hook diz "ferramenta ausente: aviso e segue"), o CI do PR roda as mesmas e é portão obrigatório do merge, e os bloqueios de política (refs, main/develop/homolog, R-VERIFY, segredo no delta) não dependem de `sort` nem de `mktemp`. O defeito real é o silêncio: correção mínima é aviso quando `sem_caminhos=1` ou a lista sai vazia com envio de código. Fora do escopo deste item (arquivo travado, outro cartão; não bloqueia).

Verificação: `python3 -m unittest tests.test_prepush_falha_fechada` no head 99a4fc30: 8 testes, OK (4,2 s). Suíte inteira: no CI do PR (`R-SEGURANCA`, sem suíte local por brief).

## Revalidação (E82.7, head 653b4411)
Delta lido: `forge-check parecer delta` de `99a4fc30..653b4411`; no domínio, só `tests/test_prepush_falha_fechada.py` (hunk `@@ -147`): sai o `skipUnless(shutil.which("python3"))` de `RegistrosSemPython` e o `python3` chega ao hook por um shim no PATH montado (`falsos`, linha 153, `exec "<sys.executable>" "$@"`). O teste deixa de pular em máquina sem `python3` no PATH e passa a provar sempre o ramo "controle com python3 roda os registros"; só aperta. Shim em pasta temporária do teste, sem efeito fora dele. Proposta inalterada: blob `3354881f06f29a5dcdcc2bb6efba5b44dde30be2` conferido no head; o resto do parecer vale como lido em 99a4fc30 (no git). Achados anteriores: nenhum. Verificação: `python3 -m unittest tests.test_prepush_falha_fechada` no head 653b4411: 8 testes, OK (2,5 s).

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Ferramentas: leitura e sondas locais no hook com o patch, em diretório temporário; sem varredura externa.
