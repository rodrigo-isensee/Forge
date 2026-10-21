---
tipo: review
contrato: 1
pedido: ci-postinstall-cli
branch: melhoria/ci-postinstall-cli
commit: d346475762edfb6a1f3dc1227cabfc4173f73521
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-20
---
# Review: CI, postinstall do Claude Code CLI

Escopo: `0f480c8...d346475`, 2 arquivos (`.github/workflows/ci.yml` +1 -1 e o fragmento `changelog.d/ci-postinstall-cli.md`). Quem revisa não é o autor.

Veredito: **aprovado**, sem bloqueantes.

## Ferramentas
- Sem comando de ferramenta aplicável ao diff; actionlint e zizmor sem PATH. A prova de execução é a bateria do PR, a cargo do QA. Pendência registrada, não revisão manual.

## O que foi conferido
- Escopo do script: `--allow-scripts=@anthropic-ai/claude-code` nomeia um único pacote e o comando fixa a versão exata 2.1.296. Scripts de outros pacotes, inclusive dependências, não são liberados; não há curinga nem `--ignore-scripts=false` global.
- Bateria intacta: o diff toca só a linha do `run`; o `if` do passo e os passos seguintes (validate --strict, e2e de instalação) seguem sem condição nova.
- Menor escolha: permitir o script de um pacote fixo é menos que fixar o Node, que prenderia a bateria a uma versão. Não abre caminho para script de dependência.
- Custo (R-CUSTO): nenhum serviço pago; só instalação pública do npm no runner. Não afrouxa o processo.
- Fragmento em `changelog.d/` presente e coerente.
- Causa nos logs do pedido (E1.1): falha com 1 pacote, verde com 2.

## Riscos e observações
- A flag não pôde ser exercitada localmente (npm não roda neste WSL 1); depende da bateria do PR. Se o npm do runner recusar a flag, o passo falha de forma visível.

## Achados
