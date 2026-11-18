---
tipo: qa
contrato: 1
pedido: v0474
branch: melhoria/v0475-copia-pasta
commit: a108ef531a7b40d2bcc05082f23a73ef3888aa37
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-17
---
# QA: v0475-copia-pasta (E3.44, parecer E3.57)

Escopo: `bin/forge-copia` (clone e worktree só dentro de `~/.forge-contrib`), `tests/test_forge_copia.py`, spec de mutantes, texto nas duas skills e patch em `docs/propostas/`. Sem especificação de UX nem contrato de API; as obrigações vêm do cabeçalho do script e da linha E3.44 do pedido (cópia só na pasta liberada, `--no-track`).


## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Clone nasce na pasta, branch da base sem upstream | Cria.test_clone_dentro_cria_branch_a_partir_da_base_sem_rastreio | `--no-track` | passou |
| Worktree nasce na pasta, sem upstream | Cria.test_worktree_dentro_cria_a_branch | `--no-track` | passou |
| Base inexistente sai 1 (git falhou) | Cria.test_clone_com_base_que_nao_existe_falha_com_1 | base inválida | passou |
| Recusa destino fora | Recusa.test_fora_da_pasta | fora da raiz | passou |
| Recusa `..` mesmo voltando para dentro | Recusa.test_com_ponto_ponto_mesmo_voltando_para_dentro | `..` | passou |
| Recusa link simbólico | Recusa.test_por_link_simbolico | symlink de escape | passou |
| Recusa a própria pasta (cheia e vazia) | test_a_propria_pasta_liberada, test_a_pasta_liberada_vazia_tambem_e_recusada | igualdade com a raiz | passou |
| Prefixo parecido não vale | Recusa.test_prefixo_parecido_nao_vale | `.forge-contrib-outro` | passou |
| Destino ocupado | Recusa.test_destino_ocupado | não vazio | passou |
| Branch/base com cara de opção | Recusa.test_branch_ou_base_com_cara_de_opcao | `-` inicial | passou |
| Clone sem origem; branch inválida | test_clone_sem_origem, test_nome_de_branch_invalido | argumento ausente/inválido | passou |

## Cenários e resultado real
- Local: `python3 -I -m unittest discover -s tests -p test_forge_copia.py` no head: 13 testes, OK. Skills: `test_skills_v0442.py` 4 OK. A suíte inteira roda no CI do PR (`bateria`); não há PR nem check-run neste head, então não cito run.
- `forge-testes --vermelho 2fa505d7` terminou depois do primeiro texto: 10 provas (asserção), 760 não provam, regressao=2 (as duas acima, H=falha B=ok, reproduzidas com `discover -p`), sem veredito=1 (volta ao autor). Antes disso ele ficou na fila da trava `R-TETO` (outra sessão pesada) e não deu veredito; não conta como vermelho. Substituí por cópia em `$TMPDIR` com `bin/` da base e o teste do head: `Ran 13 tests ... FAILED (failures=10)`. Os 3 que passam são recusas que dão saída 2 por acaso (python3 sem o arquivo sai 2) e ficam provados pelos mutantes. O autor deve colar o `--vermelho` oficial no PR.
- Mutação: `bin/forge-mutante tests/mutantes/v0475-copia-pasta.json`, `rev=efe73e175521`: M1 a M10 todos `morreu` (linhas 28, 31, 32, 34, 36, 54, 56, 62, 63, 65). Sobrevivente: nenhum.
- `forge-mutante --cobertura --base 2fa505d7` não rodou (fila da trava `R-TETO`). Conferência manual das guardas do diff: `..`, igualdade com a raiz, commonpath, destino ocupado, `-` inicial, ref-format, clone sem origem e os dois retornos 1 têm mutante.
- Bordas lidas sem teste dedicado, sem defeito: destino com `~` é expandido depois do teste de `..`; link como último componente apontando para dentro é aceito se vazio, comportamento coerente.
- Risco residual (não bloqueia): `forge-copia` não valida que `--origem` seja confiável; escopo do parecer de segurança paralelo.

## Revalidação (delta efe73e17..a108ef53)
`forge-check parecer delta` lista no domínio: copia-pasta-settings.patch (allowWrite sem `/workspaces/.forge-contrib`), as duas skills (texto compactado) e tests/test_forge_copia.py (`sem_manutencao` no env, sem mudar asserção). `bin/forge-copia` não mudou: mutantes M1 a M10 seguem válidos.
- A1 (antes bloqueante: teto de texto) resolvido: `python3 -I -m unittest discover -s tests -p <módulo>.py` no head a108ef53: test_metricas_texto 2 OK; test_orcamento_instrucao 8 OK; test_ambiente_git 20 OK (127 s); test_forge_copia 13 OK.
- Check-run `bateria` do sha não citado: sem PR neste head no momento da revalidação.
