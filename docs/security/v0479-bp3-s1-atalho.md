---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-bp3-s1-atalho
commit: 3e53ae726c2891e00dbcdcc66cb0ebc54318cba8
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: v0479-bp3-s1-atalho

Rodada 1, etapa E39.12 do pedido v0478 (BP3 S1, decisão D1 e D4 do dono de 2026-11-20 07:47). Escopo: `git diff 004ce869..3e53ae72` (9 arquivos): `scripts/jarvis`, `scripts/jarvis-forge`, `README.md`, fragmento do changelog, `tests/test_atalho_duravel.py` e quatro arquivos de mutantes. Revisão estática, com o teste novo e duas sondas rodadas numa cópia temporária (o próprio harness do teste: `claude`, `date` e `sleep` falsos, sem sessão real nem API).

**Parecer: aprovado**, com duas recomendações (A1, A2) que voltam ao autor antes do merge (`R-REVIEW`).

## Gatilhos
Gatilhos: execução de binário escolhido em tempo de execução (resolução do `claude`), reabertura automática de sessão em modo de permissão automático com controle remoto e canal externo, escrita de registro no estado do usuário.

## Achados
- A1 (recomendado) scripts/jarvis:124 · FORGE_QUEDA_JANELA=0 passa na validação e desliga o teto: nenhuma queda fica na janela, o laço reabre sem limite (sonda S1). Aceitar só inteiro >= 1 (ou mínimo 60), igual em scripts/jarvis-forge:288, com teste.
- A2 (recomendado) scripts/jarvis:130 · saída 143 (kill/pkill deliberado do claude) conta como queda e reabre em 10 s com --remote-control e o canal; parar de vez exige matar a sessão do tmux. Documentar no README como parar a sessão durável (ou tratar 143 como parada); igual em scripts/jarvis-forge:294.

## Sondas

## Detalhe dos achados
**A1.** Evidência: `scripts/jarvis:124` e `scripts/jarvis-forge:288` aceitam qualquer sequência de dígitos, inclusive `0`; em `supervisionar`, com janela 0, `agora - t < 0` nunca vale, a lista de quedas recentes fica vazia e o teto de 3 nunca é atingido. Sonda (fora do bloco, porque não prova bloqueante): 8 saídas 137 seguidas com `FORGE_QUEDA_ESPERA=0 FORGE_QUEDA_JANELA=0` deram 9 execuções e nenhuma linha `acao=desiste` no `quedas.log`; o esperado pela D1 é parar na 4.ª queda. Caminho de ataque: só quem controla o ambiente do usuário define a variável, e esse já controla a sessão; por isso é recomendação, não vulnerabilidade. O efeito é um laço de reaberturas sem fim (com espera 0, laço apertado) que contraria o "teto 3 em 30 min" da D1. Severidade: baixa. Correção mínima: `case "$janela" in ''|*[!0-9]*|0) janela=1800 ;; esac` (ou exigir um mínimo), nos dois scripts, e um caso no `test_janela_configuravel_so_com_numero`. Esforço: P. Dono: `devops-engineer`.

**A2.** Evidência: `scripts/jarvis:130` e `scripts/jarvis-forge:294` excluem só 129 e 130; a sonda S2 (saídas 143 e 0) deu duas execuções, a segunda com `--continue --permission-mode auto --remote-control`. Caminho: a pessoa que mata o `claude` com `kill`/`pkill` para interromper uma sessão que saiu do controle vê a sessão voltar em 10 s, de novo ligada ao controle remoto e ao canal externo. A reabertura fica parada no prompt (o `--continue` não retoma ferramenta sozinho) e o modo de permissão não muda, então não há escalada; o risco é a parada de emergência não parar. Severidade: baixa. Correção mínima: uma frase no `README.md:41` ("para encerrar de vez: `/exit`, Ctrl+C ou `tmux kill-session -t <sessão>`; `kill` no `claude` conta como queda"), ou incluir 143 entre as saídas que encerram, se o dono preferir (a D1 diz "saída anormal" sem listar sinais). Esforço: P. Dono: `devops-engineer`.

**Conferido sem achado.**
- Modo de permissão: a reabertura repete os mesmos argumentos (`scripts/jarvis:152`, `scripts/jarvis-forge:336`); só prefixa `--continue` quando falta (`scripts/jarvis:147`). Nenhum caminho acrescenta flag que pule permissão; provado por `test_reabertura_mantem_o_modo_automatico_e_o_resto_dos_argumentos` e `test_reabertura_de_conversa_ja_existente_nao_duplica_continue`.
- Escolha do binário (`resolver_claude`, `scripts/jarvis:66`): candidatos são `$HOME/.local/bin/claude` e o primeiro do PATH, só caminho absoluto de arquivo executável; ambos já são executáveis pelo usuário e o do PATH já rodava antes (`claude plugin list`). Quem planta um binário em `~/.local/bin` já tem a conta do usuário: sem ganho novo. A saída de `--version` só entra filtrada por `^[0-9]+(\.[0-9]+)+` e com tempo limite de 10 s. Com o primeiro do PATH relativo (PATH com `.`), o fallback ainda usa o `command -v claude` de antes: sem regressão, embora o comentário "nunca o diretório atual" valha só para a lista de candidatos.
- Registro `quedas.log` (`scripts/jarvis:117`): só data, rótulo do projeto, código, tentativa e ação; `XDG_STATE_HOME` relativo cai na pasta padrão; falha de escrita não interrompe. Provado por `test_quedas_log_so_com_data_projeto_saida_e_tentativa` (a saída do `claude` falso com um marcador não chega ao arquivo) e `test_xdg_relativo_cai_na_pasta_padrao`.
- Variáveis de ajuste: `FORGE_QUEDA_ESPERA` com texto de comando cai no padrão (`test_espera_padrao_dez_segundos_e_configuravel`, entrada `x; touch /tmp/nao`); fora do caso do A1, nada do ambiente chega a avaliação.
- Aviso fora do tmux (D4): só avisa, não bloqueia nem muda argumentos.

Suíte: o teste novo (`tests/test_atalho_duravel.py`) rodou nesta cópia: 68 testes, OK. A bateria inteira é a do CI do PR para a `develop`, portão do merge; não havia PR nem CI no head na hora deste parecer (o brief pediu parecer sem PR e sem suíte local).

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. A reabertura automática com controle remoto e canal externo, sem pessoa no terminal, é decisão do dono (D1 da BP3), limitada pelo teto. Não há modelo de ameaças da BP3 em `docs/security/ameacas/`; o desenho da BP3 (E39.1) não trouxe casos de abuso, e os testes do autor cobrem os casos acima.
Ferramentas: leitura do diff, o teste novo e as duas sondas no harness dele. Faltaram no ambiente (lacuna, nada instalado): varredor de segredos, linter de shell, SAST e linter de workflow; nenhum segredo à vista no diff lido.
