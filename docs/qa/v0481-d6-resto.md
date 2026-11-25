---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-d6-resto
commit: 9a708f86cf6018f09145073a52ce0e7480d9649a
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 1
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-24
---
# QA: v0481 E11.4 (PR #877, hook salvar, D6 parte a; classe C)

Escopo: `hooks/salvar.py` novo no `SubagentStop`, entrada no `hooks/hooks.json` (timeout 60), emenda da ADR 0003 (item 2), 4 fixtures, 23 testes `SalvarAoParar`, 4 specs de mutantes. O merge espera a decisão do dono pelo afrouxamento (título do PR traz `[afrouxa-regra: ADR 0003 item 2]`); **reprovado**: uma sonda minha prova que o git do hook executa filtro do `.git/config` da cópia (achado A1), e o `core.hooksPath` vazio precisa de exceção escrita no `R-VERIFY` (A2). Com os dois corrigidos, o resto passa.

## Achados
- A1 (bloqueante) hooks/salvar.py:24 · Provado por sonda: o git do hook, fora do sandbox, executa `filter.<x>.clean` do .git/config da cópia (marca criada pelo `add`); o config é do agente. GIT_SEGURO não cobre; testes e 30 mutantes não pegam. Ver docs/qa/bugs/v0481-salvar-config-da-copia.md.
- A2 (bloqueante) docs/adr/0003-hooks-deterministicos-e-silenciosos.md:116 · core.hooksPath vazio é troca de caminho dos hooks, que o R-VERIFY veda sem exceção; a emenda só o cita para o --force. Falta a exceção escrita em docs/regras/R-LIMITES.md e o destaque no título do PR, para a decisão do dono.

## Pergunta do brief: core.hooksPath vazio conflita com R-VERIFY?
Pela letra, o `R-VERIFY` (`docs/regras/R-LIMITES.md`) manda "não desative nem troque o caminho dos hooks (`core.hooksPath`)" e proíbe `--no-verify`. O hook `conformidade` aplica isso a comandos de agente. O `salvar` não é comando de agente: é código do plugin, e o agente não escolhe nada disso. Também não usa `--no-verify` nem `--force` (o teste `test_envio_recusado_sem_force_fica_no_log` e o mutante M18 guardam a forma do push). Pelo espírito, porém, os hooks do git da cópia (`pre-push` e `.githooks/`) deixam de rodar neste envio, e a guarda de branch passa a ser a do próprio hook (M5 a M9, mortos). Concluo: sem conflito com a letra aplicada ao agente; é desvio consciente do espírito, e só o dono pode aceitá-lo. A justificativa da emenda (hooks do git da cópia são código escrito pelo agente e rodariam fora do sandbox) é válida e o teste `test_hooks_do_git_da_copia_nao_rodam` a prova. Revisão do meu parecer: a 1ª versão classificou isto como recomendado; ao ler o parecer do review e o de segurança, e provar o A1 por sonda, reclassifico: o A2 é bloqueante, porque a decisão do dono precisa ver a exceção ao R-VERIFY escrita.

## Critério → teste → resultado
O pedido não tem `CA-n` numerado; as obrigações vêm do brief e da emenda da ADR 0003 (regras 1 a 6).

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Regra 1: um só brief de escrita | `test_dois_briefs_de_escrita_nao_grava`, `test_brief_de_parecer_nao_grava`, `test_sem_brief_citado_nao_age`, `test_brief_ausente_fica_de_fora` | zero, dois, brief de leitura | passou |
| Regra 1: uma só cópia, na pasta das cópias, na branch do brief | `test_duas_copias_citadas_nao_grava`, `test_copia_fora_da_pasta_das_copias_nao_grava`, `test_copia_em_outra_branch_nao_grava`, `test_clone_do_forge_usa_a_pasta_do_contrib` | duas cópias, fora da pasta, outra branch | passou |
| Só SubagentStop, só prompt do agente | `test_stop_da_sessao_nao_age`, `test_fora_de_projeto_nao_age`, `test_so_o_primeiro_registro_user_e_so_os_blocos_de_texto`, `test_registro_user_sem_mensagem_objeto_nao_age`, `test_registro_user_sem_conteudo_nao_age` | evento errado, transcrito torto | passou |
| Regra 2: só o escopo, commit WIP | `test_salva_e_envia_so_o_escopo`, `test_nada_no_escopo_nao_faz_commit` | fora do escopo, escopo vazio | passou |
| Regra 3: push sem --force, nunca em integração | `test_branch_de_integracao_nunca`, `test_envio_recusado_sem_force_fica_no_log` | main, master, develop, homolog; remoto andou | passou |
| Regra 4: git sem hooks da cópia, sem GIT_* herdadas | `test_hooks_do_git_da_copia_nao_rodam`, `test_git_herdado_nao_desvia_a_copia` | hook malicioso na cópia, GIT_DIR herdado | passou |
| Regra 5: mesclagem, conflito em andamento | `test_mesclagem_em_andamento_nao_grava`, `test_conflito_no_indice_nao_grava` | MERGE_HEAD, par UU | passou |
| Regra 6: nunca bloqueia, erro vai ao erros.log | `test_status_que_falha_vai_ao_erros_log`, `test_add_que_falha_nao_faz_commit_nem_envia`, fixtures `erro-interno`, `sem-forge-versao`, `sem-transcrito-do-agente-silencio`, `stop-da-sessao-silencio` | git falho, sem projeto | passou |
| hooks.json: salvar no SubagentStop, timeout 60 | `Hooks.test_hooks_json`, `Hooks.test_cada_hook_tem_caso_que_passa_e_que_bloqueia` | timeout, grupo que nunca bloqueia | passou |

## Sonda do A1
Sonda em arquivo: repositório temporário com `filter.x.clean = touch <marca>; cat`, `.gitattributes` com `*.txt filter=x`, e a chamada `salvar.git_da_copia(d, "add", "-A", "--", "a.txt")` com o `hooks/` deste head. Saída: `filtro do .git/config executou: True`. O mesmo vale para `core.sshCommand`, `gpg.program` e `credential.helper`, citados pelo review e pela segurança.

## Execução (clone `/root/.forge-contrib/wt/v0481-d6-resto-qa`, HEAD = `9a708f86cf60`)
- `python3 -m unittest tests.test_hooks.SalvarAoParar`: 23 testes, OK. `Hooks.test_hooks_json` e `Hooks.test_cada_hook_tem_caso_que_passa_e_que_bloqueia`: OK. `test_indice_fixtures`, `test_indice_forge`, `test_changelog`, `test_hook_erro_libera`, `test_hooks_fila27`: 132 testes, OK. O `tests.test_hooks` inteiro não rodou aqui (passa de 10 min; fica para o CI).
- Vermelho antes do verde: `forge-testes --vermelho` não aceita `-k` e o módulo inteiro estoura o prazo; fiz à mão, em cópia em `$TMPDIR` com `hooks/` da base `bbbe2d887` (sem `salvar.py` nem entrada no `hooks.json`) e os testes novos: `SalvarAoParar` 23 de 23 falham (`FAILED (failures=23)`), `test_hooks_json` falha (`FAILED (failures=1)`). Sem a implementação, caem; com ela, passam.
- Mutantes: `bin/forge-mutante` das 4 specs juntas, `--processos 4`, `rev=9a708f86cf60`: M1 a M28 e M30 `morreu` (incluindo `hooks/hooks.json:210`); M29 `equivalente` (entrada vazia vira caminho vazio, que nada casa; justificativa aceita). Nenhum sobrevivente.
- Cobertura: `forge-mutante --cobertura --base bbbe2d887`: toda condição de `hooks/salvar.py` está `coberta` (declarado, não provado, e a rodada acima prova), salvo L101 `só equivalente` (M29, aceito) e L131 `__name__ == '__main__'` sem mutante, que é só o ponto de entrada e é exercido por todos os testes que chamam o script; não bloqueio.
- Bordas lidas no código: item de escopo vazio ou sem `/` casa só o caminho exato (falha para o lado seguro); `--literal-pathspecs` impede glob no escopo; remoção de arquivo no escopo entra por `add -A --`; nome com caracteres especiais vem do `status -z`.

## CI do PR (head `9a708f86`, run 45517991360 e catraca 45517991252)
Estado lido no `gh`: passos e verificações longas SUCCESS; suíte partes 2 e 3 SUCCESS nos dois Pythons; partes 1 ainda em andamento; **partes 4 e 5 FAILURE nos dois Pythons**, `bateria (pareceres)` e `catraca` FAILURE. Não consegui ler o log (o host de logs do GitHub está fora da rede permitida), então não atribuo a causa ao diff. `bateria (pareceres)` e `catraca` falham, ao que parece, porque ainda não havia parecer de QA no head (este arquivo os resolve), mas as partes 4 e 5 ficam sem diagnóstico meu. Além disso, o merge exige o `bateria` verde no mesmo sha; o tech-lead lê os logs das partes 4 e 5 antes de pedir a decisão do dono. Os testes do item que rodei aqui passam.

## Melhoria vista
O `forge-testes --vermelho` não aceita `-k` e o módulo `test_hooks` passa de 10 min: o vermelho de uma classe nova nesse módulo só sai à mão. Vale `--vermelho` aceitar `-k` ou `--modulos` com classe.
