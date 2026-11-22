---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-ambiente-recriacao
commit: a0be36e6222bb41cf7721d58ec668aeff8928044
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-22
---
# Review de segurança: v0480-ambiente-recriacao (E119.11, revalidação da volta de CI)

Delta lido (`forge-check parecer delta`): `93a2123c..a0be36e6`, sem o que veio da develop. No domínio: `bin/forge-testes`, `scripts/preparar-estacao.sh` e `templates/projeto/.devcontainer/preparar-ambiente.sh`. Fora do domínio (não relidos): `tests/pesos-d4.json`, `tests/test_ambiente_recriacao.py`, `tests/test_forge.py` e `tests/test_testes_tocados.py`. A rodada anterior (parecer no `93a2123c`) fica no git e não é recopiada: A1 e A2 continuam fechados; C1 e C2 continuam abertos como cartões, sem mudança.

## Gatilhos
Gatilhos: comando como root fora do sandbox no postStart, download e execução de código de terceiro, alteração do PATH do shell de root, modelo de projeto.

## Detalhe dos achados

**Conferido no delta, sem achado.**
- `scripts/preparar-estacao.sh:198` e `templates/projeto/.devcontainer/preparar-ambiente.sh:110`: o til da mensagem virou `$HOME`. A mensagem só entra na lista de feitos (`fez`, `scripts/preparar-estacao.sh:64`) e é impressa como argumento de `printf` com formato fixo, nunca como formato nem por `eval`. A linha gravada no `.bashrc` continua literal (aspas simples), sem mudança.
- `scripts/preparar-estacao.sh:195`: o `grep` virou `command grep`, que ignora alias ou função de mesmo nome e segue procurando no PATH como antes; regex e efeito iguais.
- `bin/forge-testes:192`, `:235` e `:262`: só o mapa de testes afetados ganhou entradas (os scripts do ambiente e o `devcontainer.json` passam a disparar `test_ambiente_recriacao`). Isso muda só a seleção local; o CI roda a bateria inteira, então nenhum portão afrouxa.
- O ponto único do git e o PATH sem curl montado com links ficam só nos testes, fora do domínio. Nenhum segredo no delta.

## Riscos aceitos e ferramentas
Nenhum risco aceito novo; o aceite do instalador sem soma fixa continua valendo como estava. Rodados: `bash -n` nos dois scripts (ok) e `python3 -m unittest tests.test_ambiente_recriacao` (10, OK). Suíte inteira não rodada (o brief pede sem suíte local); sem PR nem CI para citar, o CI verde do PR continua condição do merge (`R-SEGURANCA`, `R-REVIEW`). Faltaram shellcheck e gitleaks (fora do PATH; nada instalado).
