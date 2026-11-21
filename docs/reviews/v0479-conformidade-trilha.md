---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-conformidade-trilha
commit: 6c0b0f039a3ad89220cf328244e8df66da31c7d9
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-21
---
# Review: v0478 (E63.2, trilha CONFORMIDADE-SEGURANCA do `hooks/conformidade.py`, head 6c0b0f03)

Diff `d4f0b10a..6c0b0f03`: 10 commits de código e teste (E63.1), `hooks/conformidade.py` +120 -12, três cartões no mesmo item,
como o pedido decide (E63: "na mesma branch, um depois do outro"); cada cartão fica abaixo do teto H1.

## O que li (regras "leitura" do `docs/engineering/praticas.md` que alcançam o diff)
- **CONTROLE-PEDIDOS-E-BRIEFS-SO-JARVIS** (`hooks/conformidade.py:3786-3871`, `:4035`): a política já tinha
  `~/.forge-contrib/{,*/}docs/{pedidos,briefs}/` com `quem: [jarvis]` (`hooks/conformidade.json:61-68`); a mudança só a faz valer
  na sessão do Forge, como a das pastas de parecer. `critico` vira atributo (classe: `CRITICO.search`; `GuardaDaProva` soma o
  controle para quem não é o jarvis): chamada única, sem custo extra no caminho comum. A leitura segue livre
  (`cpb-tech-lead-le-pedidos-libera`).
- **CONFORMIDADE-ESCRITA-NO-INDICE** (`:2687`): toda palavra não-opção conta como caminho, o terceiro campo do `--cacheinfo`
  com vírgulas também; só recusa o achado `instalacao` (`quem: []`). A lista pela entrada recusa. O `ls-files -c -o` no
  pathspec de pasta é barato: medi 0,09 s com 60 mil arquivos ignorados na pasta.
- **CONFORMIDADE-SUBSTITUICAO-NO-PROJETO** (`:2129`, `:3962`): lê o texto cru por comando simples, sem os corpos de
  heredoc; o filtro de `in` antes do parse é só custo (documentado como limite em `docs/hooks.md:58`).
- Custo do corpus: +5415 passos (0,092%), `tests/apoio_volta_unica.py:199-203` com a prova em
  `tests/provas/v0479-corpus-custo.md`; abaixo de 0,1% o aceite é do time com a confirmação escrita da segurança (E63.3).

## Sondas que rodei (nenhuma prova bloqueante)
Pela função `envio_com_substituicao` e pelo hook inteiro (fixture do tech-lead no projeto):
- recusam: `git push origin $(git branch --show-current)` (com e sem aspas), `git -c core.sshCommand=$(echo ssh) push origin x`,
  `$(printf git) $(printf push) origin x`, `echo "$(git push origin $(echo develop))"`;
- liberam: `git push origin feature/x`, o envio com log e `rc=` da skill `esperar-estado`,
  `git commit -m "$(date)" && git push origin feature/x`, `cd $(git rev-parse --show-toplevel) && git push origin feature/x`,
  `git log $(git merge-base …)..HEAD`, `gh pr view $(git branch --show-current)`;
- `bash -c "git push origin $(echo --force)"`, `eval "…"` e `B=$(echo --force); git push origin $B` passam pela função
  (nível 0, sem envio na palavra) mas o hook recusa por `eval`/`bash -c`/`$B` com ação crítica: sem furo.

## Efeito colateral: `git push origin $(git branch --show-current)` recusado também para o tech-lead
Aceitável. O valor do destino é opaco ao hook, e o destino pode ser `develop`/`main`; a recusa é a mesma classe do FD4 já
medido e documentado (`docs/hooks.md:125`, contorno "o nome literal da branch"), e `agents/tech-lead.md:23` já prescreve
`git push origin <branch>` literal. Nenhuma skill, agente ou modelo manda montar o envio com `$(…)` (procurei em `agents/`,
`skills/`, `stacks/`, `templates/`, `bin/`; o `bin/forge-fechar:783` imprime o nome já expandido). Texto nas skills: não é
necessário para o merge; vale uma palavra na skill `esperar-estado`, onde o envio longo é montado (A1).

## Ferramentas (citadas, não refeitas)
- Testes novos, rodados no head: `test_fixtures_do_controle_so_jarvis`, `test_fixtures_da_escrita_no_indice`,
  `test_fixtures_da_substituicao_no_projeto` → `Ran 3 tests in 45.300s OK`.
- `bin/forge-mutante --processos 1 --ids S3 tests/mutantes/v0479-conformidade-trilha-3.json` → `S3 · morreu · hooks/conformidade.py:3984`.
- `bin/forge-mutante --cobertura --base d4f0b10a` → rc 0 (toda condição mudada coberta).
- `bin/forge-check pr v0479-conformidade-trilha --base develop`: classe C (protegido da catraca); faltam só os pareceres.
- Suíte inteira: CI do PR (não rerrodada aqui).

## Achados
- A1 (recomendado) skills/esperar-estado/SKILL.md:44 · somar `$(…)` à lista "sem `$TMPDIR` nem `$?`, que a conformidade recusa ao lado do envio": desde o E63.1 o destino por substituição também recusa (FD4), e é ali que o envio longo é montado.
- A2 (recomendado) tests/mutantes/v0479-conformidade-trilha-3.json:86 · o arquivo declara 9 mutantes (S1-S9); o teto do papel é 8 por arquivo ("passou de 8, abra -2"): mover o S9 para um `-6`. O brief diz 36; os cinco arquivos somam 37.

## Sondas

## Parecer
Aprovado no head 6c0b0f03. Os três cartões fazem o que o E63 pede, as guardas mudadas têm mutante declarado e teste do ramo
de falha, os limites ficam escritos em `docs/hooks.md`, e o efeito colateral sobre o envio com `$(git branch --show-current)`
é aceitável e já tem contorno documentado. A1 e A2 são recomendados e viram cartão depois do merge (`R-REVIEW`).
