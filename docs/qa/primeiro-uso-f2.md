---
tipo: qa
contrato: 1
pedido: primeiro-uso-f2
branch: melhoria/primeiro-uso-f2
commit: 41b14f5
parecer: reprovado
revisor: forge:qa-engineer
escopo: completo
bugs_criticos: 0
bugs_altos: 1
bugs_medios: 1
bugs_baixos: 4
aceite_usuario: sim
data: 2026-10-13
---

# QA - primeiro uso do Forge, entrega F2 (`forge salvar`, `forge desfazer`, primeiro pedido guiado)

Testado no HEAD 41b14f5 do PR #102 (código idêntico ao 229ec44; os dois commits seguintes são só pareceres), em worktree temporária. Sem rede e sem o `gh` real (PATH com links só das ferramentas do sistema, sem `gh`), HOME e git temporários (`GIT_CONFIG_GLOBAL=/dev/null`, identidade por variáveis de ambiente), remotos bare locais. Nada tocou GitHub. Aviso da suíte: uma linha de sandbox sobre `api.anthropic.com` apareceu na saída e é do ambiente, não do teste.

## Resultado da suíte
`python3 -m unittest discover -s tests`: 342 testes, OK, 57 s. Nenhum `skip`.

Vermelho antes do verde (reexecutado): com `bin/forge-salvar` e `bin/forge-desfazer` removidos, `python3 -m unittest tests.test_salvar_desfazer` dá 23 testes, 21 falhas e 1 erro. Mutação: não há ferramenta gratuita para bash na stack da fábrica; não aplicável. Os bugs abaixo mostram lacunas que os testes atuais não cobrem.

## Matriz: critério -> teste -> resultado
Arquitetura, linha F2: "salvar fora da `main`, desfazer por revert e stash, nunca `--force`, recusa em merge". Os CA-1 a CA-10 do UX são da F1 (reteste da F1 na seção seguinte).

| Critério | Cobertura automatizada | Exploratório | Resultado |
|---|---|---|---|
| Salvar: caminho feliz | `test_salvar_desfazer` | commit, envio, árvore limpa | Ok |
| Salvar sem mudanças | idem | "Não há nada novo para salvar" | Ok, exceto BUG-F2-02 |
| Salvar na `main`/`develop`/`homolog`/HEAD solto | idem | não recusa: cria `trabalho/<data>` e salva lá; `main` remota intacta (a arquitetura prevê isso; a tarefa dizia "recusar", mas o efeito protetor é o mesmo) | Ok |
| Salvar com mesclagem em andamento (com e sem conflito) | idem | recusa, HEAD não se move, nada preparado | Ok |
| Salvar com marcas de conflito | idem | recusa listando o arquivo; com acento no nome passa | Falha parcial (BUG-F2-01) |
| Segredo novo (`.env`, `*.pem`, subpasta, `.env.example` liberado, ignorado pelo `.gitignore`) | idem | recusa e lista; nada commitado | Ok |
| Segredo já preparado (`git add -f .env`) | idem | recusa | Ok |
| Segredo em pasta com acento no nome | nenhuma | **commitado e enviado** | **Falha** (BUG-F2-01) |
| Push recusado por conflito (outro clone) | idem | mensagem certa, commit local preservado, remoto intacto | Ok |
| Push recusado por hook do servidor | nenhuma | mensagem falsa "alguém mudou" | BUG-F2-03 |
| Sem rede / sem origin | idem | trabalho salvo local, mensagem clara | Ok na primeira vez; falha na repetição (BUG-F2-02) |
| Desfazer depois de salvar (enviado) | idem | revert + push, histórico mantido | Ok |
| Desfazer registro local ainda não enviado | idem | revert, sem push | Ok |
| Desfazer com mudanças não salvas | idem | lista, pede sim, `stash -u` (inclui índice e novos) | Ok |
| Desfazer sem commits / primeiro registro | idem | primeiro registro: recusa clara; repositório sem commits e com mudanças: silêncio | BUG-F2-04 |
| Desfazer com mesclagem em andamento / último registro é mesclagem | idem | recusa clara, nada alterado | Ok |
| Recusa da confirmação (não, Enter, fim da entrada, "Sim.") | idem | nada muda, HEAD igual | Ok |
| `--recuperar` (feliz, sem nada, recusado, pop com conflito) | idem | traz de volta; sem nada: aviso; recusado: stash intacto; conflito: stash mantido | Ok, texto cru em inglês (BUG-F2-05) |
| Nunca `--force`, `reset --hard`, `clean` | teste estático | opção `--force` é recusada | Ok |
| Nenhum trabalho se perde | `git reflog` e `git stash list` | ver abaixo | Ok |

## Nada se perde (reflog e stash)
Em todos os casos acima o trabalho continuou recuperável: salvar sempre commita antes de enviar e, se o envio falha, o commit fica local; desfazer só cria revert (os registros antigos permanecem no reflog e na história) ou stash (`stash@{0}: desfeito ...`, mantido quando o `pop` falha). Segredos não salvos (`.env` solto) vão para o stash local, nunca para o GitHub. Nenhum caso perdeu arquivo. O único dano possível é o BUG-F2-01, de confidencialidade, não de perda.

## Reteste dos bugs da F1
| Bug | Resultado |
|---|---|
| BUG-03 (pasta perguntada, 11 interações) | Fechado: nome e confirmação no terminal, pasta `~/<nome>` avisada na tela; teste prende o limite de 10 |
| BUG-07 (pasta apagada) | Fechado: "a pasta ... não existe mais ... Quer baixar uma cópia de novo?"; sim baixa, não encerra com explicação, sem erro cru |
| BUG-08 (sem rede lido como sem login) | Fechado: `gh auth status` sem rede diz "sem conexão"; sem login continua mandando `gh auth login` |
| BUG-09 (repositório vazio e privado) | Fechado: oferecido no passo do nome; com conteúdo continua recusado |
| BUG-10 (colchete duplicado) | **Parcial**: sumiu na pergunta de normalização, mas continua em "Quer usar este repositório? [sim] [sim]" e "Quer baixar uma cópia ...? [sim/não; Enter = sim] [sim]" (BUG-F2-06) |

## Mensagens
Em geral português claro e sem jargão: "mesclagem (junção de trabalhos)", "guardar de lado", "nada se perdeu", sempre com o próximo passo. Pontos ruins: BUG-F2-05 (inglês cru do git no `--recuperar`), BUG-F2-03 (afirma uma causa que não aconteceu), BUG-F2-04 (silêncio) e BUG-F2-06 (colchete duplicado).

## Bugs
Todos para o agente de desenvolvimento da fábrica (dono de `bin/`).

### BUG-F2-01 - alta - segredo em pasta com acento no nome é commitado e enviado
Passos: repositório com origem; `mkdir "pasta ção"`; `echo K > "pasta ção/.env"`; `forge salvar`.
Esperado: recusar, como em `cfg/.env.local`. Obtido: "Trabalho registrado ... Enviado ao GitHub"; `git ls-files` mostra `"pasta \303\247\303\243o/.env"`. Idem para as marcas de conflito (`açao.txt` com `<<<<<<< HEAD` é salvo). Causa: `git ls-files` escapa nomes não ASCII (`core.quotepath`), então o caminho entre aspas não casa com a regex nem com `[ -f ]`. Correção: `-z` ou `git -c core.quotepath=off`. Para o público (pessoas brasileiras, pastas como "Configurações"), a proteção principal de salvar falha. O repositório é privado por padrão, o que atenua, por isso alta e não crítica. É a observação 3 da re-review, que a tratou como não bloqueante; discordo pelo vazamento. Adicionar teste com nome acentuado.

### BUG-F2-02 - média - depois de falha de rede em ramo novo, "forge salvar" de novo diz "nada novo" e nunca envia
Passos: ramo `feat` ou `trabalho/<data>` sem versão remota; mudar um arquivo; remoto indisponível; `forge salvar` (commita, falha o envio e manda "rode de novo quando puder"); religar o remoto; `forge salvar`.
Esperado: "Enviei ao GitHub o que já estava salvo". Obtido: "Não há nada novo para salvar." (rc 0), `git ls-remote` sem o ramo. A pessoa acredita que está salvo no GitHub e não está. Causa: o reenvio sem mudanças só vale se já existe `origin/<ramo>`. Correção: enviar também quando o ramo não tem versão remota. Trabalho preservado localmente.

### BUG-F2-03 - baixa - envio recusado pelo servidor aparece como "alguém mudou o trabalho"
Passos: `pre-receive` no remoto que sai com erro (proteção de branch); `forge salvar`. Obtido: texto de conflito, falso. Causa: o padrão `rejected` casa com "remote rejected" (observação 1 da re-review). Usar só `non-fast-forward|fetch first|stale info`.

### BUG-F2-04 - baixa - `forge desfazer` em repositório sem commits e com arquivos novos encerra sem mensagem
Passos: `git init`, criar um arquivo, `forge desfazer`, responder sim. Obtido: rc 1, nenhuma frase (o `stash` falha sem commit inicial e o `-q` esconde). Nada se perde. Esperado: "ainda não há nenhum ponto salvo para voltar".

### BUG-F2-05 - baixa - `--recuperar` com conflito mostra erro do git em inglês e fala de "marcas" que não existem
Passos: `desfazer` com mudança em `a.txt`; alterar `a.txt` de novo; `forge desfazer --recuperar`, sim. Obtido: "error: Your local changes ... would be overwritten ... Aborting" e depois "a pasta pode ter ficado com marcas de conflito" (não ficou: o stash foi mantido e a pasta está intacta). Esperado: texto em português dizendo que o guardado continua guardado e que é preciso salvar ou desfazer o que há na pasta antes.

### BUG-F2-06 - baixa - colchete duplicado reaparece em dois prompts do `forge novo-projeto`
Passos: repositório vazio existente (`... Quer usar este repositório? [sim] [sim]`); pasta apagada (`[sim/não; Enter = sim] [sim]`). Causa: `ler` já acrescenta `[padrão]` (linhas 78 e 160 de `bin/forge-novo-projeto`). Remover o colchete do texto.

## Cobertura que falta
Testes para: nome acentuado (BUG-F2-01), reenvio em ramo sem versão remota (BUG-F2-02), recusa do servidor (BUG-F2-03), repositório sem commits (BUG-F2-04), `pop` conflitante (BUG-F2-05), colchete nos dois prompts (BUG-F2-06). CI: scripts de `bin/` ainda fora do job `shellcheck` (pendência registrada). Skill `novo-projeto` (primeiro pedido guiado) é texto; só há teste estrutural.

## Parecer
Reprovado para a `develop` com 1 bug alto aberto (BUG-F2-01) e 1 médio (BUG-F2-02). Nenhum caso perde trabalho, e `desfazer` está sólido. A reprovação é pelo segredo que escapa em pasta com acento, que fura a promessa central de `salvar`, e pela falsa segurança do reenvio. Corrigidos F2-01 e F2-02 (com teste cada), o retorno é reteste incremental; os quatro baixos podem seguir com aceite do usuário.
