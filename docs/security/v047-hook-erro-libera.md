---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-hook-erro-libera
commit: 9e3f57c66510ceff571fd59e3153b145b8d58e6b
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-13
---
# Review de segurança: v047-hook-erro-libera

Pedido v047, etapa E3.17: parecer de segurança da HOOK-ERRO-LIBERA no head `9e3f57c6` (base `c5aa70e1`), contra as condições C1 a C8 do modelo de ameaças da E3.6 (`/root/.forge-contrib/docs/security/v047-v2-ameacas.md`, seção 1). Lido: o diff inteiro de `hooks/`, `docs/` e `changelog.d/`, e `tests/test_hook_erro_libera.py`. Rodados no head: `tests.test_hook_erro_libera` (11 testes, verdes, inclui os 25 fixtures `errointerno-*`, o E3 gerado das 48 entradas da política e o E7) e as sondas abaixo, com erro e prazo forçados pelo mesmo lançador dos testes (`forcar`, `tests/test_hooks.py`). Sem PR, sem CI do head: suíte inteira não rodada (máquina com carga 17 em 12 núcleos).

## Gatilhos
`R-SEGURANCA`: controle do Forge (hooks `conformidade` e `agentes`, `hooks/hooks.json`) e analisador de comando (o marcador da falha fechada).

## Condições C1 a C8
- **C1 cumprida.** Nenhum `.expanduser()` de `Path` em `hooks/*.py`; `expandir_home` (`hooks/_comum.py:94-98`) é a fonte. S1 e S2 da E3.6 agora recusam pela guarda normal (S9, S10). Os `os.path.expanduser` que restam (`conformidade.py:730`, `:2452`, `:2836`; `parecer.py:473`, `:829`) não lançam.
- **C2 cumprida como escrita, com lacunas (A1, A2, A3).** Termos montados do JSON (`conformidade.py:2829-2846`), `~/` nas quatro formas, `*` como trecho sem barra, política ilegível marca tudo (teste `test_politica_ilegivel_ou_sem_caminhos_marca_tudo`). O E3 gerado recusa as 48 entradas. Mas a "linha que escreve" e o termo literal deixam passar escritas que a própria guarda recusa (S1 a S8).
- **C3 cumprida.** `$`, crase e `<(` numa linha que escreve marcam (`conformidade.py:2826`; fixture `errointerno-alvo-opaco-bloqueia`).
- **C4 cumprida.** Write, Edit, MultiEdit e NotebookEdit marcam pelo caminho resolvido dentro da raiz ou casando a política (`conformidade.py:2874-2883`); sondas S11 a S13 confirmam `..`, `//` e `~/.claude.json`; fora da raiz e fora da política libera.
- **C5 cumprida no código, medida pendente.** `prazo_vencido` usa `hook.marcado`, agora do marcador da política (`_comum.py:2709-2719`, `:2785-2799`); E4 verde. A medida exigida no corpo do PR não existe ainda (sem PR); ver A4.
- **C6 cumprida.** As 18 entradas de `hooks/hooks.json` rodam o interpretador com `-s -E` (contagem por script); E7 verde com `usercustomize` e `sitecustomize` que saem com 0.
- **C7 cumprida.** `conferir_brief` (`hooks/agentes.py:796-820`) roda antes de `atualizar_estado` e qualquer exceção nela recusa; o estado que falha não leva o R-BRIEF junto (`:884-907`). Fixtures `errointerno-*` do `agentes` (8) verdes, inclusive `agentes.json` corrompido sem brief. Resíduo: uma exceção em `hook.projeto` (`:888`), antes da conferência, ainda libera; a entrada que a governa (`cwd`) vem do Claude Code, não do agente (informativo).
- **C8 cumprida.** ADR 0003 item 4, ADR 0009 seção 7, `docs/hooks.md` e a docstring de `registrar_erro` (`_comum.py:2672-2673`) dizem o alcance novo no mesmo PR.

## Achados
- A1 (bloqueante) hooks/conformidade.py:2824 · ESCRITORES não tem checkout, restore, apply nem am: `git restore --source=x docs/pedidos/v1.md` e `git checkout origin/x -- docs/pedidos/v1.md`, que a guarda recusa, passam com erro ou prazo vencido (S1, S2, S3).
- A2 (bloqueante) hooks/conformidade.py:2872 · Base trocada some do texto: `cd docs && cp x pedidos/v1.md`, `pushd docs; cp ...` e `git -C docs checkout x -- pedidos/v1.md` não citam o termo da política e passam com erro ou prazo vencido; a guarda normal recusa os três (S4, S5, S6).
- A3 (recomendado) hooks/conformidade.py:2872 · Termo só literal: `cp x docs//pedidos/v1.md`, `cp x ./docs/./pedidos/v1.md` e `cp x docs/"pedidos"/v1.md` passam com erro ou prazo; a guarda normal recusa. Exige ofuscação deliberada (S7, S8).
- A4 (recomendado) hooks/_comum.py:2791 · C5 pede no corpo do PR o número de prazos vencidos que passariam a recusar; o erros.log não guarda o comando, então o número não sai dele. Medido aqui: 846 linhas de prazo do conformidade desde 2026-11-04, 0 com o comando.

## Sondas
- S1 · Bash `git restore --source=x docs/pedidos/v1.md`, tech-lead, prazo forçado em Guarda.bash · espera: rc 2 (a guarda normal dá rc 2) · obtido: rc 0
- S2 · Bash `git restore --source=x docs/pedidos/v1.md`, tech-lead, erro forçado em Guarda.bash · espera: rc 2 · obtido: rc 0
- S3 · Bash `git checkout origin/x -- docs/pedidos/v1.md`, tech-lead, erro e prazo forçados em Guarda.bash · espera: rc 2 (a guarda normal dá rc 2) · obtido: rc 0 nos dois
- S4 · Bash `cd docs && cp x pedidos/v1.md`, tech-lead, erro e prazo forçados em Guarda.bash · espera: rc 2 (a guarda normal dá rc 2) · obtido: rc 0 nos dois
- S5 · Bash `pushd docs; cp x pedidos/v1.md`, tech-lead, erro forçado em Guarda.bash · espera: rc 2 (a guarda normal dá rc 2) · obtido: rc 0
- S6 · Bash `git -C docs checkout x -- pedidos/v1.md`, tech-lead, erro forçado em Guarda.bash · espera: rc 2 (a guarda normal dá rc 2) · obtido: rc 0

## Detalhe dos achados
Sondas sem prova de bloqueante (a guarda normal e o marcador na mesma rodada, `forcar` igual ao dos fixtures): S7 `cp x docs//pedidos/v1.md` e S8 `cp x docs/"pedidos"/v1.md` e `cp x ./docs/./pedidos/v1.md` dão rc 2 sem erro e rc 0 com erro ou prazo forçado (A3). S9 `rm ~zzq docs/briefs/b.md` e S10 `echo a > ~zz/a; echo b > docs/arquitetura/a.md`, sem forçar nada: rc 2 pela guarda (C1). S11 a S13 Write com erro forçado em Guarda.arquivo: `{raiz}/docs//pedidos/../pedidos/v.md`, `{raiz}/../proj/docs/pedidos/v.md` e `~/.claude.json` dão rc 2; `/tmp/zz-fora/x.md` dá rc 0. Legítimos com erro forçado: `git status`, `ls ~zz`, `cat docs/pedidos/v047.md`, `cp x build/y` e o comando de teste da stack dão rc 0. Controle: `git mv a.md docs/pedidos/v1.md` com erro dá rc 2 (o `mv` casa). Fora do escopo desta entrega, `curl -o`, `tar -C`, `unzip -d`, `patch` e curinga (`docs/ped*/`) em `docs/pedidos/` passam também na guarda normal: família A4 a A10 e residual R1 (sandbox) da E3.6, não regressão.

**Caminho de ataque (A1, A2).** Ator do modelo: um agente com pressa que restaura ou copia um arquivo protegido (o pedido, um brief, o desenho) por uma forma comum de shell. O prazo vencido não é raro: o `erros.log` da cópia principal tem 846 linhas de prazo de 3 s do `conformidade` em nove dias, com a máquina carregada. Nesse momento, a escrita que a guarda recusaria passa, que é o efeito H4 que a C5 deveria fechar. Severidade média (H4 do modelo), com caminho realista e sem ofuscação.

**A1, correção mínima (P, `tech-lead`).** Incluir em `ESCRITORES` os subcomandos do git que gravam arquivo, a lista inteira: `CAMINHOS_NO_GIT` (`rm`, `mv`, `checkout`, `restore`, `conformidade.py:303`) e `GIT_GRAVA_ARQUIVO` (`apply`, `am`, `_comum.py:1360`). Mutante a matar: tirar `restore` ou `checkout` da união.

**A2, correção mínima (P, `tech-lead`).** Na linha que escreve, a troca de base conta como alvo opaco (extensão da C3): `cd`, `pushd`, `-C`, `--git-dir`, `--work-tree`, `GIT_DIR` e `GIT_WORK_TREE`. Casos de abuso novos (rc 2 com erro e com prazo forçado): S4, S5 e S6. Legítimo a manter: `cd build && cp x y` só marca (recusa só em erro ou prazo, como `cp x $D`).

**A3, correção sugerida (P, `tech-lead`).** Buscar os termos também numa forma normalizada da linha: sem aspas dentro da palavra e com `//` e `/./` colapsados. Recomendado: exige ofuscação deliberada além de um erro ou prazo.

**A4 (`tech-lead`, corpo do PR).** Declarar no PR o número medido acima e que o log não permite a contagem pedida, ou registrar no `erros.log` um marcador sim/não por linha de prazo (sem o comando) para a próxima medida.

## Risco declarado: configuração corrompida recusa escrita na raiz
Com o `.forge/config.json` do projeto ilegível (`[1,`), toda decisão do `conformidade` cai em erro interno. Pela C4, todo Write, Edit, MultiEdit e NotebookEdit dentro da raiz recusa, também em arquivo comum (fixtures `erro-interno-write-na-raiz-bloqueia`, `erro-interno-write-js-com-push-bloqueia`, `erro-interno-edit-merge-no-conteudo-bloqueia`; sonda: Write e Edit em `src/` dão rc 2). No Bash, recusa a linha que escreve com termo da política ou alvo opaco (`echo x > "$PWD/src/app.js"` dá rc 2), e libera o resto (`cat > src/app.js <<< x` e o comando de teste dão rc 0). O mesmo marcador mais largo vale para `barrar_sem_versao` (`_comum.py:2741-2746`): sessão de projeto que perdeu o `.forge/versao` também recusa Write na raiz. Efeito: o time para de editar o projeto até o dono consertar o arquivo à mão (o agente não grava `.forge/config.json`) ou abrir a guarda com `FORGE_GUARDA_ABERTA=1`. É disponibilidade, não integridade, e só o dono ou um defeito corrompem o arquivo; a mensagem aponta o `erros.log` e o `R-DECISAO`. Falhar fechado aqui segue a ADR 0009, seção 7. Não é risco aceito (o aceite é do usuário, `R-SEGURANCA`); vai declarado ao dono pelo Jarvis.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: só leitura do código, `tests.test_hook_erro_libera` e sondas pelo lançador dos testes (`rodar` com `forcar`). `gitleaks`, `zizmor` e `actionlint` não aplicáveis (nenhum segredo, workflow ou dependência no diff).
