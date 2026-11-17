---
tipo: revisao-seguranca
contrato: 1
pedido: release-0.47.2
branch: melhoria/v047-release-0472
commit: b57bb55861115f7b9b5236d4349b4807fe842aa8
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-16
---
# Review de segurança: release 0.47.2 (leva v0.47.1..b57bb558)

Gatilhos: hook, controle de integração e promoção (`R-FLUXO`), catraca, workflow do CI, script distribuído aos projetos.

## Escopo e método
Leva de 40 commits (`git log v0.47.1..b57bb558`), 94 arquivos fora de testes e pareceres. Domínios lidos: `hooks/` (`parecer.py`, `conformidade.py`, `_comum.py`, `meta.py`), `bin/` (`forge-check`, `forge-fechar`, `forge-mutante`, `forge-testes`, `forge-changelog`, `forge_dono.py`, `forge_voltas.py`, `forge_transcricao.py`), `.github/workflows/ci.yml`, `tests/catraca.py`, `scripts/` e `templates/projeto/scripts/pos-release`. O commit do head só sobe a versão (0.47.1 para 0.47.2 em `plugin.json` e `dev/plugin.json`), o CHANGELOG e junta fragmentos: sem código.
Os commits da leva entraram por squash, então `forge-check parecer delta` não resolve (o sha de cada parecer não é ancestral do head). Por isso conferi por blob: para cada item que toca controle, o arquivo mesclado é idêntico ao do head do PR revisado (hooks do #569, #592 e #580; `bin/forge-fechar` do #573, #567 e #601; `ci.yml` do #567). Onde o head do PR trouxe mais que o parecer (#567 e #601), a diferença vem de junções limpas com a develop, de itens já revistos à parte.

## Gatilhos e pareceres por item (R-SEGURANCA)
Itens com controle e parecer de segurança aprovado, um por item: lote do `forge-fechar` e degrau do CI (`v047-integracao-em-lote`, #567), hook do `gh pr ready` e merge (`v047-pr-hook-rapido`, #569), texto com merge (`v047-hook-texto-merge`, #592), jargão no Stop (`v047-jargao-medida`, #580), sessão automática e `scripts/jarvis` (`v047-sessao-automatica`, #573), `forge-fechar` sem homolog (`v047-fechar-sem-homolog`, #601), catraca por script (`v047-catraca-hook-por-script`, #575), `forge-mutante` (`v047-specs-conferidas`, `v047-mutante-avisos`), `forge-testes` (`v047-maq-i9`, `v047-mapa-testes`, `v047-frontmatter-agentes`), `forge-check` (os demais `v047-*`), pós-release (`v047-pos-release`, o script que vai a todo projeto), changelog (`v047-changelog-anexar`) e as correções da develop verde (`v047-develop-verde-584`, `v047-verde-0472`, `v047-reverte-576`).

Sem parecer de segurança na leva, e sem gatilho (só texto, spec de teste ou teste): #596 brief-vagas e #591 visao-de-foco (só `docs/arquitetura`), #589 sessao-por-pedido (`docs/economia-de-tokens.md` e um teste), #578 mutantes-velhos (só specs em `tests/mutantes`), #570 fixture-etapa e #568 develop-verde-2 (só testes), e o commit de versão do head (b57bb558). Confirmei no diff de cada um que não tocam hook, `bin/`, workflow nem script. Os specs de mutantes são dado do teste dos controles, sem execução em produção: registro como lacuna de parecer, não como achado.

Itens mesclados fora do fluxo de regras, e o que houve depois:
- #567 (`afrouxa-regra`, degrau promoção para homolog): revisto antes pelo parecer `v047-integracao-em-lote` (A1 bloqueante resolvido: o passo "Nada pula degrau" roda a catraca da develop do servidor, `ci.yml` e `PROMOCOES` em `tests/catraca.py:1665-1667`). Revi a forma final do passo (env, sem interpolar `${{ }}` dentro do script, `python3 -I`): sem injeção.
- #569 (`afrouxa-regra`, resultado gravado libera ready e merge só no clone do Forge): o parecer `v047-pr-hook-rapido` reprovou no A1 e aprovou na volta; o blob mesclado é o do head aprovado (`hooks/parecer.py:567`: `estado == "aprovado" and (gravado == EXIGE or e_clone_do_forge(raiz))`). No projeto o aprovado forjado não libera.
- #576 (CI em 5 partes): mesclado, deixou a develop vermelha e foi revertido pelo #604; o parecer `v047-ci-rapido` saiu junto e `v047-reverte-576` cobre o revert. O `ci.yml` final não carrega o #576.
- #584 e #594 (develop vermelha depois deles) e #586 e #600 (CI da develop falhou no push): consertados no #604, com `v047-develop-verde-584` e `v047-verde-0472` (blobs de `hooks/` e `bin/` do #604 iguais aos do head aprovado). Nada de hook ou `bin/` mudou depois desses pareceres.
- CI da develop no commit 86ac0fcb: verde (`gh run list --branch develop`, 21m17s). O commit do head b57bb558 não tem CI próprio no que li: ele só muda versão e changelog.

## Achados
- A1 (recomendado) docs/security/release-0.47.2.md:1 · Fechar a lacuna de parecer dos itens sem gatilho (#578 specs de mutantes, #589, #591, #596) é opcional; se o dono quiser trilha completa, peça um parecer curto de "sem gatilho" por item.
- A2 (recomendado) .github/workflows/ci.yml:512 · O passo de degrau roda `python3 -I` sobre `tests/catraca.py` da develop do servidor: depende da develop protegida. Mantenha a proteção da branch (revisão obrigatória) como controle compensatório; sem mudança de código.

## Sondas

## Detalhe dos achados
**A1 · informativa · esforço P · dono: tech-lead.** Os itens listados mudam só documentação, spec de mutante ou teste. Sem caminho de ataque: spec de mutante é lida pelo `forge-mutante` no CI, que não executa nada além do que o corpo do spec declara dentro do pacote já revisto (parecer `v047-mutante-avisos`, `v047-specs-conferidas`). É registro de lacuna, não bloqueio.

**A2 · informativa · esforço P · dono: devops-engineer.** Quem controla a develop controla o degrau; é o desenho aprovado no parecer `v047-integracao-em-lote` (A1, resolvido). Não é regressão desta leva.

## Riscos aceitos e ferramentas
Nenhum risco aceito. O dono aceitou, pelo rótulo `afrouxa-regra`, o afrouxamento do #567 e do #569, ambos com parecer de segurança posterior e volta aprovada.
Rodado aqui no head b57bb558: `python3 -m unittest tests.test_catraca_promocao tests.test_pr_hook_rapido tests.test_meta tests.test_catraca` (OK) e `shellcheck` em `bin/forge-fechar`, `scripts/preparar-estacao.sh` e `templates/projeto/scripts/pos-release` (rc 0). A suíte inteira roda só no CI; o CI da develop no 86ac0fcb está verde. Faltam no ambiente: gitleaks, zizmor, actionlint e Semgrep (lacuna registrada: o workflow mudou em #567 e o zizmor e o actionlint ficam para o CI).
