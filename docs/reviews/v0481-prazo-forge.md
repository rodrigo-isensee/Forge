---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-prazo-forge
commit: a4d1287031926560dc2742f125b5456cccaa149a
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-25
---
# Review: v0481

## Achados
- A1 (bloqueante) hooks/_comum.py:2875 · AR-12: o diff muda as linhas que 7 specs antigas mutam (heredoc-donos D11; v0480-vigia-agentes-pesado M1-M2; v0480-vigia-trava-critica M1-M4), e test_toda_spec_do_forge_confere_com_a_fonte_fora_as_pendentes falha (S2; suíte 4/5 do CI). Alinhe o `de` delas.
- A2 (bloqueante) hooks/conformidade.py:127 · ESCRITA_NO_TEXTO não tem mkfifo nem mknod. Na sessão de projeto, `python3 -c "import os; os.mkfifo('.git/x')"` libera, e o `os.remove('.git/x')` da mesma linha recusa. O pedido diz que o FIFO no .git recusa nas duas sessões (S1). Inclua `mkfifo|mknod` e ponha uma fixture.
- A3 (recomendado) hooks/_comum.py:2884 · Com FIFO no .git, na sessão do Forge, `ls` também recusa (o marcador não foi calculado), mas o texto diz "a chamada com ação crítica" e "um `git` lento". Quando `hook.marcado is None`, cite o .git que não respondeu.

## Sondas
- S1 · sessão de projeto, PreToolUse Bash `python3 -c "import os; os.mkfifo('.git/x')"` no hook real · espera: 2 R-CONFORMIDADE (como `os.remove('.git/x')`, que dá 2) · obtido: 0 (libera)
- S2 · `python3 -m unittest tests.test_forge_mutante -k test_toda_spec_do_forge_confere` no a4d12870 · espera: OK · obtido: FAILED, 7 specs com o `de` fora da fonte (D11, v0480-vigia-agentes-pesado M1-M2, v0480-vigia-trava-critica M1-M4)

## Parecer
Reprovado: há dois bloqueantes, A1 e A2. O núcleo da correção está certo e entra assim que os dois forem resolvidos.

O que conferi com o hook real (`hooks/conformidade.py` em subprocesso, ambiente limpo, corte de 10 s que libera como o Claude Code), lado a lado com a base 5fb8e328:
- Pedi um FIFO no `commondir` e outro no `gitdir` da worktree, nas duas sessões (Forge e projeto), com a raiz na worktree e também na cópia principal. Testei `git push origin feature/x:main`, `git push --force` e `git commit --no-verify`: 28 casos. Na base, os 12 casos da sessão do Forge liberavam pelo corte de 10 s. No head, os 28 recusam: R-CONFORMIDADE em cerca de 3,7 s, ou R-MAIN e R-VERIFY direto quando o git responde. A liberação indevida está fechada.
- Nada que a base barrava deixou de barrar: todos os casos com 2 na base dão 2 no head. O `ls` na sessão de projeto com FIFO segue livre nas duas versões.
- Testei 21 formas de mkfifo e mknod nas duas sessões: `.git/x`, `-m`, `--`, `env`, `command`, `busybox`, `sudo`, `nice`, `timeout`, `find -exec`, `bash -c`, `./.GIT`, `.gi?`, `$(git rev-parse --git-dir)` e `cd .git && mkfifo x`. Todas recusam no head e liberavam na base. O FIFO fora do `.git` (`minha-fila`, `/tmp/...`) segue livre. Duas ficam passando: `echo .git/x | xargs mkfifo`, que tem o mesmo limite antigo de `xargs rm` e `xargs touch` e não é deste diff, e o caminho do interpretador (A2).
- Vigia de 0,5 s sob carga: ele só arma depois que a decisão já passou do prazo de 3 s, ou de 8 s no merge. Na sessão vigiada, recusar já era o resultado. Na do Forge, a linha marcada já recusava pelo `recusa_no_prazo`. Sobra a linha sem marcador na sessão do Forge: ela recusa se `registrar_erro` mais `sessao_vigiada` passarem de 0,5 s. No Forge, `registrar_erro` volta antes do git, porque a raiz não é de projeto, e `recusa_no_prazo` só faz stat. Medi a mediana em 0,35 ms e o pior caso em 0,79 ms (50 voltas, loadavg 9,3 em 12 núcleos). A folga é de cerca de 600 vezes, e quando falha, falha fechado (ADR 0009, seção 7). Não abro achado. O total fica em 8 + 0,5 s, abaixo dos 10 s do hooks.json.
- O `except (PrazoVencido, Exception)` mantém o `recusa` calculado antes, então a sessão que não se decide recusa. O alarme é de disparo único, e o `finally` restaura o sinal mesmo quando o vigia vence no meio do desarme.

Verificadores que rodei no Revisar-sha:
- `PrazoVencidoNaSessaoDoForge`, `SondaS1ComRelogioFalso` e `VigiaAgentesPesado`: 9 testes, OK.
- `bin/forge-mutante --processos 1 tests/mutantes/v0481-prazo-forge.json`: M1 a M8 morreram.
- `--cobertura --base 5fb8e328`: todas as guardas do diff estão cobertas.
- `--conferir --todas` (rc 1, 33 linhas, contra 26 na base): as 7 linhas novas são as do A1.

Mais pontos:
- CI do #888: `catraca` vermelha, à espera do rótulo do dono (mudança em hooks); `bateria (pareceres)` vermelha, à espera dos pareceres; suíte 4/5 vermelha nas duas versões de Python, o que bate com o A1.
- Tamanho H1: cerca de 34 linhas de código, dentro do teto.
- O A1 é a 6.a ocorrência do AR-12. A linha de `docs/engineering/achados-recorrentes.md` fica para o commit do autor, porque este envio leva só o parecer (brief).
