---
tipo: revisao-seguranca
contrato: 1
pedido: melhorias-de-projeto-1311
branch: melhoria/mp1311-stack-mapa-ts
commit: 803c07bf4154f3cb6e5e5315e5bd98509b0d8ba8
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-13
---
# Review de segurança: mp1311-stack-mapa-ts

## Gatilhos
Entrega de texto do pacote da stack (receita de prova do vermelho) mais um teste estrutural e um fragmento de changelog; nenhum código de produção, workflow, segredo ou dependência. Revisada a receita de `git stash` e do executor de testes da stack pelo lado da execução fora do projeto e da perda de trabalho (`R-SEGURANCA`).

## Achados
- A1 (recomendado) stacks/node-react/pronto.md:36 · RESOLVIDO em 803c07bf: o texto agora exige que o `git stash push` crie entrada antes do teste e manda o `pop` sempre, falhe o teste ou não.

## Sondas

## Detalhe dos achados
A1. Evidência: `stacks/node-react/pronto.md:36` (linha "Prova"). Sonda local em repositório descartável: com um stash antigo na pilha e o arquivo de produção já commitado, `git stash push -- a.ts` imprime "No local changes to save" e retorna 0; o `git stash pop` seguinte aplicou o stash antigo (`o.txt`) na árvore. Arquivo novo não rastreado faz o push falhar (rc=1), sem perda. Caminho de ataque: não há atacante; é risco de integridade do trabalho do próprio agente (mistura de mudança alheia; nada se perde, pois o pop em conflito preserva o stash). Severidade: baixa. Correção mínima: conferir que o push criou entrada (contagem de `git stash list` antes e depois) e só então dar pop; mandar o pop mesmo quando o teste não falha ou a execução é interrompida; valer só para produção modificada e ainda não commitada. Esforço P. Dono: tech-lead (texto da stack).

Conferência pedida. (1) Não abre execução fora do projeto: o executor roda só o `<teste>` do mapa, caminho dentro da pasta do projeto, sem URL, sem rede e sem shell com entrada externa; o stash age só nos arquivos listados (pathspec), nunca em `--all` nem `--include-untracked`. (2) Não perde trabalho: usa `pop`, nunca `drop` nem `clear`; conflito no pop mantém a entrada; a condição "árvore limpa" protege o que está fora dos arquivos de produção. Residual só o A1. O teste novo (`tests/test_forge.py:6879`) só lê texto do `pronto.md`; o fragmento de changelog não tem conteúdo executável.

## Revalidação por delta (803c07bf)
`forge-check parecer delta` desde 00cf2d22: no domínio só `stacks/node-react/pronto.md` (linhas 36 e 37); `tests/test_forge.py` fora do domínio. A1 fechado: o `push` só prossegue se `git stash list` ganhou uma linha (sem entrada, nenhum `pop`, logo não aplica stash alheio), e o `pop` é obrigatório após o teste, falhando ou não, sem deixar produção no stash. Mantém pathspec (nunca `--all` nem `--include-untracked`), `pop` e nunca `drop`/`clear`. A linha 37 só amplia o destino do `sem prova` (parecer ou relatório). Texto, sem execução nova nem superfície de ataque. `python3 -m unittest tests.test_forge.TextosAQ3Stack`: 4 testes OK. Sem PR: bateria no CI do PR.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Sem PR ainda: parecer sobre texto e um teste estrutural, sem suíte; a bateria fica para o CI do PR. Ferramentas de varredura (gitleaks, semgrep) não se aplicam a texto; não rodadas.
