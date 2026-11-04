---
tipo: revisao-seguranca
contrato: 1
pedido: versao-033
branch: melhoria/hook-parecer-034
commit: ef5e341a146734ca2e74aa05f458fddaf01243a6
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-04
---
# Review de segurança: versao-033 (frente 0.34, hook-parecer-034)

Escopo: `b45e40a..ef5e341` (6a7a85a PARECER-HOOK-DICA-EDIT; ef5e341 PARECER-BARRA-FETCH). Revisão estática e defensiva.

## Gatilhos
Controles do Forge (`R-SEGURANCA`): `hooks/parecer.py` é guarda de processo do Forge.

## Achados
- A1 (recomendado) tests/hooks/parecer/atualiza-barra-ff-only-da-branch-reprovada-na-develop.json:63 · os dois casos barra-* entram na develop por git checkout na mesma linha; falta um caso com a sessão já na develop (merge --ff-only feature/x sem checkout), que prova a regra sem depender do checkout

## Detalhe dos achados
**Decisão do hook (lógica, não só texto).** Em `hooks/parecer.py:669-671` entra um ramo novo dentro do `except ValueError` de `tirar_heredocs`: com `corpo_de_heredoc` verdadeiro, chama `bloquear("R-REVIEW", ...)` com outra mensagem. Antes, o mesmo caminho caía em `bloquear("R-REVIEW", ...)` na linha seguinte. `bloquear` (`hooks/_comum.py:2238-2244`) sai sempre com código 2, então a decisão é a mesma (recusa, mesma regra); muda só a causa exibida. As outras mudanças (`hooks/parecer.py:86`, `:688`, `:692`, `:713`) trocam só o texto do `Corrigir:` por `GRAVE_E_RODE_NOUTRA`; as condições ficaram iguais. Nada passa a ser liberado.

**A mensagem nova ensina contorno?** Não abre caminho novo. O texto "grave pelo Write ou Edit e rode o programa noutra chamada" equivale ao anterior ("grave o arquivo pelo Write ou numa chamada do Bash e rode o programa noutra" e "grave numa chamada do Bash e rode o programa noutra"). Gravar pelo Write/Edit passa pelo `conformidade` no `file_path` resolvido (a escrita em `.forge/` e nas áreas protegidas continua barrada), e o programa rodado noutra chamada é a limitação já documentada como "[B] barrado em regra, não garantido" (ADR 0009, `docs/hooks.md`, seção do `parecer`): o hook lê só a linha, e a fronteira real é o hook de git, o CI e a proteção de branch. O Write/Edit até reduz a superfície em relação ao heredoc do Bash, porque o corpo deixa de passar por um shell. Severidade do tema: informativa, pré-existente, sem caminho novo.

**Corpus do PARECER-BARRA-FETCH.** Cinco fixtures `atualiza-*` com o mesmo estado (feature/x com review reprovado no HEAD, QA aprovado, base develop). Passa (código 0): `git fetch origin develop && git merge --ff-only origin/develop`, `git fetch origin && git merge --ff-only origin/feature/x` e `git pull --ff-only origin feature/x`. Barra (código 2, stderr com `R-REVIEW: docs/reviews/p1-1.md`, que amarra a recusa ao review reprovado): `git fetch origin && git checkout develop && git merge --ff-only feature/x` e `git checkout develop && git pull --ff-only . feature/x`. O teste `tests/test_hooks_parecer_pasta.py:41-48` exige os dois lados e que o nome diga o esperado (`{("passa",0),("barra",2)}`). Os dois lados da regra estão provados; A1 só sugere um terceiro caso de barra sem o checkout na linha.

**Mutantes.** `tests/mutantes/hook-parecer-034.json` cobre o ramo novo (M1) e as quatro mensagens (M2 a M5), todos com `test_corpus_texto_passa_e_barra`; as fixtures `texto-barra-heredoc-*-dica-write` e `texto-barra-heredoc-corpo-ilegivel-e-git-diz-a-causa` (esta com `stderr_sem` para `<<'FIM'`) seguem com código 2.

A1: severidade informativa · caminho de ataque: nenhum hoje, é lacuna de prova · correção mínima: fixture `atualiza-barra-ff-only-na-develop-sem-checkout`, com o estado já na develop · esforço P · dono: autor da frente.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Teste rodado: `python3 -I -m unittest discover -s tests -p test_hooks_parecer_pasta.py` (3 testes, OK, 27 s). Suíte inteira não rodada (D-5). Sem segredo nem dependência nova no diff; `gitleaks` e `semgrep` não usados (o diff é de mensagens em Python e de JSON de teste).
