---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-perfil-fifo
commit: 517f80fd166ae8230ef6dd5af7991324975ead0e
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-25
---
# Review de segurança: v0481 (E7.22, #886, volta por delta de 8dfe968f a 517f80fd)

Gatilhos: hook de bloqueio (`hooks/_comum.py`, `diretorio_comum`; `hooks/conformidade.py`, `Guarda.barrar`), R-MAIN, R-VERIFY.

## Resumo
- Delta lido (`forge-check parecer delta`, intervalo `8dfe968f..f155a1ba`; os commits depois do 517f80fd só tocam `docs/reviews/` e `docs/qa/`): no domínio, `hooks/_comum.py` (`ler_marca_do_git` em `:153-162`, usada por `diretorio_comum` em `:177-180`) e `tests/test_hooks.py` (sai o `skipUnless` da classe `RecusaComFifoNoPerfil`; testes `test_fifo_no_ponto_git_da_worktree_nao_espera` e `test_fifo_com_conteudo_no_gitdir_nao_vale`); fora, o fragmento do changelog e `tests/mutantes/v0481-perfil-fifo-2.json` (M8, M9). Já lido na rodada anterior (E7.18, no git): `perfil_iniciante`, `barrar` e o resto do #886.
- **Só aperta ou neutro, por escrito: aperta** em `diretorio_comum` (FIFO, link para `/dev/zero` ou FIFO com o conteúdo certo no `.git`, no `gitdir` ou no `commondir` da worktree davam espera sem fim; agora `None` na hora, S3) e, por ele, na decisão do hook: na sessão do Forge, os 9 casos de raiz em worktree com FIFO nessas marcas, que liberavam pelo corte de 10 s na base e no 8dfe968f, recusam em < 0,25 s com R-CONFORMIDADE (S1); no projeto, os de `gitdir` e `.git` recusam com a regra certa em < 0,25 s (antes ~3,1 s). **Neutro** no resto: arquivo regular, link para arquivo regular, pasta, arquivo de 5000 bytes e byte fora de UTF-8 dão o mesmo resultado na base e no head (S3); nenhuma recusa da base vira liberação no head nas 108 combinações de S1 e nas 54 de S2.
- `None` de `diretorio_comum` falha fechado: `projeto_marcado` (`_comum.py:218-223`) trata a raiz como marcada e o hook recusa "o .git da raiz da sessão não se resolve". O corte em 4096 bytes só pode transformar um conteúdo inválido no caminho real que o próprio arquivo já aponta (sem ganho para quem escreve). Sem `O_NOFOLLOW`, como a base (`read_text` seguia link): o `.git` em link já sai antes por `is_symlink` (`:172`) e o link para não regular é recusado por `S_ISREG`.
- Catraca do CI: pulos de volta a 38 (base 38, 8dfe968f 39, 517f80fd 38, contados com `forca_dos_testes` da própria catraca) e asserções de 17169 para 17183; a catraca do f155a1ba já não acusa o `skipUnless` e falha só pelo rótulo do dono para `hooks/_comum.py` e `hooks/conformidade.py` (ADR 0008), o que não é achado de segurança.
- Testes: `python3 -m unittest tests.test_hooks.RecusaComFifoNoPerfil` → 7 testes, OK. Suíte inteira só no CI do PR #886 (run do f155a1ba): partes 2, 3 e 5 verdes; a parte 4/5 falha nas duas versões em `test_forge_mutante.ConferirTodas` pela spec `v0475-mp1-mp7.json: M3` (A2); `bateria (pareceres)` falhava por este parecer desatualizado. O merge depende de tudo verde.

## Achados
- A2 (recomendado) hooks/_comum.py:158 · o `if not stat.S_ISREG(os.fstat(fd).st_mode):` novo repete o `de` da M3 de tests/mutantes/v0475-mp1-mp7.json (guarda do leitor de ATIVOS, :123): o trecho aparece 2 vezes, a M3 não aplica e a parte 4/5 do CI falha. Alinhar o `de` da M3 com a linha seguinte.

## Sondas
- S1 · sonda_perfil_fifo.py, três commits, Forge e projeto, FIFO no perfil, gitdir, commondir e .git da worktree raiz, push na main, --force, --no-verify · espera: recusa sem esperar · obtido: no head as 108 recusam; Forge com FIFO nas marcas do git codigo=2 em < 0,25 s (base: libera em 10 s)
- S2 · sonda_cwd_wt.py, raiz na principal e pasta corrente na worktree, FIFO no gitdir ou commondir, três comandos, três commits · espera: nada que recusa passa a liberar · obtido: gitdir recusa com a regra em < 0,4 s; commondir na sessão do Forge libera push na main e --force em 3,1 s (base: 10 s)
- S3 · sonda_e722.py, diretorio_comum da base e do head com .git, gitdir e commondir trocados por FIFO vazio, FIFO com conteúdo, link para /dev/zero, link regular, pasta, 5000 bytes e não UTF-8 · espera: igual à base ou None no lugar da espera · obtido: 8 esperas viram None; os outros 16 casos iguais
- S4 · bin/forge-mutante --conferir --todas no 517f80fd · espera: nenhuma spec fora da fonte · obtido: tests/mutantes/v0475-mp1-mp7.json: M3, o trecho aparece 2 vezes em hooks/_comum.py

## Detalhe dos achados
**A1 (rodada E7.18): fechado.** `ler_marca_do_git` (`hooks/_comum.py:153`) abre com `O_NONBLOCK`, aceita só `S_ISREG` e lê até 4096 bytes; `diretorio_comum` a usa nas três marcas (`:177-180`). Prova: S1, S2 (gitdir) e S3; testes `test_fifo_no_ponto_git_da_worktree_nao_espera` e `test_fifo_com_conteudo_no_gitdir_nao_vale`, com os mutantes M8 e M9.

**A2.** Evidência: `hooks/_comum.py:158` repete literalmente `hooks/_comum.py:123`, que é o `de` da M3 de `tests/mutantes/v0475-mp1-mp7.json` (MP1, "só arquivo regular é lido", segurança A1 do v0475); `forge-mutante --conferir --todas` acusa o trecho duas vezes (S4) e o CI do f155a1ba falha na parte 4/5 nas duas versões. Caminho: nenhum de ataque; a guarda de mutação do leitor de ATIVOS fica sem prova enquanto a spec não for realinhada, e o CI barra o merge. Severidade baixa. Correção mínima: na M3, `de` = `        if not stat.S_ISREG(os.fstat(fd).st_mode):\n            return None` e `para` = `        if False:\n            return None` (o par é único em `_comum.py`; os testes da M3 seguem os mesmos); conferir com `bin/forge-mutante --conferir --todas` e `bin/forge-mutante tests/mutantes/v0475-mp1-mp7.json --ids M3`. Esforço P. Dono: o autor do #886. A spec fica fora do domínio desta revisão, por isso `recomendado`; volta e é corrigido antes do merge.

**Fora do delta (item próprio aberto na E7.18): reduzido, não fechado.** Com a pasta corrente numa worktree e FIFO no `commondir`, a sessão do Forge ainda libera push na main e `--force` em ~3,1 s (S2), agora pelo `git` do hook, que também lê o `commondir`, e não mais por `diretorio_comum`; o `--no-verify` passa a recusar. Seguem valendo as partes (2) e (3) da correção proposta na E7.18 (recusar `mkfifo`/`mknod` sob `.git/` também na sessão do Forge; o prazo vencido na sessão do Forge recusar a linha que toca uma trava). Item próprio na `develop`, sem esperar o #886.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática, `forge-check parecer delta`, a classe `RecusaComFifoNoPerfil`, `forge-mutante --conferir --todas`, a contagem da catraca e as sondas S1 a S3 (scripts no scratchpad da sessão, `git archive` dos três commits, hook rodado como em produção com `python3 -s -E`, vigia de 3 s e corte de 10 s como o Claude Code; só repositórios temporários, nada externo). Varredor de segredos, SAST e auditor de dependências: o delta não traz dependência nem segredo.
