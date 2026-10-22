---
tipo: revisao-seguranca
contrato: 1
pedido: impl-n-fechar-a
branch: melhoria/impl-n-fechar-a2
commit: bf0606059c9b082900fae957b7e4ab52e0324163
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-22
---
# Review de segurança: impl-n-fechar-a (lote N-FECHAR-a refeito, A1 a A6)

Escopo: `git diff a3dbe22..bf06060` (`bin/forge-fechar`, `docs/fechamento-integrador.md`, `changelog.d/impl-n-fechar-a2.md` e os seis arquivos de teste novos `tests/test_fechar_*.py`), com releitura da função `limpar_entrega`, do `fim` e do `conferir_base` inteiros no commit revisado. Base de comparação: o adendo de ameaças `docs/security/ameacas/n-fechar.md` (controles C-A1 a C-A5, casos de abuso e o A6) e o parecer da branch antiga (7ad9f5f). Leitura estática e sondas em cópia própria (`git archive` do commit em `$TMPDIR/sec-nfa2/`), sem rede e sem `gh` real; o HEAD da worktree compartilhada não foi trocado.

## Gatilhos
- **Controles do Forge** (`R-SEGURANCA`): o `bin/forge-fechar` conduz o merge na `develop` (passos 1 a 6) e apaga worktree, branch local e remota (passo 7).
- **Log com possível credencial**: máscara e pasta 700 não mudaram; o log só ganhou o `fim:` com o código do sinal e a lista do `prune -v`.
- Sem rede nova, dependência nova nem custo (`R-CUSTO`).

## Achados

## Detalhe dos achados
Nenhum bloqueante. Conferência dos controles do adendo no commit revisado:

- **Nada mescla sem checks e pareceres.** A ordem dos passos 1 e 2 não mudou; o 2b (`bin/forge-fechar:438-439`) roda depois do passo 2 e antes do reuso do PR aberto e do `pr create`. Passo 4 e merge preso ao head intactos. Nenhuma asserção dos testes antigos saiu: `tests.test_fechar` na cópia, 80 testes OK; os seis arquivos novos, 32 testes OK.
- **A5, 2b falha fechado (C-A5-1 a C-A5-5).** `conferir_base` (`:343-370`): `ls-remote` com erro ou vazio, base local diferente do servidor, `merge-base --is-ancestor` com código diferente de 1, `merge-base --all`, os dois `diff --no-renames --name-only -z`, `sort -zu`/`comm -z` e `rev-list` terminam em `die`; sem `|| true`, sem `fetch` nem escrita em `refs/`; nomes em comum impressos com `%q` (`:365`). Testes de renome, nome com quebra de linha, servidor mudo, diff que falha e base atrasada presentes.
- **A4, sinais (C-A4-1, C-A4-2, C-A4-4).** `trap 'exit 143|130|129'` para TERM, INT e HUP (`:204-206`), depois do `trap fim EXIT`; os registradores ignoram os três (`:171`), e o `fim` também (`:191`), mata o `sleep` pendente (`:192`) e apaga a pasta do 2b (`:195`). As esperas usam `dormir` (`sleep &` e `wait`, `:209-214`), então o trap vale na hora. Testes do sinal no pid, no grupo, INT e HUP e da rodada seguinte ao corte, todos verdes. O documento (`docs/fechamento-integrador.md`, seção "Espera longa e corte por sinal") diz que só `fim: código 0` depois da linha de entrega fechada é sucesso, proíbe `pkill -f` e manda conferir o PR e rodar `--limpar`.
- **A1 e A2, comandos impressos escapados (C-A1-1 a C-A1-4, C-A2-1 a C-A2-4).** `printf '%q'` no caminho, na branch, na seção do config e no pedido em todo comando de "pendente, rode:", nos avisos com comando e na linha final do `--limpar` (`:251`, `:254`, `:274`, `:301`, `:311`, `:326`, `:331`, `:563`). Sonda do `%q` com `;`, `$(`, crase, `&`, `|`, `'`, `>`, `#` e `~` no começo: tudo escapado. Caminho lido inteiro (`substr($0,10)`), `prune -v` com o aviso de que é do repositório todo, seção do config por nome exato e por texto fixo (`secao_da_branch`, `:227-238`); código do git diferente de 0 e 1 vira `config=pendente`, nunca `ok`.
- **A3, faixas (C-A3-1 a C-A3-4).** `faixa` (`:65-71`): regex de dígitos e tamanho antes do valor, base 10, `--espera` de 0 a 7200 s, pausa e intervalo com teto sempre e piso 0 só com `FORGE_FECHAR_TESTE=1`. Sem injeção aritmética: o `$((10#$v))` só roda depois da regex.
- **A6, sha da branch antes da worktree.** O sha da branch local é lido antes de mexer na worktree (`:244`); sha que não confere deixa a worktree e a branch pendentes, sem `git worktree remove` (`:253-255`); teste com arquivo ignorado preservado. O desvio em relação ao commit antigo e8ec48e: a conferência agora vem **depois** do caso "você está na worktree" (`:250-252`), e não antes. Medi o efeito numa sonda (`--limpar` rodado de dentro da worktree de uma branch com commit novo e PR antigo `MERGED` com o mesmo nome): rc 3, `worktree=pendente branch=pendente`, nada apagado localmente. O script continua sem apagar nada, então o controle do adendo (deixar a worktree pendente) está cumprido. O que muda é só o aviso: ele não diz que há commit sem merge (ver R1).

Recomendações (não bloqueiam; nenhuma tem caminho de ataque realista):
- **R1 (baixa, medido; vem do desvio do A6).** De dentro da worktree de uma branch com commit sem merge, o aviso (`bin/forge-fechar:251`) manda rodar `git worktree remove ... && git branch -D ...` sem dizer que há commit sem merge. Quem segue a linha perde os arquivos ignorados e a branch. Também na lista "pendente, rode:" de uma branch sem merge saem `git worktree remove` e `git branch -D`, como na base e na branch antiga. Não é ataque: é instrução que, seguida sem ler, destrói trabalho do próprio usuário. Correção mínima: trocar a ordem dos dois primeiros testes, com a conferência do sha primeiro, como no e8ec48e; ou, para sha sem merge, imprimir `git log <base>..<ref>` no lugar dos comandos destrutivos. Esforço P. Dono: tech-lead (N-FECHAR-b, mesmo arquivo).
- **R2 (baixa, medido; é a R1 do parecer 7ad9f5f e fica para o N-FECHAR-b, como o pedido decidiu).** `tmp2b` e `dorme_pid` continuam sem valor inicial no topo do script (`:192`, `:195`). Com `tmp2b` herdado do ambiente, o `fim` roda `rm -rf` nesse caminho em qualquer saída. Sonda com `--dry-run` na cópia: a pasta indicada sumiu. Com `dorme_pid` herdado, o `fim` roda `kill` num pid do mesmo usuário. O ambiente é do próprio usuário (fronteira d do adendo). Correção mínima: `tmp2b="" dorme_pid=""` junto das variáveis iniciais. Esforço P. Dono: tech-lead.
- **R3 (informativa).** No `fim`, `trap - EXIT` (`:190`) vem antes de `trap '' TERM INT HUP` (`:191`). Um sinal entre as duas linhas sairia sem `fim:`. A janela é de uma instrução; trocar a ordem fecha. Esforço P.
- **R4 (informativa, anterior ao lote).** A dica do passo 2 (`:423`) e as linhas do `--dry-run` (`:375`, `:381`) mostram `$ref` sem `%q`. O nome já passou pelo `check-ref-format`, e quem roda é quem deu o `--ref`. Cabe no N-FECHAR-b.
- **R5 (informativa).** Um TERM mandado só ao pid durante um `ler` (substituição de comando) só é tratado quando o subprocesso acaba: até 2 pausas, 60 s no teto. Com TERM no grupo de processos, que é o que o teto do Bash faz, o efeito é imediato. O merge não é afetado.
- **R6 (informativa).** O `bin/forge-fechar` segue fora de `PROTEGIDOS` da Catraca (Q-1 do adendo): o portão deste lote é o review e este parecer.

## Riscos aceitos e ferramentas
- Nenhum risco aceito novo. Riscos residuais já declarados no adendo e no documento: quebra semântica sem arquivo em comum e `develop` que anda entre o 2b e o merge (só o CI do PR pega); com o sha conferido, a remoção da worktree ainda apaga os arquivos ignorados dela (comportamento antigo do git sem força).
- Ferramentas usadas: leitura estática, sondas em cópia e os testes `tests.test_fechar` mais os seis arquivos novos. Lacunas (nada instalado, `R-CUSTO`): `shellcheck`, `gitleaks`, `semgrep`, `zizmor`, `actionlint` e `osv-scanner` não estão no PATH; o shellcheck roda no CI da fábrica. A sonda de revert de cada commit sozinho (P3 = B) é do review do tech-lead e não foi refeita aqui.
