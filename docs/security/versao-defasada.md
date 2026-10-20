---
tipo: revisao-seguranca
contrato: 1
pedido: versao-defasada
branch: melhoria/versao-defasada
commit: ac07db30731623e60de954ae1518bfaabd314af7
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-20
---
# Review de segurança: versão defasada (E2.3, rodada 2)

Rodada 2, revalidação por delta sobre `2b6abdd..ac07db3` (lista de `forge-check delta --parecer` sobre o parecer anterior: `bin/forge-check`, `hooks/parecer.py`, `hooks/doutor.py`, `scripts/jarvis-forge`, `README.md`, `docs/hooks.md`, fragmento, `tests/`). O delta toca controles do Forge (o hook `parecer` e a guarda do `forge-check`), por isso eles foram relidos inteiros, não só as linhas mudadas. Revisão estática e local, em paralelo ao code review. Evidência própria em ac07db3: `python3 -m unittest tests.test_doutor tests.test_forge.FerramentaDefasadaNoForge tests.test_forge.FerramentaDefasadaNoProjeto tests.test_forge.HookParecerGuardaDaVersaoNoProjeto tests.test_forge.HookParecerGuardaDaVersaoNoForge tests.test_hooks`: `Ran 123 tests ... OK`.

## Gatilhos
Controles do Forge em `hooks/`, `bin/` e `scripts/` (R-SEGURANCA): a guarda de versão entra no hook `parecer` (portão de `gh pr create/ready/merge`), muda de bloqueio para aviso no Forge (decisão D do dono) e passa a mostrar a verificação desligada.

## Achados

## Detalhe dos achados
**O que foi conferido (pedido no brief).**
- *Hook `parecer`: só bloqueia com prova positiva e nunca no Forge (decisão D).* `hooks/parecer.py:177` chama `guarda_de_versao` (`:160`), que usa a mesma `avaliar_versao` do `forge-check` (`bin/forge-check:2935`) antes de `pedidos_da_branch`, e só chama `bloquear` com nível `bloqueio`. Esse nível só sai com estado `atrasada` e `not forge` (`bin/forge-check:2957`-`2958`); no Forge e nos clones, `atrasada` vira `aviso` em todos os subcomandos e no hook. Erro de comparação vira `aviso` (`:2955`). Há teste dos dois lados: `HookParecerGuardaDaVersaoNoProjeto` (barra; em dia passa mudo; erro só avisa) e `HookParecerGuardaDaVersaoNoForge` (só avisa). Exceção fora das capturadas faz o hook falhar fechado (ADR 0009, seção 7): pode atrapalhar, não abre o portão.
- *`e_o_forge` não vira Forge num projeto.* `bin/forge-check:2864` devolve falso quando há `.forge/versao` na raiz ou acima dela, antes de ler o manifesto, como `e_clone_do_forge` (`hooks/_comum.py:70`). Escrever `.claude-plugin/plugin.json` com `name: forge` num projeto não troca o bloqueio pelo aviso (`test_manifesto_do_forge_num_projeto_nao_o_torna_o_forge`). Para apagar `.forge/versao`, seria preciso passar pelo hook `conformidade`, que protege `.forge/`; e mesmo assim um projeto sem `.forge/versao` já não tinha cache para provar nada. O caminho contrário (um `.forge/versao` numa pasta acima do clone fazer o Forge bloquear) só deixa a guarda mais rígida e não dá vantagem a ninguém.
- *Verificação desligada aparece e não apaga prova.* Com `FORGE_VERIFICAR_VERSAO=0` no ambiente do `forge-check`, ou com `consulta: desligada` no cache, a saída diz `versão não conferida (verificação desligada)` (`bin/forge-check:2918`, `:2926`, `:2931`). Um `defasado: true` da mesma versão continua bloqueando mesmo com a variável ligada, porque o teste de `desligada` só entra nos ramos sem prova. No doutor (`hooks/doutor.py:109`), a consulta desligada grava `consulta: desligada` e mantém o `defasado: true` e o `ultima` anteriores quando `atual` é o mesmo (`consultar_versao` devolve `atual` também no estado `desligada`, `bin/forge_versoes.py:151`). Um agente que ponha a variável no próprio comando só ganha mais avisos; não perde o bloqueio.
- *rev-list falho vira aviso.* Em `scripts/jarvis-forge:122`, a falha do `rev-list` depois do `fetch` chama `atrasado` (`:105`), que imprime `ATRASADO desde <data>` e marca `avisou_defasagem`; a reanexação não fica muda. O teste está em `test_doutor`.
- *Rede e custo (R-CUSTO).* O delta não acrescenta chamada de rede: o hook e a guarda usam só `git` local e arquivos, e o `jarvis-forge` reaproveita o `fetch` que já existia.
- *Nada atualiza o plugin pelo agente (R-CONFORMIDADE).* As mensagens só pedem o comando à pessoa (`ATUALIZAR_NO_FORGE`, `ATUALIZAR_NO_PROJETO`); nenhum caminho novo grava na cópia vigente nem no plugin instalado.
- *Runner do `test_hooks` (`tests/test_hooks.py:288`).* A exceção só vale com `codigo` esperado 0, com a chave `stderr` na fixture e com o hook `parecer`. Bloqueio sai com código diferente de zero e cai no ramo que confere a linha da regra, então a exceção não esconde bloqueio. As três fixtures de clone esperam `versão não conferida`, o que bate com o clone falso sem `origin/develop`.
- *Texto único (AntiDuplicacao).* O hook, o `docs/hooks.md` e o fragmento citam as regras pelo ID; nenhum trecho de regra aparece entre aspas.

**Status das recomendações da rodada 1.** R1 (verificação desligada sem rastro): resolvida, como descrito acima. R3 (rev-list mudo): resolvida. R2 (`--base homolog` no Forge): perdeu o objeto com a decisão D, porque no Forge a guarda só avisa e não há bloqueio para contornar; o aviso continua seguindo `--base`. Fica como observação, sem cartão.

**R4 (recomendado, informativa).** `tests/test_hooks.py:289` confere o aviso com `assertIn`; nessas três fixtures, outra saída a mais no stderr com código 0 passaria despercebida. Não há caminho de ataque: é perda de precisão do teste, não do controle. Correção mínima: conferir que o stderr tem só a linha do aviso. Esforço P. Dono: `tech-lead`.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática do delta e dos controles que ele toca, `forge-check delta` e a bateria de testes acima. Ausentes no PATH (não instaladas, R-CUSTO): `gitleaks`, `shellcheck`, `semgrep`, `osv-scanner`; o `shellcheck` roda no CI do PR (critério do merge, E2.5). O delta não traz dependência nova nem segredo.
