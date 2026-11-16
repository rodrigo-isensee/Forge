# Pós-release

Propósito: explicar o que `scripts/pos-release` faz depois de cada release, em linguagem simples. Público: o dono do projeto e o `devops-engineer`. Revisão: 2026-11-16.

O texto abaixo só explica. Quem manda é o script: o dono não digita roteiro de comandos, roda um comando só.

## Como rodar
1. Ensaio, num alvo descartável: `ALVO_POS_RELEASE=<alvo descartável> scripts/pos-release ensaio` (troque o nome da variável pelo que está em `alvo-variavel` no arquivo de passos). `alvo-variavel` tem de ser a mesma variável que os passos de fato leem para chegar ao alvo; senão o script confere um alvo e os passos usam outro.
2. Real, depois do ensaio verde: `ALVO_POS_RELEASE=<alvo real> scripts/pos-release real`.

O alvo é sempre informado de forma explícita. Não existe valor de reserva.

## O que o script garante
- Antes do primeiro comando, ele confere o alvo: variável vazia, valor padrão do projeto, alvo que não casa com o modo (ensaio só em descartável, real só no real) ou regra ambígua fazem o script recusar; nesse caso nenhum comando rodou (saída 2).
- Para no primeiro passo com erro (saída 1) e diz qual foi e quantos não rodaram.
- Termina com uma linha de resumo que começa por `pos-release:` (`OK`, `FALHOU` ou `RECUSADO`). Credencial na conexão (`usuário:senha@`, `password=`, `senha=`, `token=`) sai mascarada.

## O que fica em cada arquivo
- `docs/devops/pos-release.passos`: os passos e as regras do alvo (versionado e revisado como qualquer mudança em entrega).
- Este arquivo: a explicação. Mudou um passo, atualize o `.passos`; a descrição de cada passo vai no nome dele.
