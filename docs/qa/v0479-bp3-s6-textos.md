---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-bp3-s6-textos
commit: add56507bb1db36604abe66ec804c9266a539e66
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-20
---
# QA: v0479-bp3-s6-textos (E39.32)

Mudança só de texto: `agents/jarvis.md`, `skills/trabalho-em-paralelo/SKILL.md`, nova `skills/trabalho-em-paralelo/sessao-duravel.md`, `docs/retomada-de-sessao.md`, invariantes em `tests/config.json` e o fragmento de changelog. Sem código de produção. Sem especificação de UX própria: as obrigações são as decisões D1 a D5 do dono (pedido v0478), `R-NEUTRO` (neutralidade), `R-TETO` e as invariantes do núcleo do Jarvis.

## Achados
- A1 (recomendado) skills/trabalho-em-paralelo/sessao-duravel.md:23 · O texto manda rodar `forge-check retomada` e `--contar`, subcomando que não existe neste head (`forge-check retomada` sai com usage); é a S4 (E39.33). Integrar a S6 só depois da S4, ou o Jarvis segue um comando inexistente.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Núcleo do Jarvis lê a skill na abertura (D1) | `test_jarvis_nucleo.py` (43) e invariante nova "Na abertura e antes de disparar…" em `RegrasInviolaveis` | tamanho do `agents/jarvis.md` (7806 caracteres) dentro do teto | passou |
| Texto da regra D4 (segundo Jarvis recusa) e D1 (retomada antes de disparo) não some | invariantes novas de `sessao-duravel.md` (7 padrões), conferidas por `RegrasInviolaveis`, `AntiDuplicacao`, `RegrasComId` | texto removido ou reescrito | passou |
| Ponteiro `Abertura e queda` na SKILL | invariante `\*\*Abertura e queda:\*\*` | link quebrado | passou |
| `R-NEUTRO`: nada de projeto específico | `Neutralidade` e `NeutralidadeDoNucleo` | termos proibidos | passou |
| Agentes, skills e referências válidas | `Agentes`, `Skills`, `Referencias` | frontmatter e links | passou |
| Texto de CI pago preservado (tirou a cópia de `ritmo-e-corte.md` da SKILL) | `test_textos_ci_custo.py` (5) | `ritmo-e-corte.md` segue sendo a fonte | passou |
| Modelos de projeto e skills v0442 | `test_modelos_projeto.py` (20), `test_skills_v0442.py` (4) | n/a | passou |

## Cenários e resultado real
Rodado local, cada módulo com `python3 -I -m unittest discover -s tests -p <arquivo>`, TMPDIR do sandbox, sem a suíte inteira.
- `test_jarvis_nucleo.py`: Ran 43, OK. `test_modelos_projeto.py`: Ran 20, OK. `test_skills_v0442.py`: Ran 4, OK. `test_textos_ci_custo.py`: Ran 5, OK.
- `test_forge.py` inteiro estourou 550 s (Terminated, sem veredito; o resto é da bateria do CI). Rodei só as classes do domínio (`-k`): Agentes, Skills, Referencias, Neutralidade, NeutralidadeDoNucleo, RegrasInviolaveis, DiretrizesDoDonoNaRWip, AntiDuplicacao, RegrasComId: Ran 28, OK.
- `neutralidade.py` é biblioteca (Ran 0, não é teste).
- Vermelho antes do verde e mutação: não se aplicam, a mudança não traz regra de código; as invariantes novas são o próprio guarda do texto e conferem o texto presente no head. O CI do PR roda a bateria (`bateria` do mesmo sha) e é a prova da suíte inteira.
- Conferência de texto: `docs/retomada-de-sessao.md` marca a substituição parcial (D5) e aponta a proposta e a skill; a proposta citada (`docs/propostas/v0479-bp3-sessao-duravel.md`) não está nesta branch (vem de outro repositório), por isso não conferi o link.
