---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-pv-d3-modelo
commit: 146b40503055203b10961594b7845fbbc7d55518
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: v0479-pv-d3-modelo (v0478 E57.78)

Escopo: diff `8ee73d15..146b4050` (PR-VERDE D3, E57.75): `templates/projeto/.githooks/pre-push` passa a rodar, em todo envio de branch, o comando de uma linha da chave opcional `registros` do `.forge/config.json`; mais texto em `templates/projeto/CLAUDE.md`, `stacks/*/pronto.md`, fragmento de changelog, mutantes e testes (`tests/test_prepush_so_docs.py`, classe `ConferenciaDeRegistros`).

## Gatilhos
Gatilhos: hook de envio (guarda do fluxo), execução de comando vindo de configuração do repositório.

## Achados
- A1 (bloqueante) templates/projeto/.githooks/pre-push:347 · O comando de registros herda o descritor 9 da trava do pre-push (aberto na linha 288 e fechado só para a etapa local, linha 154); processo que ele deixe vivo prende a trava e barra os envios seguintes da máquina. Correção: 9>&- nas linhas 347 e 349 e teste espelho.

## Sondas
- S1 · registros `setsid sleep 300 >/dev/null 2>&1 & echo $! > pid`, envio de código com pre-push.local, depois 2º envio com FORGE_PREPUSH_ESPERA=1 · espera: 2º envio rc 0 · obtido: rc 1, "a vez não chegou em 1 s; a checagem não rodou e o envio foi barrado"

## Detalhe dos achados
**A1.** Evidência: `templates/projeto/.githooks/pre-push:288` abre a trava (`exec 9>>"$trava"`) no shell principal e não a fecha; `:154` tira o descritor só da etapa local (`9>&-`, com o comentário "um servidor que a etapa deixe vivo não prende os envios"), garantia provada por `TravaDaChecagem.test_trava_nao_passa_para_a_etapa`. As invocações novas em `:347` e `:349` não fecham o 9, então o comando de registros (e tudo o que ele lançar em segundo plano) segura a trava por usuário (`forge-prepush-<uid>.lock`, comum a todos os projetos da máquina). Caminho: um `registros` que suba um servidor, um vigia ou um cache em segundo plano (caso comum em ferramenta de índice) deixa a trava presa; todo envio seguinte, em qualquer projeto do usuário, espera `FORGE_PREPUSH_ESPERA` e é barrado até o processo morrer. Não é contorno (falha fechada), mas é regressão provada de uma garantia que já existia (S1, sonda que reusa o arnês `TravaDaChecagem`). Severidade: baixa (disponibilidade do próprio usuário; a chave mora em `.forge/`, pasta protegida). Correção mínima: acrescentar `9>&-` às duas invocações (`timeout -- "$prazo_reg" bash -c "$registros" </dev/null 9>&-` e `bash -c "$registros" </dev/null 9>&-`) e um teste espelho de `test_trava_nao_passa_para_a_etapa` com o `setsid sleep` vindo de `registros`. Alternativa equivalente: liberar a trava (`exec 9>&-`) logo após `rodar_etapa`, antes do bloco de registros. Esforço: P. Dono: autor da E57.75.

## Avaliação dos pontos pedidos
**Execução de comando vindo de arquivo do repositório.** Não abre fronteira de confiança nova. O hook já executa conteúdo versionado do mesmo repositório: ele próprio (`core.hooksPath=.githooks`), o `.githooks/pre-push.local` (`:274-275`) e o PATH de `caminhos_extra` do mesmo `.forge/config.json` (`:231-269`). Quem escreve `.forge/config.json` escreve também `.githooks/`; para os agentes, as duas pastas estão em `PASTAS_PROTEGIDAS` (`hooks/conformidade.py:330`). O valor passa por `json` sob `python3 -I` (sem módulo plantado na raiz), é recusado quando não é texto ou não é imprimível (`:335`, barra quebra de linha, escape de terminal e separadores Unicode), roda com `</dev/null` a partir da raiz, depois de o laço de refs e o `unset GIT_DIR ...` já terem valido, e o prazo é conferido só por `case` (`:342`), sem aritmética sobre o valor do ambiente. Sem injeção: o comando é, por desenho, o texto da chave. Testes de abuso: `ConferenciaDeRegistros` (9 casos, rodados aqui: OK).

**"Só avisa" (falha aberta).** Os desvios que deixam o envio seguir são: sem `python3` (`:326`, com aviso), config ilegível ou com raiz que não é objeto (aviso no Python), config que é link (`:325`, sem aviso, mesmo critério de `caminhos_extra` em `:238`; provado por `test_config_que_e_link_nao_e_lido`) e, sem `timeout` no PATH, a conferência sem prazo (`:349`). Aceitável: a conferência é adiantamento do que o CI do projeto reprova, não a guarda que decide; não há variável nem opção que a pule; e quem consegue trocar o config por link ou tirar o `python3` do PATH consegue editar o próprio hook. Nenhum desses caminhos afrouxa checagem anterior.

**Só aperta?** Sim, exceto A1. O bloco fica depois de todas as checagens anteriores e antes do `exit 0` final; só acrescenta saídas `exit 1` (comando fora de 0, chave inválida, prazo inválido); envio só de remoção não roda o comando (`refs_branches`, provado por `test_envio_so_de_remocao_nao_roda`). A1 é aperto indevido (barra envios alheios), não afrouxamento.

Observação sem achado: diferente da etapa local, o comando de registros não entra no encerramento de órfão (`encerrar_etapa`); se quem pediu o envio morre, ele segue até o prazo (180 s). Limitado pelo `timeout`; fica como nota.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Suíte: sem PR nem execução de CI neste head (`gh run list` vazio); rodei só `tests.test_prepush_so_docs.ConferenciaDeRegistros` (9 OK) e a sonda S1; o merge segue exigindo CI verde. Ferramentas ausentes no ambiente (lacuna): `gitleaks`, `shellcheck`, `semgrep`.
