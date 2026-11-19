---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-catraca-movidas
commit: 6c1f86913acbbd8185b4dba9c1b7985c5f457f5b
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-18
---
# Review: v0478 (E28.2, catraca com movidas)

Diff 2904a68a..6c1f8691: `tests/catraca.py` (+7/-1, dentro do teto H1), 3 testes em `tests/test_catraca.py`, spec `tests/mutantes/v0479-catraca-movidas.json` (M1, M2) e fragmento em `changelog.d/`.

## Sondas

## Parecer
Aprovado. A `regra_guardas_dos_hooks` agora junta as saídas de `fm.analisar_com_textos` dos hooks lidos e as passa por `fm.movidas`, a mesma função que o `forge-mutante --cobertura` usa; `movidas` devolve uma linha por linha de entrada, na ordem, e o `zip(lidos, por_arquivo)` com `next(linhas)` devolve a cada arquivo as suas linhas sem desalinhar (o arquivo ILEGIVEL sai antes de entrar em `por_arquivo` e em `lidos`).

Não afrouxa (R-QA, R-REVIEW):
- `movida` só sai quando o texto da apagada entra `coberta` (mutante não equivalente de spec do diff) noutro hook do mesmo diff, uma coberta por apagada; sem mutante no destino, o destino segue `sem mutante` e a origem segue `apagada`, ambos em `FALTAS_DE_MUTANTE` (teste `..._sem_mutante_no_destino_barra`).
- Apagada de fato, com mutante de outra condição noutro hook, segue `apagada` (teste `..._apagada_de_verdade_barra_...`).
- O conjunto de destinos da catraca é mais estreito que o da ferramenta (só os arquivos de controle de `guardas_do_diff`, não todo Python do diff): a catraca fica igual ou mais estrita que o `--cobertura`, nunca mais frouxa.

Ferramentas e testes (sem suíte local, CI no PR):
- `bin/forge-mutante --cobertura --base 2904a68a`: rc=0, sem linha de falta; `--conferir`: "o trecho de cada spec do diff está no lugar", rc=0.
- Os 3 testes novos: OK no head. M1 aplicado: `..._com_mutante_no_destino_passa` falha (morto). M2 aplicado: `..._sem_mutante_no_destino_barra` e `..._apagada_de_verdade_...` falham (morto). Cópia em pasta temporária, ambiente limpo.
- As duas linhas novas de controle têm um mutante cada; não há `if`/`raise` novo no diff.
