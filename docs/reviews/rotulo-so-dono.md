---
tipo: review
contrato: 1
pedido: rotulo-so-dono
branch: melhoria/rotulo-so-dono
commit: 11d91963f2d951bdadad4aebc370062140491dcc
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-19
---
# Review: o rótulo afrouxa-regra só do dono do Forge (E1.2)

Revisor independente (outra instância do `tech-lead`, D-ETAPAS-INST = A); o autor da E1.1 não revisa. Diff lido: `976a159...11d9196` (3 commits: regra, hook com 12 fixtures, fragmento).

## O que foi conferido
- **E1 (regra, texto único):** o item novo está só em `docs/regras/R-CONTRIB.md` (`grep` de "só do dono do Forge" e "só o dono do Forge aplica" fora do `changelog.d/` acha só ele); diz quem (a conta do `gh` dona do repositório do Forge, com decisão do dono registrada), o quê (pr/issue edit, pr create, `gh api` em `issues/<n>[/labels]`, mutação GraphQL) e a proibição expressa para qualquer outro contribuidor, como na decisão do dono. As duas frases-chave entraram em `invariantes` (`tests/config.json`): só acréscimo, nenhuma remoção.
- **E2 (hook):** `gh_rotulo` / `aplica_afrouxa_regra` / `exigir_dono` em `hooks/conformidade.py`. A conta vem de `gh api user --jq .login`; o dono, de `parecer.slug_do_forge()` (campo `repository` do `plugin.json` em vigor, o mesmo slug que o resto do hook usa). Conta ilegível, dono ilegível ou conta diferente barram (falha fechado); `bash -c`, `eval`, `$(...)`, heredoc para shell e lançadores são percorridos até `PROFUNDIDADE`; linha que não se analisa (`ValueError`) e cita o rótulo exige o dono.
- **O caminho novo em `principal` só analisa o rótulo:** roda só com raiz da sessão num clone do Forge, ferramenta Bash, fora de `PostToolUse` e papel sem lista de permissão; cria uma `Guarda` e chama apenas `rotulo_na_sessao_do_forge`, cuja única saída de bloqueio é `exigir_dono` → `barrar("R-CONTRIB", ...)`. Depois, a condição de retorno é a mesma de antes (`not (com_lista and na_sessao_do_forge)`), então nenhuma outra regra passa a valer na sessão do Forge. No caminho completo (papel com lista, ou sessão de projeto com `sessao_forge` verdadeiro), `gh()` chama `gh_rotulo` só se `self.sessao_forge`; nas sessões de projeto o atributo é `False` (definido em `__init__`) e o comportamento não muda. A refatoração de `graphql_perigoso` em `textos_da_api` preserva o resultado (ilegível continua barrando).
- **Os 12 testes** (fixtures `tests/hooks/conformidade/rotulo-so-dono-*.json`, `gh` falso no `PATH`, sem rede): bloqueiam outra conta em pr edit, issue edit, pr create `--label`, `gh api .../labels`, GraphQL `addLabelsToLabelable` e `bash -c` aninhado; bloqueiam conta ilegível (`gh` sai 1) com `bug,Afrouxa-Regra` (vírgula e maiúsculas); liberam a conta do dono (pr edit e api, `Rodrigo-Isensee` vs. slug em minúsculas), outro rótulo, `--remove-label` e corpo que só cita o nome. Cobrem o comportamento novo e as bordas principais.
- **Ferramentas (saída citada, não refeita):** `python3 -m unittest tests.test_hooks -v` nesta worktree: `Ran 20 tests in 89.669s OK` (inclui `test_fixtures`, com as 12). A suíte completa (870 OK) é do autor, na E1.1. `python3 tests/catraca.py --base 976a159`: aponta `R-CONFORMIDADE: mudança em hooks/conformidade.py ... só passa com o rótulo afrouxa-regra do dono` (esperado: o PR muda um hook de controle; o rótulo é do dono, no merge).
- **Regras da fábrica:** `R-CUSTO` (nenhum serviço pago; `gh api user` é a API gratuita, só quando o comando cita o rótulo), `R-NEUTRO` (nenhum nome fixo no código: o dono vem do `plugin.json`; o login só aparece em fixture), invariantes preservadas, fragmento novo em `changelog.d/rotulo-so-dono.md`, sem edição do `CHANGELOG.md` nem da versão. Commits limpos, Conventional Commits em português, um por mudança coerente.
- **Segurança:** o hook é controle; o parecer de segurança é do `security-engineer` (E1.3, `docs/security/rotulo-so-dono.md`), citado aqui e não refeito. As lacunas de leitura de texto abaixo vão para ele.

## Achados

## Detalhe dos achados
1. `docs/adr/0009-conformidade-dos-agentes.md`, seção 6, item 6 (fim) · diz "os outros papéis seguem sem guarda ali" (sessão do Forge com a pasta corrente fora de projeto); com este PR, todo papel passa pela conferência do rótulo `afrouxa-regra` ali · acrescentar uma nota curta da exceção, citando `R-CONTRIB` (sem repetir o texto da regra) · severidade: recomendado. O `.claude/CLAUDE.md` do Forge não descreve o alcance do hook `conformidade` (só cita o sandbox e o `pre-push`), então não precisa de nota.
2. `hooks/conformidade.py`, `aplica_afrouxa_regra` · o pedido (E2) cita `gh label`; o hook não confere `gh label edit <outro> --name afrouxa-regra`, `gh api` em `repos/<r>/labels/<nome>` nem as mutações `updateLabel`/`createLabel`, que renomeiam um rótulo já aplicado para `afrouxa-regra`. Não bloqueia: a catraca só aceita o último evento `labeled` com ator igual ao dono (`tests/catraca.py`, `rotulo_do_dono`), e uma renomeação não gera esse evento, então o portão não se abre por esse caminho. Também não conferido: o rótulo vindo de variável (`L=afrouxa-regra; gh pr edit 70 --add-label "$L"`), limite já declarado do hook que lê texto · levar ao `security-engineer` (E1.3) para decidir se fecha ou documenta como limite · severidade: recomendado.
3. Fonte do dono · o pedido (E2) diz "dono lido da URL do remoto do Forge"; a implementação lê o `repository` do `plugin.json` em vigor, que é a fonte que o hook já usa para o slug do Forge e que o agente não reescreve; a regra no `R-CONTRIB` descreve isso. A catraca usa outra fonte (`dono` de `tests/config.json`), hoje igual (`rodrigo-isensee`). Divergência aceita, mais firme que a URL do remoto · registrar no corpo do PR · severidade: recomendado.
4. `hooks/conformidade.py`, `principal` · erro interno que não seja `ValueError` no caminho novo cai em `executar` e, na sessão do Forge (fora de `sessao_vigiada`), libera; o texto da regra diz "na dúvida ou no erro de leitura, barra". O erro de leitura da conta e do dono barra, então o caso é só o de exceção inesperada do analisador · avaliar com o `security-engineer` se cabe um `except Exception` local que exija o dono quando a linha cita o rótulo · severidade: recomendado.

## Pendências para o merge (não são do review)
- Rótulo `afrouxa-regra` do dono, na conta dele, depois do último push (a catraca exige por `hooks/conformidade.py`).
- Sobreposição com o teto adaptativo em `tests/test_hooks.py` (anotada no pedido): o merge espera o do teto e traz a `develop` antes; se o patch mudar, `forge-check pr` aponta o alcance da revalidação.

## Parecer
Aprovado: faz o que o E1, o E2 e o E3 pedem, sem mudar outra regra; as quatro recomendações acima não impedem o QA.
