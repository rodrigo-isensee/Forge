---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-bp3-s1-atalho
commit: 7bd41f53a5a969a6a748e969425cb8ef2c816a05
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: v0479-bp3-s1-atalho

Rodada 2 (volta), etapa E39.12 do pedido v0478 (BP3 S1). A rodada 1 (aprovado no head 3e53ae72, A1 e A2 recomendados) fica no git. Delta lido: `forge-check parecer delta` de 3e53ae72 a 4d033ac4; no domínio, `scripts/jarvis`, `scripts/jarvis-forge`, `scripts/jarvis-comum.sh` (novo, carregado por `source`) e `tests/test_oraculo_sempre_atual.py` (uma linha: o Mundo copia o arquivo comum, 45f429a4); fora do domínio, o README (lido no trecho do A2), testes do atalho, índice, changelog e mutantes. Já lido na rodada 1 e sem mudança de lógica: `resolver_claude`, `registrar_queda` e `supervisionar`, movidos para o arquivo comum, fora as linhas 50, 69 e 75.

**Parecer: reprovado.** A1 e A2 estão resolvidos; o `source` do arquivo comum abriu um caminho novo (A3, bloqueante) e a validação da janela ainda deixa o teto sumir com número grande (A4, recomendado).

## Gatilhos
Gatilhos: execução de código carregado em tempo de execução (`source` do arquivo comum), execução de binário escolhido em tempo de execução, reabertura automática de sessão em modo de permissão automático com controle remoto e canal externo, escrita de registro no estado do usuário.

## Achados
- A3 (bloqueante) scripts/jarvis:59 · o source acha a pasta pelo BASH_SOURCE relativo depois do cd do projeto (linha 23): `bash scripts/jarvis --sem-tmux proj` carrega ~/proj/scripts/jarvis-comum.sh, código do projeto, antes de qualquer confiança, e sem ele quebra (S1, S2). Resolver a pasta antes do cd.
- A4 (recomendado) scripts/jarvis-comum.sh:68 · FORGE_QUEDA_JANELA com 20 dígitos estoura o inteiro, o -lt falha e o teto some (11 execuções, nenhum desiste); 08 ou 09 abortam na conta $((janela / 60)) e a 1.ª queda não reabre. Aceitar só 1 a 6 dígitos sem zero à esquerda, senão 1800, com teste.

## Sondas
- S1 · cd <cópia do Forge>; HOME=<h> bash scripts/jarvis --sem-tmux proj, com <h>/proj/scripts/jarvis-comum.sh = "echo MARCA-DO-PROJETO >&2; exit 42" · espera: carregar <cópia>/scripts/jarvis-comum.sh e abrir o claude · obtido: MARCA-DO-PROJETO, saída 42
- S2 · o mesmo comando de S1 sem o arquivo no projeto · espera: abrir o claude (como em 3e53ae72) · obtido: "line 59: <h>/proj/scripts/jarvis-comum.sh: No such file or directory", saída 1

## Detalhe dos achados
**A1 (rodada 1): resolvido.** `scripts/jarvis-comum.sh:69` devolve 1800 a toda janela sem dígito de 1 a 9. Sonda refeita no harness do teste, nos dois atalhos, 10 saídas 137 com espera 0: janela `0`, `00`, ` 0` e `-1` deram 4 execuções e uma linha `desiste`; prova em `test_janela_zero_nao_tira_o_teto_de_reaberturas`. Janela `1` é aceita e, com relógio real e espera de 10 s, deixa as quedas fora da janela: ajuste deliberado de quem controla o ambiente, não achado (o README chama as duas variáveis de "ajustes de teste").

**A2 (rodada 1): resolvido.** `scripts/jarvis-comum.sh:75` trata 143 como parada. Sonda refeita: saídas 143 e 0 deram uma execução e saída 143, nos dois atalhos; 137 e 0 seguem reabrindo (2 execuções). `README.md:41` diz como encerrar de vez (`/exit`, Ctrl+C, `kill`, `tmux kill-session -t jarvis-<projeto>`); provas em `test_interrupcao_da_pessoa_e_terminal_fechado_nao_reabrem` e `test_readme_diz_como_encerrar_de_vez`.

**A3.** Evidência: `scripts/jarvis:23` faz `cd "$HOME/<projeto>"` e só depois `scripts/jarvis:59` calcula `$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/jarvis-comum.sh`. Pelo trampolim de `scripts/instalar-atalho.sh` o caminho é absoluto (o installPath do cache) e o arquivo certo é carregado; com o script chamado por caminho relativo (`scripts/jarvis <projeto>` de dentro da cópia do Forge, uso de quem mantém a fábrica), a pasta vira `<projeto>/scripts`. Caminho de ataque: o autor de um repositório clonado em `$HOME` põe `scripts/jarvis-comum.sh` nele; quem abre esse projeto pelo atalho relativo executa o arquivo com a própria conta, no shell do atalho, antes do diálogo de confiança do Claude Code e fora do sandbox (S1). O mesmo defeito já existia em 3e53ae72 no `eu=` da reabertura no tmux (`scripts/jarvis:55`) e na `raiz` de `atualizar_plugin` (`scripts/jarvis:42`, que roda `<projeto>/bin/forge-sempre-atual` quando o projeto não tem `.git`); o `source` o leva também ao `--sem-tmux` e à sessão já dentro do tmux, e sem o arquivo no projeto o atalho relativo, que funcionava, sai com 1 (S2). Severidade: média (execução de código do projeto, com pré-condição de chamada relativa). Correção mínima: no topo de `scripts/jarvis`, antes da linha 23, `aqui="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"`, e usar `$aqui` nos três lugares que hoje recalculam a pasta depois do `cd`: a `raiz` de `atualizar_plugin` (linha 42), o `eu=` (linha 55) e o `source` (linha 59); em `scripts/jarvis-forge`, o mesmo antes do `cd "$HOME/Forge"` (linhas 216 e 220) e no `source` (linha 223), por consistência (lá o `cd` vai à própria cópia do Forge, sem caminho de ataque). Teste: S1 e S2 como casos de `tests/test_atalho_duravel.py` (chamada relativa com projeto que traz o arquivo: não o carrega; sem o arquivo: abre). Esforço: P. Dono: `devops-engineer`.

**A4.** Evidência: `scripts/jarvis-comum.sh:68-69` aceitam qualquer quantidade de dígitos. Sonda no harness do teste, 10 saídas 137, espera 0, nos dois atalhos: `FORGE_QUEDA_JANELA=99999999999999999999` deu 11 execuções, nenhum `desiste` e a mensagem "em 129437993857537365 min" (o `[ ... -lt "$janela" ]` não lê o número e nenhuma queda fica na conta); `08` deu "value too great for base" na linha 90 e a sessão terminou sem reabrir. Caminho de ataque: só quem controla o ambiente do usuário, que já controla a sessão; por isso recomendação, como o A1. Efeito: o teto da D1 some (o efeito do A1, por outra entrada da mesma família) ou a reabertura falha. Severidade: baixa. Correção mínima: `case "$janela" in [1-9]|[1-9][0-9]|[1-9][0-9][0-9]|[1-9][0-9][0-9][0-9]|[1-9][0-9][0-9][0-9][0-9]|[1-9][0-9][0-9][0-9][0-9][0-9]) ;; *) janela=1800 ;; esac` (o mesmo molde para `FORGE_QUEDA_ESPERA`, que chega ao `sleep`), com os casos `99999999999999999999`, `08` e `010` no `test_janela_configuravel_so_com_numero`. Esforço: P. Dono: `devops-engineer`.

**Conferido sem achado no delta.**
- Quem pode trocar o arquivo comum: ele é lido da pasta do próprio script; pelo trampolim, `<cache do plugin>/<versão>/scripts/`, da mesma versão do `scripts/jarvis` que o carrega. Quem escreve ali já pode trocar o próprio `scripts/jarvis`: sem fronteira nova, fora o caso do A3.
- O arquivo comum não roda sozinho (sem bit de execução; só funções e uma variável) e é carregado depois de `prefixo` e `rotulo` definidos (`scripts/jarvis:28`, `scripts/jarvis-forge:221`).
- `tests/test_oraculo_sempre_atual.py`: a linha nova só copia o arquivo comum para a pasta falsa do teste; nada muda no que o oráculo verifica.

Teste do atalho (`tests/test_atalho_duravel.py`) rodado nesta cópia no head 4d033ac4: 71 casos, sem falha. A bateria inteira é a do CI do PR para a `develop`; não há PR nem CI neste head (o brief pede parecer sem PR e sem bateria local).

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Ferramentas: o delta do `forge-check parecer delta`, o teste do atalho e as sondas no harness dele e numa cópia em pasta temporária (claude falso, sem sessão real nem API). Faltaram no ambiente (lacuna, nada instalado): varredor de segredos, linter de shell, SAST e linter de workflow; nenhum segredo à vista no delta.
