---
tipo: revisao-seguranca
contrato: 1
pedido: lote-leitura-hook
branch: melhoria/lote-leitura-hook
commit: 8c4b7b510c1f2e6f25325e35417b38fbe4a03937
parecer: reprovado
revisor: forge:security-engineer
data: 2026-10-21
---
# Review de segurança: lote-leitura-hook

Escopo: `git diff ad6d96ce6b19663f7695d361d61f59c7545bdca6 8c4b7b510c1f2e6f25325e35417b38fbe4a03937` (C1 6b74a45, C2 f34a329, C3 bb77a84, C4 8c4b7b5: `hooks/_comum.py`, `hooks/conformidade.py`, `hooks/parecer.py`, `tests/test_hooks.py`, `tests/config.json`, `docs/hooks.md`, 32 fixtures novas e 3 alteradas), contra o modelo de ameaças `docs/security/ameacas/lote-leitura-hook.md` (controles por cartão, casos de abuso e a lista da seção 6).

## Gatilhos
`R-SEGURANCA`, gatilho controles do Forge: a entrega muda a leitura da linha nos hooks `conformidade` e `parecer`, que garantem R-MAIN, R-VERIFY, R-CONTRIB, R-CONFORMIDADE e R-REVIEW/R-QA, e acrescenta ao T5 um teste que roda o bash de verdade.

## Achados
- A1 (bloqueante) hooks/conformidade.py:709 · o corpo de cada crase é conferido em cada pasta vista e de novo pela palavra (:832): 60 cd e 60 crases aninhadas dão 37 630 chamadas e 10,9 s, acima do timeout de 10 s (hooks/hooks.json:27); a base recusa a mesma linha com --no-verify em 0,34 s

## Detalhe dos achados
**A1 (média; regressão).** Evidência: o laço novo de `hooks/conformidade.py:709-711` chama `self.bash(corpo, p, nivel + 1)` para cada corpo de crase e cada pasta de `vistas`, e `hooks/conformidade.py:832` relê a mesma palavra com crase pelo `bash()`; a cada nível o corpo volta pelos dois caminhos, e no fundo cada um cai em `ilegivel` (`:776`), que consulta o disco (`repositorio_do_forge`). Sonda em cópia (`git archive` em `$TMPDIR`, hook real pela `Fixture` da própria cópia, sessão de projeto): uma linha de cerca de 2,7 KB, 60 `cd dN &&`, 60 palavras `` `echo \`echo \\\`ls\\\`\`` `` e por último `` `git push --no-verify origin feature/x` ``, leva 10,89 s no HEAD (o perfil conta 37 630 chamadas a `bash()`) e 0,34 s na base, que a recusa pela rede da ADR 0011 (crase com marcador crítico). Com `` `git push origin main` `` no lugar: 11,35 s contra 0,42 s. O tempo cresce com crases × pastas (20 × 200 já dá 9,9 s), e o tamanho da linha não tem teto.
Caminho de ataque: a sessão, por erro ou por instrução injetada em texto não confiável, monta a linha; o Claude Code mata o hook no timeout e o comando segue (premissa registrada em `hooks/conformidade.py:115`). O que a base segurava contra construção deliberada (ação com marcador crítico dentro de crase) passa: `--no-verify` pula também o `pre-push`, e `rm .githooks`, `core.hooksPath` e `forge sugerir` não têm outra camada local; para a main sobra a proteção do servidor. É afrouxamento de controle, que o dono vedou (decisão de 2026-10-15 no pedido).
Correção mínima: em `Guarda.bash`, não conferir duas vezes o mesmo `(corpo, pasta, nivel, so_substituicoes)` (memória por linha) e um teto de chamadas por linha que, ao estourar, recusa a linha (fecha na dúvida, como `PROFUNDIDADE`), mais uma fixture com essa forma que espere 2 em poucos segundos. Esforço P. Dono: `tech-lead`.

**Releitura do resto da entrega (sem bloqueio).**
- Lista da seção 6 do modelo: (1) as famílias da matriz sobem para 2, menos o `pesado` em `FORA_DO_T2` com o motivo e o controle negativo de `<<'EOF'` (sondas: `cat <<EOF⏎$(L)⏎EOF` recusa; `cat <<'EOF'⏎$(L)⏎EOF` libera; o bash não roda o corpo). (2) N1 e N2 cobertos: `x="$(git push origin main)"`, `x="$(echo "a"; git push origin main)"`, `echo "$(echo "a"; gh pr merge …)"` e `x="$(gh pr merge "feature/x" …)"` recusam. (3) O ramo do S3 continua (`ilegivel`, `hooks/conformidade.py:776-785`, fixture `contrib-forge-local-cd-crase-pr-merge-bloqueia`). (4) O `ValueError` de `tirar_heredocs` é tratado nos três chamadores: `Guarda.bash` recusa (`:670-683`), `rotulo_na_sessao_do_forge` exige o dono se a linha cita o rótulo (`:1349`), `alvos_de_escrita` lê a mais (`:1641`, só autoria). (6) As fixtures `-libera` (commit com crase em par, `x="$(date)"`, `gh pr create --draft` com heredoc literal) liberam.
- T5 (N3, seção 4 do modelo): `rodado_pelo_bash` (`tests/test_hooks.py`) usa `PATH` numa pasta inexistente dentro de uma pasta temporária nova, `--norc --noprofile -r -c`, ambiente só com `PATH` e `HOME`, stdin vazio, prazo de 5 s, `start_new_session` e `killpg` no fim; a evidência vai ao stderr e a afirmação 1 confere todas as palavras da ação. A guarda `PROIBIDO_NO_ORACULO` roda antes de cada execução e tem caso negativo para cada item proibido. No CI, a falta de bash 4 ou de `-r` é falha. Sem rede e sem custo (R-CUSTO). Rodado na cópia: os três testes novos passam.
- `parecer`: `conferir_linha` (`hooks/parecer.py:340`) recusa acima de `PROFUNDIDADE` e na linha ilegível (fecha); o `PREFILTRO` continua sobre o texto inteiro. A mesma linha adversária do A1 leva 0,09 s nele.
- Invariante em `tests/config.json`: `def conteudos_de_crase` passa de `hooks/conformidade.py` para `hooks/_comum.py`, onde a função mora agora, e `hooks/conformidade.py` passa a exigir a chamada `conteudos_de_crase\(`. A proteção não diminui; o título do PR deve dizer que o item mudou de lugar, com o motivo (CLAUDE.md do Forge).

**Recomendações (fora do bloco; resíduos anteriores à entrega, mesma classe, ações sem marcador crítico).** Todas saem 0 também na base, e o bash roda a ação (confirmado pelo oráculo do modelo de ameaças). Severidade baixa: para essas ações, a construção deliberada já passa por variável (`C=gh; $C repo delete …`, item [B] de `docs/hooks.md`), e com marcador crítico a rede da ADR 0011 recusa. Mas `docs/hooks.md` e o fragmento do changelog dizem que o heredoc com corpo que expande recusa, e isso não vale nos casos R1 e R2.
- R1. `hooks/_comum.py:767`: `(?<!\\)` toma `\\$(` por escapado (o bash troca `\\` por `\` e roda o `$(…)`), e `$\`⏎`(L)` (a quebra escapada some no corpo sem aspas) não casa. `cat <<EOF⏎\\$(gh repo delete d/p --yes)⏎EOF` e a forma com `$\`⏎ liberam. Correção: contar a paridade das barras e tirar `\`⏎ antes de procurar, ou recusar qualquer `$(`/crase em corpo sem aspas. Esforço P.
- R2. `hooks/_comum.py:716`: o fim do corpo compara com `.strip()`, e o bash só aceita a linha igual (com `<<-`, sem as tabs do começo). O hook fecha antes, e um `<<Y` que para o bash ainda é corpo abre um heredoc falso que esconde a linha que o bash roda: `cat <<X⏎ X⏎cat <<Y⏎X⏎gh repo delete d/p --yes⏎Y` libera (também com `X ` e com `<<-X`). Correção: comparar como o bash, ou tratar a linha que só bate sem os espaços como dúvida. Esforço P. Sem tocar em `corpos_de_heredoc` (`:552`), que já trata esse caso para o marcador crítico.
- R3. Cartão HOOK-N4, severidade baixa no `conformidade`: `x="$(case a in a) gh repo delete d/p --yes;; esac)"` libera, o bash roda, e com marcador crítico a rede (`case`) recusa. As minhas sondas com aspa dupla dentro de `"$(…)"` recusaram nos dois hooks; a forma exata que passa no `parecer` precisa vir no cartão para medir a severidade dele.
- R1 e R2 podem entrar na volta do A1 (mesmo cartão, HEREDOC-FURO-HOOK, mesma função) ou virar cartão próprio. A decisão é técnica.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do diff, sondas do hook real em cópias por `git archive` do HEAD e da base em `$TMPDIR`, oráculo do bash local com `PATH` inexistente, `-r` e ambiente limpo, e perfil da execução. `gitleaks`, `zizmor` e `actionlint` não se aplicam (sem segredo, workflow ou dependência na entrega). Nada foi instalado, nada saiu da máquina e nada foi gravado fora de `$TMPDIR`, além deste parecer.
