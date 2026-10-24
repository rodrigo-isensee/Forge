---
tipo: revisao-seguranca
contrato: 1
pedido: bateria-shellcheck-prepush
branch: melhoria/bateria-shellcheck-prepush
commit: c6fc94683001f5f8db2e94b2fa2152f0c34da167
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-22
---
# Review de segurança: bateria-shellcheck-prepush

Escopo revisado: `git diff a3dbe22..c6fc946` (8afd7b3 e c6fc946): `.githooks/pre-push` (linhas 58 e 242), `tests/test_pre_push_shellcheck.py` (novo) e `changelog.d/bateria-shellcheck-prepush.md` (novo).

## Gatilhos
Controles do Forge (`R-SEGURANCA`): o `.githooks/pre-push` é o controle local de `R-MAIN`, `R-VERIFY` e da fila de `R-TETO`. Nenhum outro gatilho (sem segredo, rede, dependência nem workflow tocado).

## Achados

## Detalhe dos achados
Sem achado bloqueante. Verificações feitas:

- **Linha 58 (`fila_vivas`), equivalência lógica.** Antes: `[ -e f ] && [ ! -L f ] || continue` pula quando `!(-e && !-L)`, isto é, `!-e || -L`. Depois: `if [ ! -e f ] || [ -L f ]; then continue; fi`, a mesma condição por De Morgan. Sonda em `$TMPDIR` com arquivo regular, pasta, link para arquivo, link pendente e caminho ausente: as duas formas dão o mesmo resultado nos cinco casos (regular e pasta contam; link, link pendente e ausente são pulados). Nenhuma senha que antes contava passa a ser pulada, nem o contrário; a forma `if` também não depende de o primeiro teste dar falso para cair no `continue` (o risco que a SC2015 aponta). A fila, a trava e o bloqueio de envio direto às branches protegidas não foram tocados pelo diff.
- **Linha 242 (diretiva SC2317).** Posta antes da definição de `parar`, a diretiva vale só para o corpo dessa função (escopo de função), não para o resto do hook. `parar` é chamada de fato pelo `trap parar TERM INT HUP` (linha 249) e o corpo (4 linhas) não tem código morto: ignora novos sinais, encerra só o filho da suíte, avisa e sai com 1. A diretiva não esconde código inalcançável real hoje e traz o motivo na mesma linha.
- **Teste sem rede (`R-CUSTO`).** `tests/test_pre_push_shellcheck.py` só lê o arquivo do hook e, se a ferramenta de análise estática estiver no PATH, a executa localmente; nenhum acesso de rede nem serviço pago. Rodado aqui: 2 testes verdes e 1 pulado (ferramenta ausente).
- **Changelog.** Só texto; sem efeito de segurança.

Recomendações (não bloqueantes, informativas):
- R1 (informativa, P, `tech-lead`): como a diretiva cobre a função inteira, código inalcançável acrescentado no futuro dentro de `parar` deixaria de ser apontado. O teste novo já exige motivo em toda diretiva; o review de mudanças futuras em `parar` deve lembrar disso. Nada a mudar agora.
- R2 (informativa, P, `devops-engineer`): o teste que roda a ferramenta é pulado quando ela falta no PATH; a garantia real fica no job do CI (`.github/workflows/ci.yml:157`, que inclui `.githooks/pre-push`). Aceitável, já que o CI é o portão; a confirmação de que o job passa com a diretiva seguida de comentário vem do próprio CI do PR.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática do diff, sonda local da condição da linha 58 em `$TMPDIR` e a execução do teste novo. Lacuna: a ferramenta de análise estática de scripts não está no PATH desta estação (não instalada, conforme `R-CUSTO` e a postura do papel); a verificação dela fica com o job do CI.
