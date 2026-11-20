---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-bp3-s1-atalho
commit: e686f2eb464aafc1dc03b9622a1fc45c640ab18f
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: v0479-bp3-s1-atalho

Rodada 3 (volta), etapa E39.12 do pedido v0478 (BP3 S1). As rodadas 1 (3e53ae72) e 2 (7bd41f53, reprovado por A3) ficam no git. Delta lido: `forge-check parecer delta` de 7bd41f53 a e686f2eb; no domínio, `scripts/jarvis`, `scripts/jarvis-forge`, `scripts/jarvis-comum.sh` (linhas 68-69), `bin/forge-testes` (uma linha do mapa: o README passa a rodar `test_atalho_duravel`) e `tests/test_oraculo_sempre_atual.py` (a cópia do arquivo comum no Mundo, já lida na rodada 2); fora do domínio, `tests/test_atalho_duravel.py` (classe nova `ChamadaPorCaminhoRelativo` e os casos do A4), mutantes e o fragmento do changelog. Já lido e sem mudança: `resolver_claude`, `registrar_queda` e o laço de `supervisionar`.

**Parecer: aprovado.** A3 e A4 estão resolvidos, com sonda refeita fora do harness do teste e caso de teste para cada um; nada novo no delta.

Gatilhos: execução de código carregado em tempo de execução (`source` do arquivo comum), execução de binário escolhido em tempo de execução, reabertura automática de sessão em modo de permissão automático com controle remoto e canal externo, escrita de registro no estado do usuário.

## Sondas
- S1 · na cópia: HOME=<h> FORGE_ABERTURA_FEITA=1 bash scripts/jarvis --sem-tmux proj, com <h>/proj/scripts/jarvis-comum.sh = "echo MARCA-DO-PROJETO >&2; exit 42" · espera: carregar o arquivo da cópia e abrir o claude · obtido: sem a marca, saída 0, 1 execução
- S2 · o comando de S1 sem o arquivo no projeto · espera: abrir o claude · obtido: saída 0, 1 execução, sem "No such file"
- S3 · TMUX=x FORGE_QUEDA_ESPERA=0 FORGE_QUEDA_JANELA=<v> bash scripts/jarvis proj, 10 saídas 137, v = 99999999999999999999, 08, 09, 010, 1234567 · espera: janela 1800, 4 execuções e um desiste · obtido: nos cinco, 4 execuções, um desiste, "em 30 min", sem erro de base
- S4 · como S3 com scripts/jarvis-forge --dev, v = 99999999999999999999 e 08; e scripts/jarvis com v = 999999 · espera: 4 execuções e um desiste · obtido: 4 execuções e um desiste nos três; 999999 aceito ("em 16666 min")

## Detalhe dos achados
**A3 (rodada 2, bloqueante): resolvido.** `scripts/jarvis:15` guarda `aqui` antes do `cd` da linha 25 e as quatro pastas que eram recalculadas depois dele usam `$aqui`: a `raiz` de `atualizar_plugin` (linha 45), o `eu=` (58), o `source` (62) e o `doutor` (94, que a correção mínima não listava e o autor cobriu). `scripts/jarvis-forge:19` faz o mesmo (linhas 189, 225 e 237). Provas: S1 e S2 e, no teste, `test_projeto_com_arquivo_comum_falso_nao_e_carregado`, `test_projeto_sem_arquivo_comum_abre_normalmente`, `test_atualizacao_do_plugin_nao_roda_ferramenta_do_projeto` e `test_reabertura_no_tmux_usa_o_caminho_absoluto_do_script`, nos dois atalhos.

**A4 (rodada 2, recomendado): resolvido.** `scripts/jarvis-comum.sh:69` aceita só 1 a 6 dígitos sem zero à esquerda, senão 1800 (S3, S4); prova em `test_janela_configuravel_so_com_numero` (os valores do A4 mais `1234567`, `-5`, `1.5` e ` 5`) e nos limites 1 e 999999. `FORGE_QUEDA_ESPERA` não ganhou o mesmo molde: só chega ao `sleep` (que lê `08` em decimal), não entra em conta nem no teto, e um valor enorme só adia a reabertura, efeito que só quem controla o ambiente produz; sem achado.

**Conferido sem achado no delta.**
- `aqui` com `CDPATH` exportado e chamada relativa: o `cd` imprime a pasta e `aqui` fica com duas linhas, o `source` falha e o atalho sai com erro, sem carregar código de outra pasta (fecha, não abre); o mesmo padrão já existia antes do delta e o `CDPATH` é do próprio usuário.
- `bin/forge-testes`: a linha muda só o mapa de quais testes rodam quando o README muda; não toca controle nem bloqueio.

Teste do atalho (`tests/test_atalho_duravel.py`) rodado nesta cópia no head e686f2eb: 81 casos, sem falha. A bateria inteira é a do CI do PR para a `develop`; não há PR nem CI neste head (o brief pede parecer sem PR e sem bateria local).

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Ferramentas: o delta do `forge-check parecer delta`, o teste do atalho e as sondas numa cópia em pasta temporária (claude falso, sem sessão real nem API). Faltaram no ambiente (lacuna, nada instalado): varredor de segredos, linter de shell, SAST e linter de workflow; nenhum segredo à vista no delta.
