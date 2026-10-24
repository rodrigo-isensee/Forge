---
tipo: qa
contrato: 1
pedido: F4-ATUALIZAR
branch: melhoria/f4-atualizar
commit: 3149881b69272ea9259afca70b9e642f955a23d5
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-23
---
# QA: F4-ATUALIZAR (`forge atualizar` com a branch nascida da develop e conflito de `.forge/versao`)

Parecer sobre o commit final, depois do review e da segurança aprovados na revalidação 2. Base de comparação: `origin/develop`.

## Achados

## Critério → teste → resultado
O pedido não tem especificação de UX com `CA-n`; as obrigações vêm do texto da F4 (LISTA-F), do escopo E1 e das regras `R-CONFORMIDADE` e `R-QA`.

| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| F4: branch nasce da develop atual (local atrasada) | `test_a_branch_nasce_da_develop_atual_mesmo_com_a_local_atrasada`; E2E caso 6 | develop local atrás do remoto | passou |
| F4: develop avança no meio, sem conflito, entra por merge local | `test_develop_que_avanca_no_meio_sem_conflito_entra_na_branch`; E2E caso 5 | merge só na branch do upgrade | passou |
| F4: conflito só em `.forge/versao` oferecido ao dono; "s" mantém a nova | `test_conflito_em_forge_versao_oferece_manter_a_nova_e_conclui`; E2E caso 1 | resposta do dono em terminal simulado, nunca pipe | passou |
| F4: "n" desfaz a mesclagem | `test_conflito_em_forge_versao_recusado_pelo_dono_desfaz_a_mesclagem`; E2E caso 2 | sem arquivo em conflito, sem MERGE_HEAD | passou |
| Versão da develop maior, menor ou fora de X.Y.Z (`R-CONFORMIDADE`) | `test_conflito_com_versao_maior...`, `..._menor...`, `test_versao_da_develop_fora_do_formato...` (0.4, lixo); E2E casos 3, 3b, 3c | sem TypeError, aviso de rebaixar, pergunta com padrão N | passou |
| Outro conflito além de `.forge/versao` não é resolvido pelo comando | `test_conflito_em_outro_arquivo_nao_e_resolvido_pelo_comando`; E2E caso 4 (regras.txt e versao juntos) | lista os dois, desfaz | passou |
| "Nada a fazer" não mescla na branch em uso (main ou outra) | `test_nada_a_fazer_na_main...`, `test_nada_a_fazer_em_branch_qualquer...`; E2E caso 6b | main intacta, sem merge | passou |
| Develop local divergente ou à frente nunca é mexida e o dono é avisado | `test_develop_local_divergente...`, `test_develop_local_a_frente...`; E2E casos 7 e 7b | nunca força, nunca perde commit | passou |
| Arquivos trazidos listados, com destaque para `.forge/`, `.claude/`, hooks | `test_a_saida_lista_os_arquivos_trazidos_da_develop` | n/a | passou |
| Sem remoto ou sem terminal: fluxo de antes | `test_sem_remoto_o_fluxo_de_hoje_continua`; E2E caso 10 (rc 2, nada mexido) | sem terminal | passou |

## Cenários e resultado real
Ambiente: `$TMPDIR/qa-f4` (HOME próprio, remoto bare local, sem rede, `claude` falso). Roteiro: `$TMPDIR/qa-f4/driver.py`, que reaproveita o harness de `tests/test_atualizar.py` e responde no terminal simulado (pty). Todos os casos terminaram sem Traceback, sem `MERGE_HEAD`, com `git status` limpo e nada enviado (os heads do remoto só mudaram pelo "outro clone" simulado).

| Caso | rc | Estado final e mensagem ao dono |
|---|---|---|
| 1. Conflito só em `.forge/versao` (0.1.0 na develop), "s" | 0 | na `forge/upgrade-9.9.0`, versão 9.9.0, merge commitado; mostra as duas versões; "Conflito resolvido" |
| 2. Mesmo conflito, "n" | 1 | mesclagem desfeita, branch como estava; "Desfiz a mesclagem... resolva à mão"; oferece voltar (padrão N) |
| 3. Develop com `1.0.0-rc1`, "n" | 1 | aviso "não está no formato X.Y.Z... mais seguro n"; tudo desfeito |
| 3b. Develop com `lixo`, "s" | 0 | mesmo aviso; o dono mantém a nova por escolha própria (o aviso orienta, não impede) |
| 3c. Develop com `99.0.0`, "s" | 0 | aviso "a da develop é MAIOR; responder s rebaixa"; rebaixa só por escolha do dono |
| 4. Conflito em `regras.txt` e `.forge/versao` | 1 | "deu conflito em: .forge/versao, regras.txt. Desfiz a mesclagem"; não pergunta sobre a versão; limpo |
| 5. Develop avançou no meio, sem conflito | 0 | merge local, lista `novo.txt`, nada enviado |
| 6. Develop local atrás do remoto, parado na main com "nada a fazer" (6b) | 0 | main com o mesmo sha, nenhuma branch criada, `novo.txt` ausente; mensagem "nenhuma branch criada e nada mesclado"; develop local avançou por fast-forward e avisou |
| 7. Develop local divergente | 0 | develop local intacta (mesmo sha); aviso "divergiu"; merge só na branch do upgrade |
| 7b. Develop local à frente do remoto | 0 | develop intacta; aviso "N commit(s) ainda não enviados" antes de seguir |
| 9. Sem develop (local e remota) | 1 | falha na simulação do `forge-upgrade`, "não mudei nada"; comportamento anterior à F4, fora do escopo |
| 10. Sem terminal | 2 | recusa e explica; nada mexido |

Suíte do pedido: `python3 -m unittest tests.test_atualizar` rodou 73 testes, OK. A suíte completa não foi rodada aqui (teto de memória); roda no pre-push.

Vermelho antes do verde: com o `bin/forge-atualizar` de `origin/develop` no lugar do da branch, `python3 -m unittest tests.test_atualizar.AtualizarComDevelopQueAvancou` falhou 14 dos 15 testes (o que sobrou é o do fluxo sem remoto, que já funcionava). Arquivo restaurado com `git checkout`, árvore limpa.

Mutação: não rodada; a stack do Forge (shell e Python da biblioteca padrão) não tem ferramenta gratuita no `pronto.md`. Compensação: os 14 testes que falham sem a implementação e as bordas acima.

Observações, sem bloqueio nem bug:
- A9 do review (mensagem de desfazer depois do commit da resolução) segue como recomendado do review; não reproduzi caminho que a exponha.
- No caso "n", depois de "Desfiz a mesclagem" o comando pergunta "Voltar para a versão X?"; é o comportamento definido, mas pode parecer estranho ao dono que a pergunta de voltar o plugin venha de um conflito.
