---
tipo: revisao-seguranca
contrato: 1
pedido: v0474
branch: melhoria/v0474-h1-ferramenta
commit: 4ddaa68bb20c6f79d68e518b9c7e2ab72aa04782
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-17
---
# Review de segurança: v0474 (E2.26, H1 no forge-check)

Diff lido: `origin/develop...4ddaa68b` (bin/forge_tamanho.py novo; bin/forge-check `tamanho_do_pr`, `pr_da_branch(corpo=)`, avisos do `brief gerar`; bin/forge-testes; specs de mutantes M29, M30 e as do H1; tests/test_forge_tamanho.py; tests/test_testes_tocados.py; fragmento de changelog).

## Gatilhos
Gatilhos: controle do Forge (bin/forge-check pr), entrada externa (corpo do PR lido do gh), subprocesso de rede.

## Conferência
- Entrada não confiável não vira comando: o corpo do PR só passa por `re.search` (bin/forge_tamanho.py:13, :39) e nunca é impresso nem executado; a violação ecoa só o total e o `number` convertido em `int` (bin/forge-check:8473). Os nomes de arquivo do `--numstat -z` (bin/forge-check:2050) só viram chave de dicionário passada a `e_codigo`.
- Subprocesso sem shell: `gh pr view <branch> --json ...` em lista, `stdin=DEVNULL`, teto de 10 s, `FileNotFoundError` e `TimeoutExpired` tratados (bin/forge-check:8463-8468). A branch vem do git (`branch_da_ref`, `branch_do_sha`) ou do `headRefName` do `--pr`; o git não aceita nome de branch começado por `-`, então não há injeção de opção no `gh`.
- Falha: módulo ausente sai com rc 2 (`modulo_do_bin`, bin/forge-check:9604-9611, fechada); sem `gh`, sem rede, sem PR, `--previo` ou base do fluxo, só avisa (bin/forge-check:1421-1426), como a decisão do dono H1 manda; o `forge-fechar` roda o `pr` de novo. O `--numstat` que falha avisa e não barra (bin/forge-check:1412-1414), aceitável num controle que, pela decisão, é de aviso fora do PR aberto.
- Regex sem retrocesso catastrófico: 400 mil caracteres hostis em 0,06 s.
- Nada afrouxou: `.github/`, `.githooks/` e `tests/config.json` sem mudança no diff (catraca do CI intacta); `conferencia_do_head` continua somada nas duas chamadas (bin/forge-check:1461, :1477); M29 e M30 trocam a conferência por `[]`, mutante de mesma força que a remoção anterior.

## Achados
- A1 (recomendado) bin/forge_tamanho.py:13 · o <n> da linha de motivo não é comparado ao total: `teto: excedido, 9 linhas, ok` libera um item de 160 linhas (sonda local, tem_motivo True). Integridade do controle, sem ganho de atacante: o autor já escreve o corpo do PR.
- A2 (recomendado) bin/forge-check:1427 · o estado do PR não é olhado: o corpo de um PR fechado da mesma branch vale como motivo. Conferir `state == OPEN` ou documentar que vale o último PR da branch.

## Sondas

## Detalhe dos achados
A1: evidência bin/forge_tamanho.py:13 e :39; caminho: o autor do item (o próprio time) escreve qualquer número; ganho: nenhum além de pular um aviso que ele mesmo poderia justificar. Severidade informativa. Correção mínima: `tem_motivo(corpo, total)` exigindo `int(grupo) >= total`, ou aceitar e registrar. Esforço P. Dono: o autor do item.
A2: evidência bin/forge-check:1425-1427 e :8470-8474; caminho: branch reaproveitada depois de um PR fechado; ganho: nenhum de segurança. Severidade informativa. Correção mínima: `pr.get("state") == "OPEN"` antes de ler o corpo. Esforço P. Dono: o autor do item.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Teste rodado: `python3 -m unittest tests.test_forge_tamanho` (20 testes, OK) e as sondas da regex e do `linhas_de_codigo` acima. A suíte inteira fica com o CI do PR e o QA paralelo (E2.27). Ferramentas de varredura de segredo, SAST e de workflow ausentes no PATH (lacuna registrada; o diff não toca workflow).
