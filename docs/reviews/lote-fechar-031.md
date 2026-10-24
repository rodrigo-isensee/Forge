---
tipo: review
contrato: 1
pedido: lote-fechar-031
branch: melhoria/lote-fechar-031
commit: 432a0a7934fe72373e8dd476e8238d6a3a58ec39
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-24
---
# Review: lote-fechar-031

## Achados
- A1 (bloqueante) tests/test_fechar_orfao.py:116 · classe: teste que não exercita o que o nome diz. O commit novo na worktree faz o script parar no passo 2 (rc 1, head local difere do remoto); o passo 7 não roda, resumo() é [] e o assertNotEqual passa à toa. O caminho novo de dentro da worktree com commit não mesclado fica sem teste.
- A2 (recomendado) bin/forge-fechar:163 · classe: mensagem de erro que não resolve. Em pasta com setgid (2755), o chmod 700 do GNU mantém o setgid (fica 2700) e o script para pedindo "chmod 700", que não resolve. Sugestão: chmod 0700/u-s,g-s ou citar o bit na mensagem.
- A3 (recomendado) bin/forge-fechar:148 · classe: comentário desatualizado. Ainda diz que a pasta "só é aceita ... com modo 700"; agora o modo é ajustado. Alinhar com o comentário da linha 161.
- A4 (recomendado) bin/forge-fechar:723 · classe: comando pendente sem conferência. O --sem-limpar imprime git branch -D (mesmo sem branch local) sem a conferência de sha que a R-VERIFY exige. Sugestão: pôr o --limpar, que confere, como primeira opção e condicionar a linha à branch local existir.

## O que foi lido
- Diff `d150ec8...432a0a7` inteiro (4 commits, 6 arquivos), `bin/forge-fechar` nas linhas 140-175, 350-460, 540-546 e 712-735, e `docs/fechamento-integrador.md` na branch (passos 1 a 7, `--sem-limpar`, `--limpar`, log).
- `docs/engineering/achados-recorrentes.md` (PA-7): sem itens; nenhum se aplica.
- Testes: `python3 -m unittest tests.test_fechar tests.test_fechar_log_check tests.test_fechar_orfao` → `Ran 95 tests ... OK`. A suíte completa, o shellcheck e a validação do plugin ficam com o pre-push e o CI (regras "ferramenta"); não as refiz.

## Conferências pedidas (sondas em `$TMPDIR/tech-lead-rev-lf031/`, repositório e HOME descartáveis do próprio teste)
- `chmod 700`: só roda depois de `[ ! -L ]`, `mkdir -p`, `[ -d ] && [ ! -L ]` e `[ -O ]`, então só alcança diretório do próprio usuário e nunca um link nem um arquivo: link → "link simbólico" e o alvo continua 0755; arquivo → `mkdir -p` falha, arquivo intacto (testes novos de `test_fechar_log_check.py` e `test_l1_...` cobrem). A janela entre a checagem e o `chmod` (TOCTOU, o `chmod` segue link) existia antes para o `mktemp`; é do parecer de segurança (E2.1), não refaço aqui. Setgid: ver A2.
- Dentro da worktree da branch: sonda e `test_de_dentro_da_worktree_da_branch_sai_para_a_principal_remove_e_fecha_com_0` mostram `registro: saí da worktree ...`, `limpeza: remota=ok worktree=ok branch=ok`, `fim: código 0`. Branch na principal: sonda dá `worktree=pendente branch=pendente`, código 3 e o aviso "não achei outra para sair", como o doc diz. A guarda do commit não mesclado continua antes do `worktree remove` (linha 376), mas sem teste que a alcance (A1).
- `--sem-limpar`: código 3, `limpeza: pulada (--sem-limpar)`, comandos pendentes, nenhum `branch -D` nem `worktree remove`, log com `fim: código 3`; com `--limpar` dá erro de uso, rc 1, sem chamada; com `--dry-run` só descreve. Sonda sem worktree: só as linhas de branch e remota (A4).
- `logdir` relativo: o script já faz `cd` para a raiz (linha 142) antes; a sonda com `FORGE_FECHAR_LOG_DIR=logrel` grava em `<raiz>/logrel/`, o mesmo lugar de antes. Absolutizar só protege o `fim:` depois do `cd` do passo 7.
- `docs/fechamento-integrador.md` diz o mesmo que o código nos três itens (passo 7, seção `--sem-limpar`, "Log em arquivo"); o cabeçalho de uso também.
- Commits: um por item, com o teste dele, mais o fragmento `changelog.d/lote-fechar-031.md`; Conventional Commits em português. `R-NEUTRO` e `R-CUSTO`: nada novo.

## Parecer
Reprovado só por A1: o caminho de mais risco do E2 (remover a worktree de dentro dela, agora que a guarda de sha é o único freio) não tem teste que chegue ao passo 7. Sugestão: mesclar antes (ou usar `--limpar` com o PR MERGED no gh falso), fazer o commit na worktree, rodar o `--limpar` de dentro dela e conferir `worktree=pendente`, worktree e branch presentes e código 3. A2 a A4 são recomendados. Na volta, revalido por delta (`forge-check delta --parecer`).
