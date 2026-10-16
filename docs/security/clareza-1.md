---
tipo: revisao-seguranca
contrato: 1
pedido: clareza-1
branch: melhoria/clareza-pacote-1
commit: 4a83650c49af18bdf537b8b2394cc347cead94c8
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-16
---
# Review de segurança: clareza-1

Escopo: `git diff b16d20f22a3f3d540ffdca42a70ec653ded0c0cf...4a83650c49af18bdf537b8b2394cc347cead94c8`, 8 arquivos (+117 / -5). O foco está nos controles do Forge que o diff toca: `docs/regras/R-DECISAO.md`, `tests/config.json` e `agents/jarvis.md`. Também revisei o modelo de pedido, a skill `modo-iniciante` e o `agile-coach`. Considerei quatro ameaças:
- uma regra ou um invariante afrouxar ou sumir;
- "delegado" ou "ordem ampla" virar atalho para o agente decidir sozinho custo, acesso, exceção a regra ou ato irreversível;
- o recibo ou o formato de pergunta pedirem segredo ou dado pessoal;
- instrução de segurança perdida nas duas linhas alongadas do `jarvis.md`.

## Gatilhos
`R-SEGURANCA`: a mudança toca `docs/regras/` (`R-DECISAO`) e `tests/config.json` (invariantes), que são controles do Forge.

## Resumo
**Aprovado.** Não houve afrouxamento. Encontrei dois achados de severidade baixa e um informativo, nenhum bloqueante. Como os confirmei:
- **Comparação programática com a base:**
  - `R-DECISAO.md`: nenhuma linha antiga saiu.
  - `tests/config.json`: nenhuma chave nem item removido e nenhum valor alterado; só houve acréscimo.
  - `agents/jarvis.md`, linhas 33 e 108: a comparação caractere a caractere (`difflib`) só mostra inserções. O texto anterior está inteiro, incluindo `R-DECISAO`, a gravação no mesmo turno e "nunca sobe sozinho".
- **"delegado":** as exceções estão explícitas em `docs/regras/R-DECISAO.md:27` (custo `R-CUSTO`, acesso, exceção a regra `R-CONFORMIDADE`, ato irreversível; "continuam indo ao usuário") e em `templates/projeto/docs/pedidos/_modelo.md:16`.
- **"ordem ampla":** a regra (`docs/regras/R-DECISAO.md:28`, `agents/jarvis.md:108`) só cobre itens `confirmado` ou `delegado`. Item novo ou irreversível volta como pergunta. Ou seja, a mudança restringe a ordem ampla, não a amplia.
- **Recibo e formato de pergunta:** nenhum dos dois pede segredo nem dado pessoal. A regra de credencial "nunca pelo chat" (`skills/modo-iniciante/SKILL.md:28`) segue intacta. O exemplo neutro trata a opção que custa dinheiro como "decisão de custo à parte" (`skills/modo-iniciante/SKILL.md:42`).
- **Testes:** `python3 -m unittest tests.test_clareza` rodou 5 testes, OK.

## Achados

### S1 (baixa): a saída "decidam vocês" é oferecida em toda pergunta, sem repetir as exceções no ponto de uso
- **Evidência:**
  - `skills/modo-iniciante/SKILL.md:37` (item 6 do formato) oferece "Se preferir, diga 'decidam vocês'" em toda pergunta.
  - `agents/jarvis.md:108` manda seguir o formato "nos dois perfis", com "a saída 'decidam vocês'".
  - As exceções só aparecem em `docs/regras/R-DECISAO.md:27` e no modelo de pedido (`_modelo.md:16`).
- **Caminho de ataque (sem adversário externo; é erro de agente):**
  1. Uma pergunta de custo ou de acesso sai no formato fixo com a saída "decidam vocês".
  2. O usuário leigo responde "decidam vocês".
  3. O agente segue a recomendação e marca o item como `delegado`, porque o texto que ele lê na hora (skill e jarvis) não traz a exceção.
- **Impacto:** a decisão de custo (`R-CUSTO`) ou de acesso fica sem o dono. A regra continua proibindo isso, por isso a severidade é baixa e não alta.
- **Correção mínima:** no item 6 da skill e na frase do `jarvis.md:108`, acrescentar "(não se oferece em pergunta de custo, acesso, exceção a regra ou ato irreversível; `R-DECISAO`)".
- **Esforço:** P. **Dono:** autor da branch (tech-lead E1).

### S2 (baixa): o invariante protege a frase das exceções, mas não a lista
- **Evidência:**
  - `tests/config.json`, chave `docs/regras/R-DECISAO.md`, guarda `nunca são delegáveis assim` e `viram item \`delegado\``.
  - A lista em si (`**custo** (\`R-CUSTO\`), **acesso**, **exceção a regra** (\`R-CONFORMIDADE\`) e **ato irreversível**`, `docs/regras/R-DECISAO.md:27`) não está protegida.
- **Caminho de ataque:** uma edição futura tira um item da lista, por exemplo "**acesso**", e mantém a frase. Os testes passam e "acesso" vira delegável sem destaque no título do PR, contornando a política de afrouxamento.
- **Correção mínima:** acrescentar ao invariante o trecho literal da lista, ou um trecho por item (`\\*\\*custo\\*\\*`, `\\*\\*acesso\\*\\*`, `\\*\\*exceção a regra\\*\\*`, `\\*\\*ato irreversível\\*\\*`). O mesmo vale para `_modelo.md:16` ("Custo, acesso, exceção a regra e ato irreversível nunca são delegáveis").
- **Esforço:** P. **Dono:** autor da branch (tech-lead E1).

### S3 (informativa): `## Registro de clareza` fica no pedido versionado
- **Evidência:** `templates/projeto/docs/pedidos/_modelo.md:21-26` e `:46-47`. As tags gravam um `<resumo>`; o item `delegado` grava a frase literal do usuário.
- **Avaliação:** o modelo não pede segredo nem dado pessoal, e o pedido já grava decisões literais hoje, então não há caminho de ataque novo. O risco é um resumo de `NAO-ENTENDI:` copiar algo que a pessoa colou por engano no chat, como um token.
- **Sugestão (opcional):** em "Tags de registro", uma linha dizendo que o resumo nunca leva segredo nem dado de pessoa.
- **Dono:** autor da branch.

## Plano em cartões
- S1 e S2: um cartão para o autor da branch, de esforço P. Não bloqueiam este parecer. Se forem corrigidos nesta branch, o novo HEAD precisa de novo parecer (o `commit:` muda).
- S3: recomendação opcional, a critério do autor.

## Lacunas de ferramenta
Nenhuma destas ferramentas está no PATH desta máquina: `gitleaks`, `semgrep`, `osv-scanner`, `zizmor`, `actionlint`, `trivy`. Não instalei nenhuma (`R-CUSTO`).
- **Impacto:** baixo. O diff só traz texto e um teste Python sem dependência nova; não toca workflow nem dependências.
- **Segredos:** no lugar do `gitleaks`, fiz uma busca manual no diff por padrões de segredo e dado pessoal (token, senha, chave, CPF, e-mail). Só encontrei texto de regra e do exemplo neutro.

## Riscos aceitos
Nenhum.
