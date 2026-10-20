---
tipo: revisao-seguranca
contrato: 1
pedido: versao-defasada
branch: melhoria/versao-defasada
commit: 2b6abddd698eb0385e8d7ac08021ba5e9152f309
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-20
---
# Review de segurança: versão defasada (E2.3)

Rodada 1, sobre `8833e1c..2b6abdd` (`bin/forge-check`, `bin/forge_versoes.py`, `hooks/doutor.py`, `scripts/jarvis-forge`, docs e testes). Revisão estática e local; em paralelo ao code review da E2.2, sem refazê-lo. Evidência própria: `python3 -m unittest tests.test_doutor tests.test_forge.FerramentaDefasadaNoForge tests.test_forge.FerramentaDefasadaNoProjeto` em 2b6abdd: `Ran 80 tests ... OK`.

## Gatilhos
Controles do Forge em `hooks/`, `bin/` e `scripts/` (R-SEGURANCA): uma guarda nova que bloqueia subcomandos do `forge-check`, o cache do doutor lido como prova e um `fetch` novo do `jarvis-forge`.

## Achados

## Detalhe dos achados
**O que foi conferido (pedido no brief da E2.3).**
- *Só bloqueia com prova positiva.* No Forge e nos clones, `bin/forge-check:2879` só devolve `atrasada` quando o objeto da base não existe na cópia (`:2894`) ou o `merge-base --is-ancestor` devolve 1; código diferente de 0 e de 1 vira `erro`. A cópia vigente é um clone completo (`scripts/jarvis-forge:50`, sem `--depth` nem `--filter`), então faltar o objeto quer dizer que a cópia não buscou depois dele: prova, não suposição. Nos projetos (`bin/forge-check:2902`), só bloqueia com `defasado: true`, `atual` igual à versão desta cópia e menor que `ultima`; cache de outra versão não prova nada (`:2925`).
- *Erro de comparação não vira verde silencioso.* Toda falha de leitura, de git, de tempo (`subprocess.TimeoutExpired` é `SubprocessError`) ou de formato vira `versão não conferida` no stderr e a conferência segue (`bin/forge-check:2929`); exceção não prevista sai com rc diferente de zero, não com verde. Os únicos `ok` mudos são os sem prova: pasta sem `.forge/versao`, projeto sem cache (o resíduo já registrado no Histórico) e `defasado` diferente de `true` (ver R1).
- *Desligar por variável ou arquivo do projeto.* O `git` do `forge-check` roda sem as `GIT_*` herdadas (`bin/forge-check:324`), então o agente não redireciona a comparação pelo ambiente do próprio comando. O cache fica em `.forge/`, pasta que o hook `conformidade` não deixa agente gravar nem apagar (`hooks/conformidade.py:107`, `:551`). A única chave que desliga é a da pessoa, no ambiente da sessão (R1).
- *Nenhum caminho atualiza o plugin pelo agente (R-CONFORMIDADE).* A guarda só lê; o doutor só grava o cache; no `jarvis-forge`, com a sessão aberta, `avisar_na_sessao_aberta` (`scripts/jarvis-forge:113`) faz só `fetch` das refs remotas da cópia vigente, sem tocar a árvore; o fast-forward que já existia continua só na abertura feita pela pessoa. Toda mensagem manda a pessoa rodar o comando.
- *Rede e custo (R-CUSTO).* A guarda não usa rede (só `git` local e arquivos). Há dois pontos novos de chamada, ambos à mesma origem já consultada e sem custo: o `fetch` na reanexação (`scripts/jarvis-forge:117`, 30 s no máximo), exigido pela VD-1 escolhida pelo dono; e a nova tentativa do `git ls-remote` do doutor depois de 10 min quando a consulta falhou (`hooks/doutor.py:26`, `:88`), em vez de uma por dia. Nenhum destino novo, nenhum serviço pago.
- *Cache tratado como dado.* O `forge-check` só usa `atual` e `ultima` depois do `re.fullmatch` de versão (`bin/forge-check:2919`-`2925`) e imprime a própria versão e o próprio commit, nunca texto do cache. O doutor continua imprimindo `texto` só em `systemMessage` ao usuário (ADR 0003), e esse texto nasce de tags filtradas pelo mesmo `fullmatch` (`bin/forge_versoes.py:24`). No `jarvis-forge`, a data vem de `git log --format=%cs` da própria cópia; nada é avaliado pelo shell.
- *Texto único.* As regras são citadas por ID no código, no `docs/hooks.md` e no fragmento.

**Concordância com o A1 do code review (não duplicado aqui).** `hooks/parecer.py:171` chama `cmd_pr` sem passar por `executar` (`bin/forge-check:3036`), então o portão do `gh pr create/ready/merge` não tem a guarda. Do lado da segurança, a correção do A1 deve manter as mesmas propriedades conferidas acima: bloquear só com prova positiva, erro vira aviso e não bloqueio, sem rede. Como ela muda `hooks/`, o commit novo pede nova rodada desta revisão (ADR 0004). Dono: `tech-lead` (implementação).

**R1 (recomendado, baixa).** `FORGE_VERIFICAR_VERSAO=0` (ou endereço do Forge inválido) faz o doutor gravar `defasado: false` no dia (`hooks/doutor.py:107`, estado `desligada` de `bin/forge_versoes.py`), e a guarda dos projetos fica muda, inclusive sobre uma prova de atraso do dia anterior. Caminho: só a pessoa define essa variável no ambiente da sessão (agente não a propaga ao hook nem grava `.claude/`); não é ataque, é um desligamento sem rastro na saída do `forge-check`. Correção mínima: gravar o estado no cache (por exemplo `consulta: desligada`) e o `forge-check` dizer `versão não conferida (consulta desligada)`; não sobrescrever um `defasado: true` anterior da mesma versão com `false` vindo de consulta desligada. Esforço P. Dono: `tech-lead`.

**R2 (recomendado, baixa).** No Forge, a base comparada segue `--base` do subcomando (`bin/forge-check:2875`): `forge-check pr --base homolog` (ou `main`) compara com uma ref mais antiga e passa com uma cópia atrás da `origin/develop`. Caminho: o agente escolhe o argumento; fica rastro na linha de comando, e PR para `homolog` é promoção legítima. Correção mínima: no Forge, exigir também a `origin/develop` no histórico da cópia, qualquer que seja a base. Esforço P. Dono: `tech-lead`.

**R3 (recomendado, informativa).** `scripts/jarvis-forge:122`: se o `rev-list` falhar depois de um `fetch` bem-sucedido, o `2>/dev/null` deixa a reanexação muda. Improvável (a ref acabou de ser gravada); correção mínima: tratar a falha do `rev-list` como `ATRASADO desde <data>`. Esforço P. Dono: `tech-lead`.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática do diff e a bateria de testes acima. Ausentes no PATH (não instaladas, R-CUSTO): `gitleaks`, `shellcheck`, `semgrep`, `osv-scanner`; o `shellcheck` roda no CI do PR (critério do merge, E2.5). Sem dependência nova nem segredo no diff.
