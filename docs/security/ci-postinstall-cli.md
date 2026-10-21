---
tipo: revisao-seguranca
contrato: 1
pedido: ci-postinstall-cli
branch: melhoria/ci-postinstall-cli
commit: d346475762edfb6a1f3dc1227cabfc4173f73521
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-20
---
# Review de segurança: ci-postinstall-cli

## Gatilhos
CI/CD (workflow `.github/workflows/ci.yml`) e execução de script de instalação de pacote (`R-SEGURANCA`).

## Achados

## Detalhe dos achados
Sem achado bloqueante. Conferido no diff `0f480c8..d346475` (2 arquivos):

- Escopo da permissão: `.github/workflows/ci.yml:120` passa `--allow-scripts=@anthropic-ai/claude-code`, um único nome de pacote, e o pacote instalado está fixo em `@2.1.296`. A permissão nomeia o pacote, não é curinga nem `--ignore-scripts=false` global; o script de instalação de dependência não ganha autorização por essa linha. É o mesmo pacote e a mesma versão que o passo já instalava antes; muda só a autorização do postinstall que baixa/liga o binário nativo.
- Bateria intacta: o diff altera uma linha e o fragmento; nenhum passo saiu, nenhum `if:` mudou (o passo mantém `!cancelled() && steps.gate.outputs.pesada == 'true'`), e `claude plugin validate . --strict` e o e2e de instalação continuam logo depois (linhas 121 a 126).
- Menor escolha: fixar o runtime em versão anterior deixaria o CI preso a uma versão de runtime sem patches de segurança e não atacaria a causa (a versão mais antiga do instalador de pacotes não rodava o script; a seguinte rodava). Permitir o script de um pacote nomeado e de versão fixa é mais estreito. Não há outra ocorrência de instalação de pacote global nos workflows (`grep` em `.github/workflows`).
- Custo (`R-CUSTO`): nenhum. Pacote público, runner já em uso, sem serviço novo.
- Residual (recomendação, não bloqueia): o postinstall é código do fornecedor do pacote que roda no runner; a versão fixa limita a janela, e a bateria do PR roda com `permissions` do workflow, sem segredo de publicação neste passo. Se a versão for subida, revisar a mudança do script. Quando o pacote passar a trazer o binário por dependência opcional, o `--allow-scripts` pode ser retirado.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Lacunas: o instalador de pacotes e o runtime não estão no PATH deste ambiente (WSL), então a semântica exata de `--allow-scripts` na versão do instalador de pacotes usada no runner não foi reproduzida aqui; a conferência foi pela leitura do diff e pela causa registrada no pedido (E1.1, dois logs). `actionlint` e `zizmor` também sem PATH. A prova funcional é a bateria do PR.
