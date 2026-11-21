---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-aviso-versao-parada
commit: 063a2d567e8500d6fcaa23d1ec4cae15adcb1c98
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-21
---
# QA: aviso de versão parada (v0478 E69.6)

Código testado: `1d47aa8e` (E69.3). O head da branch (`aaf8d31b`) só soma o parecer de segurança. Desenho: `docs/propostas/aviso-versao-parada.md` (seções 4 a 7); não há `docs/ux/` nem contrato de API nesta demanda, então os critérios são RF1 a RF5 e a seção 4 do desenho.

## Achados
- A1 (recomendado) hooks/doutor.py:195 · RF4 e seção 6 do desenho: sem cache nenhum ou com a consulta desligada, o desenho previa o aviso semanal "versão não conferida"; o hook fica mudo (só há o caso com `ultima` guardada). Sem teste. Virar cartão, ou o dono retira a linha do desenho.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| RF1 aviso quando a carregada < última | test_p1_*, test_p2_*, test_em_dia_nao_avisa_nem_mede, test_em_dia_com_a_ultima_igual_* | igual à última: silêncio | passou |
| RF2 causa e comando da pessoa (P1 a P4) | test_p1, test_p2, test_p3, test_p4, test_na_sessao_do_forge_o_comando_e_o_jarvis_forge | etapa estranha fora do texto; instalada de outro projeto não conta | passou |
| RF3 sem repetir e sem mudo | test_antes_de_2_dias_fica_em_silencio, test_um_por_dia_e_volta_no_dia_seguinte_com_a_contagem, test_causa_que_muda_no_mesmo_dia_avisa_de_novo | 1 dia (silêncio), 2 dias (avisa) | passou |
| RF4 sem rede | test_sem_rede_usa_a_ultima_guardada_com_a_data, test_data_guardada_fora_da_forma_nao_vai_ao_texto | data malformada | passou; parte "sem cache" não coberta (A1) |
| RF5 medida | test_a_medida_grava_o_aviso_e_o_alcance, test_alcance_sem_aviso_nao_mede | alcance sem aviso não mede | passou |
| Entradas hostis (R-SEGURANCA) | test_pasta_da_ferramenta_que_e_link_nao_e_lida, test_estado_da_ferramenta_fora_da_forma_*, test_instalada_ilegivel_*, test_instalada_fora_da_forma_*, test_estado_proprio_fora_da_forma_recomeca_a_contagem | link, JSON fora da forma, tamanho | passou |

## Cenários e resultado real
- `python3 -I -m unittest discover -s tests -p test_doutor.py` (TMPDIR próprio): 128 testes, OK.
- Mutantes: `bin/forge-mutante` nas 4 specs `tests/mutantes/v0478-aviso-versao-parada*.json`, 31 mutantes, todos `morreu` (saída 0, M1 a M31, linhas de `bin/forge_versoes.py` e `hooks/doutor.py`). Spec de rev `aaf8d31b53b1`.
- `forge-mutante --cobertura --base bead3e53`: só linhas `coberta`, nenhuma condição sem mutante; linha `spec editada · tests/mutantes/v047-sempre-atual-4.json` (retorno `[]` para `None` em `pasta_do_sempre_atual`, coerente com o diff).
- Vermelho antes do verde: ver "Vermelho" abaixo.
- Suíte inteira: não rodada localmente; vale o check-run `bateria` do CI do PR.

## Vermelho
`bin/forge-testes --vermelho bead3e531280deece5eb00b3641722e178c7905b --modulos test_doutor` (saída 1):
```
vermelho: base=bead3e531280 head=aaf8d31b53b1 módulos=test_doutor (restrito por --modulos)
contagem: não prova (passa na base)=108; prova (asserção)=19; regressão=1
tests.test_doutor.HookDoutor.test_abrir_em_menos_de_cem_ms_em_media · H=falha · B=ok · regressão
```
Os 19 testes novos da classe `VersaoParada` caem na base e passam no HEAD. A regressão é o teste de CPU do hook, sensível à carga da máquina (load average 18 a 19 durante a prova, com outras sessões pesadas): no HEAD ele passou 3 de 3 isolado (`-k test_abrir_em_menos_de_cem`, load 10) e a classe inteira passou, 128 testes OK, na rodada anterior. Tratado como teste instável (reportado), não como defeito do diff; o CI diz a última palavra pelo check-run `bateria` do mesmo sha.

## Revalidação (v0478 E69.11, escopo incremental)
Delta `1d47aa8e..063a2d56` lido por `forge-check parecer delta`: só texto. `bin/forge_versoes.py` (docstring sem o caminho de `docs/propostas/`), `docs/hooks.md:16` (descrição do aviso de versão parada) e um comentário em `tests/test_doutor.py`. Nenhuma linha de lógica mudou. Rodados com `python3 -I`: `test_reval_delta.py` (10 testes, OK) e `test_doutor.py -k VersaoParada` (23 testes, OK). Sem suíte inteira e sem vermelho (não há teste novo). A1 (recomendado) segue como no parecer anterior. Parecer mantido: aprovado.
