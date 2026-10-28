---
tipo: revisao-seguranca
contrato: 1
pedido: lote-prepush-parecer
branch: melhoria/lote-prepush-parecer
commit: 97629b0d4ba02e6367aae0bafb4198ab2c13dead
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-28
---
# Review de segurança: lote-prepush-parecer

Pedido LOTE-PREPUSH-PARECER-REV, etapa E2.1. Faixa revisada: `9c4c6159f88c1d1a07f248fd448c52f0e6ec0f8e...5ca9a43d31b1b273ae47c906800bb4cd56105962` (8 arquivos: `.githooks/pre-push`, `bin/forge-fechar`, três agentes, fragmento de changelog, mutantes e `tests/test_pre_push_parecer_curto.py`). Revalidação do zero na rodada REV-1 (decisão técnica de 2026-10-28 14:53, parecer anterior `a74dcb0` sobre `5ca9a43`); a volta 1 (`97629b0`) foi revalidada por delta `95c7b85..97629b0` (decisão técnica de 2026-10-28 17:10).

## Gatilhos
`R-SEGURANCA`: controle do Forge (o `.githooks/pre-push`, que barra envio direto às branches protegidas, reescrita de histórico e decide quanto da suíte roda antes do envio).

## Achados

## Revalidação por delta (volta 1, `97629b0`)
`forge-check delta --parecer` sobre o parecer anterior lista só três arquivos de teste: `tests/mutantes/lote-prepush-parecer-b.json` (+46, novo), `tests/mutantes/lote-prepush-parecer.json` (+25 -25) e `tests/test_pre_push_parecer_curto.py:209-250` (+42). `git diff --quiet 95c7b85..97629b0 -- .githooks hooks bin scripts` confirma: o `.githooks/pre-push` e o resto do código não mudaram, então as conclusões abaixo valem para o head novo sem releitura de controle.

- **Mutantes:** M5, M7, M8 e M9 só mudaram de arquivo (para o `-b.json`), com `de`/`para`/testes iguais. M6 ganhou a justificativa de equivalência da parte do `--suite`, que confere: `--suite` faz `exec </dev/null` (`.githooks/pre-push:104`), `n_refs` fica 0 e `so_parecer` devolve 1 em `:181`; o mutante continua morto pelo teste do envio de código. Os novos M10 (`[ ! -L "$1" ]` em `:324`), M11 (prova pelo `.verde` em `:191`), M12 (recaptura em `:243`) e M13 (árvore do fim igual à do início) apontam texto que existe no hook e testes que existem.
- **Testes novos:** `test_prova_da_suite_que_e_link_nao_e_seguida_ao_anotar_o_envio_curto` prova que o acréscimo não escreve no destino de um link (o `.verde` link continua link e o alvo vazio) e que o link não vale como prova; `test_quem_esperou_a_vez_anota_a_arvore_do_inicio_da_suite` segura a trava com `flock`, commita durante a espera e confere que a árvore anotada é a testada. Os dois só criam arquivos e processos no diretório temporário do teste e encerram só o grupo que iniciaram; nada de rede, nada fora do temporário.
- Os dois requisitos do brief seguem: o caminho curto não deixa passar commit com arquivo fora de `docs/{reviews,security,qa,devops}/` sem a suíte (filtro inalterado), e a nova tentativa (`git pull --rebase` e push de novo) passa pelo pre-push inteiro.

## Detalhe dos achados
Sem bloqueante. O que foi conferido, contra o requisito do brief:

- **O caminho curto não deixa passar código sem a suíte.** O filtro do delta em `.githooks/pre-push:192-201` não mudou: apagar ou renomear, modelo (`_*`), `docs/security/ameacas/`, `docs/security/aceites/` e qualquer arquivo fora de `docs/{reviews,security,qa,devops}/` devolvem 1. Delta vazio (commit vazio ou merge sem mudança de árvore) lê uma linha vazia e cai no `*`, falha fechada. Nome com quebra de linha ou caractere especial sai entre aspas pelo git e também cai no `*`. O que mudou é só a fonte da prova da árvore remota (`:191`): `.verde` ou `.dirigida`, as duas pelo `tem_prova` (`:176-178`: arquivo regular, do próprio usuário, não link, linha exata). A pasta das provas é a da trava (`XDG_RUNTIME_DIR` ou `forge-<uid>` com modo 700 conferido, `:12-40`), então outro usuário da máquina não planta prova. O teste `test_codigo_junto_com_o_parecer_continua_rodando_o_plano_do_codigo` cobre código junto com parecer.
- **A prova dirigida.** Só o dirigido verde, com árvore limpa no início e no fim e o `HEAD^{tree}` igual, anota `.dirigida` (`:332-336`); o dirigido já recusa diff que toca `bin/forge-testes`, `tests/config.json` ou `.githooks/` (`:282`). Aceitar essa prova no `so_parecer` segue a decisão M8 e o corte 2 da decisão do dono de 2026-10-24 (commit só de parecer não roda a suíte; o CI do PR repete tudo). A prova é por árvore e não por branch: em tese, um envio só de parecer para uma branch fora de `melhoria/*` cuja árvore remota só passou pelo dirigido seria curto. Não há caminho pelo hook: a primeira chegada dessa árvore a outra branch é ref nova (remoto zerado) ou envio de várias refs, e os dois rodam a suíte inteira e anotam `.verde`; o CI repete tudo. Informativa, sem achado.
- **Sem a trava no caminho curto.** O envio curto decide antes da fila (`:204-205`) e não abre o descritor 9; roda quatro classes leves. A anotação por acréscimo (`:326`) pode correr com o `aparar` de uma suíte inteira (`tail` mais `mv`, `:328-329`): o pior caso é a linha acrescentada se perder (a escrita foi para o arquivo já substituído) e o próximo envio rodar a suíte, falha fechada. Uma linha parcial não casa com `grep -x` contra 40 hexadecimais. O `.verde` cresce sem aparar entre suítes inteiras, 41 bytes por envio curto: informativa.
- **A nova tentativa não pula o pre-push.** O texto novo dos três agentes (`agents/tech-lead.md:17`, `agents/qa-engineer.md:21`, `agents/security-engineer.md:15`) manda `git pull --rebase` e `git push origin <branch>` de novo, que passa pelo hook inteiro outra vez; nada de `--force` nem `--no-verify` (`R-VERIFY`). As duas mensagens novas do hook (`:115`, `:121`) trocam o conselho de `git fetch`/"faça rebase" por `git pull --rebase` e mantêm a recusa (saída 1) e a frase de que reescrever histórico é decisão do usuário. Depois do rebase, a árvore remota com o parecer do outro portão só é prova se ele a anotou nesta máquina; senão a suíte roda, falha fechada.
- **A recaptura do início depois da espera** (`:242-244`) só faz anotar a árvore que de fato foi testada quando o `HEAD` mudou durante a espera; sem ela a anotação já falhava fechada. Não abre caminho novo.
- **`bin/forge-fechar:375`** e o comentário do E3: só comentário, conferido contra o `PREPUSH-DELETE` do hook (`:140-147`).
- **Achados recorrentes (PA-7):** `docs/engineering/achados-recorrentes.md` está sem itens; nada a conferir.

Recomendações (não devolvem; dono `tech-lead`, esforço P):

1. Comentários que descrevem a semântica da prova ficaram falsos: `.githooks/pre-push:174` diz que a prova da suíte inteira "segue só no `.verde`", mas `:334` acrescenta ao `.verde` a árvore de um envio curto cuja base só tem a prova dirigida; e `:260-261` diz que "só a suíte inteira anota a prova", mas o dirigido anota `.dirigida`. Hoje o único leitor dos dois arquivos é o `so_parecer`, que aceita os dois, então não há efeito; o risco é um leitor futuro tratar o `.verde` como "suíte inteira passou" e pular a suíte por isso. Correção mínima: reescrever os dois comentários para "`.verde`: árvore com prova (suíte inteira ou curto sobre base provada); `.dirigida`: árvore aprovada pelo dirigido; nenhum dos dois quer dizer, sozinho, que a suíte inteira rodou nesta árvore".
2. A frase nova dos três agentes ("o pre-push de um envio só de parecer não espera a fila da suíte") vale só quando a prova da árvore remota existe nesta máquina; sem ela, o envio entra na fila e roda a suíte. Correção mínima: acrescentar "quando a árvore remota tem prova; sem ela, roda a suíte e espera a vez".

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: `shellcheck .githooks/pre-push` (rc=0); testes do item `tests.test_pre_push_parecer_curto` e `tests.test_pre_push_parecer` (29 testes OK em `5ca9a43`; 31 testes OK em `97629b0`, na worktree do commit revisado); os dois JSON de mutantes carregam. Os mutantes (`tests/mutantes/lote-prepush-parecer.json`) são da etapa de QA. Faltaram no PATH: `gitleaks`, `zizmor`, `actionlint`, `semgrep`, `osv-scanner` (lacuna; o diff não toca workflow nem dependência, e o CI do PR roda a bateria).
