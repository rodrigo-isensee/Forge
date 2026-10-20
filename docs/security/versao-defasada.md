---
tipo: revisao-seguranca
contrato: 1
pedido: versao-defasada
branch: melhoria/versao-defasada
commit: 4c078a96a811e88d4e1d8bc35b12a6b031283d9c
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-20
---
# Review de segurança: versão defasada (E2.3, rodada 3)

Rodada 3: revalidação por delta sobre a volta 3 do autor, `136c4cb..4c078a9`. A lista de `forge-check delta --parecer` sobre o parecer anterior (`ac07db3..4c078a9`) traz só os arquivos da volta 3 (o comando deixa de fora docs/reviews e docs/security): `hooks/parecer.py`, `docs/hooks.md`, as 3 fixtures de clone do `parecer`, `tests/test_forge.py` e `tests/test_hooks.py`. O delta toca um controle do Forge (o hook `parecer`), por isso a guarda e a sua ligação foram relidas inteiras (`hooks/parecer.py:160`-`186`, `bin/forge-check:2907`-`2970`, `hooks/_comum.py:735`-`753`). Revisão estática e local, em paralelo ao code review.

Evidência própria em 4c078a9: `python3 -m unittest tests.test_forge.FerramentaDefasadaNoForge tests.test_forge.FerramentaDefasadaNoProjeto tests.test_forge.HookParecerGuardaDaVersaoNoProjeto tests.test_forge.HookParecerGuardaDaVersaoNoForge tests.test_hooks`: `Ran 54 tests ... OK`. Mutante (cópia em `$TMPDIR` por `git archive`, sem tocar a worktree): com a chamada `guarda_de_versao(fc, raiz)` de `hooks/parecer.py:175` trocada por `pass`, `test_projeto_com_copia_atrasada_barra_o_pr_de_ponta_a_ponta` falha (`AssertionError: 0 != 2`).

## Gatilhos
Controles do Forge em `hooks/` (R-SEGURANCA): o hook `parecer`, portão de `gh pr create/ready/merge`, deixa de escrever o aviso de versão com código 0.

## Achados

## Detalhe dos achados
**O que foi conferido (pedido no brief).**
- *Projeto com prova positiva de atraso continua barrado; Forge nunca (decisão D); sem saída com código 0 (ADR 0003).* `guarda_de_versao` (`hooks/parecer.py:160`) só chama `bloquear("R-CONFORMIDADE", ...)` com nível `bloqueio`, e não devolve nem imprime nada nos outros casos. O nível `bloqueio` só sai de `avaliar_versao` com estado `atrasada` e `not forge` (`bin/forge-check:2957`-`2958`); no Forge e nos clones, o atraso vira `aviso`, que o hook agora descarta. O `print(..., file=sys.stderr)` saiu de `verificar` e o `import sys` também; não sobrou outra escrita no stderr no caminho liberado. O runner (`tests/test_hooks.py:288`) volta a exigir stderr vazio em todo código 0, sem exceção para o `parecer`, e as 3 fixtures de clone voltaram a esperar silêncio: o R4 da rodada 2 (o `assertIn`) deixa de existir. No Forge, o aviso continua chegando pelo `forge-check` (`guarda_de_versao`, `bin/forge-check:2962`) e pelo `forge-fechar`, que roda o `forge-check pr`.
- *A remoção do aviso não abre caminho para liberar com erro escondido.* O estado `erro` só nasce onde não há prova de atraso: cache ilegível, cache sem versões ou exceção de `OSError`, `SubprocessError` ou `ValueError` (`bin/forge-check:2950`, `:2923`, `:2928`). Um `defasado: true` válido para esta versão nunca vira `erro`. Liberar no erro é o que o dono decidiu (só avisa) e o aviso segue no `forge-check pr`. Antes, era um stderr com código 0, que o Jarvis não lê como bloqueio. Exceção fora das três capturadas não é engolida: sobe até `executar` (`hooks/_comum.py:750`), que falha fechado na ação crítica (ADR 0009, seção 7). Para fabricar um `erro` estragando o cache, um agente teria de escrever em `.forge/`, e o hook `conformidade` protege esse caminho (`hooks/conformidade.py:30`). Isso não muda com este delta.
- *O teste de ponta a ponta prende a ligação da guarda.* `test_projeto_com_copia_atrasada_barra_o_pr_de_ponta_a_ponta` (`tests/test_hooks.py:318`) roda o hook de verdade, por subprocesso, sobre a fixture `pr-com-pareceres-aprovados` num projeto com `.forge/versao`, com o cache `.forge/run/versao-nova` dizendo `defasado` para a versão do `plugin.json` da cópia em teste. Espera código 2 e uma linha `R-CONFORMIDADE: forge-check...`, e o mesmo caso sem atraso libera mudo. Como review e QA estão aprovados, só a guarda pode dar o código 2. O mutante acima mostra que o teste falha se a chamada sair de `verificar`.
- *Rede e custo (R-CUSTO).* O delta não acrescenta chamada de rede: tira código do hook e acrescenta um teste que só grava arquivos locais.
- *Nada atualiza o plugin pelo agente (R-CONFORMIDADE).* O delta não cria caminho de escrita na cópia vigente nem no plugin instalado; a mensagem de bloqueio continua pedindo o comando à pessoa.
- *Texto único (AntiDuplicacao).* A docstring do hook e o `docs/hooks.md:19` citam as regras pelo ID (`R-CONFORMIDADE`) e a ADR pelo número; nenhum trecho de regra aparece entre aspas.

**Status das recomendações anteriores.** R1 e R3 (rodada 1): continuam resolvidas, o delta não as toca. R2 (rodada 1): sem objeto pela decisão D. R4 (rodada 2, `assertIn` no stderr): resolvida, porque o stderr com código 0 volta a ser conferido como vazio.

**Observação (sem achado).** Num projeto, erro de comparação agora passa pelo hook sem nenhum rastro na hora do `gh pr create`; o rastro fica na saída do `forge-check pr`, que o fluxo roda antes do PR. Isso segue a ADR 0003 e a decisão do dono (erro só avisa). Não há caminho de ataque: quem ganharia com o silêncio precisaria de um cache ilegível, e o `.forge/` é protegido.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática do delta e dos controles que ele toca, `forge-check delta --parecer`, a bateria de testes acima e um mutante local. Ausentes no PATH (não instaladas, R-CUSTO): `gitleaks`, `shellcheck`, `semgrep`, `osv-scanner`; o `shellcheck` roda no CI do PR (critério do merge, E2.5). O delta não traz dependência nova nem segredo, e não mexe em shell.
