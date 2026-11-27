---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-f4-vigia-fluxo
commit: 04b508f60417897819537305b78a9e4db5258971
parecer: reprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 1
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-27
---
# QA: v0481 F4 (vigia sem rede), volta 1, delta 8d755e50..04b508f6

- ci: 04b508f60417897819537305b78a9e4db5258971 vermelho
  (`gh pr checks 931` no head: suíte partes 1, 2, 3 e 5, verificações longas, passos, python 3.14, instalação e `catraca` verdes; `suíte (python 3.12, parte 4/5)` vermelha (A1); `bateria` e `bateria (pareceres)` vermelhas pela falta dos pareceres deste head. Não aprova com check vermelho.)

## Achados
- A1 (bloqueante) bin/forge_estado.py:84 · R-QA: a parte 4/5 do CI cai (test_forge_mutante.py:1564): M7 e M8 de tests/mutantes/v0481-s1-status.json têm o trecho `de` 2 vezes aqui, copiado na papel_do_pr. Torne o `de` único no mesmo commit.

## Critério → teste → resultado
Sem especificação de UX nem `CA-n`; as obrigações vêm de E34.1, E34.6 (hook sem rede, ADR 0003 item 7) e R-TETO. O A1 e o A2 da 1ª rodada (guarda 618 e fork) são o foco do delta.

| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Hook sem rede: lê só `prs-abertos.json`; ausente, vencida (>900 s), no futuro (>60 s) ou fora da forma cala | `test_hook_vigia_f4` (lista em disco) | vazio, 900 s, 60 s, arquivo não regular | passou |
| Lista gravada por `gravar_prs_abertos`, só PR com papel, modo 0600; sem pasta de estado, nada | `test_grava_so_o_pr_com_papel_fora_o_fork_e_em_0600` | sem pasta | passou |
| PR de fork (ou sem `isCrossRepository`) fora (S1 da segurança) | `PapelDoPr.test_pr_de_fork_ou_sem_o_campo_fica_fora` | campo ausente, `None`, ACTION_REQUIRED | passou |
| Papel do PR por estado; todo papel está na lista do vigia | `PapelDoPr.*` | check pendente, base main, rótulo | passou |
| Aviso fixo: até 3 PRs, 1 agente preso, teto de 280 | `test_hook_vigia_f4`, laço de fixtures de `tests/test_hooks.py` | 3 PRs e mais M, 280 caracteres | passou |
| `proximo` renova a lista vencida, uma leitura do `gh` | `tests/test_proximo.py` (20 linhas novas) | lista vencida, falha do gh | passou |
| Guarda 618 virou `livres = [] if vivos`, isenta com motivo | `--cobertura`, M3 de v0480 | agente vigente | passou |
| Toda spec confere com a fonte | `ConferirTodas.test_toda_spec_do_forge_confere...` | `de` único | **falhou** (A1) |

## Cenários e resultado real
- Afetados locais (em `tests/`): `python3 -m unittest test_hook_vigia_f4 test_vigia_parado test_vigia test_proximo`: 100 testes OK. Parte 4/5 reproduzida: `python3 -m unittest test_forge_mutante.ConferirTodas.test_toda_spec_do_forge_confere_com_a_fonte_fora_as_pendentes` falha com `['tests/mutantes/v0481-s1-status.json: M7', '... M8']`; `bin/forge-mutante --conferir --todas` lista as duas ("o trecho aparece 2 vezes em bin/forge_estado.py").
- Vermelho antes do verde, `bin/forge-testes --vermelho 8d755e503e51f53e37af2befea60ba7622b26dc8 --modulos tests.test_hook_vigia_f4`: `vermelho: base=8d755e503e51 head=04b508f60417 módulos=test_hook_vigia_f4 (restrito por --modulos)`; `contagem: não prova (herdada da base)=18; prova (API ausente)=24` (24 novos falham na base; nenhum cai no head).
- Cobertura, `bin/forge-mutante --cobertura --base 2bdf1a2e93848891987b1536ae6039c6269b576f` (rc 0, `rev=04b508f6`): toda condição mudada `coberta`; `isenta · hooks/vigia.py:618(base)` com o motivo da spec, que cruza a linha e se apoia no M3 de v0480. Com `--base 8d755e50` a linha sai `isenta velha` (rc 1) só porque aquele head já não tem a condição; a base do pedido é o Base-sha.
- Mutantes (`--processos 3 --base 8d755e503e51...`): as 7 specs `v0481-f4-vigia-fluxo*.json`, rc 0, 49 mutantes `morreu`, nenhum sobrevivente nem sem veredito; `v0480-vigia-time-parado.json` M1 a M8 `morreu`, rc 0.
- Não rodei a suíte inteira (G3); o CI do head é a evidência das demais partes.

## Revalidação
Na volta, `forge-check parecer delta docs/qa/v0481-f4-vigia-fluxo.md`; reteste o A1 (o teste de `ConferirTodas` e a spec `v0481-s1-status.json`) e, se mexer em `hooks/vigia.py` ou `bin/forge_estado.py`, os mutantes do delta.
