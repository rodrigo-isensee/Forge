---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-ae5-retro-pendentes
commit: 600bbecf622bd734806ae351276e844f9a55cc10
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-21
---
# QA: v0478 (E58.65, AE5.1 forge-check retro --pendentes)

## Achados
- A1 (bloqueante) tests/test_retro_pendentes.py:79 · `forge-testes --vermelho` sai rc 2 (sem veredito): test_24h_exatas indexa `[1][-1]` e na base dá erro (IndexError), nem asserção nem API ausente. R-QA: sem veredito não vale como vermelho; tornar a asserção sem indexar.
- A2 (recomendado) tests/test_retro_pendentes.py:156 · test_entrada_ilegivel_da_2 e test_pendentes_e_pedido_sao_exclusivos passam na base (rc 2 por argparse já ocorria); não provam o código novo. Nada bloqueia: os mutantes cobrem as guardas.

## Critério → teste → resultado
Sem especificação de UX; as obrigações são as de AE5.1 (pendente = tag da main com mais de 24 h sem retro com `Cobre:`).
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| 24 h exatas não é pendente, 25 h é | test_24h_exatas_nao_e_pendente_e_25h_e | limite 24 h | passa no HEAD; vermelho sem veredito (A1) |
| tag fora da main não é pendente nem cobre | test_tag_fora_da_main_nao_e_pendente_nem_cobre | ref da main | prova (asserção) |
| `Cobre:` com versão inexistente avisa e não cobre | test_cobre_com_versao_que_nao_existe_avisa_e_nao_cobre | versão inválida | prova |
| `Cobre:` fora da primeira seção, seção sem corpo, só cabeçalho do modelo | três testes homônimos | vazio | prova |
| link e arquivo grande não cobrem; pasta que é link; `_*.md` fora | test_link_e_arquivo_grande_nao_cobrem, test_pasta_de_retros_que_e_link_fica_fora, test_arquivo_com_sublinhado_fica_fora | link, máximo | prova |
| `--desde`, `--raiz-pedidos`, `--main` local | test_desde_ignora_as_tags_anteriores, test_retros_vem_do_raiz_pedidos_quando_dado, test_main_local_com_outra_ponta | filtro | prova |
| modelo preenchido cobre; dois modelos iguais | test_modelo_preenchido_cobre_e_os_dois_modelos_sao_iguais | n/a | prova (API ausente) |
| entrada ilegível sai 2; exclusivo com `--pedido` | test_entrada_ilegivel_da_2, test_pendentes_e_pedido_sao_exclusivos | agora, main, desde inválidos | passa; não prova (A2) |

## Cenários e resultado real
- Vermelho (`bin/forge-testes --vermelho 821db42e --modulos test_retro_pendentes --prazo 1100`): `vermelho: base=821db42ed97e head=600bbecf622b`; contagem: não prova (passa na base)=2; prova (API ausente)=2; prova (asserção)=13; sem veredito=1; rc=2.
- Mutantes (3 specs, uma chamada por spec): M1 a M24 todos `morreu`, rc 0 em cada. `forge-mutante --cobertura --base 821db42e`: todas as linhas de `bin/forge-check` mudadas `coberta`; `não coberto: tests/pesos-d4.json` (dado, não guarda), rc 0.
- Pasta de controle real (só leitura, `bin/forge-check retro --pendentes --agora 2026-11-21T07:45:14Z --raiz-pedidos /root/.forge-contrib --desde v0.47.0`): rc 1, `pendentes=10` (v0.47.0, .1, .3 a .10). A pasta não foi alterada.
- Sem suíte local; a bateria do CI do mesmo sha não foi consultada por esta passada.
