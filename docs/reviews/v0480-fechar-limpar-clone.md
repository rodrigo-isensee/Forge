---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-fechar-limpar-clone
commit: 5ff5fb4cf68646f8a09fc909df5bc927b9844e1c
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0478 (E132.14, PR #831, revalidação por delta da volta E132.13)

Revalidação do PR #831 no head 5ff5fb4c, depois do parecer reprovado em 7ba9f0ba (E132.10). Só o delta lido.

## Delta lido
`forge-check parecer delta docs/reviews/v0480-fechar-limpar-clone.md`: intervalo `7ba9f0ba..5ff5fb4c`; no domínio `bin/forge-fechar`, `tests/mutantes/v0480-fechar-limpar-clone.json`, `tests/test_fechar_config.py`, `tests/test_fechar_limpar_clone.py` (33 linhas a mais, 4 a menos). Fora do domínio, só os pareceres de QA, review e segurança.

## O que foi conferido
- A1 (bloqueante, SC2100): `local -a sem` virou `local -a sem_busca` em `origem_atual` (`bin/forge-fechar`:607, :610 e :611), só o nome; nenhuma lógica nova. O job `bateria (verificações longas)` do CI no head 5ff5fb4c (run 45314696983) está verde, o que prova o shellcheck limpo (aqui não há shellcheck local).
- A2 (recomendado): o teste de `tests/test_fechar_config.py`:104 passou a se chamar `..._nao_ganha_config_e_sai_clone_nenhum`, coerente com a asserção.
- Teste novo `test_head_mesclado_que_esta_copia_nao_le_e_buscado_e_o_clone_ancestral_sai`: o head mesclado nasce numa outra cópia, a branch sai da origin e o teste afirma que esta cópia não tem o objeto antes do fechamento; o clone ancestral sai (`clone=ok`). Cobre a busca dos `merged_heads` que o review anterior só leu.
- Mutante M13 (tira `$merged_heads` da busca, `bin/forge-fechar`:610): `bin/forge-mutante --processos 1 --ids M13` · `M13 · morreu`.
- Testes dos arquivos tocados: `python3 -m unittest tests.test_fechar_limpar_clone tests.test_fechar_config` com 12 testes OK.
- CI do PR no head 5ff5fb4c (run 45314696983): suítes 3.12 e 3.14 (5 partes cada), `verificações longas`, `passos`, `instalação`, `catraca` e tetos de pulados verdes; `bateria (pareceres)` vermelho só porque os pareceres de review e QA do head anterior reprovam, o que este parecer e o do QA resolvem.

## Parecer
Aprovado. O bloqueio A1 caiu com a troca de nome e o shellcheck do CI ficou verde no head; o A2 foi resolvido na mesma volta, e o teste novo, com o mutante M13 morto, fecha a busca dos heads mesclados que esta cópia não lê.
