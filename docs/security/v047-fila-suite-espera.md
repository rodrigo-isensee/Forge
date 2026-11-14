---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-fila-suite-espera
commit: 1e04c56fe51c0165e112a1fcd5aab23ea52cc666
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-14
---
# Review de segurança: v047 (FILA-SUITE-ESPERA, PR 553)

Intervalo `origin/develop..1e04c56f` (3 commits): `.githooks/pre-push` (posição na fila, aviso de trava velha, dona morta por `kill -0`, registro de envio barrado, espera da trava por laço `flock -n`), `docs/hooks.md`, fragmento de changelog, `tests/test_pre_push_fila.py` e dois arquivos de mutantes. Etapa E1.172, instância que não fez a entrega.

## Gatilhos
`R-SEGURANCA`: hook git de controle (o `pre-push` é guarda do fluxo, `R-FLUXO`/`R-VERIFY`) e escrita de arquivo em pasta temporária possivelmente compartilhada.

## Achados
- A1 (recomendado) .githooks/pre-push:525 · Na linha de conferir, o pid lido da trava vai ao comando sugerido sem exigir número (no ramo "sem troca de dona"); quem copia e cola rodaria o texto gravado na trava. Só o próprio usuário grava ali; trocar pid não numérico por <pid>.

## Sondas

## Detalhe dos achados
**A1** · evidência: `.githooks/pre-push:518` lê `pid` de `texto_da_trava` (filtrado a imprimíveis, até 200 bytes, sem espaço depois do `read`) e `.githooks/pre-push:525` o interpola em `ps -o pid,etime,args -p ${pid}`. No ramo da idade (> 2100 s) o pid não passa pelo `^[0-9]+$` do ramo da dona morta. Sonda local: `printf 'pid 1;id ns 9 desde x\n' | LC_ALL=C tr -cd '[:print:]'` mantém `1;id`. · caminho de ataque: exige gravar a trava, que fica em pasta do próprio usuário (modo 700, conferida por `trava_confere` com `-O` no descritor aberto); quem grava ali já tem a conta, logo não há ganho de privilégio. O efeito seria só induzir um copiar e colar. · severidade: informativa. · correção mínima: antes do `echo` da linha 525, `[[ "$pid" =~ ^[0-9]+$ ]] || pid=""` (o texto já cai em `<pid>`). · esforço: P. · dono: o autor da entrega (devops-engineer/tech-lead do pedido).

### O que foi conferido e está correto
- **Saída ao terminal (injeção de escape):** tudo que vem de outro processo passa por `texto_da_trava` (só imprimíveis) e campos cortados em 12/8 caracteres (`:506`); as senhas da fila passam por `quem_na_fila`, que deixa só dígitos e hífen (`:496`). Sem caminho para sequência de controle.
- **`kill -0` (`pid_sumiu`, `:512-516`):** não envia sinal; só roda com pid numérico e do mesmo namespace (`:521`); "sem permissão" conta como vivo; o resultado só gera aviso. Nada libera a trava, apaga senha ou pula a fila (`R-TETO` mantida): reuso de pid ou pid forjado no máximo cala ou dispara um aviso.
- **Registro de barrados (`registrar_barrado`, `:527-532`):** recusa link, recusa arquivo de outro dono, `umask 077`, só acrescenta linha de campos fixos (data, `push|suite`, número validado). A janela entre o teste `-L` e o `>>` só é explorável por quem já escreve na pasta 700 do usuário. Crescimento: uma linha por envio barrado, desprezível.
- **`FORGE_FILA_INTERVALO`:** validado como inteiro (`:409`), como `FORGE_TRAVA_ESPERA`; vem do ambiente do próprio usuário (valor 0 só aumenta o volume de linhas; valor enorme só adia a linha).
- **Troca de `flock -w` por laço `flock -n` + `sleep 0.2`:** a exclusão continua sendo o `flock` do kernel no descritor 9; o limite `limite_ns` e o `barrar` seguem valendo; não abre corrida que deixe duas suítes rodarem.
- **Docs e changelog:** descrevem o comportamento real, sem afrouxar recusa existente.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Suíte inteira: CI do PR 553 no head `1e04c56fe51c0165e112a1fcd5aab23ea52cc666` (run 43597037335, conclusão `success`; a única checagem vermelha é a `catraca`, que pede o rótulo do dono, fora da segurança). Local: `python3 -m unittest tests.test_pre_push_fila` (8 testes, OK, inclui link na fila e no registro, dona morta e de outro namespace); `shellcheck -S warning .githooks/pre-push` rc=0. Faltaram no ambiente: gitleaks, zizmor, actionlint (a entrega não toca workflow nem traz segredo; registrado como lacuna, `R-CUSTO`).
