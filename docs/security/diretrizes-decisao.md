---
tipo: revisao-seguranca
contrato: 1
pedido: v046
branch: melhoria/diretrizes-decisao
commit: 39c163cc5d2fdfd69982e1eb3e80815aea0202e6
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-13
---
# Review de segurança: diretrizes-decisao (v046 E26.14)

Revisado: `git diff c340c322..3a86bd38` (R-DECISAO.md, falar-com-o-dono/SKILL.md, fragmento de changelog). Só texto; sem código, workflow nem segredo.

## Gatilhos
`R-SEGURANCA`: regra de decisão do dono e controle de escopo e aceite (texto protegido por invariantes de `tests/config.json`). Sem gatilho de código ou pipeline.

## Achados
- A3 (recomendado) docs/regras/R-DECISAO.md:15 · A diretriz 8 perdeu "nem a do dono" e "origem": a regra agora só diz "não passa calada"; a skill falar-com-o-dono/SKILL.md:14 ainda manda decisão ruim do dono voltar a ele. Mantenha uma palavra que cubra o dono na regra.

## Revalidação por delta (E26.21)
Delta 3a86bd38..39c163cc (`forge-check parecer delta`): só R-DECISAO.md e falar-com-o-dono/SKILL.md, texto. A1 (6 trechos de `invariantes` removidos) corrigido: `python3 -m unittest tests.test_forge.RegrasInviolaveis` OK (3 testes) no head. A2 corrigido: "(não amplia autorização)" voltou em R-DECISAO.md:24. O formato `decidido: <porta> — <critério> — <fato>` é só descritivo. O texto novo encurtado não afrouxa controle: a escolha provisória segue sujeita aos vetos da `R-DECISAO`. Custo declarado (diretriz 8 sem "nem a do dono" e sem "origem" em R-DECISAO) sem caminho de ataque realista: vira recomendado A3, não bloqueante. A1 e A2 do parecer anterior ficam fechados.

## Sondas
- S1 · python3 -m unittest tests.test_forge.RegrasInviolaveis (head 39c163cc) · espera: OK, sem trecho invariante ausente · obtido: OK (3 testes)

## Riscos aceitos e ferramentas
Nenhum risco aceito. As diretrizes 1, 8 e 9 (custo em tokens e ganho por opção, origem do item, conferência de decisão ruim, também a do dono) não afrouxam controle: o texto manda levar ao dono, e a escolha provisória segue sujeita aos vetos da `R-DECISAO`. Suíte inteira: só no CI (sem PR aberto agora); rodado só o teste de invariantes (OK). Sem lacuna de ferramenta (revisão de texto).
