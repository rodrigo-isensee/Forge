---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-achados-fora-dominio
commit: e31a7ba4e881798f49b0f145b9140bc1b294f29d
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-16
---
# QA: v047 achados recorrentes fora do domínio (E2.256)

Código testado: `e31a7ba4`; o head local `ca0e47cc` só soma os pareceres de review (E2.254) e segurança (E2.255), sem código. Pedido de controle sem UX: a obrigação é a regra do changelog (`docs/engineering/achados-recorrentes.md` é anexo do portão, PA-7, e não vence parecer no `pr`, na conferência do head e no `parecer delta`). Sem PR aberto, não há check-run `bateria`; rodei os testes do item localmente.

## Achados
- A1 (recomendado) bin/forge-check:2996 · `cmd_delta` (forge-check delta) ainda filtra só LIVRES, então o anexo conta como mudança de domínio ali; a divergência com `parecer delta` é intencional no changelog? Registrar ou alinhar.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Conferência do head aceita o anexo depois da entrega conferida | `AchadosRecorrentesForaDoDominio.test_achados_depois_da_entrega_conferida_nao_tira_a_cobertura` | anexo após a conferida | passou |
| Arquivo vizinho na mesma pasta continua tirando a cobertura | `...test_outro_arquivo_depois_da_entrega_conferida_tira` | `docs/engineering/praticas.md` | passou |
| `pr`: parecer no mesmo commit do anexo vale | `...test_parecer_no_mesmo_commit_dos_achados_vale` | commit misto parecer+anexo | passou |
| `pr`: parecer no mesmo commit de outro arquivo vence | `...test_parecer_no_mesmo_commit_de_outro_arquivo_vence` | vizinho | passou |
| `parecer delta` não lista o anexo e lista o vizinho | `...test_parecer_delta_nao_le_os_achados` | anexo vs vizinho no mesmo delta | passou |

## Cenários e resultado real
- `python3 -m unittest tests.test_parecer_conteudo`: 20 testes, OK (30 s).
- Vermelho antes do verde: `bin/forge-testes --vermelho 98a191f71631d6a2c3ba8a6c27034864786071cb --modulos test_parecer_conteudo --prazo 400` rc=0. Abertura: `vermelho: base=98a191f71631 head=ca0e47ccc8d4 módulos=test_parecer_conteudo`; `revertidos à base: bin/forge-check, changelog.d/v047-achados-fora-dominio.md, docs/reviews/..., docs/security/...`; `contagem: não prova (passa na base)=17; prova (asserção)=3`. Os 3 que provam (`test_achados_depois...`, `test_parecer_delta_nao_le...`, `test_parecer_no_mesmo_commit_dos_achados_vale`) caem na base; os 2 de guarda (vizinho vence) passam nos dois lados por desenho; nenhum cai no HEAD.
- Mutação: `bin/forge-mutante tests/mutantes/v047-achados-fora-dominio.json` rc=0, `pedido=v047 rev=e31a7ba4e881`; `AF-M1 · morreu · bin/forge-check:1488`, `AF-M2 · morreu · :1779`, `AF-M3 · morreu · :3143`. Um mutante por ponto que usa `ANEXOS_DO_PORTAO`; a lista bate com o diff (a constante e a derivação `ACHADOS_RECORRENTES` não decidem).
- Cobertura: `forge-mutante --cobertura --base 98a191f7`: `coberta · bin/forge-check:3143 · ...:AF-M3`; as outras duas linhas mudadas são atribuições, não condições.
- Achados recorrentes (PA-7): AR-1 (lista incompleta) conferido, sem sobra; AR-2 (ramo de falha sem teste) sem ramo novo; AR-12 (spec desatualizada pelo commit) conferido, trechos `de` batem com o head; demais AR são de review/segurança.
- Suíte inteira: só no CI do PR (ainda sem PR); o mutante e o vermelho acima são de módulo.
- Bugs: nenhum.
