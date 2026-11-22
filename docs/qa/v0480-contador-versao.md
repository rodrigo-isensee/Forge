---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-contador-versao
commit: fb4d5390b925256caa28286bef2f997d8af66489
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 1
bugs_baixos: 1
data: 2026-11-22
---
# QA: v0478 · E103.5 · bin/forge-contador

Sem especificação de UX nem contrato de API; as obrigações são o cabeçalho de `bin/forge-contador` (uso, linha 1, teto, saída 0/2) e a linha da skill `fluxo-do-pedido`. Sem suíte local; o check-run `bateria` do mesmo sha é do CI do PR (sem PR, E103.5).

## Achados
- A1 (bloqueante) bin/forge-contador:47 · `plugin.json` ilegível (`{`) ou não objeto (`[]`) na REF dá traceback (JSONDecodeError/AttributeError) e rc 1; o cabeçalho promete rc 2 "versão ilegível" e `main` só captura `Erro`. Reproduzido.
- A2 (recomendado) bin/forge-contador:63 · `git ls-tree` cita nome não ASCII (`"changelog.d/a\303\247\303\243o.md"`), o `endswith(".md")` falha e o fragmento some da contagem (esperado 3, obtido 2). Use `-z`.
- A3 (recomendado) bin/forge-contador:130 · `--historico` sem `--quadro` é aceito e ignorado em silêncio; o teto vem da árvore da raiz e os fragmentos da REF. Falhar com rc 2 ou documentar.
- A4 (recomendado) tests/mutantes/v0480-contador-versao-2.json:1 · as 3 specs declaram pedidos diferentes (`-2`, `-3`) e `forge-mutante` recusa a rodada única; o padrão do Forge é o mesmo `pedido` com id único.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Linha 1: fragmentos da REF sem README e patch+1 | LinhaDaVersao.test_conta_fragmentos_*, test_le_a_ref_* | README e arquivo não .md; árvore suja | passou |
| Versão pela marca sem plugin.json | test_sem_plugin_json_usa_a_ultima_marca, test_sem_plugin_json_nem_marca_parte_de_zero | sem marca | passou |
| Teto de .forge/config.json (padrão 20) | test_teto_da_configuracao, test_teto_invalido_e_erro | 0, negativo, string, bool | passou |
| Saída 2 em erro (git, versão, config) | test_versao_ilegivel, test_configuracao_ilegivel, test_ref_inexistente, test_sem_develop | `{` e `[]` na config | passou; plugin.json ilegível: sonda reprovou (A1) |
| `--quadro`: abertos por coluna, versões que faltam | Backlog.test_so_quadro, test_quadro_vazio | quadro sem abertos | passou |
| `--historico`: dia, previsão, crescendo | test_previsao_pela_vazao_liquida, test_crescendo_sem_data, test_vazao_zero_sem_data | vazão menor ou igual a zero | passou |
| Quadro ausente é erro | test_quadro_ausente_e_erro | arquivo inexistente | passou |
| Skill manda começar pela saída | skills/fluxo-do-pedido/SKILL.md (leitura do diff) | n/a | conferido |

## Cenários e resultado real
- Testes do arquivo: `python3 -I -m unittest discover -s tests -p test_forge_contador.py` com TMPDIR: 16 testes, OK.
- Saída real, só leitura, contra `/root/.forge-contrib/KANBAN.md` e `docs/kanban/historico.md` (nada gravado):
  - `0.47.15: 6 de 20`
  - `backlog: 163 abertos (Entrada 65 · Pronto para fazer 79 · Em andamento 8 · Bloqueado 3 · Aguardando o dono 8) · versões que faltam: 9 · hoje +0 -9`
  - `previsão: 2026-12-11 pela vazão líquida de 8.7/dia nos últimos 3 dias`
  - Conferido à mão: contagem por coluna igual às linhas de dados do quadro; saídas do dia 9 (5 Em andamento→Pronto, 1 Entrada→Pronto, 3 Pronto para fazer→Pronto), entradas 0.
- Sondas (repositório descartável): plugin.json `{` → traceback, rc 1 (A1); `[]` → AttributeError (A1); nome `ação.md` → contagem 2 de 3 (A2); `--historico x` sem quadro → saída normal (A3); `--raiz /nao` → rc 2 com mensagem.
- Mutantes (um por spec, pedidos distintos): spec 1: M1..M8 morreram; spec -2: M1..M8 morreram (M2 e M5 por erro com controle verde); spec -3: M1..M8 morreram (M6 por erro). Nenhum sobrevivente. `bin/forge-contador` é ferramenta nova, não guarda existente; `--cobertura` não se aplica.
- Vermelho: `forge-testes --vermelho 900bfdfe --modulos test_forge_contador --prazo 90`: 10 provam (asserção), 1 não prova (passa na base), 5 sem veredito (os 5 de Backlog, erro na base: voltam ao autor, não valem como vermelho). A rodada sem `--modulos` estourou o prazo (rc 143, sem veredito).
- Nenhum teste cobre o caso de A1; o autor soma o teste com o conserto.
