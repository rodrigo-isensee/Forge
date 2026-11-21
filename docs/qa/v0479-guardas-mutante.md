---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-guardas-mutante
commit: b2c7255d6e0013f91c7db551c3ab08bcdd4a8589
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-20
---
# QA: v0478 E62.14 (cinco mutantes declarados para guardas do bin/forge-check, head b2c7255d)

O diff contra a base 8ee73d15 só toca testes, a spec de mutantes e o fragmento de changelog (`git diff 8ee73d15 HEAD -- bin` vazio). Não há código de produção novo.

## Critério → teste → resultado
| Critério (guarda) | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| G1 testes do QA lidos na ref, não no HEAD | PrLeARefNaoOHead.test_teste_do_qa_na_ref_dispensa_com_o_head_atras | HEAD atrás da ref | passou; mutante morreu |
| G2 domínio conferido na ref | PrLeARefNaoOHead.test_codigo_mudado_na_ref_derruba_com_o_head_no_commit_revisado | commit revisado no HEAD, código mudado na ref | passou; mutante morreu |
| G3 base do brief vai ao pr | BaseDaEtapa.test_base_do_brief_vai_ao_pr_pelo_remoto | base ausente | passou; mutante morreu |
| G4 só aprovado e riscos-aceitos aprovam | PrPrevio.test_reprovado_com_previo_e_rc_1 | parecer reprovado | passou; mutante morreu |
| G5 commit só de pareceres paralelos barra | RecusaNoPr.test_commit_do_head_com_parecer_paralelo_e_recusado_com_a_dica | parecer paralelo | passou; mutante morreu |

Conferência da lista contra o diff: o diff não muda linha de guarda em `bin/`; os cinco mutantes cobrem as cinco guardas que o pedido declara (G4 e G5 em teste já existente da base). Nenhuma linha de guarda mudada sem mutante.

## Provas
Mutantes (`bin/forge-mutante tests/mutantes/v0479-guardas-0-47-12.json`, rc=0, todos morreram):
```
forge-mutante: pedido=v0478 rev=b2c7255d6e00 spec=8e48d48f7318aa1808b8c2fbc9757fdcbb45109657ebb8c9e2d5604224897e92
G1 · morreu · bin/forge-check:2050
G2 · morreu · bin/forge-check:2094
G3 · morreu · bin/forge-check:8837
G4 · morreu · bin/forge-check:2073
G5 · morreu · bin/forge-check:2092
```

Módulos tocados, com TMPDIR próprio: `test_parecer_conteudo` 22 testes OK; `test_forge_check_pr` 49 testes OK.

Vermelho (`bin/forge-testes --vermelho 8ee73d15 --modulos test_parecer_conteudo,test_forge_check_pr`, rc=1):
```
vermelho: base=8ee73d156db5 head=b2c7255d6e00 módulos=test_parecer_conteudo,test_forge_check_pr (restrito por --modulos)
revertidos à base: changelog.d/v0479-guardas-mutante.md
mantidos no HEAD: tests/mutantes/v0479-guardas-0-47-12.json, tests/test_forge_check_pr.py, tests/test_parecer_conteudo.py
contagem: não prova (passa na base)=71
nenhum teste prova a mudança.
```
Leitura: o rc 1 era esperado. O pedido só acrescenta testes a guardas que a base já tem, então o teste passa na base por construção e o vermelho de código não existe. A prova de que cada teste morde é a mutação: sem o teste, o mutante sobrevive; com ele, os cinco morrem. Por isso não bloqueia. Nenhum teste cai no HEAD (H=ok em todos).

Suíte inteira: não rodada local; vale o check-run `bateria` do mesmo sha no CI do PR.
