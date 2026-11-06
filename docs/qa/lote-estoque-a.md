---
tipo: qa
contrato: 1
pedido: versao-034
branch: melhoria/lote-estoque-a
commit: 9e7d397ebe03ea3fc5c32cc8759ae32017e6e1fd
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-05
---
# QA: versao-034 (lote A do estoque, E2.5)

Base: o log da suíte inteira do push do lote (/tmp/push-lote-a2.log, head enviado 9e7d397, `push_rc=0`), sem rodar a suíte de novo (decisão do dono de 2026-11-05 14:59). Cada item já tem o próprio QA; aqui só o lote junto. Sem especificação de UX: o critério é o de cada item. Review da junção e segurança não são deste parecer.

## Achados
- A1 (recomendado) /tmp/push-lote-a2.log:55 · o log não é verboso: os 30 pulos aparecem só como `OK (skipped=30)` e as marcas `s` do processo 2, sem nome de teste; quem quiser saber quais pulam roda o módulo com -v.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Suíte inteira passa sobre a junção | push do lote, 99 módulos em 2 processos | n/a | passou: `Ran 2646 tests in 2028.342s (2 processos)`, `OK (skipped=30)` |
| Mapa conhece os modelos lidos por test_modelos_parecer_avisos_2 e test_textos_034 (c32d320) | test_testes_tocados.MapaCobreOQueOsTestesLeem.test_todo_arquivo_lido_por_um_modulo_roda_esse_modulo | arquivo lido sem entrada no mapa | passou; era 8 falhas no push anterior |
| Pareceres citam o ID da R-DECISAO, sem copiar (c565e9d, 8ea4c84) | test_forge.AntiDuplicacao.test_regra_so_na_fonte | frase de regra fora da fonte | passou; era 2 falhas |
| Modelo de segurança da raiz igual ao do template (432d18a) | test_modelos_citados.ModelosCitados.test_modelo_de_seguranca_da_raiz_igual_ao_do_template | dois arquivos idênticos | passou; era 1 falha |
| No máximo 20% dos módulos sem peso (9e7d397) | test_forge.PesosDaSuite.test_no_maximo_20_por_cento_dos_modulos_sem_peso | limite de 20% | passou; era 1 falha |
| Texto refinado de PERMISSAO-AGENTES-MD na junção (f99351a) | test_textos_034.PermissaoAgentesMd.test_skill_manda_avisar_antes_de_delegar_edicao_de_agents | frase da skill | passou |
| Heredocs dentro do orçamento (falha de tempo do push anterior, carga 17) | test_hooks.Hooks.test_muitos_heredocs_recusam_dentro_do_orcamento | limite 5,0 s | passou; maior medida 2,67 s |

## Cenários e resultado real
Suíte do push (resumo copiado do log):
- `processo 1: rc 0, 964 testes, 2028.1 s, 44 módulos`
- `processo 2: rc 0, 1682 testes, 1215.1 s, 55 módulos`
- `Ran 2646 tests in 2028.342s (2 processos)` e `OK (skipped=30)`; nenhuma linha FAIL ou ERROR no log (grep).
- Linhas que não são falha: `catraca: a API do GitHub não respondeu por inteiro (KeyError|OSError); vale como sem rótulo.` (3, saída de teste de erro da catraca), `AVISO: --confiar ...` e `AVISO: j/lint pulado: actionlint ausente no PATH` (2), todas de testes que passaram.

Cobertura do lote por leitura (módulo do item, todos presentes entre os 99 do log):
- achado-teto-doc: test_achado_teto_doc. invariante-gatilho: test_invariante_gatilho. modelos-parecer-avisos-2: test_modelos_parecer_avisos_2. pergunta-maior-menor: test_pergunta_maior_menor. permissao-agentes-md: test_permissao_agentes_md.
- textos-034: test_textos_034 (conferindo a redação refinada na junção, f99351a). aq1-texto-v2: test_aq1_texto. aq3-texto-v2: 11 testes novos em test_forge. fechar-esperar-rotulo: test_fechar (+ tests/mutantes/fechar-esperar-rotulo.json). conferente-leitura-git: test_guarda_conferente.
- f22-release-v2 e pareceres-033: só texto, sem teste próprio; entram na suíte estrutural (test_forge, neutralidade) e já têm QA por leitura; o A1 do QA da f22 (invariante "um só por candidato") segue recomendação dele.
- Correções da volta da E2.1 (mapa, citação da R-DECISAO, modelo de segurança, pesos): cada uma tem o teste que a reprovou no push de 17:20, na tabela acima, e todos passam no push de 22:05.
- Mudança sem teste que a cubra: nenhuma achada. Mapa e pesos são guardados por testes que reprovam o lote se faltarem.
- Vermelho antes do verde e mutação: não refeitos aqui; vêm dos pareceres de cada item e das falhas observadas no push de 17:20, que provam os guardas da junção.
