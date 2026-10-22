---
tipo: qa
contrato: 1
pedido: impl-n-doutor
branch: melhoria/impl-n-doutor2
commit: eb6db50ffddaa4d53e0aba23348b24b70d242b3c
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
revisor: forge:qa-engineer
data: 2026-10-22
---
# QA: impl-n-doutor (E1.4)

Sem UX nem API. Diff `a3dbe22..eb6db50` (commits `526ef0b`, `1f3bc73`, `e4a82bc` e o fragmento `eb6db50`). Não escrevi o diff. Review (`a86c76c`) e segurança (`4523ca7`) aprovados sobre `eb6db50`; depois dele só entraram esses dois pareceres. Base das obrigações: desenho §1 e §3 (itens 1, 2 e 4) e o adendo de ameaças. Tudo numa cópia em `$TMPDIR` (`git archive eb6db50`), sem rede e sem `gh` real (R-CUSTO).

## Obrigação -> teste -> resultado
| ID | Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|---|
| Q-1 | 62: só a presença do nome, nunca o valor; lista fixa sem o nome da chave de API (P-A = A; A62-1, A62-2, C62-5) | `test_doutor_custo`: nome no ambiente, no `env` do projeto e no `settings.local`; marcador fora de stdout, cache e `erros.log` | valor da credencial | passou; `git grep` do nome da chave de API em `bin/` e `hooks/`: nada |
| Q-2 | `apiKeyHelper` por presença, nunca executado (A62-3) | teste do arquivo-sentinela | execução de código do repositório | passou |
| Q-3 | JSON só de arquivo regular, até 1 MiB; fonte ruim não derruba as outras (A62-4, A62-5) | `settings_gigante...` (5 MiB e pipe sem escritor) e `formato_estranho...` | tamanho máximo, pipe, `env` não objeto, valor vazio ou só espaço | passou; ver recomendação 1 |
| Q-4 | Silêncio sem sinais; frase "pode estar" (A62-6, C62-4); SessionStart grava no cache sem o valor | `sem_nenhum_dos_nomes`, `o_aviso_diz_que_pode...`, `o_hook_do_inicio...` | máquina por assinatura | passou |
| Q-5 | RELOGIO-WSL: aviso acima de 300 s, uma vez por dia, atrasado e adiantado, número em minutos calculado por nós | `test_doutor_relogio` (Stop duas vezes, adiantado, 60 s) | limiar 300 s; segundo Stop em silêncio | passou |
| Q-6 | Falha da consulta não marca o dia; versão que falhou ou `FORGE_VERIFICAR_VERSAO=0` não consultam o relógio (AR-7) | `consulta_do_relogio_que_falha...`, `com_a_consulta_de_versao_que_falhou...`, `consulta_desligada...` | falha de rede | passou |
| Q-7 | `HEAD` sem redirecionamento, sem credencial, certificado validado, host público na 443, prazo total (AR-1 a AR-3, CR-1 a CR-3) | `redirecionamento_nao_e_seguido...`, `host_local_sem_ponto_ip...`, `conexao_que_nunca_responde...`, `o_pedido_nao_leva_credencial...` | IP, `localhost`, porta diferente, servidor pendurado | passou |
| Q-8 | `Date` defensivo e teto de 30 dias; `FORGE_RELOGIO_REMOTO` só com `FORGE_PERMITE_LOCAL=1` (AR-4 a AR-6) | `cabecalho_ausente...`, `desvio_de_dez_anos...`, `o_ponto_de_injecao...` | sem fuso, lixo, 10 anos | passou |
| Q-9 | Modo completo mostra o aviso do relógio e o `--rapido` não | `o_doutor_completo_mostra_o_aviso_e_o_rapido_nao` | rápido sem rede | passou |
| Q-10 | F8: três branches protegidas em silêncio; sem proteção cita a branch e a skill `ci-cd`; proteção clássica vale (A8-5) | `test_doutor_protecao_gh` (3 testes) com `argv` conferido | só `--method GET` | passou |
| Q-11 | Ruleset inativo ou sem regra de PR e checks não conta; 403, 404 de repositório, formato ruim, sem rede e `nameWithOwner` estranho viram "não consegui conferir" ou silêncio, nunca "protegida" (A8-1 a A8-4) | `ruleset_desativado...`, `403_e_404...`, `404_de_branch_sem_o_repo_view...`, `formato_inesperado...`, `nome_do_repositorio_fora_do_padrao...`, `sem_rede...` | injeção de opção e de caminho | passou |
| Q-12 | Outro host não é consultado; `--rapido` e hook não chamam o `gh`; branch ausente no remoto é pulada; saída do `gh` não vai ao aviso (A8-6 a A8-8) | `outro_host...`, `modo_rapido_e_o_hook...`, `branch_que_nao_existe...`, `a_saida_do_gh_nunca...` | modo rápido | passou |
| Q-13 | R-VERIFY/P3 = B: cada commit se reverte sozinho e a suíte que sobra fica verde | sonda abaixo | independência dos itens | passou |
| Q-14 | Fragmento `changelog.d/impl-n-doutor2.md` com o nome da branch e uma entrada | `tests.test_forge` no pre-push; leitura | nome do fragmento | passou |
| Q-15 | E1 pede 4 itens, inclusive o M11 | n/a: sem commit na branch | n/a | ausente (ver abaixo) |

## Execução
- Módulos afetados (`test_doutor`, `test_doutor_custo`, `test_doutor_relogio`, `test_doutor_protecao_gh`, `test_atualizar`): `Ran 173 tests`, `OK`, sem rede.
- Ambiente sujo (`ANTHROPIC_AUTH_TOKEN` e `CLAUDE_CODE_USE_VERTEX` exportados): `test_doutor` e `test_atualizar` `Ran 128 tests`, `OK`. O ajuste de fixture em `tests/ambiente_git.py` cumpre o "o que pode quebrar" do desenho.
- **Vermelho antes do verde:** com `bin/` e `hooks/` da base `a3dbe22` e os testes do HEAD, os três módulos novos dão `Ran 45 tests`, `FAILED (failures=36, errors=31)`. Os que passam são guardas de ausência.
- **Reversão por commit (P3 = B):** num clone, `git revert --no-commit` de cada um sobre `eb6db50`, sem conflito, e os módulos `test_doutor*` e `test_atualizar` que sobram: sem `526ef0b` 162 testes OK; sem `1f3bc73` 153 OK; sem `e4a82bc` 159 OK; sem `eb6db50` 173 OK. Confirma o PQ-5 do Jarvis e o review.
- **Mutação (só no diff, à mão, sem ferramenta na stack):** 6 mutantes. Mortos: limiar do relógio multiplicado por 10, "adiantado" trocado por "atrasado", `GET` trocado por `POST` no endpoint de regras, `enforcement` ignorado. Sobreviveram: limite de JSON de 1 MiB para 10 MiB (o teste usa 5 MiB e não pega o 10 MiB nem a fronteira exata) e retirada do `S_ISREG` (equivalente na prática: pipe sem escritor lê vazio e vira JSON inválido, e `/dev/zero` estoura o limite).
- A suíte completa roda no pre-push deste envio.

## M11
O E1 pede quatro itens e a entrega traz três. O M11 não tem commit: o autor parou pela regra de parada (sem cache de plugin na máquina, o passo 0 do desenho não se faz). Concordo com a parada, e nada no diff finge o item (`bin/forge-atualizar` intocado, fragmento e commits citam só 62, RELOGIO-WSL e F8). Julgamento contra o E1: o E1 não está completo, e esta entrega só cumpre o E1 se o dono cortar o M11 (pergunta na pré-entrega, R-DECISAO) ou o cartão M11-CACHE o assumir. O QA não corta nada e não bloqueia por isso: o que foi entregue está correto. O PR não pode declarar o E1 inteiro feito.

## Recomendações
Não bloqueiam; incluo as do review e da segurança que conferi.
1. Teste de fronteira do limite de 1 MiB em `tests/test_doutor_custo.py`: arquivo de exatamente 1 MiB lê, e 1 MiB + 1 byte não (mata o mutante que sobreviveu).
2. Teste que compare `SINAIS_DE_CUSTO` de `bin/forge-doutor` com a lista de `tests/ambiente_git.py` (review).
3. Comentário em `bin/forge-doutor` (`enforcement` ausente conta como ativo, porque o endpoint de regras só devolve as ativas) (review e segurança).
4. `conferir_protecao_github` repete o `conferir_gh`: dois `gh auth status` no modo completo (review).
5. `CLAUDE_CODE_USE_BEDROCK=0` conta como presente: falso aviso raro, e o texto já diz "pode estar" (review).

## Achados
