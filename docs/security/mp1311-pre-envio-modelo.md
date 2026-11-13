---
tipo: revisao-seguranca
contrato: 1
pedido: melhorias-de-projeto-1311
branch: melhoria/mp1311-pre-envio-modelo
commit: 27c401073885775dff35b8c15d29f2595f3c2d85
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-13
---
# Review de segurança: melhorias-de-projeto-1311 (pré-envio no modelo, E1.34)

Head 27c40107, diff contra a base c5aa70e1: migração 0.47.1 (passo pre-envio), `forge-upgrade` com vários passos por versão, `forge-init`, modelo `pre-push.local` e modelo de PR, arquivos de pronto das stacks.

## Gatilhos
Hook de git que executa comando no envio (`pre-push.local`) e migração que grava arquivo executável no projeto: gatilho de controle e de execução de código. Sem segredo, dado pessoal, rede ou dependência nova.

## Achados
- A1 (recomendado) bin/forge-init:69 · `escapar` cobre `/`, `&` e `|`, não `\` nem quebra de linha; hoje sem efeito, porque o texto vem do arquivo de pronto da stack, que é do Forge.

## Sondas

## Detalhe dos achados
Verificado sem achado bloqueante:
- Stack lida do `CLAUDE.md` do projeto (migrar-pre-envio:23-30) é validada por `[a-z0-9-]+` e por existência do arquivo (linha 36) antes de virar caminho: sonda com `../../x` imprimiu aviso e não criou `.githooks/pre-push.local`.
- Valores gravados no `pre-push.local` vêm só de `stacks/<stack>/pronto.md` (conteúdo do Forge, não do projeto nem de entrada externa); substituição por `str.replace` na migração, sem shell. O teste PreEnvioDoModelo trava aspas simples no comando (tests/test_forge.py:1287).
- Não sobrescreve nem segue arquivo existente (`exists()` ou `is_symlink()`, migrar-pre-envio:56,61); idempotente (segunda rodada rc=0, sem criar).
- `.git/info/exclude`: caminho vem de `git rev-parse --git-path`; só acrescenta os arquivos criados.
- `forge-upgrade`: `migracoes_pendentes` restringe a `migrar` e `migrar-*` dentro de `migrations/` do próprio plugin; rótulo e LEIA derivados do nome do arquivo, sem entrada do projeto; execução sem shell (lista de argumentos).
- `pre-push.local` executa `bash -c "$rapido"` com comando do próprio repositório do projeto, mesma fronteira de confiança do `.githooks/pre-push` existente; falha fecha (exit 1) e orienta; ausência de código da stack pula com aviso, não abre brecha de bypass além do que o dono já controla.
- Modelo de PR é só texto.

Esforço de A1: P; dono: devops-engineer (ou dono do `forge-init`).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática e sondas locais; testes rodados: `tests.test_adotar` (24 OK) e `tests.test_forge.PreEnvioDoModelo` (14 OK). Suíte inteira: CI do PR (não há PR aberto; não conferido). Lacuna: nenhuma ferramenta de varredura invocada, nenhuma é necessária para este diff.
