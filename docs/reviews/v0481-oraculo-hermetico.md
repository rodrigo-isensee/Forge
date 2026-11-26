---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-oraculo-hermetico
commit: 2affeefe68cc7006f370800400b22276ee9f64c7
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-26
---
# Review: v0481 (E27.2, testes herméticos do oráculo do sempre-atual)

1ª rodada completa no 2affeefe, diff contra a develop 707fea56 (4 arquivos, +41 -25, só testes e fragmento de changelog).

## Achados

- A1 (bloqueante) tests/sem_claude_ancestral.py:67 · Com --proc o oráculo troca PROC e proc_coerente por dublê em todos os casos; nenhum teste lê mais o /proc real. Mutante PROC="/proc-nao-existe" (produção adiaria tudo) passa no oráculo (59 OK) e no test_sempre_atual (142 OK); na base o oráculo no CI o mata (S1)
- A2 (recomendado) tests/test_oraculo_sempre_atual.py:24 · O "Limite conhecido" (a ocupação olha o /proc inteiro) e o cabeçalho de tests/test_sempre_atual.py:2 (o oráculo cobre com /proc de verdade) ficaram falsos com a árvore do teste
- A3 (recomendado) tests/sem_claude_ancestral.py:49 · A mensagem de uso não cita [--proc]; --proc sem valor ou sem script depois cai em IndexError (linha 52) em vez da mensagem de uso

## Sondas

- S1 · 2affeefe com bin/forge_sempre_atual.py:33 PROC = "/proc-nao-existe"; unittest tests.test_oraculo_sempre_atual e tests.test_sempre_atual · espera: ao menos uma falha (adiaria tudo por duvida:proc) · obtido: 59 OK e 142 OK

## Parecer

Reprovado, por um bloqueante (A1).

O que está certo:
- Nenhum teste apagado, pulado nem renomeado. A única asserção removida é a de preparo em `vivo()` (comm lido do /proc real), trocada pela montagem determinística da árvore. Cada caso continua afirmando o mesmo comportamento: adia com `claude` ou `forge-fechar` vivo no escopo, e o processo de verdade segue vivo.
- Código de produção intocado (`git diff 707fea56...2affeefe -- bin` vazio). A costura é só do lançador de teste, que nenhum script do Forge lê.
- `ForgeCheck.test_raiz_depois_do_subcomando_e_git_isolado`: o `gh` falso de "sem PR" mantém as três afirmações (rc 0, veredito aprovado, stderr vazio) e tira a dependência de credencial.
- Testes afetados rodados no sandbox do Bash, no meu clone, no 2affeefe: `tests.test_oraculo_sempre_atual` mais o caso do `test_forge`, 60 testes OK em 139 s (na base, segundo o pedido, falham 40).
- Tamanho: zero linha de código de produção. As guardas mudadas (`if proc:`, `if resto[0] == "--proc"`) são do lançador de teste, não código de controle da classe C, então não pedem mutante declarado.

A1, a perda de cobertura: antes, o oráculo rodava no CI sobre o `/proc` da máquina. Era o único teste da suíte que provava, de ponta a ponta, que `PROC = "/proc"` e `proc_coerente()` dão "coerente" num `/proc` de verdade. O `test_sempre_atual` só usa árvore falsa (`mock.patch.object(fsa, "PROC", ...)`). Agora o lançador força `proc_coerente = lambda: True` e a pasta do teste sempre, e um defeito que fizesse a ferramenta adiar tudo em produção (S1) passa verde em toda a suíte. Isso fere o critério do brief: o que cada teste afirma continua afirmado. Sugestões, à escolha do autor:
- (a) Um caso que rode no CI sobre o `/proc` real: a ferramenta pelo lançador sem `--proc`, com um `claude` falso vivo, afirmando o `adiado` com a pasta dele. No sandbox ele dá `duvida:proc` e precisa de tratamento explícito, sem pular em silêncio no CI.
- (b) Um teste do núcleo que chame `fsa.proc_coerente()` e `fsa.processos_de_interesse()` sem dublê e afirme o resultado conforme o namespace, comparando `os.readlink("/proc/self")` com `os.getpid()`. Ele tem de matar o mutante da S1 no CI.

A2 e A3 são recomendados e viram cartão depois do merge, salvo se o autor os resolver junto na volta.

CI: a branch ainda não tem PR (E27.3), então não há run do 2affeefe e a linha `ci` não é gravada. A próxima rodada pede o PR em rascunho aberto e o CI do head verde.
