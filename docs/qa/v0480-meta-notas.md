---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-meta-notas
commit: e31f2416990cc6ed223b76584141805061eea624
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-22
---
# QA: v0478 / meta-notas (E109.6)

Dois cartões em `hooks/meta.py`: a medida de idioma das notas entre chamadas de ferramenta (E25.1, META-NOTAS-ENTRE-FERRAMENTAS) e a reconta no segundo Stop (E109.1, META-NOTAS-RECONTA). Sem especificação de UX; as obrigações vêm dos cartões e das mensagens dos commits 988f0ab43 e 064e58ce4. Diff lido contra a base 900bfdfe2: 10 arquivos, nenhum fora do escopo.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Nota em outro idioma acusa | `NotasEntreFerramentas.test_nota_em_outro_idioma_na_rodada_acusa`; eval `test_nota_entre_ferramentas_em_ingles_e_acusada` (deixou de ser `expectedFailure`) | rodada com nota inglesa | passou |
| Nota no idioma do dono não acusa | `test_controle_notas_no_idioma_do_dono_nao_acusam` | controle | passou |
| Rodada anterior e subagente não contam | `test_nota_de_rodada_anterior_nao_conta`, `test_nota_de_subagente_nao_conta` | fala do dono fecha a rodada; `isSidechain` | passou |
| Final no transcrito não é nota | `test_mensagem_final_no_transcrito_nao_conta_como_nota` | final igual à nota | passou |
| Nota curta, mista ou dono sem lista não contam | `test_nota_curta_fica_sem_idioma_e_nao_conta`, `test_dono_sem_lista_nao_mede_notas` | vazio e mínimo; idioma sem lista | passou |
| Linha ilegível ou registro fora da forma não quebra | `test_linha_ilegivel_nao_interrompe_a_rodada`, `test_registro_fora_da_forma_e_pulado_sem_erro` | JSON quebrado, tipos inesperados | passou |
| Custo limitado (teto; tool_result não decodifica) | `test_notas_param_no_teto_da_medida`, `test_resultado_de_ferramenta_nem_se_decodifica` | teto de caracteres (30,30,10) | passou |
| META-NOTAS-RECONTA: segundo Stop não reconta nota nem final anterior | `test_segundo_stop_sem_fala_do_dono_nao_reconta_a_nota`, `test_final_anterior_que_chegou_depois_ao_transcrito_nao_conta`, `test_nota_nova_depois_da_marca_ainda_conta` | marca (uuid) e resumo da final | passou |
| Marca de outro transcrito, ilegível ou fora da forma é ignorada | `test_marca_de_outro_transcrito_nao_vale`, `test_marca_ilegivel_ou_fora_da_forma_e_ignorada` | arquivo `notas.json` corrompido | passou |
| Nota cuja chamada traz o texto `tool_result` ainda conta | `test_nota_cuja_chamada_traz_tool_result_ainda_conta` | texto de ferramenta no input | passou |

## Execução (local, só os arquivos tocados)
- `python3 -I -m unittest discover -s tests -p test_meta.py`: 49 testes, OK.
- `python3 -I -m unittest discover -s tests/evals -p test_erros_por_papel.py`: 18 testes, OK (expected failures=3, os outros dois da mesma classe de backlog, não deste diff).
- Suíte inteira: não rodada aqui; vale o check-run `bateria` do CI do PR no mesmo sha.

## Vermelho antes do verde
`forge-testes --vermelho 900bfdfe24352def4272749213a74baceb69cc21 --modulos test_meta` (módulo tocado; a rodada completa de 232 módulos foi interrompida e não vale):
```
vermelho: base=900bfdfe2435 head=064e58ce43a4 módulos=test_meta (restrito por --modulos)
contagem: não prova (passa na base)=32; prova (API ausente)=4; prova (asserção)=13
```
Os 17 testes novos de `NotasEntreFerramentas` caem na base (13 por asserção, 4 por API ausente) e passam no head; os 32 que passam na base são os já existentes. Nenhum teste novo ficou como "não prova".

## Mutação (`forge-mutante`, uma chamada por spec)
`forge-mutante --cobertura --base 900bfdfe2435...`: `base=900bfdfe24352def4272749213a74baceb69cc21 mb=900bfdfe24352def4272749213a74baceb69cc21 rev=064e58ce43a4a9f25093ff826847297da1c4780d`; toda condição mudada em `hooks/meta.py` (linhas 281 a 345) tem mutante declarado; única observação `spec editada · v047-g4-medida-idioma.json` (o trecho `de` do M6 acompanhou a nova linha 345, legítimo).
- `v0478-meta-notas.json`: M1 a M8 morreu (rc 0).
- `v0478-meta-notas-2.json`: M9 a M14 morreu (M11 a M14 por erro do teste declarado sob o mutante, com controle verde, vale como morte) (rc 0).
- `v0478-meta-notas-3.json`: M15 a M22 morreu (M19, M21, M22 por erro, idem) (rc 0).
- `v047-g4-medida-idioma.json`: M1 a M8 morreu (rc 0).
Nenhum sobrevivente; nenhum equivalente declarado.

## Observações sem achado
- A marca grava só uuid e sha256 da final, nunca o texto; confere com o cabeçalho do módulo.
- Gravação de `notas.json` roda a cada Stop com dono conhecido; desde e31f2416 a falha de escrita vai ao `erros.log` e a linha da medida segue (A1 da segurança, E109.7).

## Revalidação (E109.10, head e31f2416)
Delta `064e58ce..e31f2416` (`forge-check parecer delta`): `hooks/meta.py` (try/except OSError em torno de `gravar_json`, linha 323), `tests/test_meta.py`, `tests/mutantes/v0478-meta-notas-3.json` (M22), `changelog.d`. Obrigação nova: falha ao gravar a marca não perde a linha da medida (A1 de `docs/security/v0480-meta-notas.md`).
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Marca que não grava não perde a linha, erro vai ao log | `NotasEntreFerramentas.test_marca_que_nao_grava_nao_perde_a_linha_da_medida` | `notas.json` no lugar de pasta (IsADirectoryError) | passou |
- `python3 -I -m unittest discover -s tests -p test_meta.py`: 50 testes, OK.
- `forge-mutante tests/mutantes/v0478-meta-notas-3.json`: `M22 · morreu · hooks/meta.py:326 · (erro) o teste declarado deu erro sob o mutante e passa sem ele`; M15 a M21 seguem mortos; rc 0.
- Suíte inteira: vale o check-run `bateria` do CI do PR no mesmo sha.
