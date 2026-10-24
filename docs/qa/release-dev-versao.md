---
tipo: qa
contrato: 1
pedido: release-dev-versao
branch: melhoria/release-dev-versao
commit: ccaef64fdb8d76d087f3772b6c2737f36ef13484
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-23
---
# QA: release-dev-versao

Código conferido: `c3b7be0` (o head `ccaef64` só soma os pareceres de review e segurança). Pedido sem especificação de UX: as obrigações são o E1 do pedido RELEASE-DEV-VERSAO (a release grava a versão nos dois manifestos, cada um só se existir) e as recusas dos pareceres de review (A1, A2) e segurança (R1 a R3).

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1 grava a versão nos dois manifestos | `Release.test_sobe_a_versao_dos_dois_manifestos_quando_o_dev_existe`; sonda B | resto do JSON intacto | passou |
| E1 "cada um quando existe" | `Release.test_sem_o_manifesto_dev_a_release_nao_cria_nada`; sonda A | sem `dev/` | passou |
| Manifesto inválido recusado, nada gravado | `Release.test_manifesto_que_nao_e_json_falha_sem_gravar_nada`; sondas C, I | JSON quebrado (dev e raiz) | passou |
| Sem `version` de topo recusado | `Release.test_manifesto_sem_version_de_topo_falha_sem_gravar_nada`; sondas D, E | objeto sem chave, lista, `version` só aninhado | passou |
| Link simbólico recusado | `Release.test_manifesto_link_simbolico_e_recusado_sem_gravar_nada`; sondas F, H, J | link para fora, na raiz, quebrado | passou |
| Caminho fora da raiz recusado | `Release.test_manifesto_que_resolve_fora_da_raiz_e_recusado_sem_gravar_nada`; sonda G | `dev` link para fora | passou |
| Versão do dev igual à do Forge | `test_forge.PluginDeDesenvolvimento.test_versao_igual_a_do_forge` | n/a | passou |

## Cenários e resultado real
- `python3 -m unittest tests.test_changelog`: 35 testes, OK (skipped=1, o do nome da branch, que depende da branch).
- `python3 -m unittest -v tests.test_forge`: 419 testes, OK; `test_versao_igual_a_do_forge ... ok`.
- Vermelho antes do verde, `bin/forge-testes --vermelho db55859529da47652babded81461d2b0500ef79f`, rc=0: `vermelho: base=db55859529da head=ccaef64fdb8d`, revertidos à base `bin/forge-changelog`, o fragmento e os dois pareceres; "prova (asserção)=5": os 4 testes de recusa e o de dois manifestos caem na base e passam no head; os testes herdados passam nos dois (não provam, esperado); 1 pulado.
- Ponta a ponta, repositório de sonda em `$TMPDIR/qa-reldevversao/` (script `sonda.sh`, saída `sonda.log`), usando `bin/forge-changelog` da branch:
  - A (sem `dev/`): rc=0, raiz 0.1.0 para 0.2.0, resto do JSON idêntico (inclusive `version` aninhado em lista), `dev/` não criado, fragmento apagado.
  - B (com `dev/`): rc=0, os dois manifestos em 0.2.0, formatação e demais chaves intactas, fragmento apagado.
  - C (JSON inválido), D (sem `version`), E (JSON lista), F (link simbólico), G (`dev` link para diretório fora), H (manifesto da raiz link), I (raiz inválida), J (link quebrado): todos rc=1 com mensagem nomeando o arquivo; hash de todos os arquivos da sonda igual antes e depois (nada gravado, fragmento e CHANGELOG.md intactos).
- Mutação: pedido toca `bin/`, mas não é de controle declarado (`tests/mutantes/` sem spec do pedido); os 4 testes de recusa e o de gravação caem sem o código, o que o vermelho acima mostra. Linhas de guarda do diff (link, fora da raiz, JSON, `version` de topo, ordem leitura antes de escrita) têm teste cada.
- Fora do bloco de achados: a recomendação A4 do review (gravação textual troca o primeiro `"version"`, não o de topo) já está em cartão (CHANGELOG-JSON-LINK) e não bloqueia: os manifestos reais têm o `version` de topo antes de qualquer objeto aninhado e o `test_versao_igual_a_do_forge` pega a divergência.
- Suíte completa fora do pre-push: não rodada (restrição do pedido); `scripts/validar-plugin.sh` fica com o pre-push.
