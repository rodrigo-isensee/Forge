---
tipo: qa
contrato: 1
pedido: primeiro-uso-f5
branch: melhoria/primeiro-uso-f5
commit: 1396c7e
parecer: aprovado
revisor: forge:qa-engineer
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
aceite_usuario: nao
data: 2026-10-14
---

# QA - primeiro uso do Forge, entrega F5 (`forge atualizar`, `forge voltar-versao`, aviso de versão nova)

Testado no HEAD e532702 do PR #111 (último commit só de parecer), em worktree temporária. Sem rede (o "Forge publicado" é um repositório bare local) e sem o `gh` real (PATH com um `gh` que só falha; nenhum comando de `gh` foi executado). `claude` falso dos testes, HOME e `GIT_CONFIG_GLOBAL` temporários, projeto criado com `forge-init` e `origin` bare local. O aviso de sandbox sobre `api.anthropic.com` na saída é do ambiente. Nenhum código foi alterado.

## Resultado da suíte
`python3 -m unittest discover -s tests` (PATH com `gh` falso): 452 testes, OK, 100 s. Nenhum `skip`. Com um PATH mínimo, sem `grep`, a suíte falha por ambiente (30 falhas de `forge-salvar`), não por defeito do PR; refeita com o PATH normal e `gh` bloqueado, verde.
Vermelho antes do verde e mutação: não refeitos; valem os do parecer de autor (20 falhas e 4 erros sem a mudança nos testes novos). Esta exploração é complementar.

## Matriz (exploração com o `claude` falso)
| Cenário | Esperado | Resultado |
|---|---|---|
| `atualizar` caminho feliz (resposta `s`) | mostra versões e novidades, guarda ponto e marca, simula, troca plugin (`--scope user`, tag `#v9.9.0`), cria `forge/upgrade-9.9.0`, doutor sem novidade, nada no remoto | passou |
| `atualizar` recusa (`n`) | nada muda, sem ponto, sem chamada ao `claude` | passou |
| simulação falha | para antes de mexer; plugin e projeto intactos; ponto e marca descartados | passou |
| doutor acha problema novo, aceita voltar | oferece voltar; volta à branch de antes, plugin na versão anterior | passou |
| doutor acha problema novo, recusa voltar | fica como está e diz como voltar depois | passou |
| problema que já existia (hook do git desligado) | não oferece voltar; lista como "já existiam" | passou |
| sem rede | "Não consegui ver se há versão nova... Não mudei nada." saída 1 | passou |
| árvore suja (`atualizar` e `--fixar`) | recusa, manda `forge salvar`/`forge desfazer` | passou |
| Ctrl-C (SIGINT) no `marketplace add` | marketplace original devolvida, fonte gravada, aviso de recuperação | passou, com ressalva (F5-02) |
| `--fixar` | só fixa o plugin na versão em uso, projeto intocado | passou |
| já em dia / sem terminal / opção desconhecida | mensagens e saídas 0 / 2 / 2 | passou |
| `voltar-versao` caminho feliz (não mesclada) | volta à branch de antes, branch da atualização guardada, plugin na tag anterior | passou |
| `voltar-versao` duas vezes | segunda: "nenhum ponto de retorno", saída 1 | passou |
| `voltar-versao` sem ponto | mensagem clara, nada muda | passou |
| `voltar-versao` com árvore suja | recusa antes de tudo | passou |
| aviso diário de versão nova | `SessionStart` mudo; `Stop` mostra uma linha mandando rodar `forge atualizar` no terminal; segunda vez no dia, mudo; no dia seguinte, avisa de novo | passou |
| agente roda `forge atualizar`/`voltar-versao`/`forge-atualizar` direto, por `bash -c`, `sh -c`, `env`, `script`, `cd && ...`, caminho absoluto | barrado (`R-CONFORMIDADE`, saída 2) com mensagem em português | passou |
| agente usa indireção (`$(which forge) atualizar`, `$f atualizar`, `bash <<<`, `pty.spawn`) | barrado | FALHOU (F5-01) |
| mensagens em português claro | texto simples, sem jargão desnecessário | parcial (F5-02) |

Nunca houve perda de trabalho nem estado sem o plugin: em todos os cenários de falha o plugin ficou na versão anterior ou foi devolvido, e nenhum arquivo do projeto foi apagado.

## Bugs
- `docs/qa/bugs/F5-01-hook-nao-barra-atualizar-por-indirecao.md` (média): o hook não barra formas com expansão do shell e a trava `tem_terminal` se vence com `pty.spawn` e `printf 's\n' |`; uma atualização completa rodou sem pessoa no terminal. Recuperável por `forge voltar-versao`. Passos para reproduzir no arquivo.
- `docs/qa/bugs/F5-02-mensagens-confusas-na-atualizacao.md` (baixa): aviso do doutor no meio da atualização pedindo `forge-upgrade`, "Pronto" seguido de "Algo não saiu como esperado", e depois do Ctrl-C o `voltar-versao` fala de uma versão que nunca foi instalada.

## Recomendados abertos da review (não bloqueiam; confirmados)
`devolver_original` fora do `_sem_interrupcao`; `voltar-versao` sem ponto não recupera pela fonte gravada; `CtrlCNaTroca` depois do `unittest.main()`; forma da fonte gravada; `stderr` do `git()` do `voltar-versao`; ponto e marca que ficam no Ctrl-C.

## Parecer
Aprovado, com aceite do usuário para os dois bugs abertos (um médio e um baixo). Nada perde trabalho nem deixa a pessoa sem o plugin; o F5-01 é a trava que pode ser contornada por um agente e deve ser tratado no PR seguinte (ou antes, a critério do dono). A pendência já registrada do spike continua: confirmar o checkout da tag na primeira atualização real.

## Reteste (volta 2, HEAD 1396c7e)
Mesmo método: worktree temporária, sem rede, `gh` bloqueado no PATH, `claude` falso, HOME e git temporários. Nenhum código foi alterado.

- Suíte: `python3 -m unittest discover -s tests` com `gh` bloqueado: 459 testes, OK, 108 s, sem `skip`.
- **F5-01 (corrigido).** Com `CLAUDECODE` e `CLAUDE_CODE_ENTRYPOINT` no ambiente, `$(which forge) atualizar`, `f=forge; $f atualizar`, `` `which forge` voltar-versao ``, `bash <<< "forge atualizar"`, `pty.spawn(['forge','atualizar'])` e `printf 's\n' | pty.spawn(['python3','bin/forge-atualizar'])` (o caso que antes trocava o plugin) saem com código 2 e a mensagem "isto é com você, não com o Claude... Não mudei nada". Nenhuma chamada ao `claude` falso, nenhuma branch nova. O ancestral `claude` sem variável é coberto por `Dentro.test_ancestral_chamado_claude_recusa...` (verde na suíte).
- **F5-02 (corrigido).** Caminho feliz: um texto só, sem bloco do doutor pedindo `forge-upgrade` no meio, termina com "Pronto", a branch `forge/upgrade-9.9.0`, o `gh pr create` e "Para voltar". Doutor com problema novo: "Os arquivos do projeto foram atualizados na branch ..., mas o doutor (a checagem de saúde do projeto) achou coisa nova", sem "Pronto" antes de "Algo não saiu como esperado". Ctrl-C na troca: "Interrompido. Nada foi atualizado: o Forge continua na versão 0.12.0.", sem ponto nem marca sobrando, e `voltar-versao` diz que não há ponto de retorno (não fala mais de uma 9.9.0 nunca instalada).
- **Regressão (sem `CLAUDECODE`, simulando o terminal da pessoa).** Caminho feliz, recusa (`n`), simulação falha, doutor novo com voltar aceito (plugin refixado em v0.12.0, branch da atualização guardada, projeto na `main`) e recusado, sem rede, árvore suja (`atualizar`, `--fixar`), `--fixar`, `voltar-versao` feliz e repetido, Ctrl-C: todos como no primeiro parecer. Nada perdeu trabalho e nenhum deixou a pessoa sem o plugin.

Parecer do reteste: aprovado, sem bugs abertos (F5-01 e F5-02 fechados). Ficam só os recomendados já registrados da review e a pendência do spike (confirmar o checkout da tag na primeira atualização real).
