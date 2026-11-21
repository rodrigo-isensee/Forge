---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-ae5-retro-pendentes
commit: c38abefad5b1b87c04628b6524c579f87b6bd529
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-21
---
# QA: v0478 (E58.65, AE5.1 forge-check retro --pendentes)

## Critério → teste → resultado
Sem especificação de UX; as obrigações são as de AE5.1 (pendente = tag da main com mais de 24 h sem retro com `Cobre:`).
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| 24 h exatas não é pendente, 25 h é | test_24h_exatas_nao_e_pendente_e_25h_e | limite 24 h | prova (asserção); A1 do parecer anterior resolvido (tupla inteira) |
| tag fora da main não é pendente nem cobre | test_tag_fora_da_main_nao_e_pendente_nem_cobre | ref da main | prova (asserção) |
| `Cobre:` com versão inexistente avisa e não cobre | test_cobre_com_versao_que_nao_existe_avisa_e_nao_cobre | versão inválida | prova |
| `Cobre:` fora da primeira seção, seção sem corpo, só cabeçalho do modelo | três testes homônimos | vazio | prova |
| link e arquivo grande não cobrem; pasta que é link; `_*.md` fora | test_link_e_arquivo_grande_nao_cobrem, test_pasta_de_retros_que_e_link_fica_fora, test_arquivo_com_sublinhado_fica_fora | link, máximo | prova |
| `--desde`, `--raiz-pedidos`, `--main` local | test_desde_ignora_as_tags_anteriores, test_retros_vem_do_raiz_pedidos_quando_dado, test_main_local_com_outra_ponta | filtro | prova |
| modelo preenchido cobre; dois modelos iguais | test_modelo_preenchido_cobre_e_os_dois_modelos_sao_iguais | n/a | prova (API ausente) |
| entrada ilegível sai 2; exclusivo com `--pedido` | test_entrada_ilegivel_da_2, test_pendentes_e_pedido_sao_exclusivos | agora, main, desde inválidos | passa; não prova (A2) |

## Cenários e resultado real (revalidação no head e375c67a)
- Delta (`forge-check parecer delta`): intervalo 600bbecf..e375c67a; no domínio bin/forge-check (`_texto_da_retro`, `fora`), tests/test_retro_pendentes.py, 4 specs de mutantes, changelog.
- Vermelho (`bin/forge-testes --vermelho 821db42e --modulos test_retro_pendentes --prazo 1100`): `vermelho: base=821db42ed97e head=e375c67ae9c0`; contagem: não prova (passa na base)=2; prova (API ausente)=2; prova (asserção)=16; sem veredito=0; rc=0. test_24h_exatas agora `B=falha · prova (asserção)`; os 2 testes novos (fifo/pasta, docs link) provam. Os 2 testes que passam na base (entrada ilegível, exclusivo com --pedido) são cobertos pelos mutantes e não bloqueiam.
- Mutantes (4 specs, uma chamada por spec, `timeout 1500`): M1 a M8, M9 a M16, M17 a M24, M25 a M29, todos `morreu`, rc 0 em cada. Nenhum sobrevivente.
- `forge-mutante --cobertura --base 821db42e`: todas as linhas de guarda mudadas `coberta`; só `não coberto: tests/pesos-d4.json` (dado), rc 0.
- Pasta de controle real (só leitura, `forge-check retro --pendentes --raiz-pedidos /root/.forge-contrib --desde v0.47.0`): `pendentes=10`, pasta não alterada.
- Sem suíte local; a bateria do CI do mesmo sha não foi consultada por esta passada.

## Revalidação no head 2d378b98
- Delta de código e testes sobre f324dfa4 (merge da develop c9d69234, separado com `git diff c9d69234 HEAD`): só 2d378b98, a docstring de `cmd_retro_pendentes` sem o caminho e a entrada `("tests/test_retro_pendentes.py", "docs/retrospectivas/"): (1, "teste-le")` na guarda C-2 de `tests/test_reval_delta.py`. Nenhuma lógica mudou.
- `python3 -I -m unittest discover -s tests -p test_retro_pendentes.py` (TMPDIR do sandbox): 20 testes, OK.
- `... -p test_reval_delta.py`: 10 testes, OK (a contagem 1 da entrada confere com a citação real do teste).
- Vermelho e mutantes: a lógica não mudou desde e375c67a; as provas anteriores seguem. Sem suíte local; bateria do CI não consultada.

## Revalidação no head 8d2efa1f
- Delta (`forge-check parecer delta`, intervalo 2d378b98..8d2efa1f, sem o que veio da develop): `bin/forge-check` (COBRE_DA_RETRO, VERSAO_DA_TAG, REF_DA_MAIN viram texto e compilam no uso via `re.match`/cache do `re`), 3 specs de mutantes ajustadas, uma contagem em tests/test_reval_delta.py (README.md 15 para 16, citação de teste).
- `test_retro_pendentes.py`: 20 testes, OK. `test_hooks_volta_corpus.py`: 33 testes, OK.
- `forge-mutante` nas specs `v0478-ae5-retro-pendentes`, `-2`, `-3` (uma chamada por spec; `rev=8d2efa1fdc94`): M1 a M8, M9 a M16, M17 a M24, todos `morreu`, nenhum sobrevivente.
- Vermelho (`bin/forge-testes --vermelho 821db42e --modulos test_retro_pendentes --prazo 1100`): `vermelho: base=821db42ed97e head=8d2efa1fdc94`; contagem: não prova (passa na base)=2; prova (API ausente)=2; prova (asserção)=16; rc=0. O delta não traz teste novo.
- Sem suíte local; bateria do CI não consultada por esta passada.

## Revalidação no head c38abefa
- Delta (`forge-check parecer delta`, 8d2efa1f..c38abefa): merge da develop (#763); no domínio só a resolução do conflito em `bin/forge-testes` (a tupla FORGE_CHECK traz `test_retro_pendentes` e `test_comparar`, os dois itens), mais `bin/forge-check`, `tests/pesos-d4.json` e a citação `bin/forge_comparar.py` em `tests/test_reval_delta.py`, todos vindos da develop. Nenhuma lógica de AE5.1 mudou.
- `test_retro_pendentes.py`: 20 testes, OK. `test_comparar.py`: 66 testes, OK. `test_testes_tocados.py`: 196 testes, OK (1 skip do próprio módulo, pré-existente).
- Vermelho e mutantes: a lógica de AE5.1 não mudou desde 8d2efa1f; as provas anteriores seguem. Sem suíte local; bateria do CI não consultada.
