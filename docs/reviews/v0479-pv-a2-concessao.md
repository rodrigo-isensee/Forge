---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-pv-a2-concessao
commit: 4c325c557ee7cf5544a28488eb06346ae9bfbc1f
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 (E57.61, PR-VERDE A2, concessão presa ao commit)

## Achados
- A1 (bloqueante) bin/forge_autorizacao.py:29 · a ressalva é lista negativa (AR-3), e o item 5 da ADR 0018 faz da lista só teste: a regra é o vocabulário positivo. "depois", "antes", "sem", "só com" saem ativa (S1, igual ao S2 da segurança). Corrija pelo vocabulário positivo numa função que o gravar da G1.2 reuse.
- A2 (recomendado) bin/forge_autorizacao.py:30 · "depois do Commit só pareceres" aceita qualquer arquivo de docs/devops/ (patch, documento) e de qualquer branch nas quatro pastas. Restrinja aos arquivos cujo frontmatter tem `branch:` igual ao Ramo; isso fecha junto o A1 da segurança (rename para docs/qa/).
- A3 (recomendado) docs/propostas/v0479-pr-verde-de-primeira.md:61 · o A2 do desenho é do gravar (E1: "o gravar lê o sha dos pareceres... recusa"; oráculo concessao-solta em tests.test_autorizacao_gravar, :103). Esta branch entrega só a metade do leitor: o PR diz "A2 parcial" e a metade do gravar vira cartão preso à G1.2.

## Sondas
- S1 · corpo "pode aplicar o rótulo afrouxa-regra no item PV-A2 depois do CI verde" (idem "antes da release", "sem a segurança", "só com o QA"), Estado-inicial ativa, fixture ItemPresoAoCommit · espera: ('adulterada', 'ativa com ressalva na mensagem') · obtido: ('ativa', '')

## Parecer
Reprovado pelo A1. O resto do diff está correto e simples: o `git` sem as `GIT_*` herdadas e com falha fechada, `Commit` sha40 e `Ramo` sem `-` inicial nem `..` (sem injeção de opção), o nome exato do ramo conferido de novo no frontmatter depois do `git grep -F`, e o leitor só aperta, porque hoje nenhum consumidor lê o `ativa` além do `autorizacao ler`. Tamanho dentro do H1 (73 linhas em `bin/`).

**Pergunta do autor (a regra no leitor cumpre o A2?).** Em parte. O leitor conferir na leitura é necessário de todo jeito, porque o PV-A4 vai ler o arquivo no head. Mas a E1 da ADR 0018 põe a derivação e a recusa no `gravar`, e o desenho (`:61`, `:103`) diz que o A2 depende da G1.2 e tem o oráculo `concessao-solta` em `tests.test_autorizacao_gravar`, que ainda não existe. Com a G1.2 fora da `develop`, o certo é entregar o leitor agora e declarar o resto (A3). Mesclar como A2 completo fecharia o item sem a barreira de gravação.

**A1, detalhe.** `bin/forge_autorizacao.py:29` e `:153`: a `RESSALVA` lista marcas proibidas. Faltam quatro das que a própria ADR cita (`antes`, `depois`, `sem`, `menos` sozinho), e mesmo completa ela continua sendo a forma do AR-3, que o item 5 recusa de propósito. Correção: uma função única com o vocabulário fechado do item 5 (termos de ato, `item <CARTAO>`, termos de validade do item 6, verbos de permissão, artigos, preposições e cortesia). Concessão `ativa` com palavra fora dele fica `adulterada`. Um teste confere que nenhuma marca da ADR entra no vocabulário. A G1.2 depois importa a mesma função, e as duas leituras não divergem. Corrigir só o A2 da segurança (as quatro palavras) fecha a sonda, mas mantém a classe AR-3.

**Limite registrado, sem achado.** O `ler` roda o `git` na raiz principal e usa `refs/remotes/origin/<Ramo>` sem buscar. Se a ref local estiver velha, o leitor não vê um envio novo de código depois do `Commit`. A conferência contra o head é do PV-A4 (catraca no próprio head), e isso cabe no desenho.

**A4 da segurança (pareceres exigidos × ao menos um).** Concordo com o recomendado. A classe exigida é conferida no merge (`forge-check classe` pelo `bin/forge-fechar`), e a docstring de `:168` já declara "ao menos um".

**Ferramentas citadas, sem refazer.** A classe nova `tests.test_autorizacao.ItemPresoAoCommit` passou (6 testes, OK, 3,5 s). `bin/forge-mutante --cobertura --base d4f0b10a` deu rc 0, com todas as guardas do diff cobertas por mutante declarado (M1 a M28 em quatro specs). Não rodei a suíte inteira, que fica no CI do PR (o brief diz sem suíte local). A execução dos mutantes fica com o QA (E57.63).
