---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-placar-prometido
commit: b57a96761cfd79434411d1978ff1e537a07c8b7c
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-22
---
# Review de segurança: v0478 (E110.7, revalidação do placar prometido)

Revalidação por delta da rodada anterior (`afc7083d`, E110.3; o texto dela fica no git). Delta lido: `forge-check parecer delta docs/security/v0480-placar-prometido.md`, intervalo `afc7083d..b57a9676` sem o que veio da `develop`; no domínio, `bin/forge-placar` (`:111` regex `PROMETIDO`, `:555` texto da falta) e `bin/forge-testes` (`:196` mapa ganha `test_placar_prometido`). Fora do domínio: o teste do pedido, dois specs de mutantes, `tests/pesos-d4.json`, `tests/test_testes_tocados.py` e o fragmento de changelog.

## Gatilhos
Gatilhos: nenhum (inalterado desde a rodada anterior; sem hook, regra, catraca, `.github/`, dependência, segredo ou dado pessoal).

## Detalhe
**A1 da rodada anterior (recomendado): corrigido.** `bin/forge-placar:111` limita a parte inteira a `\d{1,6}`; a parte fracionária segue sem teto, mas `float` de 6 dígitos inteiros com qualquer fração é finito, então `:596` nunca produz `inf` e o `--json` não emite `Infinity`. Valor fora do formato cai na falta de `:554`/`:555`, com o texto novo citando o teto.

Sondas locais (regex extraída do head, `python3 -I`):
- `prometido: 1234567%` e `prometido: <400 noves>%`: sem casamento (vira falta).
- `prometido: 999999%`, `-999999.<5000 noves>%` e `999999,<400 noves>%`: casa, valor finito.
- 1 MB de dígitos seguidos de `x` e 500 mil espaços: cerca de 0,2 s no total, sem retrocesso catastrófico.

Teste do achado: `tests/test_placar_prometido.py` ganha o caso de 400 dígitos com `json.loads(..., parse_constant=self.fail)` e rc 1, e o caso-limite de 6 dígitos com rc 0; `python3 -m unittest tests.test_placar_prometido` com 14 testes OK neste head. O mapa de `bin/forge-testes:196` passa a rodar esse módulo quando `bin/forge-placar` muda, sem efeito de segurança.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Suíte inteira: fica para o CI do PR (não rodada aqui, conforme o brief); rodado só o teste do pedido. Ferramentas: leitura estática do delta e sondas locais; sem varredura de segredos ou dependências por não haver gatilho nem dependência nova.
