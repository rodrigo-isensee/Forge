---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-conformidade-sessao-forge
commit: fe8607dfc22953432cf43dbf4ea4fbf2158292d2
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 (E51.3, CONFORMIDADE-DESLIGADA-NA-SESSAO-DO-FORGE)

Escopo lido: `git diff 0f6034ea...fe8607df` (2 commits: e8fb3404 e fe8607df), `hooks/conformidade.py`, `hooks/vigia.py`, `docs/hooks.md`, `changelog.d/`, `tests/test_hooks.py` (classe `HookSessaoDoForge`), fixtures `e51-*` e `tests/mutantes/v0479-conformidade-sessao-forge.json`. Contra o cartão do brief da E51.1: (1) as travas valem na sessão do Forge fora de projeto (clone e `wt/*`) para todo papel; (2) o `vigia` trata o clone como projeto e grava `violacoes.jsonl`.

## Achados
- A1 (recomendado) docs/hooks.md:68 · "Ainda não coberto" segue listando "a ativação no próprio Forge (ADR 0008, 4.4)", mas a linha 63 e o parágrafo do vigia agora a ligam em parte: dizer o que já vale (travas e vigia) e o que falta.
- A2 (recomendado) hooks/conformidade.py:3784 · a trava é reconhecida pelo texto da recusa (prefixo `PUSH_DIRETO`, trecho `TAG_E_VERSAO`): um `barrar` novo com a mesma frase entra calado no conjunto e um que mude a frase sai; preferir marca explícita no `barrar` (argumento ou categoria).
- A3 (bloqueante) hooks/conformidade.py:3784 · a recusa de alvo opaco com ação crítica (R-CONFORMIDADE, `o hook não modela`) não entra no predicado: `B=develop; git push origin $B` e `F=--force; git push $F origin melhoria/x` saem 0 na wt real (S1, S2); no projeto recusam. Mesmo defeito do A1 da segurança.

## Sondas
- S1 · hook desta cópia, CLAUDE_PROJECT_DIR=/workspaces/Forge, cwd nesta wt, forge:tech-lead, Bash `B=develop; git push origin $B` · espera: código 2, como no projeto · obtido: código 0
- S2 · mesmo leiaute, Bash `F=--force; git push $F origin melhoria/x` · espera: código 2, como no projeto · obtido: código 0

## Parecer
Reprovado, por um bloqueante (A3): a trava pedida pelo cartão da E51.1 se anula com o ramo ou a flag numa variável, forma que o projeto já recusa. O A3 é o A1 do parecer de segurança (`docs/security/v0479-conformidade-sessao-forge.md`, sondas S1 a S3 dela), lido depois do meu exame e reproduzido aqui no leiaute real pelas sondas S1 e S2. A causa é a do A2: o predicado escolhe a trava pelo texto da recusa e deixa de fora a recusa do alvo opaco com ação crítica (`conformidade.py:2159`, e as irmãs em 2017, 2119 e 2127). Correção sugerida: o predicado aceita também essas recusas (de preferência por marca explícita no `barrar`, o que resolve o A2 junto), com uma fixture `e51-*` por forma (`$B` no refspec, `$F` na flag, `${B:-develop}`) e mutante por guarda nova.

O resto está certo e fica: a `GuardaDaProva` ganha `travas`, ligada só por `na_sessao_do_forge` (raiz da sessão no clone, fora de `PostToolUse`), e passa adiante as recusas com `R-MAIN`, `R-VERIFY`, push direto para a integração e tag `v*`; o resto da linha segue livre (ADR 0009, seção 6), o que a fixture `e51-wt-escrita-dev-libera` e o mutante M5 (`return True`) provam. Nenhuma trava existente afrouxa: a mudança só acrescenta recusa ao caminho fora de projeto, e o caminho do papel com lista segue igual. O `vigia` passa `clone_do_forge=True`, como os outros hooks, com o estado em `Hook.run`. As duas constantes trocam só o texto por referência, com a mensagem idêntica.

Tamanho (H1): cerca de 35 linhas de código em `hooks/`, um comportamento. Guardas do diff: as 3 linhas de decisão novas (`if self.travas ...`, o `return` do predicado, o argumento na chamada) e a do `vigia` têm mutante declarado (M1 a M7), com fixtures do ramo de falha (`-bloqueia`) e do livre (`-libera`). O M7 do `fix-037-uniao-seg.json` só acompanha a assinatura nova da chamada.

Execução: `python3 -m unittest tests.test_hooks.HookSessaoDoForge -v` com ambiente limpo: 2 testes, OK. `bin/forge-mutante --processos 1 --ids M5,M7`: `M5 · morreu · hooks/conformidade.py:3784` e `M7 · morreu · hooks/vigia.py:509`. Sonda no leiaute real (hook com `CLAUDE_PROJECT_DIR=/workspaces/Forge`, `cwd` nesta worktree, papel `forge:tech-lead`): `git push origin HEAD:develop` sai 2 (`R-CONFORMIDADE: push direto para develop`), `git tag v9.9.9` sai 2 (`R-FLUXO`), `gh pr merge 1 --admin` sai 2 (`R-MAIN`), `git push origin <branch de trabalho>` sai 0. Suíte completa: fica para o CI do PR (brief; o módulo `test_hooks` inteiro passa de 600 s).

Na volta, revalido pelo `forge-check parecer delta`. A1 e A2 viram cartão depois do merge, salvo se a correção do A3 já resolver o A2 (`R-REVIEW`).
