---
tipo: qa
contrato: 1
pedido: lote-docs-regra5
branch: melhoria/lote-docs-regra5
commit: 3802b9e581ca6fa52dc51f46227afb3e6918ada3
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-26
---
# QA: lote-docs-regra5

Escopo: textos do pre-push depois do M8 (README, `agents/tech-lead.md`, regra 5 de `docs/economia-de-tokens.md`) e os testes que os fixam. Sem UI: E2E de navegador e acessibilidade não se aplicam. Base `edb5358` (a `origin/develop`), head testado acima. Sem gatilho de segurança.

## Achados
- A1 (recomendado) README.md:68 · o texto não diz que diff que toca bin/forge-testes, tests/config.json ou .githooks/, árvore suja ou mais de uma ref também caem na suíte inteira (o hook faz); falha fechada, só omissão
- A2 (recomendado) docs/economia-de-tokens.md:10 · "É ferramenta de iteração, não portão" convive com "o pre-push roda só os testes afetados (bin/forge-testes)"; o pre-push usa o filtro como portão do envio, vale uma frase

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1: README sem "o `pre-push` e o CI rodam a suíte inteira", com "só os testes afetados" | tests.test_forge.PrePushSoOsAfetados.test_readme_e_tech_lead_dizem_so_os_afetados | frase antiga ausente | passou (base: falha) |
| E1: tech-lead V2 sem "roda uma vez, no push", com "fica no CI do PR" | o mesmo | frase antiga ausente | passou (base: falha) |
| E1: V2 do tech-lead com o texto novo | tests.test_forge.EsperaDoPushEVerificadores.test_v2_dirigida_e_na_fila | texto exato | passou (base: falha) |
| E1: regra 5 cita M8, 2026-10-24, "CI de todo PR" e não afirma a suíte inteira no pre-push | tests.test_testes_tocados.NaoEPortao.test_regra_5_cita_o_script_e_a_decisao_do_dono | n/a; ainda cobra bin/forge-testes | passou (base: falha) |

## Cenários e resultado real
- `python3 -m unittest tests.test_forge tests.test_testes_tocados -q` no head: 508 testes, OK (97 s).
- Vermelho na base (`forge-testes --vermelho edb5358cae21318c8323e6ef9e173a700deb9b8e --modulos test_forge,test_testes_tocados`): rc 0. Abertura: `vermelho: base=edb5358cae21 head=3802b9e581ca módulos=test_forge,test_testes_tocados`; revertidos à base os 4 arquivos de texto; `contagem: não prova (passa na base)=505; prova (asserção)=3`. Os 3 testes acima provam; nenhum cai no head.
- Conferência frase a frase com `.githooks/pre-push` da develop: dirigido só para uma ref `refs/heads/melhoria/*`, com `bin/forge-testes`, base e plano "dirigido (", sem tocar filtro, mapa ou hook; o resto cai em `scripts/suite-paralela.py`. README, tech-lead e regra 5 dizem o mesmo (melhoria/* só os afetados; fora dela e caminho sem regra, suíte inteira; bateria completa no CI de todo PR; bloqueios de conteúdo ficam). A "decisão do dono M8, 2026-10-24" bate com o registro do pedido. Sem divergência de comportamento.
- Grep da frase antiga em tests/*.py, agents, skills, stacks, docs, templates, bin, scripts: nenhuma sobra afirmando suíte inteira no pre-push. Restam citações só como asserção negativa (testes novos), a docstring de `bin/forge-testes:26` (review, QA, CI e main rodam a suíte inteira, correto e fora do escopo) e `R-QA` (regra com ID, intocada).
- PA-7 (`docs/engineering/achados-recorrentes.md`): lista vazia ("nenhum ainda"), nada a conferir.
- Nota de processo: dois commits (5c782de deixa um teste vermelho, 3802b9e corrige), já registrado no pedido como decisão técnica.
