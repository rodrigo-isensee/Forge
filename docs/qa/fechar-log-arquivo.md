---
tipo: qa
contrato: 1
pedido: fechar-log-arquivo
branch: melhoria/fechar-log-arquivo
commit: 12fb5147b5a96c2413b1afc0f924a5a2a3517af1
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-21
---
# QA: fechar-log-arquivo (log em arquivo do forge-fechar)

O código testado é o do commit acima; o HEAD da branch (6cd6803) só acrescenta os pareceres de review e de segurança (sem mudança de código).

## Achados

## Critério → teste → resultado
O pedido não usa CA-n; as obrigações são E1 e E2.

| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1: primeira linha `log: <caminho>` | test_log_em_arquivo_com_um_registro_por_passo...; sonda S1 | primeira linha (antes do passo 1) | passou |
| E1: arquivo com hora por passo, modo 600 | mesmo teste; sonda S1 (`stat` = 600) | modo 600; um registro por passo 1 a 7 | passou |
| E1: tela igual à de antes | sonda S2 (tela sem a 1ª linha == log sem a hora) | n/a | passou |
| E1: segredo mascarado no log, inteiro na tela | test_log_tambem_guarda_a_saida_de_erro...; sondas S3 e S4 | stdout e stderr | passou |
| E1: pasta por FORGE_FECHAR_LOG_DIR | testes (pasta do setUp); sonda S5 | pasta alternativa | passou |
| E1: vale no --dry-run | test_dry_run_tambem_grava_o_log; sonda S1 | n/a | passou |
| E2: testes, doc e fragmento | suíte; leitura do diff | n/a | passou |

## Cenários e resultado real
- Suíte completa (`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -q`, raiz da worktree em 6cd6803): `Ran 1270 tests in 419.096s` / `OK`.
- `scripts/validar-plugin.sh`: `Validation passed`.
- Sondas em $TMPDIR, repositório git próprio com remoto local, sem rede:
  - S1 `--dry-run`: rc 0, primeira linha `log: .../forge-fechar-logs/forge-fechar-p1-<hora>-<pid>.log`, arquivo modo 600, 9 registros com hora UTC (passos 1 a 7 mais aviso).
  - S2: a saída na tela, sem a linha `log:`, é idêntica ao log sem o prefixo de hora (`diff` vazio).
  - S3 stderr: `err token=ghp_ZZZ999` inteiro na tela, `token=***` no log, rc 1 preservado.
  - S4 stdout: `--titulo 'x ghp_ABCDEF123456'` aparece inteiro na tela (1 ocorrência) e `ghp_***` no log (0 ocorrências do token).
  - S5: com FORGE_FECHAR_LOG_DIR em outra pasta, o log foi para ela.
- Vermelho antes do verde: conferido pelo review (teste no commit ea5968a antes do código 12fb514); não refeito aqui.
- Mutação: sem ferramenta gratuita para shell na stack do Forge; não aplicável.

## Observações (não bloqueiam; já viram o cartão FECHAR-LOG-ENDURECER)
- Máscara sem maiúsculas (`GH_TOKEN=`), sem `usuario:senha@` na URL e sem `Basic`; o texto `token <palavra>` em prosa também é mascarado.
- O script não espera os registradores ao sair: quem lê o log logo após o fim pode ver a cauda atrasada (na sonda S3, o log estava completo após um instante).
- Pasta de log pré-existente sem conferência de dono e link; sem limpeza de logs antigos.
