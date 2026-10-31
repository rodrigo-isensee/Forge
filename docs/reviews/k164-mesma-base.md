---
tipo: review
contrato: 1
pedido: k164-mesma-base
branch: melhoria/k164-intervalo
commit: 97b178fe9b378f7010e96debf336ddd416b1cdaf
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-30
---
# Review: k164-mesma-base (E2, branch melhoria/k164-intervalo)

Escopo revisado: `git diff 8c07b4448aecc1a46202b69a81df9f48ebc01ea5 97b178fe9b378f7010e96debf336ddd416b1cdaf` (5 commits: testes antes do código em 36f0773, código em 5072c7b, spec de mutação em 66c39d6 e b10bdfc, fragmento em 97b178f). Revisão inteira, não por delta (primeira rodada desta branch).

## Achados
- R1 (recomendado) agents/tech-lead.md:18 · o formato do achado nos agentes, nos modelos de parecer e na docstring de bin/forge-check:59 segue só `<arquivo>:<linha>`; documentar o `[-<linha>]` aceito (tests/test_volta_por_delta.py:857 fixa o texto atual; mudar junto)
- R2 (recomendado) tests/test_forge.py:4177 · falta o caso de borda do intervalo de uma linha só (`5-5`): o mutante `>` para `>=` em bin/forge-check:1283 sobrevive; somar `5-5` aceito ao teste e um mutante à spec
- R3 (recomendado) bin/forge-check:1283 · o `split("-")` duas vezes na mesma condição fica mais legível com `ini, _, fim = m.group(4).partition("-")` numa linha antes do elif

## Parecer
Aprovado. Faz o que a E2 pede, nem mais nem menos: a expressão `ACHADO` aceita `arquivo:a-b` (um hífen só, dois números), o intervalo invertido vira erro nomeado, e malformados (`3-`, `-3`, `3-5-7`, `3--5`, `a-b`) seguem recusados pela própria expressão, porque o arquivo é `\S+?` antes do único `:`. O campo `linha` é tratado como texto em todos os consumidores (bin/forge-check:1370, 1509, 1520), então o intervalo sai copiado inteiro no brief de volta, como o teste afirma. Nenhum outro leitor do bloco em `hooks/`, `scripts/` nem `.githooks/`.

Ferramentas (citadas, não refeitas à mão; o Forge não tem `docs/engineering/praticas.md`, sem regra de ferramenta pendente):
- `python3 -m unittest tests.test_forge.VoltaComRecomendacao tests.test_volta_por_delta`: 78 testes, OK.
- `bin/forge-mutante tests/mutantes/k164-intervalo.json` (rev 97b178fe9b37): M1 a M4 morreram.
- `bin/forge-mutante --cobertura --base 8c07b444`: rc 0, linha 1283 coberta por M2 e M3.
- Sem shell tocado; shellcheck não se aplica.

M14 (`R-REVIEW`, decisão M14): cumpre. `git diff --numstat --no-renames 8c07b44...HEAD` conta 4+2 em bin/forge-check e 15 em tests/test_forge.py, 21 linhas (fora a spec em tests/mutantes/ e o fragmento); um comportamento só (o intervalo no achado); não toca `hooks/`. bin/forge-check está em PROTEGIDOS: a segurança (E1.3) revisa à parte.

Regras: `R-NEUTRO` respeitada (nome da branch e textos neutros; a origem órfã ficou só como fonte); `R-CUSTO` sem efeito; nenhuma invariante afrouxada; fragmento em changelog.d/ presente. Commits em Conventional Commits, testes antes do código. R1 a R3 não devolvem.
