---
tipo: revisao-seguranca
contrato: 1
pedido: v0457
branch: melhoria/trava-modelo
commit: 5c38e04ea8d010b3250b2c934278a66e94eff43e
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-13
---
# Review de segurança: trava-modelo (v0457, 4b, E23.110)

Entrega revisada: E23.29, a isenção da cópia do modelo de projeto na trava de arquivo em vigor (`hooks/conformidade.py`), contra as condições C1 a C10 do parecer E23.28 (Histórico do v0457, 2026-11-12 11:34) e as 22 fixtures de abuso `trava-modelo-a01` a `a22`. Head `5c38e04e`, base `origin/develop`.

## Gatilhos
`R-SEGURANCA`: muda um controle do Forge (hook de conformidade) e afrouxa uma trava (rótulo afrouxa-regra, `R-CONFORMIDADE`).

## Achados
- A1 (recomendado) tests/hooks/conformidade/trava-modelo-a05-githooks-do-modelo-link-bloqueia.json:19 · a descrição fala da pasta .githooks do modelo trocada por link, mas o link é templates/projeto/gh; faltam fixtures para o nome literal trocado por link, link pendente para a raiz, link para fora do clone e core.hooksPath absoluto (as sondas passam)
- A2 (recomendado) hooks/conformidade.py:1195 · risco residual C10: o Bash deixa trocar templates/projeto por link para a raiz (mv e ln -s passam); um processo concorrente pode trocar a pasta entre a conferência e a escrita do Write; vai ao aceite do dono no PR

## Sondas

## Detalhe dos achados

### Condições C1 a C10 (E23.28) no head 5c38e04e
| Condição | Onde | Situação |
|---|---|---|
| C1 lista exata pós-realpath (só `templates/projeto/.githooks/<arquivo>` e `templates/projeto/.forge/config.json`; `.claude/` do modelo travado) | `hooks/conformidade.py:1188-1193`, `ISENCAO_DO_MODELO` em `:307-308`, `casa` com `*` de um nome só | vale; a1, a4-a6, a9-a13 |
| C2 só clone do Forge (nunca sessão de projeto) | `:1189-1191` (`raiz_e_projeto`, `e_clone_do_forge`, contrib ou raiz da sessão) | vale; a3, a21 e `TravaModelo.test_c2_*` |
| C3 o modelo não vale ali (PLUGIN e `core.hooksPath`) | `:1199-1210`; git com erro conta como "vale" | vale; a22, `test_c3_*` |
| C4 só Write e Edit | `:1182`; o Bash não passa por `isencao_do_modelo` | vale; a18-a20 |
| C5 caminho absoluto literal, sem variável, `~` nem `..` | `:1184`, `CAMINHO_LITERAL` em `:310` e `normpath == texto` | vale; a14-a17 |
| C6 cadeia sem link para dentro do clone e nlink 1 | `:1194-1197` | vale, com a leitura "nenhum link que aponte para dentro do clone" (o link `~/.forge-contrib` para fora segue legítimo, fixture `pelo-link-do-home-libera`); o alvo real continua preso por C1 |
| C7 política como dado validado, falha fechado | `isencao_valida` em `:2678-2682`; exceção na conferência zera a isenção em `:1170-1173` | vale; `test_c7_*`, `test_erro_na_conferencia_nao_isenta` |
| C8 22 casos de abuso como fixtures e mutantes | 22 fixtures `a01`-`a22` + 5 liberações; 22 mutantes em `tests/mutantes/trava-modelo*.json` | vale; 22 de 22 mortos (M21 morre por erro do teste declarado, aceitável) |
| C9 PR com rótulo afrouxa-regra e destaque no título | fora deste head (sem PR, pelo brief) | pendente no PR; o fragmento `changelog.d/trava-modelo.md` já declara o afrouxamento |
| C10 risco residual ao aceite do dono | este parecer, A2 | pendente: aceite do dono no PR |

A liberação é estreita: `caminho_barrado` só pula as regras `.githooks/` e `.forge/config.json` quando o caminho resolvido é igual ao que `isencao_do_modelo` devolveu (`:917-921`); as demais regras, a lista de escrita por papel e o `.claude/` do modelo seguem valendo (sonda P12: a raiz `.githooks/pre-push` continua barrada com a isenção calculada na mesma guarda).

### Casos de abuso contra as ameaças
As 22 fixtures cobrem as ameaças do E23.28: escrita na raiz por link (`ln -s ../.. templates/projeto/r`, a1, a2), pasta ou arquivo do modelo como link (a4-a7), link físico (a8), fuga da lista (a9-a11), arquivos em vigor da raiz (a12, a13), forma do caminho (a14-a17), outras ferramentas (a18-a20), repositório que não é o Forge ou sessão de projeto (a3, a21) e o modelo em vigor (a22; o PLUGIN fica no teste de unidade, porque a fixture roda o hook deste clone). Batem.

A1: dimensões que a matriz ainda não fixa, conferidas por sonda direta em `Guarda.isencao_do_modelo` (todas deram o esperado): P1 `templates/projeto/.githooks` trocada por link `../../.githooks` com o caminho literal da lista, recusa; P2 link pendente do modelo para `.githooks/commit-msg` da raiz, recusa; P3 link do modelo para fora do clone, recusa (exceção, falha fechado); P4 `core.hooksPath` absoluto dentro do modelo, recusa; P4b `core.hooksPath=.githooks`, isenta; P5 NotebookEdit, recusa; P6-P8 `//`, `/./` e quebra de linha no fim, recusa; P9-P11 a pasta, subcaminho de `config.json` e outro arquivo de `.forge/`, recusa; P14 clone do Forge fora do contrib e da raiz da sessão, recusa. Correção mínima: fixar P1 a P4 como fixtures (e corrigir a descrição da a5). Severidade informativa, esforço P, dono `tech-lead`.

### A2: risco residual (C10)
Evidência: o Bash do `tech-lead` passa por `mv templates/projeto templates/x`, `rm -rf templates/projeto`, `ln -s .. templates/p2` e `mv templates/p2 templates/projeto` (fixture montada a partir da a18, código 0 em todos), e `isencao_do_modelo` confere o caminho antes de o Write escrever. Caminho de ataque: um agente desviado (injeção de prompt) dispara em segundo plano um laço que troca `templates/projeto` por um link para a raiz e pede o Write na cópia do modelo; se a troca cair entre a conferência e a escrita, o Write grava `.githooks/pre-push` ou `.forge/config.json` em vigor no clone. Severidade baixa: exige ação deliberada e concorrente; o efeito fica no clone de trabalho, aparece no diff, e o CI e o merge do dono continuam o portão; não sobe o teto que o hook já aceita (script em arquivo e nome numa variável, `hooks/conformidade.py:311-312`). Correção mínima, se o dono não aceitar: barrar no Bash a remoção, a troca de nome e a criação de link sobre `templates/projeto` e `templates/` no clone do Forge (esforço P, dono `tech-lead`). Recomendado: aceitar.

## Riscos aceitos e ferramentas
Risco residual que vai ao dono (C10, a aceitar no PR com o rótulo afrouxa-regra, C9): troca por link entre a conferência e a escrita (A2), baixo. Não há risco aceito gravado em `docs/security/aceites/`; o parecer é `aprovado` porque o residual não bloqueia, e o aceite dele é condição do merge, não deste parecer.

Verificado: `python3 -m unittest tests.test_hooks.TravaModelo tests.test_hooks.Hooks.test_fixtures_da_trava_modelo` (7 testes, OK) e `bin/forge-mutante` nas três specs (M1 a M22 mortos), no head 5c38e04e. A suíte inteira é do CI do PR. Ferramentas de varredura de segredo e de dependência não se aplicam à mudança (sem dependência nova nem segredo).
