---
tipo: revisao-seguranca
contrato: 1
pedido: v0457
branch: melhoria/escopo-ponto
commit: 22e6bce13053072c0c2d88da4e8b3ca04b4125e6
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-12
---
# Review de segurança: escopo-ponto (E23.58, volta por delta)

Revalidação por delta `0a0a7c80..22e6bce1` (E23.56) do parecer da E23.54. O A10 está corrigido com a correção mínima proposta, sem afrouxar nada: `parecer_de_portao_da_branch` recebe o Base-sha e passa-o a `veredito_trocado` (`bin/forge-check:2564` e `:2377`), então a busca do veredito trocado cobre a branch inteira, e o intervalo do escopo segue no Desde. A S8 refeita no head dá rc 1, e o cruzamento que a matriz não fez (volta anterior que tira o reprovado da pasta num octopus, subpasta e `git mv` juntos) também. Nenhum bloqueante; A6 e A9 seguem como cartões da versão seguinte.

## Gatilhos
`R-SEGURANCA`: controle do Forge (a conferência de entrega decide o que é escopo da entrega e o que é anexo de portão).

## Achados
- A6 (recomendado) bin/forge-check:2240 · cartão para a versão seguinte, furo anterior a esta branch: os filtros L08 e G2 (:2470) confiam na origin/develop local na etapa codigo; reescrita por git update-ref, escondem do escopo o arquivo fora do declarado (S4, S5)
- A9 (recomendado) bin/forge-check:1610 · cartão: o pr escolhe o parecer por (data, nome) e confia que a entrega recusou o forjado; defesa em profundidade: recusar o parecer cujo commit: tem outro veredito noutro arquivo da pasta na história da branch

## Sondas

## Detalhe dos achados
**A10, corrigido.** `bin/forge-check:2564` passa `base_sha` (validado como commit e ancestral do head em `:2453` a `:2460`, antes de qualquer uso) e `:2377` o repassa a `veredito_trocado`, que roda `rev-list --full-history base_sha..head` e o `ls-tree` do Base-sha (`:2345` a `:2349`). Merge da develop dentro da branch só acrescenta commits à busca: mais versões lidas, o que só pode recusar (falha fechada), nunca aceitar. Mutante M36 (voltar a `de`) na lista de `tests/mutantes/v0457-escopo-ponto-5.json`; M10 e M20 com o `de:` da linha nova (AR-12 conferido).

Refeito no head, numa worktree destacada própria, com uma subclasse de `MatrizDaBuscaDoVeredito` fora da árvore; cada sonda roda também numa cópia do head com o M36 aplicado, para provar que tem força:
- S8 (x.md reprovado sobre o revisado; volta 2 apaga o x.md e cria `docs/notas/b.md`, conferida D; volta 3 cria `docs/reviews/y.md` aprovado com o `commit:` do revisado): head rc 1, `fora do declarado no brief "docs/reviews/y.md"`, intervalo D..head; com o M36, rc 0 (`ok (anexo do portão)`).
- Cruzamento 1: volta 2 é um octopus de três pais cujo merge faz `git mv docs/reviews/x.md docs/notas/x.md` (conferida no octopus); volta 3 faz `git mv docs/notas/x.md docs/reviews/sub/y.md` e troca o veredito para aprovado. Head rc 1, sub/y.md fora; M36 rc 0.
- Cruzamento 2: o mesmo, com o commit do revisor num ramo lateral do octopus (não é primeiro pai). Head rc 1; M36 rc 0.
- Cruzamento 3: revisor num ramo lateral do octopus, que apaga o x.md no merge; volta 3 cria `docs/reviews/sub/y.md` aprovado. Head rc 1; M36 rc 0.
- Cruzamento 4: o ramo lateral do revisor cria e apaga o x.md antes do octopus (o x.md nunca está numa árvore de primeiro pai); volta 3 cria sub/y.md aprovado. Head rc 1; M36 rc 0.

Conclusão: nada bloqueante nesta branch e nenhum cartão novo de segurança. A matriz da E23.56 cruza a janela com cada dimensão, não as dimensões entre si; os cruzamentos acima passam no head, e incluí-los como células é melhoria de teste do QA, não defeito. Nota de estilo ao tech-lead (não é achado): a docstring de `veredito_trocado` (`:2339`) ainda fala em "intervalo" e o parâmetro se chama `de`, embora agora receba o Base-sha.

**A6 (sem mudança, cartão).** O texto da E23.42 vale. Cartão: "L08/G2 confiam na origin/develop local na etapa codigo". Dono: tech-lead.

**A9 (cartão).** A defesa em profundidade da E23.50 vale (o `pr` recusa o parecer vigente quando outro arquivo da pasta, em qualquer commit da branch, tem o mesmo `commit:` e `branch:` com outro `parecer:`). Dono: tech-lead.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Lido: `forge-check parecer delta` (só `bin/forge-check` no domínio) e o diff de `tests/test_selo_e_entrega.py` e das listas de mutantes. Rodado no head, numa worktree destacada própria: `tests.test_selo_e_entrega` (98 testes, OK, 364 s) e `tests.test_conf_escopo` (16 testes, OK), e as cinco sondas acima no head e no M36. Os mutantes M1 a M36 e a cobertura são do QA. Varreduras de segredos e de workflow não se aplicam (sem segredo nem workflow no diff).
