---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-hook-raiz-forge
commit: 1644a83f0b3c4ed16e9fd5c8b49b71d4c6288980
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-27
---
# Review de segurança: v0481 (E37.18, #930, volta 4, por delta)

Gatilhos: hook de bloqueio (`hooks/conformidade.py`), R-CONFORMIDADE, R-VERIFY (pre-push da raiz), o que roda fora do sandbox (postStart do container como root), o manifesto que decide as travas da sessão.

## Resumo
- Delta lido (`forge-check parecer delta`, `aa347213..1644a83f`).
  - No domínio: a guarda de `hooks/conformidade.py:4357-4358` (as duas partes da correção do A13), a docstring, `docs/hooks.md:69`, as fixtures `raiz-forge-s10`, `-s11` e `-s12` e o piso 37 de `tests/test_hooks.py:2931`.
  - Fora do domínio: os mutantes `tests/mutantes/v0481-hook-raiz-forge-{3,4}.json`.
- Estado dos achados anteriores:
  - A13: resolvido nos casos provados. S10, S11 e S12 dão rc 2 na raiz. As variantes da volta 3 seguem recusando (S9, F1 a F6, F9 a F11, R1 a R7, W9, WR1), e os legítimos seguem livres (L1 a L9, L11).
  - Mas a mesma promessa do delta ("lida sem aspas", "a variável colada no primeiro componente recusa") não se cumpre com a barra invertida nem com a colagem por aspas. É o A15.
  - A14, A10 e A11: abertos, sem mudança no delta (recomendados).
- ci: 1644a83f vermelho só por processo (`gh pr checks 930`).
  - A suíte, a instalação, os passos e as verificações longas do head estão verdes.
  - `bateria (pareceres)` e `catraca` estão vermelhas pelos pareceres deste head.
  - O head do PR andou para `a2c596ac` só com os pareceres de QA e review, sem código.

## Achados
- A15 (bloqueante) hooks/conformidade.py:4357 · explorável: S13 · a correção do A13 não vê a barra invertida (`for d in .git\hooks`) nem a variável colada por aspas ou barra (`$d"s"`, `"$d"s`, `$d\s`, `$d's'`), que chega à guarda já como `$ds`: o pre-push ou o manifesto da raiz do Forge são gravados (rc 0)
- A14 (recomendado) hooks/conformidade.py:4357 · aberto, fora do delta, cartão: a lista de `for` com curinga ou chaves (`for d in .githoo*`, `for d in .{githooks,x}`) passa na raiz e no projeto; dimensão da matriz: o valor que o bash expande na lista
- A10 (recomendado) hooks/conformidade.py:130 · aberto, sem mudança no delta: ESCRITA_NO_TEXTO não vê `open(…,'r+')` com `print(file=)` nem `subprocess`; o controle de fato é o sandbox negar a escrita nessas entradas da raiz
- A11 (recomendado) hooks/conformidade.py:4301 · aberto, sem mudança no delta: checar_texto do clone só casa a entrada literal; `os.path.join('.git','hooks',…)` passa na raiz do Forge; hoje o sandbox nega .git/hooks

## Sondas
- S10 · Bash `for d in .git''hooks; do printf x > $d/pre-push; done`, cwd na raiz do Forge, papel devops-engineer · espera: rc 2 · obtido: rc 2 (resolvido)
- S11 · Bash `read d <<< .git''hooks; printf x > $d/pre-push`, cwd na raiz do Forge, papel devops-engineer · espera: rc 2 · obtido: rc 2 (resolvido)
- S12 · Bash `for d in .githook; do printf x > ${d}s/pre-push; done`, cwd na raiz do Forge, papel devops-engineer · espera: rc 2 · obtido: rc 2 (resolvido)
- S13 · Bash `for d in .git\hooks; do printf x > $d/pre-push; done`, cwd na raiz do Forge, papel devops-engineer · espera: rc 2, como no projeto · obtido: rc 0
- S14 · Bash `for d in .githook; do printf x > $d"s"/pre-push; done`, cwd na raiz do Forge, papel devops-engineer · espera: rc 2 · obtido: rc 0
- S15 · Bash `for d in .claude-plugi; do printf x > "$d"n/plugin.json; done`, cwd na raiz do Forge, papel devops-engineer · espera: rc 2 · obtido: rc 0

## Detalhe dos achados
Como as sondas rodaram: `/root/.forge-contrib/wt/_sec136-v0481-sonda.py <cópia> forge|projeto` (56 entradas: a lista da volta 3 e as novas B1 a B11 e LC1 a LC10), sobre a montagem da fixture `raiz-forge-s0-write-githooks-bloqueia`, com o hook do head revisado. No arquivo, S10 é F6, S11 é R7, S12 é F5, S13 é B1, S14 é B2 e S15 é B11.

- **A15 (alta):** a ameaça é a do A9, do A12 e do A13. Um agente sob injeção grava o pre-push ou o manifesto da raiz numa chamada só. Ganha execução fora do sandbox no próximo push do dono, ou desliga as travas da sessão.
  - Causa 1 (S13): `palavra_juntada` tira só as aspas, mas o bash também junta `.git\hooks` em `.githooks`. No projeto, S13 recusa (rc 2, "o hook não modela"); na raiz, passa.
  - Causa 2 (S14, S15, e também `"$d"s`, `$d\s`, `$d's'` e S14 na cópia de `wt/`): o destino chega a `destino_opaco` já sem aspas nem barra, como `$ds/pre-push`. `palavra_juntada("$ds")` é uma referência inteira, sem `*`, e não há `ds=` na linha, então nada casa. No projeto, essas também passam (fora desta branch), mas o delta e `docs/hooks.md:69` prometem que a variável colada recusa.
  - Correção mínima, testada (`/root/.forge-contrib/wt/_sec136-v0481-patch.py`), trocando as linhas 4357-4358:
    ```python
    primeiro = palavra_juntada(caminho).split("/")[0]
    colada = "*" in primeiro or any(  # A15: `$d"s"`, `"$d"s`, `$d\s` chegam aqui como `$ds`
        not re.search(rf"\$(?:{n}|\{{[#!]?{n})(?!\w)", self.texto_da_linha)
        for n in re.findall(r"\$\{?(\w+)", primeiro))
    if colada or any(EM_VIGOR_NO_TEXTO.search(t) or EM_VIGOR_NO_TEXTO.search(
            re.sub(r"\\(.)", r"\1", palavra_juntada(t))) for t in textos):
    ```
    - A barra: o texto do valor também é lido sem a barra invertida (`re.sub(r"\\(.)", r"\1", …)`). Fecha S13.
    - O nome cru: recusa quando o nome da variável do primeiro componente não aparece na linha crua como referência inteira (`$ds` ou `${ds…}`), porque ele nasceu de uma colagem por aspas ou barra. Fecha S14 e S15.
    - O `[#!]?` e o `(?!\w)` mantêm `${d,,}`, `${#d}` e `${d:-x}` no caminho de antes. Sem eles, a fixture `pp-sessao-forge-wt-tech-lead-variavel-caixa-qa-bloqueia` troca de mensagem (segue rc 2).
  - Conferido numa cópia em `$TMPDIR` (exportada do head por `git archive`, com o patch):
    - S9 a S15, B3 a B5 e B10 dão rc 2. Nada que recusava passou a liberar.
    - Os legítimos seguem livres: L1 a L9, L11 e os novos LC2, LC4 e LC6 a LC10 (`"$TMPDIR"/y`, `"${TMPDIR}/y"`, `out=$(mktemp -d); printf x > "$out"/f`, `D=$TMPDIR/a; printf x > "$D"/b`, `wc -l "$f" > "$TMPDIR"/n`).
    - `tests.test_hooks.Hooks.test_fixtures_fatia_1` a `_4` e `test_fixtures_da_raiz_do_forge`: OK (4 subtestes de pid pulados pelo sandbox).
  - O que falta junto:
    - Fixtures: S13, S14 e S15 na raiz (rc 2) e um legítimo com a variável entre aspas sozinha no componente (`printf x > "$TMPDIR"/y`, rc 0). Piso de recusas: 40.
    - Mutantes: tirar a leitura sem a barra e tirar a checagem do nome cru.
    - `docs/hooks.md:69` passa a citar `.git\hooks` e `$d"s"`.
  - Esforço P. Dono: tech-lead.
- **Custo documentado, sem achado:** LC1, LC3 e LC5 (`for f in a b; do printf x > ${f}.out; done`, `out=$(mktemp); printf x > ${out}.bak`) já recusam no head. A variável colada sem valor calculado fecha na dúvida, como prometido, e a mensagem manda escrever o caminho literal.
- **A14:** segue como na volta 3 (F7 e F8 dão rc 0 na raiz e no projeto). Vira cartão (G1.2). Dono: tech-lead.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Varreduras de segredos, SAST e workflows não se aplicam: o delta é um hook, fixtures e documentação, sem dependência nem workflow. A suíte inteira foi lida do CI do head. Local, com `flock /root/.forge-contrib/trava-teste-b.lock`, rodei as sondas acima no head e na cópia com o patch, e as fatias de fixtures de `tests.test_hooks` na cópia com o patch.
