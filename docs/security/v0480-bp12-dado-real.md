---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-bp12-dado-real
commit: 0fedb7b6886125f54f600c9d1f569005621f4a1a
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-23
---
# Review de segurança: v0478 (PR #832, BP12, revalidação por delta, E144.9)

Rodada anterior: parecer no head 82277931 (E144.5, commit 540aef6a), no git; não recopiada aqui.

## Delta lido
`forge-check parecer delta`: intervalo `82277931..0fedb7b6`; no domínio só `skills/ux-design/SKILL.md` (diff lido inteiro). Fora do domínio: `docs/qa/` e `docs/reviews/` (pareceres). Nada em hook, bin, script, workflow, controle do Forge, segredo ou dependência.

Gatilhos: nenhum de código; dado pessoal só como texto de processo (LGPD, minimização).

## Veredito: só aperta ou neutro
- `skills/ux-design/SKILL.md:13` (Empatizar): **aperta**. Passa a citar "dado real ou amostra anonimizada", alinhando a skill ao portão de `templates/projeto/docs/constituicao.md:13` e oferecendo o caminho minimizado.
- `skills/ux-design/SKILL.md:15-16` (Idear sem "ou ASCII"; Prototipar "sem build nem dependência externa"): **neutro**. A proibição de dependência externa no protótipo continua.
- `skills/ux-design/SKILL.md:22,49` (hipótese "como tal"; "lê e grava"): **neutro**, redação.

## Achados anteriores
- A1 (recomendado, rodada 82277931): **fechado** por 0fedb7b6. A parte "só origem, data, quantidade" não foi levada à skill; fica coberta pela constituição do projeto (`constituicao.md:13`), norma que a skill aplica, e a skill agora aponta a amostra anonimizada. Sem caminho de ataque realista restante que justifique outra volta (proporcionalidade).

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Testes dos arquivos tocados no head 0fedb7b6: `PraticasDeEspecificacao`, `Neutralidade`, `NeutralidadeDoNucleo`, `Orcamento` (test_forge) e `test_orcamento_instrucao` (20 testes, OK). Suíte inteira no CI do PR #832, não rodada local, conforme o brief. Varreduras de segredo e dependências não se aplicam a diff só de texto.
