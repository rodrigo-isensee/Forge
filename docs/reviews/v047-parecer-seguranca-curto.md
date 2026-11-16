---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-parecer-seguranca-curto
commit: 02fe845d9896048bc0a4b504ac9bac0b3a9c7018
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-16
---
# Review: v047-parecer-seguranca-curto (E2.278, entrega E2.276, TEMPO-A A10)

Parecer completo (não havia parecer anterior), no head 02fe845d, base 5e74c70e. Diff: `agents/security-engineer.md`, `docs/security/_modelo.md` e a cópia do template, `tests/test_achado_teto_doc.py`, fragmento `changelog.d/`. 35 linhas a mais, 4 a menos; código contado: 25 linhas de teste, dentro do teto M14.

## Achados
- A1 (recomendado) skills/cyber-security/SKILL.md:18 · a regra nova manda citar a mitigação "pelo ID dela" (`M1.1`), mas o formato do modelo de ameaças não exige ID por mitigação; sem ele, não há o que citar. Sugestão: o item 5 da skill numera as mitigações (M<n>.<m>), como já fazem docs/security/forge-check-lote.md e conf-correcao.md.
- A2 (recomendado) bin/forge-check:3039 · o esqueleto de `forge-check parecer novo` para revisao-seguranca ainda escreve a linha de gatilhos sem o prefixo `Gatilhos: ` do modelo novo. Fica para depois da integração em curso do bin/forge-check (DECISÃO DO DONO 16/11 09:16); cartão, não volta.

## Sondas

## Parecer
Aprovado. Faz o que a E2.276 pede (proposta A10 do TEMPO-A, DECISÃO DO DONO 16/11 07:17): mitigação pelo ID, gatilhos em uma linha, volta sem recópia; nem mais, nem menos. O texto cita regras pelo ID (`R-SEGURANCA`, `R-REVIEW`), os dois modelos seguem idênticos e nenhum invariante sai. Mudança só de texto, sem guarda nova: não pede mutante declarado.

Checklist de leitura: 1 (escopo) ok; 2 (ADR 0004, regras com ID) ok; 3 (legível) ok; 7 (testes) ok com a ressalva de que são testes de texto, adequados a mudança de documento; 9 (commit único, Conventional Commits, fragmento de changelog) ok; 11 (teste de presença com lista fixa de três arquivos e quatro frases) ok. Os demais itens não alcançam o diff.

Testes rodados na raiz do clone, no head 02fe845d:
- `python3 -m unittest tests.test_achado_teto_doc`: 4 testes, OK.
- `python3 -m unittest tests.test_modelos_parecer_avisos_2 tests.test_modelos_projeto tests.test_modelos_citados`: 22 testes, OK.
- Mutante manual (cópia do head em pasta temporária): segunda linha no parágrafo de `## Gatilhos` dos dois modelos; `tests.test_achado_teto_doc` falha (2 falhas), mutante morto.

Suíte: a suíte inteira roda no CI do PR, que ainda não existe (o brief pede sem PR); o merge espera o CI verde.

Os dois recomendados não bloqueiam (`R-REVIEW`): A1 vai como cartão para a skill `cyber-security` (dono: security-engineer); A2 como cartão para o bin/forge-check depois da integração dele. Nenhuma classe repetida em `docs/engineering/achados-recorrentes.md`: sem linha AR nova.
