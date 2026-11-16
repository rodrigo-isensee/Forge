---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-caminho-runner
commit: 72d2eaa01398a1f9d9713347fe2a9620fa035863
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-13
---
# Review de segurança: v047 caminho-runner (E5.23)

Head revisado: 72d2eaa0. Delta: `scripts/verificar-contribuicao.sh:55` (o home do runner passa a virar `@/` em vez de `@`), dois casos em `tests/test_forge.py` e o mutante `tests/mutantes/v047-caminho-runner.json`. Parecer aprovado.

## Gatilhos
Guarda de contribuição contra vazamento de caminho pessoal e segredo (R-SEGURANCA, controle do Forge). A mudança fecha um furo: o marcador antigo comia a barra final do home do runner, e um caminho pessoal colado logo depois dele escapava da varredura.

## Achados
- A1 (recomendado) scripts/verificar-contribuicao.sh:41 · O regex exige barra depois do nome: barras repetidas entre o diretório de homes e o nome, ou o nome no fim da linha ou antes de aspa, escapam. Anterior a este delta.

## Sondas

## Detalhe dos achados
Verificado por execução do mesmo trecho de substituição e regex do script, com entradas construídas por partes para não gravar caminho pessoal no parecer.

Funciona (acusa): home do runner seguido de caminho pessoal colado, com uma barra, com duas ou três barras e com `./` no meio; o mesmo para o diretório de usuários do macOS; caminho pessoal entre aspas simples ou duplas, desde que a barra final exista; prefixo `/mnt/<letra>/`; `file://`; home do runner repetido duas vezes antes do pessoal; nome `Runner` com maiúscula. Os 15 testes de `VerificarContribuicao` passam, e o mutante CR-M1 reverte exatamente a linha 55 e é morto pelo teste citado.

Passa sem acusar, tudo anterior ao delta e não causado por ele:
- Barras repetidas entre o diretório de homes e o nome (`home//nome/x`) e o segmento `./` entre eles. Caminho de ataque: só um colaborador que cole um caminho já anormal; ganho, vazar o nome de usuário local num PR. Severidade baixa.
- Caminho sem barra final (`HOME=/home/nome` no fim da linha). O teste `test_dados_neutros_dos_testes_passam` aceita de propósito `em /home/ana`, então é decisão de projeto; o risco é vazar um nome real nessa forma. Severidade baixa.
- Home do runner com barra dupla e nome vazio (`runner//nome/`) passa, mas não é caminho pessoal real.

Correção mínima (A1, esforço P, dono tech-lead, pedido à parte, sem devolver esta entrega): trocar as barras do regex por `/+` entre o diretório e o nome, e decidir se o nome sem barra final deve ser acusado quando seguido de fim de linha ou aspa, com caso de abuso e corpus de legítimos.

## Riscos aceitos e ferramentas
Nenhum risco aceito. CI do PR: não há PR aberto; rodei o teste afetado (`VerificarContribuicao`, 15 testes, OK) e as sondas locais. Suíte inteira fica para o CI do PR. Ferramentas externas (gitleaks, semgrep) não usadas: o delta é uma linha de shell sem segredo.
