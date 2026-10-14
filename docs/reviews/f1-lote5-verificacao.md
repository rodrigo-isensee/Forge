---
tipo: review
contrato: 1
pedido: f1-lote5-verificacao
branch: melhoria/f1-lote5-verificacao
commit: d331c2b
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-13
---
# Parecer de autor: lote 5 da fonte F1 (regras por ferramenta ou leitura)

Escopo: seção "Regras e quem as decide" em `templates/projeto/docs/engineering/praticas.md`, parágrafo no checklist da skill `engineering-practices`, frase no item 3 do `tech-lead`, invariantes em `tests/config.json` (só acrescentam) e linha em `[Não publicado]`.

Conferido: 310 testes verdes; `scripts/validar-plugin.sh` passa. Comandos como marcadores genéricos, sem stack (`R-NEUTRO`); sem custo (`R-CUSTO`). `hooks/conformidade.json` intocado de propósito: "tech-lead não grava fora de `docs/reviews/`" fica como recomendação para PR futuro (no CHANGELOG). Migração: o `forge-upgrade` não migra, pois o `praticas.md` é do projeto; ajuste manual opcional, registrado no CHANGELOG.

Parecer de autor, feito pelo mesmo agente que escreveu a mudança; o review independente fica a cargo do `tech-lead` no PR.

## Review independente
Revisor: forge:tech-lead (sessão separada da do autor). Escopo: `origin/develop..d331c2b` (commits `54c9b7b` e `d331c2b`).

**Validação local** (cota do Actions esgotada; saídas reais no checkout de `d331c2b`):
- `python3 -m unittest discover -s tests`: 310 testes, OK (53 s).
- `scripts/validar-plugin.sh`: "Validation passed", rc 0.
- `tests/catraca.py --modo regras --base origin/develop --head HEAD`: rc 0, sem violação.
- `tests/catraca.py --modo pareceres --ramo melhoria/f1-lote5-verificacao --base-ref develop`: rc 0.
- `tests/catraca.py --modo pr-texto` com o corpo do PR em `PR_BODY`: rc 0.
- Versão e changelog: `plugin.json` continua em 0.12.0, igual à base (correto, a versão sobe só na release); `[Não publicado]` ganhou a linha.
- `bin/forge-check docs`: ver a linha abaixo.

**Checagens do pedido**
- Neutralidade: nada de stack no núcleo. A tabela usa marcadores `<comando ... do pronto.md>`; o teste `Neutralidade` passa.
- Não enfraquece: o diff só acrescenta linhas. Regra de ferramenta sem comando vira pendência (skill, template e tech-lead dizem "pendência no parecer", e o invariante protege a frase).
- Citações: a skill cita "regra 5 de `docs/economia-de-tokens.md`", que é número de item, não ID `R-`. Nenhuma regra é copiada.
- Nome real da fonte: não aparece no diff; só o código F1, como `docs/fontes-de-praticas.md` prevê.

**Achados (nenhum bloqueia)**
1. **Chave do filtro diverge entre skill e template: recomendado.** A skill fala em `decidida por: leitura`, frase protegida pelo invariante, mas o template usa a coluna "Decidida por" com o valor `leitura`. Um projeto que segue o template não tem a frase literal. Sugestão: a skill dizer "coluna 'Decidida por' da tabela de `praticas.md`".
2. **Itens do checklist sem linha na tabela: recomendado, é o ponto que mais pode enfraquecer o review.** Os itens 4 (entradas e erros), 6 (N+1, bundle), 8 (acessibilidade) e 9 (commits) não aparecem no template. O texto diz que o review "lê só as regras leitura" da tabela e que o checklist "vale para o que é de leitura". Pela leitura mais coerente, o checklist inteiro continua valendo para o que não é ferramenta, mas isso não está escrito. Sugestão: uma frase explícita.
3. **Duplicação: recomendado.** O item 3 do `tech-lead` repete quase inteiro o parágrafo da skill; pode apenas citar a skill.
4. **CHANGELOG: recomendado.** A entrada é longa, e a recomendação para o `hooks/conformidade.json` é backlog, não mudança entregue. Vale virar cartão.

**Veredito: aprovado.** Nenhum achado bloqueia; os itens 1 a 4 ficam para um PR seguinte. Não alterei o conteúdo, conforme o pedido.
