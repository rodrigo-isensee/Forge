---
tipo: revisao-seguranca
contrato: 1
pedido: v048
branch: melhoria/v048-dono-pesos
commit: 64183ee2507ebfb92ed62ea70a45cd1abf16a826
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-28
---
# Review de segurança: v048 (#959, DONO-DA-GERACAO-DOS-TEMPOS, E6.13, volta 1 por delta)

Delta `ca3c07bb..64183ee2` (correção do A1 do code review: o PR passa a ser achado pelo sha da execução em `commits/<sha>/pulls`). `forge-check parecer delta`: no domínio só `scripts/pesos-do-ci.py`; testes, fixtures e specs de mutantes fora do domínio, lidos como evidência. A rodada anterior (aprovada em `ca3c07bb`) fica no git.

Gatilhos: dado externo não confiável (API do GitHub) alimentando artefato versionado da suíte, CI (confiança em execução de PR).

## Detalhe
Sem achado. A condição deixada na rodada anterior foi cumprida:

- **Guardas mantidas.** `scripts/pesos-do-ci.py:65-73` (`execucao_de_pr_valida`) não mudou de lógica: na execução, `pull_request`, ci.yml, `repository` e `head_repository` iguais ao `--repo`, `completed/success`; no PR, `merged_at` string, base `develop`, `head.repo` igual ao `--repo` (fork fora), `head.sha` não vazio e igual ao `head_sha` da execução. A nova `pr_unico_valido` (`:76-83`) aplica essa função a cada PR da rota e aceita só quando **exatamente um** a cumpre; nenhum ou mais de um descarta. Um válido entre PRs barrados (fork, não mesclado, outra base, outro sha) entra, o que é correto: o PR válido sozinho prova que o código da execução é o mesclado na develop.
- **Sha validado antes de virar caminho.** `:79-82`: `head_sha` só como `str` e `SHA.fullmatch` (`[0-9a-f]{40}`, `fullmatch` não aceita `\n` final) antes de formatar `repos/{repo}/commits/{sha}/pulls`. Sondas locais com a API injetada, todas `False` e sem nenhuma chamada à API: `"a"*40+"\n"`, `"a"*40+"/../x"`, 41 caracteres, `"g"*40`; controle válido `True`; execução de fork `False`; `head.sha` booleano no PR `False`. Testes: `test_execucao_de_pr_malformada_nao_quebra_nem_entra` (sem sha, outro tipo, curto, com `../`, maiúsculas; afirma `pedidos == []`), `test_resposta_de_prs_que_nao_e_lista_de_prs_validos_nao_entra`, `test_dois_prs_validos_no_mesmo_sha_descartam_a_execucao_e_o_de_fork_no_sha_nao_conta`, `test_guardas_de_fork_e_de_sha_do_pr_valem_cada_uma_sozinha`.
- **Mutantes das guardas.** `forge-mutante` no Revisar-sha: M7, M8, M9 (`v048-dono-pesos-1.json`) e M14, M15, M16, M17 (`v048-dono-pesos-2.json`) morreram.
- **Teto de chamadas.** Uma leitura de `commits/<sha>/pulls` por execução de PR no lugar da de `pulls/N`; continua no máximo uma página de 100 execuções, sem amplificação.
- **Fixtures da API real** (`tests/fixtures/pesos-do-ci/`): só ids de execução, branch, sha, número e base de PR, todos públicos do próprio repositório; sem token, cabeçalho ou dado pessoal além do dono do repositório no `full_name`.
- **CI, permissão e segredo.** Nenhum arquivo em `.github/` no delta; sem token ou escopo novo.

Suíte: `python3 -m unittest tests.test_pesos_do_ci` local, 29 testes OK. CI do PR #959 no Revisar-sha (run 46157387219): suíte 5/5, passos, verificações longas, instalação e catraca verdes; só `bateria (pareceres)` e o agregador `bateria` vermelhos, à espera dos pareceres.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática, a suíte do arquivo, `forge-mutante` e sondas locais sem rede. Faltaram no PATH, sem instalar (`R-CUSTO`): o varredor de segredos, o de workflows e o SAST da skill; lacuna sem efeito, o delta não toca workflow nem traz credencial.
