---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-placar-fases
commit: 2343148728af2cf625c63ac236290daa2344d29b
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-18
---
# Review de segurança: v0479-placar-fases (v0478 E20.3)

Escopo: diff `0c47762a..23431487` (bin/forge-placar, tests/evals/test_placar.py, mutantes, changelog, docs/melhoria-continua.md). Ferramenta só de leitura, local, sem rede.

## Gatilhos
Gatilhos: nenhum (sem autenticação, segredo, dependência nova, CI, rede nem controle do Forge; a entrada externa é um arquivo local `--prs` gerado pelo operador).

## Achados
- A1 (recomendado) bin/forge-placar:207 · `--prs` com mergedAt de forma válida e data inválida (2026-13-45) ou JSON aninhado fundo (linha 197) sai em traceback com código 1, que o cabeçalho reserva a "reprovado"; capturar ValueError e RecursionError e sair 2 como fonte ilegível.

## Sondas

## Detalhe dos achados
Fronteiras lidas:
- `--prs` (bin/forge-placar:189-215): lido por `ler` (erro sem conteúdo do arquivo), `json.loads`, tipo conferido (lista, dict); o corpo do PR só passa pela regex `SEM_TESTE` (ancorada, sem quantificador aninhado, linear) e nunca é impresso; a saída só traz semanas calculadas e contagens. Sonda com `ESC[31m` no corpo: a linha `sem_teste:` não ecoa o byte. Sem caminho de injeção no terminal nem no JSON.
- git (bin/forge-placar:534-588): `subprocess.run` com lista, sem shell; `base..ponta` vêm de `%P` do próprio git; `git show <sha>:<nome>` começa com o sha, então o nome do arquivo não vira opção. Leitura de blob não executa filtro nem textconv sem configuração local do operador. Nome do item (linha 584) vem do assunto do merge e é limitado por `[^'\s]+`; nome de ref do git não admite caractere de controle, e o `--json` escapa os de controle.
- `--ref` vai ao git como argumento posicional (linha 171, anterior a esta branch, e agora em `itens_do_dia`): um valor começando por `-` seria opção do git, mas quem o passa é o próprio operador na linha de comando; sem caminho de ataque, não é achado. Se um dia o `--ref` vier de arquivo ou de outro agente, use `--end-of-options` antes dele.

A1: evidência bin/forge-placar:207 (`fromisoformat` sem captura) e :197 (`json.loads` capta só `JSONDecodeError`) · caminho: arquivo `--prs` malformado, gerado à mão ou por versão diferente do gh; não há atacante, só operador confuso pelo código de saída · severidade: baixa (robustez) · correção mínima: `except (json.JSONDecodeError, RecursionError)` na 197 e `try/except ValueError: continue` (ou SystemExit código 2) na 207 · esforço: P · dono: tech-lead (autor do item).

## Riscos aceitos e ferramentas
Sem risco aceito. Ferramentas: leitura do diff e sondas locais em `$TMPDIR` (`python3 -I bin/forge-placar --prs <arquivo>` com data inválida, JSON aninhado 100000 níveis e corpo com caractere de controle). Suíte: não rodada localmente (brief: sem suíte local); a suíte inteira fica com o CI do PR. Varredor de segredos e SAST não estão no PATH: lacuna registrada; o diff não traz credencial.
