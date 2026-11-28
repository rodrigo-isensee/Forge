---
tipo: revisao-seguranca
contrato: 1
pedido: v048
branch: melhoria/v048-validar-yaml-workflow
commit: d7a8c8f9e4508668b497477e1283b08ae0322fb5
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-28
---
# Review de segurança: v048, validador de YAML dos workflows (E13.6), 1ª rodada

Gatilhos: CI/CD (validador dos workflows de `.github/`, que vai entrar no envio)

Escopo lido: `d7a8c8f9` contra a base `a1971853` (`scripts/validar-yaml-workflow.py`, `tests/test_validar_yaml_workflow.py`, `tests/mutantes/v048-validar-yaml-workflow.json`, fragmento do changelog). Os commits seguintes da branch (`933a51fd`, `34dde413`) só trazem os pareceres de QA e de review, sem código.

O que se confirma: o validador **não executa nada** (só importa as bibliotecas de expressão regular, `sys` e `pathlib`; nada de subprocesso, avaliação, import dinâmico nem rede) e **não acrescenta dependência**. **Erro de leitura falha fechada**: arquivo ausente, link quebrado, pasta e byte inválido em UTF-8 saem com rc 2 (linhas 65-69, conferido à mão). A saída não abre brecha para comando do log do CI: as linhas vêm de `splitlines()`, então chave e valor não carregam quebra de linha, e toda linha começa por `<arquivo>:<n>:`. O corpus legítimo passa: os 5 workflows, o `ci.yml` do modelo de projeto, os dois `dependabot.yml` e o `actionlint.yaml` saem com rc 0. Os 13 testes passam neste head.

O que não se confirma: **custo linear** (A1) e **não seguir link** (A2). As duas coisas estavam pedidas no brief e falham com repro. Severidade baixa nas duas: para explorar, alguém precisa pôr no repositório uma linha ou um link que passe pelo review. Elas bloqueiam por serem defeito de comportamento provado contra o requisito declarado (`R-SEGURANCA`), não por serem vulnerabilidades de alto impacto. A correção é pequena.

## Achados
- A1 (bloqueante) scripts/validar-yaml-workflow.py:40 · a remoção do comentário (`\s+#.*$`) é quadrática numa sequência de espaços sem `#`: 4,1 s numa linha de 40 KB, e o tempo quadruplica cada vez que a linha dobra (S1). Uma linha longa num workflow trava o envio de todos. Trocar por `\s#.*$` e `.rstrip()`, que é linear e passa os 13 testes
- A2 (bloqueante) scripts/validar-yaml-workflow.py:66 · `read_text` segue link e lê arquivo especial sem limite: um link para `/dev/zero` em `.github/workflows/` prende o validador (S2), e um link para fora do repositório ecoa o conteúdo na saída (S3). Recusar o que não é arquivo regular (`lstat` + `S_ISREG`) e passar de 1 MiB, com rc 2
- A3 (recomendado) scripts/validar-yaml-workflow.py:62 · sem argumento e sem `.github/workflows/` (ou com a pasta vazia), sai rc 0 sem ler nada: falha aberta quando o envio chamar o script de outro lugar. Com zero arquivos lidos, sair com rc 2 e uma mensagem no stderr

## Sondas
- S1 · `validar("a: x" + " "*N + "y\n")` com N = 10000, 20000, 40000 · espera: tempo linear, abaixo de 0,05 s (1 milhão de linhas curtas, 10 MB, levam 5,2 s) · obtido: 0,27 s, 1,02 s, 4,10 s; com `\s#.*$` e `.rstrip()`: 0,000 s nas três
- S2 · `ln -s /dev/zero .github/workflows/zero.yml; timeout 10 scripts/validar-yaml-workflow.py` (cópia do script numa árvore temporária) · espera: rc 2 (não é arquivo regular) · obtido: rc 124, o script lia sem parar até o timeout
- S3 · `ln -s <tmp>/fora.txt .github/workflows/link.yml` (fora.txt: `segredo: token: XYZ-fora-do-repo`), sem argumento · espera: rc 2, sem ecoar o conteúdo de fora · obtido: rc 1 e `link.yml:1: valor simples com ... token: XYZ-fora-do-repo` no stdout

## Detalhe dos achados
**A1.** Evidência: `scripts/validar-yaml-workflow.py:40` e a sonda S1, com `validar()` carregado do head. Caminho: hoje, só quem escreve um workflow. Quando o cartão PREPUSH-VALIDA-YAML ligar o script ao envio, uma linha longa de espaços (colada sem querer ou posta por um PR mesclado) faz o envio de cada contribuidor levar minutos, e no CI queima o tempo do job: uma linha de 400 KB passaria de 6 minutos. Não há ganho para quem ataca além da negação de serviço do fluxo. Severidade baixa. Correção mínima: na linha 40, `re.sub(r"\s#.*$", "", resto).rstrip()`. Conferi numa cópia que os 13 testes continuam verdes e que S1 cai para 0,000 s. Falta um teste com linha longa de espaços dentro de um orçamento de tempo, que é o orçamento pedido para um analisador de entrada livre. Esforço P. Dono: `devops-engineer`.

**A2.** Evidência: `scripts/validar-yaml-workflow.py:62` (o glob aceita link) e `:66` (`read_text` segue o link e lê o arquivo inteiro). Caminho: o git versiona link simbólico. Um link em `.github/workflows/` para `/dev/zero` (ou para um arquivo enorme) prende o envio de quem atualizar a branch (S2). Um link para fora da árvore imprime até 60 caracteres por valor e a chave inteira do arquivo de destino (S3), e no CI isso iria para o log. Severidade baixa: o PR teria de passar pelo review, e no CI do PR o autor já controla o código que roda. Correção mínima: antes de ler, `st = os.lstat(arq)`; se não for `stat.S_ISREG(st.st_mode)` (isso já recusa link, pasta, FIFO e dispositivo) ou se `st.st_size` passar de 1 MiB, imprimir `<arq>: não é arquivo regular` (ou `grande demais`) no stderr e retornar 2. Isso vale com argumento e sem ele. Testes: um link para um arquivo válido sai 2 e um arquivo acima do teto sai 2. Esforço P. Dono: `devops-engineer`.

**A3.** Evidência: `scripts/validar-yaml-workflow.py:61-62,73`. Repro: uma cópia do script numa árvore sem `.github/workflows/` (e outra com a pasta vazia) sai com rc 0 e saída vazia. Caminho: o envio ou o CI chamam o script de um lugar onde a pasta não é resolvida (por exemplo, uma cópia instalada fora do repositório) e o verde chega sem nada conferido, que é a mesma aparência de verde do #929. Severidade baixa. Correção mínima: se nenhum arquivo foi lido, imprimir no stderr e retornar 2. Esforço P. Dono: `devops-engineer`.

Fora destes achados e já registrados por outros pareceres, sem repetir aqui: o mutante `break` sobrevivente (QA A1), o índice derivado que deixa o CI do head vermelho (review A1) e os subprocessos do teste sem `-I` (review A3).

Suíte: o CI do Revisar-sha está vermelho (run 46166823206, workflow CI, `failure`, pelo índice derivado do review A1). Este parecer não afirma CI verde. Rodei só os 13 testes do arquivo novo, as sondas S1 a S3 e o repro do A3.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática, sondas locais em árvore temporária e cronometragem de `validar()`. Faltaram no PATH, e ficam como lacuna: o varredor de segredos, o SAST, os linters de workflow e o auditor de dependências da skill `cyber-security`. Nenhum deles mudaria este parecer, porque não há dependência nova nem workflow alterado.
