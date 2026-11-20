---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-pv-m1-medida
commit: 5221863e2d25308ec35dfae91241e01ea6790ece
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: v0478 (E57.30, revalidação do PR-VERDE M1 no head 5221863e)

Revalidação por delta (`R-REVIEW`): li só `forge-check parecer delta docs/security/v0479-pv-m1-medida.md`, intervalo `c5c0a232..5221863e`. No domínio, só `bin/forge-placar` (+2/-2: o conjunto `AUTORES_DEPENDABOT` em `:792` e a comparação exata em `:864`, mais a frase do docstring em `:75`). Fora do domínio: `tests/evals/test_placar.py` e duas specs de mutante. O aviso do delta sobre o merge `1be9b4b` não muda nada: o único arquivo do domínio no intervalo é o já citado. A rodada anterior (head c5c0a232) está no git e não é recopiada. Não rodei a suíte local (o brief não pede); a suíte inteira é do CI do PR.

## Gatilhos
Gatilhos: nenhum (o delta não toca `.github/`, `hooks/`, `docs/regras/`, controle, segredo, dependência nem rede).

## Achados

## Sondas

## Detalhe dos achados
Estado dos achados anteriores:
- **A1** (recomendado, `bin/forge-placar:863` na rodada anterior) **resolvido** em `bin/forge-placar:792` e `:864`. Refiz a sonda com a mesma entrada: PR com 1.º head `CI failure` e `Catraca success`, `ci-primeira --ate 2026-11-20 --dias 7`. Resultados:
  - autor `{"login":"not-dependabot-fan"}` → `total: verde na 1.ª 0.00% (0/1)`, rc 0 (antes: `nenhum PR aberto na janela`);
  - autor `fulano` → mesma saída;
  - `{"login":"app/dependabot"}` e `"dependabot[bot]"` → `nenhum PR aberto na janela`, ou seja, ficam fora como a D7 manda.
  - Variantes de borda: `{"login":"Dependabot[bot]"}`, `{"login":"dependabot"}`, `null` e `["app/dependabot"]` (lista) contam na taxa, sem exceção.

  O erro possível agora só leva a contar um PR do bot, e isso puxa a taxa para baixo, nunca a infla. Para quem não é o bot, não há mais caminho para tirar o próprio vermelho da medida. O teste `test_dependabot_e_o_login_exato_nao_a_substring` (`tests/evals/test_placar.py:872`) cobre os dois logins exatos e os três casos que devem continuar contando.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Ferramentas: `forge-check parecer delta`, leitura do diff e sondas locais com o próprio `bin/forge-placar` (`python3 -I`, sem rede). `gitleaks`, `semgrep` e `zizmor` não estão no PATH: lacuna registrada, e o delta não toca workflow nem segredo.

## Parecer
Aprovado no head 5221863e. O A1 da rodada anterior está resolvido e não há achado novo.
