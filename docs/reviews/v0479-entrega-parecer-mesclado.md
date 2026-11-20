---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-entrega-parecer-mesclado
commit: 5376b86d2b441a17f4aba8b05c37d94e8a5e94a4
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 E50.16 (ENTREGA-PARECER-MESCLADO, volta E50.15, A6 da segurança)

Revalidação pelo delta (`forge-check parecer delta`, intervalo `aebace71..5376b86d`; H3, `R-REVIEW`): hooks/conformidade.py, docs/hooks.md, changelog.d, tests/test_hooks.py, as specs `v0478-guardas-conformidade` (M4, M5) e `v0479-entrega-parecer-mesclado-5`, 7 fixtures `pp-sessao-forge-wt-*` novas e 2 removidas (as `-libera` do dono pela variável e acima do teto viraram `-bloqueia`). Fora do domínio nada foi relido.

## Sondas

## Parecer
Aprovado no head 5376b86d.

E50.15 (A6 da segurança): `parecer_no_texto` deixa de conferir o papel e recusa, para todo papel e dono incluído, a construção que o hook não modela e a linha sem leitura que citam qualquer das cinco pastas; `PARECER_NO_TEXTO` perde o `(?:/aceites)?` (desnecessário, `docs/security` com borda casa `docs/security/aceites`, M31) e ganha `re.I` (`${d,,}`, M27). As três formas do A6 (S17 a S19 da segurança) viraram fixtures `-bloqueia`, e o dono segue livre na própria pasta pelo caminho literal (fixtures `-redireciona-*-libera`). Docstring, `docs/hooks.md` e o fragmento do changelog dizem o mesmo que o código. As duas linhas de guarda apagadas estão em `isentas` com motivo, e `--cobertura --base aebace71` dá as duas mudadas cobertas (3787 por M4, M5 e M25; 3820 por M28).

Sondas minhas pelo lançador de `tests/test_hooks.py` (contexto da fixture `pp-sessao-forge-wt-tech-lead-variavel-vizinha-qa-bloqueia`): `d=docs/reviews; echo x > $d/../qa/n.md` rc 2; `echo x > docs/reviews/n.md` (tech-lead) rc 0; `echo x > docs/qa/n.md` (tech-lead) rc 2; `git add docs/reviews/n.md && git commit -m x` rc 0. A pasta partida na variável (`d=docs; echo x > $d/qa/n.md`, rc 0) é o resíduo que a segurança declarou fora do escopo e igual em projeto (BP-5); não é achado deste delta.

Rodei com ambiente limpo: `test_fixtures_do_parecer_pelo_papel` OK; `forge-mutante --processos 1` M25 a M31 da spec 5 e M4 e M5 da v0478 morreram; `scripts/verificar-contribuicao.sh 8a503799` ok. Sem shell tocado. A suíte inteira fica com o CI do PR (`R-REVIEW`).
