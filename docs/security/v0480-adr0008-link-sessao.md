---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-adr0008-link-sessao
commit: 7dc47a7e908a2c3feafe0e9ab06c7c48bf670f86
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-24
---
# Review de segurança: v0478 (E172.14, PR #856, emenda da ADR 0008)

Escopo: diff `5f1c6e97..7dc47a7e`, dois arquivos de texto: `docs/adr/0008-governanca-de-contribuicoes.md` (linha de estado, item (b) da seção 5 na linha 72, emenda nova no fim) e `changelog.d/v0480-adr0008-link-sessao.md`. Nenhum código, hook, workflow nem teste tocado.

## Gatilhos
Gatilhos: mudança em ADR de governança que cita controle do Forge (portão para tornar o repositório público).

## Achados

## Sondas

## Detalhe dos achados
Classificação por escrito: **só aperta ou neutro.**
- Aperta: o item (b) da seção 5 (`docs/adr/0008-governanca-de-contribuicoes.md:72`) acrescenta "links de sessão" à lista do que se varre antes de tornar público; nada sai da lista, (a), (c) e (d) não mudam.
- Neutro: a emenda (fim do arquivo) declara que não é trava nova, que a coautoria fica e que reescrever o histórico continua decisão do dono. As duas referências a código conferem no head: `hooks/conformidade.py:3403` (`gh_trava`, tupla `publico` em 3409) segue recusando tornar público sem mudança neste PR (a citação do item (b) na mensagem fica como cartão, como a emenda diz); `scripts/verificar-contribuicao.sh:37-40` varre só o diff contra a base, como a emenda diz.
- Critério de reversão: só remove a linha por nova emenda datada, com decisão do dono; não afrouxa nada hoje.
- Decisão do dono: item 14 (BP10 C3) da resposta de 2026-11-24 11:19 no pedido v0478 ("Sim."), coerente com o desenho `docs/propostas/bp10-higiene-segredo.md:42` (C3) e a severidade baixa de F3 (linha 31).
- Sem segredo nem link de sessão real no texto do diff; o fragmento de changelog só descreve a emenda.

Observação sem caminho de ataque (não é achado): o gitleaks nas regras padrão não reconhece link de sessão nem caminho pessoal; no dia do gatilho a varredura do item (b) precisa de regra própria e de ler os corpos de PR pela API, que o gitleaks não lê. Isso já valia para as categorias antigas do item (b) e não é introduzido por esta emenda.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. CI do PR #856 verde no head 7dc47a7e (run 45422852421, `success`); rodei localmente só `tests.test_changelog` (91 testes, OK), o teste do arquivo tocado. Revisão estática por leitura; nenhuma ferramenta de varredura necessária para diff só de texto.
