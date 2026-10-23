---
tipo: revisao-seguranca
contrato: 1
pedido: F4-ATUALIZAR
branch: melhoria/f4-atualizar
commit: 671c6251eade090150d8c12c562804e1f79b4780
parecer: reprovado
revisor: forge:security-engineer
data: 2026-10-23
---
# Review de segurança: F4-ATUALIZAR

Escopo: `git diff origin/develop...671c625` (base `7423c44`): `bin/forge-atualizar` (`adiantar_develop_local`, `integrar_develop` e a chamada em `atualizar`), `README.md`, `changelog.d/f4-atualizar.md`, `tests/test_atualizar.py`. Revisão estática e sondas locais em repositórios descartáveis (`HOME` em `$TMPDIR/security-engineer-f4`), sem rede externa.

## Gatilhos
Controle do Forge (`R-SEGURANCA`): `.forge/versao`, que só o dono altera, pelo terminal (`R-CONFORMIDADE`); e a `main` local, que é do usuário (`R-MAIN`).

## Achados
- A1 (bloqueante) bin/forge-atualizar:212 · integrar_develop roda mesmo quando o forge-upgrade não criou forge/upgrade-<nova> (saída 0 em "nada a fazer", bin/forge-upgrade:56): mescla origin/develop na branch em uso, inclusive na main local (sonda S7). Integrar só se a branch atual for forge/upgrade-<nova>
- A2 (recomendado) bin/forge-atualizar:82 · a pergunta não mostra a versão que a develop gravou em .forge/versao; se ela for maior que a nova, responder s rebaixa o arquivo. Mostrar as duas (git show :3:.forge/versao) e avisar quando a da develop for maior
- A3 (recomendado) bin/forge-atualizar:9 · a docstring diz "nem mescla" e o README.md:77 "sem push nem merge", mas agora há merge local de origin/develop; ajustar o texto e listar na saída os arquivos trazidos da develop, em especial .forge/, .claude/ e hooks (sonda S5)

## Detalhe dos achados
**A1. Mesclagem fora da branch do upgrade (classe: conformidade, `R-MAIN`, integridade do repositório local).** Evidência: `bin/forge-atualizar:212` chama `integrar_develop` sempre que o `forge-upgrade` sai com 0; `bin/forge-upgrade:56-58` sai com 0 sem trocar de branch quando `.forge/versao` da árvore já está na versão alvo ("nada a fazer"), e o `main` do `forge-atualizar` compara só a versão do plugin, não a do projeto. Caminho: o dono roda `forge atualizar` parado na `main` local, que já recebeu a release com `.forge/versao` na versão nova, enquanto a `develop` do remoto avançou; `integrar_develop` (linha 75) cria na `main` local o commit `chore(forge): traz a develop para a atualização`. Vale igual para uma branch de funcionalidade e para a `develop` local com commit próprio. Não há atacante nem envio: o pre-push bloqueia a `main` e o dono pode desfazer. Ainda assim a ferramenta do Forge altera, sem perguntar, a branch que a `R-MAIN` reserva ao usuário e quebra a promessa do próprio comando. Severidade: média (integridade, sem exploração). Correção mínima: em `integrar_develop`, sair com True sem mesclar quando `git branch --show-current` for diferente de `forge/upgrade-<nova>`, e um teste do caso "nada a fazer" na `main`. Esforço: P. Dono: devops-engineer (código), qa-engineer (teste).

**A2. Escolha sem a informação (classe: decisão do dono informada).** Evidência: `bin/forge-atualizar:82`. O padrão é N, então nada muda sem resposta. Mas, se a `develop` já estiver numa versão acima da nova (alguém do time atualizou para uma versão mais nova), responder "s" rebaixa `.forge/versao` e o projeto fica marcado numa versão anterior às migrações já aplicadas. Severidade: baixa. Correção: mostrar os dois valores (`git show :2:` e `:3:.forge/versao`) e, quando o da develop for maior, avisar ou recomendar N. Esforço: P. Dono: devops-engineer.

**A3. Texto e transparência da mesclagem (classe: documentação).** Evidência: `bin/forge-atualizar:9`, `README.md:77`. A sonda S5 mostra que a mesclagem traz `.claude/settings.json` e `.githooks/pre-push` da develop e a saída diz só "trouxe as mudanças". Não é caminho novo de ataque: o conteúdo já está na `develop` do projeto, que entrou por PR, e o diff da branch do upgrade contra `origin/develop` continua mostrando só `.forge/versao` (S5). Os hooks versionados passam a valer na árvore local, como num `git pull`. Correção: ajustar o texto e imprimir a lista de arquivos trazidos. Esforço: P. Dono: devops-engineer.

**Perguntas do pedido, com a resposta.**
- *Um agente grava ou resolve `.forge/versao` pelo novo caminho sem a resposta do dono?* Não. A pergunta nova (linha 82) só é alcançada depois dos portões que já existiam no `main`: `recusar_dentro_do_claude` (variáveis `CLAUDECODE`/`CLAUDE_CODE_ENTRYPOINT` e processo ancestral `claude`) e `tem_terminal` (stdin e stdout em tty). A sonda S1 confirma: `yes s | forge-atualizar` e `CLAUDECODE=1 forge-atualizar` saem com 2 e nada muda. Nenhuma variável de ambiente nova responde por ele. `fv.confirmar` aceita stdin por pipe quando a função é chamada direto (S2), mas é o mesmo caso de um agente rodar `git checkout --ours .forge/versao`, que é assunto do hook `conformidade`, e não um caminho novo. Resíduo que já existia antes desta entrega, informativo: processo que limpe as variáveis, se desligue do ancestral e aloque um pty passaria pelos portões; não muda aqui.
- *A mesclagem traz mudança em `.forge/`, `.claude/` ou nos hooks sem o dono ver?* Traz para a árvore local sem listar (S5, A3), mas nada que já não esteja na `develop` do projeto. O PR do upgrade não esconde nada: o diff contra a `develop` é só o do upgrade.
- *O desfazer em outro conflito deixa o repositório limpo?* Sim. S3 (resposta N), S4 (conflito em `.forge/versao` e `a.txt`) e S6 (hook `commit-msg` que falha no commit da mesclagem, resposta s) terminam com HEAD igual ao de antes, `git status --porcelain` vazio e sem `MERGE_HEAD`. O commit não usa `--no-verify` (`R-VERIFY`).
- *`adiantar_develop_local`:* só avança (confere `--is-ancestor`, `update-ref` com valor antigo e `--ff-only`), e a sonda S8 mostra a `develop` local com commit próprio intacta. Sem achado.

**Sonda rodada** (`scratchpad/sonda.sh`, repositórios bare locais em `$TMPDIR/security-engineer-f4`). Resultados: S1 saída 2 nos dois casos; S2 `versao=0.3.0 status=[] merge_head=nao`; S3 e S4 `head_igual=sim status=[] merge_head=nao`; S5 arquivos trazidos `.claude/settings.json .githooks/pre-push` e diff contra origin/develop `[.forge/versao]`; S6 `head_igual=sim status=[] merge_head=nao`; S7 `branch=main main_mudou=sim ultimo=chore(forge): traz a develop para a atualização`; S8 `develop_local_intacta=sim`. `python3 -m unittest tests.test_atualizar`: 64 testes, OK.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: revisão manual, sondas com git e python3 locais. Lacuna: `gitleaks`, `semgrep`, `zizmor`, `actionlint` e `osv-scanner` não estão no PATH. A entrega não mexe em workflow nem em dependência; nenhum segredo à vista no diff.
