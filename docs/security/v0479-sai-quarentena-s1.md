---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-sai-quarentena-s1
commit: 0e1e73639b761a4a4400dc1fd41a9281e57e61be
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: sonda S1 sai da quarentena (v0478 E37.41, parecer E37.53)

Escopo: `git diff 004ce869..0e1e7363`, 4 arquivos: `tests/config.json` (controle), `tests/test_hooks.py`, `tests/provas/v0479-sai-quarentena-s1.md` e `changelog.d/v0479-sai-quarentena-s1.md`.

Gatilhos: arquivo de controle (`tests/config.json`, `teto_pulados`), teste do hook `parecer` (`tests/test_hooks.py`).

## Sondas

## Detalhe dos achados
Sem achados. **A mudança só aperta**, nada afrouxa:
- `tests/config.json:930`: `teto_pulados` cai de 2 para 1, o valor de antes da quarentena (`TETO_PULADOS_ORIGINAL = 1`, `tests/quarentenas.py:13`). A catraca T3 (`tests/catraca.py:747`) só barra subida; `regra_teto_pulados({"teto_pulados": 2}, {"teto_pulados": 1})` devolve `[]` (conferido).
- `tests/test_hooks.py:1325`: sai só o `@unittest.skip("quarentena ...")` da `test_liberar_ou_provar_a_carga_recusa_a_sonda_s1`; o corpo do teste não muda. Um teste a mais roda no CI, um pulo a menos.
- Coerência teto × quarentenas: `quarentenas_abertas('tests')` = 0 e `teto_passa_da_quarentena(1, 0)` = False (conferido no head); não sobra outra quarentena aberta nem referência ao cartão `TESTE-SONDA-S1-RELOGIO` em `tests/`.
- Teste que tira dúvida, rodado no head: `python3 -m unittest tests.test_hooks.Hooks.test_liberar_ou_provar_a_carga_recusa_a_sonda_s1 tests.test_hooks.SondaS1ComRelogioFalso` → `Ran 3 tests ... OK` (9,1 s, sem carga extra). A prova das 10 rodadas sob carga é do autor (`tests/provas/v0479-sai-quarentena-s1.md`).
- Risco residual (não é achado de segurança): se a S1 voltar a oscilar no CI, o teto 1 não absorve o pulo e a suíte reprova; isso falha fechado, que é a direção certa para um controle.
- Segredo: nenhuma ocorrência de padrão de token, chave ou credencial nas linhas acrescidas (busca: 0).

## Riscos aceitos e ferramentas
Nenhum risco aceito nem pendente de aceite. Sem suíte local (brief); a suíte inteira é do CI do PR, que ainda não existe para esta branch: o merge na `develop` exige o CI verde. Lacuna: gitleaks, osv-scanner, semgrep, zizmor e actionlint fora do PATH; o diff não toca workflow nem dependência.
