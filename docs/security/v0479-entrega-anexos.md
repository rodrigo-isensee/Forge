---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-entrega-anexos
commit: df0aef74d183d9b89d108ac9dadc0352bf2b870e
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: registro de bug do QA como anexo do portão na volta (v0478 E62.1, E62.3)

Diff lido inteiro: `d4f0b10a..df0aef74` (base `develop`), dez arquivos: `bin/forge-check`, `docs/hooks.md`, `docs/hooks-fixtures.md`, `changelog.d/v0479-entrega-anexos.md`, as quatro fixtures `pp-sessao-forge-wt-*-qa-bugs-*`, `tests/mutantes/v0479-entrega-anexos.json` e `tests/test_selo_e_entrega.py`. Nenhum código de hook mudou: `hooks/` fica igual ao da base, e a mudança de comportamento está só em `bin/forge-check`.

Gatilhos: controle do Forge (`bin/forge-check entrega`, barreira de papel do hook `conformidade`), afrouxa-regra com condição do dono (DECISÃO DO DONO 2026-11-20 17:29, item 2).

## Achados
- A1 (recomendado) docs/hooks.md:55 · O texto afirma docs/qa/bugs/ só do qa, mas o commit montado pelo git sem citar o caminho passa: Write em $TMPDIR mais git apply, git update-index --cacheinfo, git cherry-pick. Registrar o resíduo (o mesmo das pastas de parecer do E50.1) na linha e na docstring do forge-check:3108.

## Sondas

## Detalhe

**(1) Quem grava em `docs/qa/bugs/` na sessão do Forge.** A regra é `hooks/conformidade.json:73` (`docs/qa/`, `quem: ["qa"]`), aplicada pelo prefixo, então cobre a subpasta sem código novo. As fixtures novas provam isto na worktree em `wt/*` com sessão do Forge: o `qa-engineer` grava pelo Write (libera); o `tech-lead` pelo Write, o `security-engineer` pelo Edit e o agente de stack pelo `>` do Bash são recusados com `parecer de QA é do qa: docs/qa/`. Rodei `tests.test_hooks.Hooks.test_fixtures_do_parecer_pelo_papel` no head: 42 fixtures `pp-*`, OK. Também sondei o hook com o papel `dev` na mesma montagem. Recusam (rc 2): `./docs//qa/bugs/x.md`, `docs/reviews/../qa/bugs/x.md`, `cp /tmp/a docs/qa/bugs/x.md`, `git checkout origin/develop -- docs/qa/bugs/x.md` e `git restore --source=HEAD~1 docs/qa/bugs/x.md`. Liberam (rc 0): `git apply /tmp/p.patch`, `git update-index --add --cacheinfo 100644,<blob>,docs/qa/bugs/x.md` e `git cherry-pick <sha>`. `docs/QA/bugs/` também libera, mas cria outro caminho no git, que `nome.startswith(BUGS_DO_QA)` (`bin/forge-check:3337`) não aceita. Conclusão: pelas ferramentas de arquivo e pelo Bash com o caminho literal, só o `qa-engineer` grava. A rota pelo índice do git (A1) fica aberta. Ela não é nova: vale igual para os pareceres do E50.1 e cai na classe que `docs/hooks.md` já trata como não modelada (`git apply`, `git am`).

**Caminho de ataque do A1 e severidade.** O agente autor da volta grava um patch por Write em `$TMPDIR` e o aplica com `git apply` ou `update-index`. Depois commita, num commit só de `docs/qa/`, um registro de bug que a conferência mostra como `escopo: ok (anexo do portão ...)`, sem leitura. O ganho é esconder da conferência um arquivo de texto. Nenhum consumidor trata `docs/qa/bugs/` como autoridade: só a própria conferência o lê (`grep` em `bin/`, `hooks/` e `scripts/`). O commit não pode levar código, porque `commit_so_de_parecer` exige só `docs/qa/`. Severidade baixa. A correção mínima é de texto: registrar o resíduo em `docs/hooks.md:55` e na docstring de `bin/forge-check:3108` ("a barreira é a do hook"). Fechar a rota no hook é outro item, da trilha do `conformidade`. Esforço P. Dono: `tech-lead` (autor do E62.1).

**Lógica nova (`bin/forge-check:3105-3117`, `:3337-3339`).** Só vale com `valido` (o Desde de conferida ou Revisar-sha, registro do Jarvis), só em etapa de código e sem caractere de controle no nome. O `rev-list` que falha ou vem vazio recusa. Todo commit do intervalo que muda o arquivo tem de mexer só em `docs/qa/` ou ser merge que fica com o blob de um dos pais. Pelo `--full-history`, os commits do lado mesclado também entram. Quando o `qa-engineer` é autor da volta, ou nenhum autor é lido, vale só com o blob do último `parecer conferido`, que é falha fechada, como o E50.6. Os cinco mutantes de `tests/mutantes/v0479-entrega-anexos.json` atacam cada uma dessas guardas. `python3 -m unittest tests.test_selo_e_entrega.BugDoQaNaVolta` no head: 10 testes, OK.

**(2) A mudança só aperta?** Não. Ela aceita mais do que antes. Até a base, um arquivo de `docs/qa/bugs/` (sem frontmatter) mudado no intervalo caía no `else` de `linhas_de_entrega` e saía `escopo: confira`, que pede leitura. Agora sai `escopo: ok (anexo do portão: registro de bug de qa ...)` quando cumpre as condições acima. É afrouxamento da conferência de entrega, e o rótulo `afrouxa-regra` é o correto. Não confirmo "só aperta". As fixtures do hook só acrescentam prova: nenhuma recusa vira liberação. O afrouxamento é o que a DECISÃO DO DONO de 2026-11-20 17:29, item 2, autoriza ("com a mesma barreira de papel (só o QA grava ali)"). A condição se cumpre na forma em que a barreira já vale para os pareceres, com o resíduo do A1, que é o mesmo dos pareceres.

**Suíte.** A suíte inteira roda no CI do PR, que ainda não existe (o brief pede o parecer sem PR). Rodei só o teste novo e o das fixtures, citados acima. O CI verde do PR continua sendo condição de merge.

## Riscos aceitos e ferramentas
Nenhum risco aceito por este parecer. Ferramentas: leitura do diff, `unittest` e sondas locais do hook pela montagem de `tests/test_hooks.py`. `gitleaks` e o SAST não estão no PATH desta máquina (lacuna). O diff não traz segredo nem dependência nova.
