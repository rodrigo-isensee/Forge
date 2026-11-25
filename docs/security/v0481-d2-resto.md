---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-d2-resto
commit: ec5c7040a3176579a18b8c2429a540ab7e2b44d6
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-24
---
# Review de segurança: v0481 (E11.12, #881, D2 `forge-check pronto`)

Gatilhos: controle do Forge (`bin/forge-check`, novo `bin/forge_pronto.py`, mapa do `bin/forge-testes`).

Base `30dde21`..`ec5c704`, 3 commits, 10 arquivos, 446 linhas a mais e 1 a menos. Lidos inteiros: `bin/forge_pronto.py`, `cmd_pronto` e o parser em `bin/forge-check`, `tests/test_forge_pronto.py`, as três specs de mutante, e o restante do diff (`bin/forge-testes`, `docs/indice-forge.md`, `tests/pesos-d4.json`, fragmento de changelog).

## Veredito: só aperta ou neutro
- **Nenhuma checagem existente muda.** A única linha removida no diff troca a tupla `FORGE_CHECK` de `bin/forge-testes:153` para acrescentar `test_forge_pronto` (um teste a mais no mapa, nenhum a menos). `docs/indice-forge.md` e `tests/pesos-d4.json` só ganham uma linha cada. Catraca, workflows, hooks, pre-push, `cmd_pr`, `forge_tamanho` e as classes de neutralidade não aparecem no diff. As correções de "sem_manutencao" e de trecho de mutante ficam só nos arquivos novos da própria branch (`tests/test_forge_pronto.py`, `tests/mutantes/v0481-d2-resto*.json`).
- **O `pronto` é um subcomando novo, só do lado do autor.** Nada no diff lê o resultado dele como prova: não substitui o `pr`, a catraca nem o CI, que continuam sendo o portão. Por isso não abre caminho para pular revisão.
- **O teto H1 é igual ou mais rígido que no `pr`.** O total vem de `contagens_do_intervalo(ancora, HEAD, estrito=True)` a partir da base comum, o mesmo intervalo do `base...HEAD` do `pr`, com o mesmo `e_codigo` e o mesmo `tem_motivo` (`bin/forge_pronto.py:42`). Sem PR aberto e sem `--corpo`, o `pr` só avisa (`bin/forge-check:1477-1482`), e o `pronto` reprova (`bin/forge_pronto.py:39-40`). Isso aperta.

## rc 2 (não verificável) nunca vira passa
- No `cmd_pronto`, a falha de merge-base ou do diff sai com 2 (`bin/forge-check:1227-1231`), e o `--corpo` ilegível também sai com 2 (`:1232-1237`). Testes: `CmdPronto.test_base_ausente_sai_2` e `test_corpo_ilegivel_sai_2`.
- Em cada passo, qualquer código diferente de 0 reprova (`bin/forge_pronto.py:54-59`), inclusive o 2 de não verificável, o processo morto por sinal e o comando que não abre (`rodar` devolve 2). O `pronto` sai com 1, nunca com 0. Ele perde a distinção entre 1 e 2 vinda do passo, mas falha fechado. A catraca com código diferente de 0 entra nas falhas (`:44-47`).
- Sem `gh`, sem rede, com o PR fechado ou sem PR, o corpo fica `None` (`bin/forge-check:1239-1241`), e isso reprova (`bin/forge_pronto.py:39-40`). Teste: `test_sem_corpo_e_sem_pr_reprova` e `test_pr_aberto_da_o_corpo_e_fechado_nao`.
- Saída de passo fora de UTF-8: `subprocess.run(text=True)` levanta `UnicodeDecodeError`, que não é capturado. O processo morre com traceback e sai com 1, não com 0 (sonda local, abaixo). Falha fechado; a mensagem é ruim, mas não há caminho de ataque.

Sonda local (arquivo `sonda_pronto.py` no rascunho da sessão, contra o Revisar-sha): passo com saída 2, 1, 3 ou 255, morto por SIGKILL ou inexistente → `conferir` devolve 1 em todos. Catraca com saída 2, 1 ou SIGKILL → 1 falha. Corpo `None` → 1 falha. 151 linhas com `teto: excedido, 150 linhas, x` → 1 falha. Nenhuma combinação deu 0.

## Observações (sem caminho de ataque, não são achados)
- O `pronto` roda a `tests/catraca.py` da própria branch (`bin/forge_pronto.py:44`). O CI roda a da base (`.github/workflows/catraca.yml:40-52`). Uma branch que afrouxe a catraca passaria no `pronto` e reprovaria no CI, que segue como portão. Como pré-portão, isso não afrouxa nada. Se o autor quiser paridade, use o script da base, como o CI faz.
- `--base` chega ao `git merge-base` e ao `forge-testes --base` sem `--` antes (`bin/forge-check:1227`, `bin/forge_pronto.py:22,25`). Quem passa o argumento é o próprio autor na própria cópia. Não há fronteira de confiança.

## Suíte e CI
Rodado aqui: `python3 -m unittest -q tests.test_forge_pronto`, 14 testes OK no Revisar-sha. CI do #881 no `ec5c704`, como estava no momento deste parecer: instalação, bateria (passos), bateria (verificações longas) e árvore já provada passaram. Os 10 jobs da suíte estavam pendentes. A bateria (pareceres) falhou porque faltam os pareceres. A catraca falhou por R-CONFORMIDADE: `bin/forge-check` é controle e pede o rótulo `afrouxa-regra` do dono depois do último push (ADR 0008). Esse rótulo é decisão do dono (R-DECISAO). Este parecer serve de insumo para ela: o diff só aperta ou é neutro. O merge continua preso à suíte verde no CI.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Leitura estática, mais a sonda local acima. Não houve segredo nem dependência nova (o código só usa a biblioteca padrão). Por isso `gitleaks` e `osv-scanner` não se aplicam a este diff.
