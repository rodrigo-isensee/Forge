---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-rotulo-base-alheia
commit: 48034214f4654bf7d00788ea68f0c0790d79783e
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-26
---
# Review: v0481 E17.2 (#906, ROTULO-NAO-CAI-COM-BASE-ALHEIA)

1ª rodada completa (G1). Diff lido contra o merge-base com a develop (22ceb2c8): 1 commit, `tests/catraca.py` (3 linhas de código, teto H1 ok), `tests/test_catraca.py` (2 testes), `tests/mutantes/v0481-rotulo-base-alheia.json` (RB1, RB2) e o fragmento `changelog.d/v0481-rotulo-base-alheia.md`.

## Conferência pedida: nada de controle sai da comparação
- `pareceres_do_pedido` só alimenta o `ignorar` do `mesmo_diff`, que é o segundo caminho de `rotulo_vale_pelo_conteudo`; os `VIGIADOS_DO_ROTULO` (PROTEGIDOS, `tests/config.json`, política, `hooks/hooks.json`) e a forma compilada não moram em `docs/security/`, então o novo item de `PARECERES` não esconde mudança de arquivo de controle. As `violacoes_novas` seguem calculadas sobre o head inteiro, sem os livres.
- O aceite do usuário (`docs/security/aceites/`) sai de `tocados` pela constante `ACEITES` (mesmo prefixo de `ACEITES_DO_USUARIO` do `forge-check`); pela regra do nome nunca entraria (a pasta pai `docs/security/aceites/` não está em `PARECERES`). O caminho do "já tocado no head rotulado" é o único por onde ele entraria, e é o que RB1 cobre.
- O `ignorar` são nomes exatos; `desatualiza` do `forge-check` ainda trata aceite fora de `livres` como divergente.

## Testes e mutantes
- `python3 -m unittest test_catraca.RotuloSobreviveAoConteudo` (em `tests/`): 23 testes OK.
- `bin/forge-mutante --processos 1 tests/mutantes/v0481-rotulo-base-alheia.json`: RB1 morreu (`tests/catraca.py:1394`), RB2 morreu (`tests/catraca.py:44`).
- `bin/forge-mutante --cobertura --base 22ceb2c8`: a guarda de `tests/catraca.py:1394` coberta por RB1.
- O teste do #875 roda pelo `roda_aqui` (com `protegidos_como_no_rotulo` falso), então prova o caminho do diff efetivo e não passa à toa pelo P9.

## CI
- ci: 48034214f4654bf7d00788ea68f0c0790d79783e verde
- Vermelhos que esperam o portão: `catraca` (R-CONFORMIDADE, mudança em `tests/catraca.py`, espera o rótulo `afrouxa-regra` do dono depois do último push) e `bateria (pareceres)` (espera os pareceres).

## Achados
- A1 (recomendado) tests/catraca.py:45 · ACEITES cobre só aceites/; o forge-check (PASTAS_RECUSADAS_DE_PARECER) e o forge-changelog tratam docs/security/ameacas/ como não parecer. Um modelo de ameaças tocado antes do rótulo fica livre depois. Alinhar com as mesmas pastas, numa constante única.

## Sondas

## Parecer
Aprovado. Faz o que a E17.1 pede, sem mais: o parecer de segurança da branch entra nos livres como o review e o QA, e o aceite do usuário fica sempre dentro da comparação. Título do PR destaca o afrouxamento com a decisão do dono (R-CONTRIB); a causa do #878/#888 fica declarada em Riscos, fora do escopo. A1 não bloqueia (o modelo de ameaças não é lido por nenhuma regra da catraca) e vira cartão depois do merge.
