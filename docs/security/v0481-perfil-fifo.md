---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-perfil-fifo
commit: 8dfe968f7cfc0c8240a62136b6af02a49bc6d3df
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-25
---
# Review de segurança: v0481 (E7.18, #886, perfil sem FIFO nem git no texto da recusa)

Gatilhos: hook de bloqueio (`hooks/conformidade.py`, `Guarda.barrar`), R-MAIN, R-VERIFY.

## Resumo
- Delta lido: `5fb8e328..8dfe968f`, `hooks/conformidade.py` (+35: `perfil_iniciante` em `:1510-1529`, `barrar` em `:1568-1577`), teste `RecusaComFifoNoPerfil`, fixture `trava-prazo-no-perfil-bloqueia-iniciante`, mutantes, índice e changelog.
- Fecha o A2 do parecer da segurança no #885: com FIFO em `.forge/perfil` (na raiz, link para FIFO, na worktree e na cópia principal), push na main, `--force` e `--no-verify` recusam nas duas sessões com a regra certa em menos de 0,7 s; na base, a sessão do Forge liberava os dois primeiros em ~3,1 s e o projeto recusava pelo prazo, com R-CONFORMIDADE (S1, S2).
- **Só aperta ou neutro, por escrito: aperta** no texto da recusa (liberação da sessão do Forge fechada; no projeto, a regra certa em vez do prazo) e **neutro** no resto: nas 72 combinações das sondas (2 commits x 2 sessões x 6 lugares do FIFO x 3 comandos) e nas 36 da pasta corrente em worktree, nenhuma recusa da base vira liberação no head. A única diferença para pior é de tempo, não de decisão: A1.
- `except PrazoVencido` só envolve a escolha do texto (`:1572-1575`) e cai em `com_trecho`; `bloquear` desarma o vigia antes de imprimir. Não engole prazo de outro passo: o `barrar` só é chamado com a recusa decidida e sai por `sys.exit(2)`.
- `Hook.iniciante` no `perguntar` (`:1582`) e na guarda de escrita do perfil (`:1740`): **não precisa entrar neste item** (S5, S6). No projeto, o agente não troca o perfil iniciante por FIFO (recusa R-CONFORMIDADE); com o FIFO já lá (perfil não iniciante), os dois esperam 3 s e recusam pelo prazo, mais estrito que o experiente. Na sessão do Forge, o `perguntar` não roda e a escrita do perfil libera em 3,1 s, como liberaria sem FIFO. Unificar os leitores (o `iniciante` passar a usar `perfil_iniciante`) fica como cartão de coerência, sem achado.
- Testes: `python3 -m unittest tests.test_hooks.RecusaComFifoNoPerfil` → 5 testes, OK. Suíte inteira: só no CI do PR #886; ao escrever, as partes da suíte estão pendentes e `catraca` e `bateria (pareceres)` falham (a catraca acusa o `skipUnless` novo, a mudança em `hooks/conformidade.py` e a falta dos pareceres; não é achado de segurança): o merge depende de tudo verde.

## Achados
- A1 (recomendado) hooks/conformidade.py:1515 · perfil_iniciante chama diretorio_comum, que lê .git, gitdir e commondir com read_text (_comum.py:165-168), sem O_NONBLOCK: FIFO ali faz a recusa esperar 3 s (base: 0,27 s); a regra certa segue. Ler os três sem esperar, como o perfil (S3).

## Sondas
- S1 · base 5fb8e328, sessão do Forge, FIFO em .forge/perfil (raiz, link para FIFO, worktree e principal), `git push origin feature/x:main`, `git push --force origin feature/x` · espera: recusa R-MAIN, R-VERIFY · obtido: codigo=0 em ~3,1 s nos três lugares
- S2 · head 8dfe968f, o mesmo de S1 mais `git commit --no-verify -m x`, sessões do Forge e do projeto · espera: recusa com a regra dela, sem esperar · obtido: codigo=2 em < 0,7 s, R-MAIN, R-VERIFY, R-VERIFY nas 18 combinações
- S3 · head 8dfe968f, projeto, raiz numa worktree com FIFO no gitdir de volta ou no arquivo .git, push na main e --force · espera: recusa sem esperar · obtido: codigo=2 com R-MAIN e R-VERIFY em ~3,1 s (base: 0,27 s)
- S4 · head 8dfe968f, sessão do Forge, `mkfifo` e `os.replace` no gitdir e no commondir de .git/worktrees/<n>/ · espera: recusa (caminho .git/ protegido) · obtido: codigo=0 nos dois papéis; no projeto, codigo=2 R-CONFORMIDADE
- S5 · head 8dfe968f, projeto com perfil iniciante, `rm .forge/perfil; mkfifo .forge/perfil` e `mv` + `mkfifo` · espera: recusa · obtido: codigo=2 R-CONFORMIDADE (texto do perfil) nos dois
- S6 · head 8dfe968f, FIFO no perfil, `git reset --hard HEAD`, `git clean -fd` e Write em .forge/perfil · espera: nada que a base recusa passa a liberar · obtido: projeto codigo=2 pelo prazo em 3,1 s; Forge codigo=0, igual sem FIFO

## Detalhe dos achados
**A1.** Evidência: `hooks/conformidade.py:1515` chama `diretorio_comum` (`hooks/_comum.py:153`), que lê o arquivo `.git` da worktree (`:165`), o `gitdir` de volta (`:167`) e o `commondir` (`:168`) com `read_text`, que bloqueia num FIFO. A docstring de `perfil_iniciante` promete "sem esperar". Caminho: na sessão do projeto o hook recusa `mkfifo` em `.git` e em `.git/` (S4), então o estado não é criável pelo agente; com ele lá, o alarme de 3 s vence na escolha do texto, o `except PrazoVencido` segura e a recusa sai com a regra certa (S3). Sem caminho de ataque realista: recomendação. Severidade baixa (atraso de 3 s, decisão mantida). Correção mínima: em `diretorio_comum`, as três leituras por um leitor que abre com `O_RDONLY | O_NONBLOCK | O_NOFOLLOW`, aceita só `S_ISREG` e lê até 4096 bytes, levantando `OSError` no resto (o `except (OSError, ValueError)` de `:169` já devolve `None`). Conferido numa cópia com essa troca: os casos de S2 e S3 recusam com a regra certa em < 0,3 s (o `commondir` no projeto segue recusando pelo prazo em ~8 s, igual na base: o `git` do hook também o lê), e nos três casos de raiz em worktree da sessão do Forge (FIFO no `.git`, no `gitdir` e no `commondir`), que hoje liberam pelo timeout de 10 s na base e no head, passa a recusar com R-CONFORMIDADE ("o .git da raiz da sessão não se resolve"); só aperta. Teste: na `RecusaComFifoNoPerfil`, worktree com FIFO no `gitdir` de volta e no `.git`, `perfil_iniciante` sob `sem_travar`. Esforço P. Dono: o autor do #886.

**Fora do delta (item próprio, alta; igual na base 5fb8e328 e no head).** Na sessão do Forge (raiz na cópia principal, pasta corrente numa worktree, o caso das cópias em `~/.forge-contrib/wt/`), o agente cria um FIFO em `.git/worktrees/<n>/commondir` ou `gitdir` (S4: o hook deixa) e, na chamada seguinte, push na main, `--force` e `--no-verify` liberam: o hook trava em `diretorio_comum` (`_comum.py:167-168`, via `identificar_sessao` → `raiz_do_projeto` → `marca_de_projeto`), o prazo vence, e `prazo_vencido` trava de novo em `registrar_erro` → `raiz_do_projeto` sem alarme até o timeout de 10 s do Claude Code (rastro com `faulthandler`; 15 combinações por commit, codigo=0 em ~10 s na base e no head; no projeto, recusa pelo prazo, com R-CONFORMIDADE). A correção do A1 fecha o `gitdir`; o `commondir` com a pasta corrente na worktree segue liberando em ~3,1 s, porque o `git` do hook também lê o `commondir` e, na sessão do Forge, o prazo vencido libera. Correção mínima proposta: (1) a do A1; (2) o hook recusar `mkfifo`, `mknod` e `os.mkfifo` sob `.git/` também na sessão do Forge (a proteção de `.git/` em `hooks/conformidade.json:39-43` só vale no projeto); (3) em `prazo_vencido`, na sessão do Forge, recusar pela regra do hook a linha que `toca_uma_trava`, como VIGIA-PRAZO-TRAVA já faz na sessão vigiada. Só aperta. A proteção de branch do GitHub segue barrando a main remota; o `--force` em `melhoria/*` e o `--no-verify` locais ficam abertos. Não entra neste item porque o delta não o cria nem o piora; abrir como item próprio na `develop`, sem esperar o #886.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática, a classe `RecusaComFifoNoPerfil` e seis sondas (scripts em `$TMPDIR` da sessão, `git archive` dos commits, hook rodado como em produção com `python3 -s -E`, vigia de 3 s e corte em 10 s como o Claude Code; só repositórios temporários, nada externo). Varredor de segredos, SAST e auditor de dependências: o delta não traz dependência nem segredo.
