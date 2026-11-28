---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-guardas-mutante
commit: b2c7255d6e0013f91c7db551c3ab08bcdd4a8589
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: v0478 E62.13 (melhoria/v0479-guardas-mutante)

Escopo: diff `8ee73d15..b2c7255d` (base = develop, pai direto do head), 4 arquivos, 100 inserções e 0 remoções: `changelog.d/v0479-guardas-mutante.md`, `tests/mutantes/v0479-guardas-0-47-12.json` (spec nova, G1 a G5), `tests/test_forge_check_pr.py` (classe nova `BaseDaEtapa`), `tests/test_parecer_conteudo.py` (classe nova `PrLeARefNaoOHead`). `bin/forge-check` e todo código de controle ficam iguais.

## Gatilhos
Gatilhos: controle do Forge (testes e mutantes das guardas da catraca do `forge-check pr`/veredito).

## Só aperta
Confirmado: a entrega só aperta. Nenhuma linha removida (numstat 0 remoções), nenhum teste apagado, pulado ou afrouxado, nenhum código de produção, hook, workflow ou regra tocado. Ela só acrescenta mutantes declarados e testes que provam o ramo de falha de cinco guardas já existentes:
- G1 `bin/forge-check:2050` testes do QA lidos na ref do PR, não no HEAD;
- G2 `bin/forge-check:2094` domínio do parecer conferido na ref;
- G3 `bin/forge-check:8837` base do brief passada ao `pr` como `origin/<base>`;
- G4 `bin/forge-check:2073` só `aprovado` e `riscos-aceitos` aprovam;
- G5 `bin/forge-check:2092` commit só de pareceres paralelos barra pelo campo `commit` (AQ-5).
Cada trecho `de` aparece exatamente uma vez em `bin/forge-check` no head (âncora sem ambiguidade). Os mutantes descrevem os desvios que um atacante interno (agente que quer o merge sem portão válido) exploraria: ler o HEAD local em vez da ref do PR, ignorar a base, aceitar parecer reprovado, aceitar commit de pareceres; todos morrem, então a regressão dessas guardas passa a ser barrada.

Os testes novos são locais e passivos: repositório temporário com `git` e `mock` de `pr_da_cli`; sem rede, sem segredo, sem escrita fora do diretório temporário.

## Achados

## Sondas

## Detalhe dos achados
Sem achados. Suíte inteira não rodada aqui (só no CI; brief: sem suíte local); rodei o que a entrega acrescenta: os 5 mutantes da spec (todos `morreu`) e as 4 provas novas (OK).

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Ferramentas: `forge-mutante` (spec inteira, `--rev b2c7255d`), unittest das classes novas, `git diff --numstat`. Lacuna: `gitleaks`, Semgrep, `zizmor` e `actionlint` ausentes do PATH (não instalados, `R-CUSTO`); o diff não toca workflow nem traz credencial (lido à mão).
