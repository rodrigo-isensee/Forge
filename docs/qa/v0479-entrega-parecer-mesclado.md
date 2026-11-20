---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-entrega-parecer-mesclado
commit: 39351c755290a37abf829fedb17fe65744183491
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-20
---
# QA: v0478 E50.14 (ENTREGA-PARECER-MESCLADO-ANTES-DO-AUTOR), revalidação no head `aebace71`

Head testado: `aebace71` (revalidação do reprovado em `8cff35a0`; A1 e A2 anteriores). Delta lido por `forge-check parecer delta` (de `8cff35a0`): `hooks/conformidade.py` (A5 da segurança, `PARECER_NO_TEXTO`), 14 fixtures `pp-sessao-forge-*`, specs de mutante 5 e 6, `tests/test_hooks.py`, `tests/test_selo_e_entrega.py`, `docs/hooks.md`, fragmento do changelog. Sem suíte local: a suíte inteira fica com o CI do PR.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| A1 anterior: guarda da volta só com conferida (`and valido`) | `test_sem_conferida_a_regra_nao_vale` (agora na 1ª entrega) | 1ª entrega, `commit:` = Base-sha | M1 morreu |
| A2 anterior: fixture sem caminho pessoal | `scripts/verificar-contribuicao.sh` | caminho pessoal no diff | ok |
| E50.11 A5: variável no alvo e linha ilegível/acima do teto que citam pasta de parecer alheia recusam na sessão do Forge; dono livre; vizinho `reviewsx` e linha sem parecer livres | `test_hooks.test_fixtures_do_parecer_pelo_papel` | variável no alvo; teto; ilegível; vizinho de nome; dono | passou |
| E50.1/E50.5/E50.6 (regressão) | `ParecerMescladoNaVolta`, `ParecerDoMesmoPapelDoAutor` | `commit:` = Desde; papel do autor | 20 de 20 |

## Cenários e resultado real
- `python3 -I -m unittest discover -s tests -p test_selo_e_entrega.py -k ParecerDoMesmoPapelDoAutor -k ParecerMescladoNaVolta` → `Ran 20 tests ... OK`.
- `python3 -I -m unittest discover -s tests -p test_hooks.py -k fixtures_do_parecer_pelo_papel` → `Ran 1 test ... OK`.
- `bash scripts/verificar-contribuicao.sh` → `ok: nenhum segredo nem caminho pessoal no diff contra origin/develop.`
- `forge-mutante --cobertura --base 8a503799…`: toda condição mudada tem mutante (`coberta · … · declarado, não provado`); nenhuma linha sem mutante; `spec editada` em `v0457-escopo-ponto-2.json` e `v0478-guardas-conformidade.json` (o `de` de M4 e M5 reescrito para a nova condição, conferido no diff).
- Mutantes, rc 0 em todas: spec 1 `M1` a `M8 · morreu` (M1 `bin/forge-check:3245` agora morre); spec 5 `M25` a `M32 · morreu`; spec 6 `M33 · morreu` (`hooks/conformidade.py:3822`); spec editada `v0478-guardas-conformidade.json` `M1` a `M7` e `M12 · morreu`. Specs 2, 3 e 4 sem mudança no delta, não rerrodadas.
- Vermelho: cada mutante morto prova teste que cai sem a guarda; `forge-testes --vermelho` não rodado (estourou o prazo antes; não vale como vermelho).
- Pre-push: roda no envio (barato, sem suíte); resultado no relatório.

---
# Revalidação no head `5376b86d` (A6 da segurança, E50.15)

Delta lido por `forge-check parecer delta` (de `aebace71`): `hooks/conformidade.py` (`PARECER_NO_TEXTO` sem a isenção do dono, `re.I`, `docs/security` cobre `aceites`; `parecer_alheio_no_texto` virou `parecer_no_texto`), 11 fixtures `pp-sessao-forge-wt-*`, specs `v0478-guardas-conformidade.json` e `v0479-entrega-parecer-mesclado-5.json`, `tests/test_hooks.py` (piso de recusas de 19 para 25), `docs/hooks.md`, fragmento do changelog.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| A6: o dono que guarda a pasta numa variável não alcança a vizinha (`d=docs/reviews; echo x > $d/../qa/n.md`) | fixtures `…-tech-lead-variavel-vizinha-qa-bloqueia`, `…-qa-variavel-vizinha-aceites-bloqueia`, `…-seguranca-variavel-mae-aceites-bloqueia`, `…-seguranca-variavel-security-bloqueia` em `test_fixtures_do_parecer_pelo_papel` | variável no alvo; dono; `..` até a vizinha e até `aceites/` | passou |
| A6: a caixa não conta (`${d,,}`) | `…-tech-lead-variavel-caixa-qa-bloqueia` | caixa | passou |
| A6: teto e linha ilegível, dono incluído | `…-tech-lead-teto-reviews-bloqueia`, `…-dev-teto-reviews-bloqueia` | acima do teto; papel sem dono | passou |
| O dono grava a própria pasta pelo caminho literal | `…-tech-lead-redireciona-reviews-libera`, `…-seguranca-redireciona-security-libera`, `…-tech-lead-teto-reviews-libera` | caminho literal; dono livre | passou |
| Piso do lote de fixtures | `assertGreaterEqual(recusas, 25)` | suíte vazia | passou |

## Execução (TMPDIR da sessão, sem suíte local)
- `python3 -I -m unittest discover -s tests -p test_hooks.py -k test_fixtures_do_parecer_pelo_papel` → `Ran 1 test in 25.509s · OK`.
- Fixtures novas conferidas: cada `bloqueia` recusa pela construção da `descricao` e cada `libera` usa caminho literal; a fixture `…-seguranca-variavel-security-libera` (dono livre por variável) agora é do lote de recusa, coerente com A6.
- `forge-mutante --cobertura --base aebace71`: `coberta` em `conformidade.py:3787` (M4, M5, M25) e `:3820` (M28), ambas `declarado, não provado`; `isenta` nas duas linhas apagadas (`3794(base)`, `3793(base)`); nenhuma `isenta velha`; rc 0.
- Isentas conferidas: `self.papel not in e["quem"]` e a busca `e["caminho"] in CAMINHOS_DE_PARECER and casa(...)` não existem no head; os motivos apontam M26, M31 e as fixtures, que existem e morrem. Aceitas.
- `forge-mutante --base aebace71 tests/mutantes/v0479-entrega-parecer-mesclado-5.json`: `base=aebace7125b5873038e1c4ffefbb512cd7e111b2 … rev=5376b86d2b44`; `M25`, `M26`, `M27`, `M28`, `M29`, `M30`, `M31 · morreu`; rc 0.
- `forge-mutante --base aebace71 tests/mutantes/v0478-guardas-conformidade.json`: `M3`, `M4`, `M5`, `M6`, `M7`, `M12 · morreu`; rc 0.
- Vermelho: cada mutante morto prova teste que cai sem a guarda (M26 sem a recusa, M27 sem `re.I`, M31 sem `security` cobrir `aceites`). `forge-testes --vermelho aebace71` varre 109 módulos em duas cópias (passou de 9000 s no módulo 118 de 222) e foi interrompido: sem veredito, não vale como vermelho; a suíte inteira fica com o CI do PR.

---
# Revalidação no head `9f4c3ca3` (E50.23)

Delta lido por `forge-check parecer delta` (de `5376b86d`): do que é da branch, só `tests/test_revisor_wt.py` (commit `9f4c3ca3`, E50.20). O resto do domínio (`bin/forge-check`, `tests/test_hooks.py`, `docs/hooks.md`) veio da develop pelos merges (`c2cec75e`, `cf097822`, `c219c86b`), fora do que o parecer cobre; o aviso do delta sobre o merge de `bbdd9b0` foi conferido: merge de branch, sem efeito.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E50.1: sem autoria registrada, o parecer commitado na volta só com parecer sai como anexo do portão, não "confira" | `test_revisor_wt.ParecerTrazido.test_o_ultimo_p_trazido_com_remocao_e_ok_em_qualquer_etapa` | sem `autoria.jsonl`; parecer de outro papel | passou |
| E50.1/E50.5/E50.6 (regressão) | `ParecerMescladoNaVolta` | `commit:` = Desde | 60 de 60 |

## Execução (TMPDIR da sessão, sem suíte local)
- `python3 -I -m unittest discover -s tests -p test_revisor_wt.py` → `Ran 39 tests in 68.414s · OK`.
- `python3 -I -m unittest discover -s tests -p 'test_*.py' -k ParecerMescladoNaVolta` → `Ran 60 tests in 114.764s · OK`.
- Vermelho: a asserção antiga (`5376b86d:tests/test_revisor_wt.py`) contra o `bin/forge-check` do head cai (`FAILED (failures=1)`, esperava `escopo: confira …`); a nova passa. O teste só alinha a expectativa ao comportamento do E50.1 (autoria ausente, parecer commitado na volta só com parecer: `ok`, anexo do portão); não afrouxa guarda.
- Mutantes: nenhuma linha de guarda mudada pela branch neste delta (só teste); specs não rerrodadas. Sem `skip` novo.
- Suíte inteira: com o CI do PR, no check-run `bateria` do mesmo sha.

---
# Revalidação no head `39351c75` (E50.30)

Delta lido por `forge-check parecer delta` (de `9f4c3ca3`): `docs/hooks-fixtures.md` (índice gerado, 3097 para 3135 fixtures), `tests/apoio_volta_unica.py` (teto `interpretador` 5893967 para 5895051, +1084 passos) e `tests/provas/v0479-corpus-custo.md` (medida nova). Nenhum código de produção nem linha de guarda mudou; sem mutante novo. O aviso do delta sobre o merge de `8ddfe18` é de merge de outra branch.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Teto do corpus é a medida exata, com a autorização do dono (DECISÃO 20/11 19:09, só este item) | `tests.test_hooks_volta_corpus` | teto sem folga: um passo a mais reprova | passou |
| Índice das fixtures confere com o corpus (3135) | `tests.test_indice_fixtures` | índice gerado igual ao corpus | passou |

## Execução (TMPDIR da sessão, sem `-I`, como o pre-push)
- `python3 -m unittest tests.test_hooks_volta_corpus tests.test_indice_fixtures` → `Ran 40 tests in 276.807s · OK`.
- O aumento é de +1084 passos (0,02%), igual ao reprovado no CI do PR #734; o registro em `tests/provas/v0479-corpus-custo.md` traz a medida e a autorização. Sem `skip` novo.
- Suíte inteira: com o CI do PR, no check-run `bateria` do mesmo sha.
