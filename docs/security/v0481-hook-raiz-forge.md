---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-hook-raiz-forge
commit: 3c1bd3823c82f5383b9df5e289bf7889d4774e97
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-27
---
# Review de segurança: v0481 (E37.22, #930, volta 5, por delta)

Gatilhos: hook de bloqueio (`hooks/conformidade.py`), R-CONFORMIDADE, R-VERIFY (pre-push da raiz), o que roda fora do sandbox (postStart do container como root), o manifesto que decide as travas da sessão.

## Resumo
- Delta lido (`forge-check parecer delta`, `1644a83f..3c1bd382`).
  - No domínio: `ref_inteira` e `colada_em_vigor` (`hooks/conformidade.py:4178-4197`), a guarda de `hooks/conformidade.py:4381-4383` (o valor lido sem barra invertida), a docstring, `docs/hooks.md:69`, as fixtures `raiz-forge-s13`, `-s14`, `-s15`, `-review-s1` a `-s4`, `-tmpdir-entre-aspas` e `-colada-por-aspas-sem-entrada`, e os pisos 27 e 40 de `tests/test_hooks.py:2930-2931`.
  - Fora do domínio: os mutantes `tests/mutantes/v0481-hook-raiz-forge-{3,4,5}.json`.
- Estado dos achados anteriores:
  - A15: resolvido nos casos provados. S13, S14 e S15 dão rc 2 na raiz. `$d\s`, `"$d"s`, `$d's'` e S14 na cópia de `wt/` também recusam (B3, B4, B5, B10). As variantes anteriores seguem recusando (S9, F1 a F6, F9 a F11, R1 a R7, B6 a B9). Os legítimos seguem livres: L1 a L9, L11, LC1 a LC10, `"$TMPDIR"/y`, `"$f"x/y` e as 4 sondas do review.
  - Mas a nova leitura da colagem cai com um dado que o atacante controla: o nome colado citado inteiro em outro ponto da linha, um `ds=` na linha, ou um prefixo antes do componente (`./`, `$PWD/`, `x/../`). É o A16.
  - A14, A10 e A11: abertos, sem mudança no delta (recomendados).
- ci: o CI do 3c1bd382 (run 45958182953) está verde na suíte (5 partes), na instalação, nos passos, no python 3.14 e nas verificações longas. Vermelhos só `bateria (pareceres)` e `catraca`, por processo (pareceres do head). O head do PR andou para `d683705f` só com os pareceres de QA e review, sem código.

## Achados
- A16 (bloqueante) hooks/conformidade.py:4192 · explorável: S16 · a colagem por aspas some quando a linha cita o nome inteiro em outro ponto (`: $ds`, `# $ds`, `'$ds'`), quando tem `ds=x`, ou quando o componente vem depois de `./`, `$PWD/` ou `x/../` (linha 4381): o pre-push ou o manifesto da raiz são gravados (rc 0)
- A17 (recomendado) hooks/conformidade.py:4381 · cartão, fora desta branch: no projeto, a variável colada por aspas ou barra (`$d"s"/pre-push`, `"$d"n/plugin.json`) passa (rc 0) e grava o pre-push do projeto, que roda fora do sandbox no push da pessoa; já passava na develop
- A14 (recomendado) hooks/conformidade.py:4381 · aberto, fora do delta, cartão: a lista de `for` com curinga ou chaves (`for d in .githoo*`, `for d in .{githooks,x}`) passa na raiz e no projeto; dimensão da matriz: o valor que o bash expande na lista
- A10 (recomendado) hooks/conformidade.py:130 · aberto, sem mudança no delta: ESCRITA_NO_TEXTO não vê `open(…,'r+')` com `print(file=)` nem `subprocess`; o controle de fato é o sandbox negar a escrita nessas entradas da raiz
- A11 (recomendado) hooks/conformidade.py:4314 · aberto, sem mudança no delta: checar_texto do clone só casa a entrada literal; `os.path.join('.git','hooks',…)` passa na raiz do Forge; hoje o sandbox nega .git/hooks

## Sondas
- S13 · Bash `for d in .git\hooks; do printf x > $d/pre-push; done`, cwd na raiz do Forge, papel devops-engineer · espera: rc 2 · obtido: rc 2 (resolvido)
- S14 · Bash `for d in .githook; do printf x > $d"s"/pre-push; done`, cwd na raiz do Forge, papel devops-engineer · espera: rc 2 · obtido: rc 2 (resolvido)
- S15 · Bash `for d in .claude-plugi; do printf x > "$d"n/plugin.json; done`, cwd na raiz do Forge, papel devops-engineer · espera: rc 2 · obtido: rc 2 (resolvido)
- S16 · Bash `for d in .githook; do printf x > $d"s"/pre-push; done; : $ds`, cwd na raiz do Forge, papel devops-engineer · espera: rc 2 · obtido: rc 0
- S17 · Bash `ds=x; for d in .githook; do printf x > $d"s"/pre-push; done`, cwd na raiz do Forge, papel devops-engineer · espera: rc 2 · obtido: rc 0
- S18 · Bash `for d in .githook; do printf x > ./$d"s"/pre-push; done`, cwd na raiz do Forge, papel devops-engineer · espera: rc 2 · obtido: rc 0
- S19 · Bash `for d in .githook; do printf x > ./${d}s/pre-push; done`, cwd na raiz do Forge, papel devops-engineer · espera: rc 2, como no projeto · obtido: rc 0
- S20 · Bash `for d in .claude-plugi; do printf x > "$d"n/plugin.json; done; : $dn`, cwd na raiz do Forge, papel devops-engineer · espera: rc 2 · obtido: rc 0

## Detalhe dos achados
Como as sondas rodaram: `/root/.forge-contrib/wt/_sec138-v0481-sonda.py <cópia> forge|projeto` (77 entradas: as 56 da volta 4 e as novas N1 a N15 e NL1 a NL3), sobre a montagem da fixture `raiz-forge-s0-write-githooks-bloqueia`, com o hook do head revisado. No arquivo, S16 é N1, S17 é N5, S18 é N6, S19 é N7 e S20 é N4. O bash real grava `.githooks/pre-push` com S16 a S19, `$PWD/${d}s/…` e `x/../$d"s"/…` (`/root/.forge-contrib/wt/_sec138-v0481-bash.sh`, só em `$TMPDIR`).

- **A16 (alta):** a ameaça é a do A9 ao A15. Um agente sob injeção grava o pre-push ou o manifesto da raiz numa chamada só. Ganha execução fora do sandbox no próximo push do dono, ou desliga as travas da sessão.
  - Causa 1 (S16, S20, `# $ds`, `echo '$ds'; …`): `ref_inteira(n, linha)` procura o nome colado na linha inteira. Basta citar `$ds` em outro ponto (um `:`, um comentário, aspas simples) para `colada_em_vigor` tratar `$ds` como referência inteira, sem curinga.
  - Causa 2 (S17): com `ds=x` na linha, o hook calcula o valor de `$ds` (`x`), não entra no ramo sem valor e libera. O bash usa `$d` mais `s`.
  - Causa 3 (S18, S19, `$PWD/${d}s/…`, `x/../$d"s"/…`): a guarda olha só `split("/")[0]` do texto, que é `.`, `$PWD` ou `x`. S19 é a colagem por chave do A13 (volta 4): no projeto recusa, na raiz passa.
  - Correção mínima, testada (`/root/.forge-contrib/wt/_sec138-v0481-patch.py`):
    - Em `colada_em_vigor` (4191-4196), os padrões de prefixo (`"*" + n[k:]` para cada `n[:k]` citado inteiro) valem sempre, somados ao componente; o `*` sozinho só quando não há prefixo e o nome não aparece inteiro:
      ```python
      padroes = [componente]
      if m:
          n = m[1]
          prefixos = ["*" + n[k:] for k in range(1, len(n)) if ref_inteira(n[:k], linha)]
          padroes += prefixos or ([] if ref_inteira(n, linha) else ["*"])
      ```
    - Em `destino_opaco`, antes de calcular `valores` (4377), o primeiro componente sai do caminho normalizado e sem o prefixo da raiz, e a colagem recusa antes do valor:
      ```python
      juntada = re.sub(r"^(?:\$\{?(?:PWD|CLAUDE_PROJECT_DIR)\}?|\$\(pwd\))/", "", palavra_juntada(caminho))
      primeiro = os.path.normpath(juntada).split("/")[0]
      if colada_em_vigor(primeiro, self.texto_da_linha):
          self.barrar(...)  # a mesma recusa de 4384
          return
      ```
  - Conferido numa cópia em `$TMPDIR` (exportada do head por `git archive`, com o patch):
    - S13 a S20 e N1 a N15 dão rc 2. Nada que recusava passou a liberar.
    - Os legítimos seguem livres: L1 a L9, L11, LC1 a LC10, NL1 (`"$f"/out`) e NL2 (`"$TMPDIR"/y; : $TMPDIRx`).
    - Custo: NL3 (`for f in a; do printf x > $f"s"/x; done`) já recusa no head e segue recusando: `*s` casa `.githooks`, fecha na dúvida.
    - `tests.test_hooks.Hooks.test_fixtures_da_raiz_do_forge` e `test_fixtures_fatia_1` a `_4`: OK (4 subtestes de pid pulados pelo sandbox), com as fixtures novas da volta 5.
  - O que falta junto:
    - Fixtures na raiz (rc 2): S16, S17, S18 e S19.
    - Mutantes: tirar a soma dos padrões de prefixo quando o nome aparece inteiro; tirar o `normpath`; mover a checagem de volta para depois do valor.
    - `docs/hooks.md:69` passa a dizer que o componente é lido depois de `./`, `$PWD/` e `..`, e que o valor calculado de um nome colado não libera.
    - Dimensões novas da matriz: a posição do componente colado no caminho (depois de `./`, `$PWD/`, `x/../`) e o nome colado citado ou atribuído em outro ponto da linha.
  - Esforço P. Dono: tech-lead.
- **A17 (alta no projeto, fora desta branch):** no projeto (`forge: true`), S14, S15, S16 a S18, S20, B3 a B5, B7, `$d$'s'` e `set -- .githook; printf x > $1"s"/pre-push` dão rc 0. O pre-push do projeto roda fora do sandbox no `git push` da pessoa, com a mesma ameaça. Já passava na develop (a guarda do projeto não modela a colagem por aspas), então vira cartão, não bloqueio desta branch. Correção: a mesma leitura de `colada_em_vigor`, normalizada como no A16, na guarda do projeto. Dono: tech-lead.
- **A14:** segue como na volta 4 (F7 e F8 dão rc 0 na raiz e no projeto). Cartão (G1.2). Dono: tech-lead.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Varreduras de segredos, SAST e workflows não se aplicam: o delta é um hook, fixtures e documentação, sem dependência nem workflow. A suíte inteira foi lida do CI do head. Local, com `flock /root/.forge-contrib/trava-teste-b.lock`, rodei as sondas acima no head (raiz e projeto) e na cópia com o patch, e as fatias de fixtures de `tests.test_hooks` na cópia com o patch.
