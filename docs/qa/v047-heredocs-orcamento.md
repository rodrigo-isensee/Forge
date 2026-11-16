---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-heredocs-orcamento
commit: ec8997a6bfb365a9061316ea7905d12e8d5279a7
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-14
---
# QA: v047-heredocs-orcamento

Intervalo `origin/develop..ec8997a6` (classe C, só testes: `menor_custo` no apoio e nas medidas de orçamento dos hooks; limites iguais). Obrigação: TESTE-HEREDOCS-ORCAMENTO-ESTAVEL (E1.200); sem especificação de UX nem contrato de API.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Abaixo do limite mede uma vez | `MenorCustoDasMedidas.test_abaixo_do_limite_mede_uma_vez` | logo abaixo do limite (2,9 de 3,0) | passou |
| No limite ou acima repete e vale a menor | `test_no_limite_ou_acima_mede_de_novo_e_vale_a_menor` | no limite (3,0, estrito), menor na 1ª, 2ª e 3ª | passou |
| Regressão passa do limite nas 3 e para na 3ª | `test_regressao_passa_do_limite_nas_tres_e_para_na_terceira` | máximo de 3 medidas | passou |
| Limites iguais, medida por CPU do hook | `test_linha_adversaria_de_crases_e_pastas_recusa_dentro_do_orcamento` (limite/2 igual ao da base) | teto de caracteres e linha grande | passou (18 s) |
| Limites iguais nas demais medidas | `test_comando_logico_le_os_limites_uma_vez_por_texto` (1,0 s), `test_muitos_heredocs_recusam_dentro_do_orcamento` (3,0 s), `test_orcamento_sai_numa_linha_de_formato_fixo` | limites de CPU inalterados | passou (3 testes, 118 s) |

## Cenários e resultado real
- Diff conferido: os limites (`limite / 2`, 1,0, 3,0, `PRAZO_DA_LINHA_S`) não mudaram; só o modo de medir. O esperado do fixture continua conferido em cada medida (`executar_fixture`), então a repetição não mascara decisão errada. Regressão real passa do limite nas 3 medidas (teste 3).
- `python3 -m unittest tests.test_medida_cpu`: 15 testes, OK.
- Vermelho: `forge-testes --vermelho origin/develop` estourou o prazo (170 s, rc=124; saída: `vermelho: base=f4b0c2aeb42b head=ec8997a6bfb3 ... revertidos à base: changelog.d/v047-heredocs-orcamento.md, tests/apoio_volta_unica.py`, sem veredito). À mão, numa cópia de `HEAD` com só `tests/apoio_volta_unica.py` da `origin/develop`: `python3 -m unittest tests.test_medida_cpu` e o teste das crases caem com `ImportError: cannot import name 'menor_custo'`, FAILED (errors=1) cada um. O vermelho é por importação, e os 3 testes novos só existem com o apoio.
- Mutação (`R-QA`): `bin/forge-mutante tests/mutantes/v047-heredocs-orcamento.json`:
  `forge-mutante: pedido=v047-heredocs-orcamento rev=ec8997a6bfb3 spec=0b8016f9...`; M1 morreu (apoio_volta_unica.py:56), M2 morreu (:56), M3 morreu (:58), M4 morreu (:55). 4 de 4; 4 linhas de guarda do `menor_custo`, cada uma com mutante.
- CI: a branch não tem PR nem check-run `bateria` neste sha (`gh run list --branch` vazio); a suíte inteira fica para o CI do PR, que o tech-lead confere.
- `forge-check docs`: ver Provas do relatório.
