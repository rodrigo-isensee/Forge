---
tipo: qa
contrato: 1
pedido: pn5-esperar-estado
branch: melhoria/pn5-esperar-estado
commit: 9e4eb2a3a6b5d0684f6ac9ead3a2a441a03508f2
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-29
---
# QA: pn5-esperar-estado

Skill `esperar-estado` (espera de PR pelo estado, saída em MERGED ou CLOSED) e carga no `agents/tech-lead.md` (`R-QA`). Sem gatilho de segurança: texto de skill e de agente, sem hook nem controle.

## Achados

## Critério → teste → resultado
Sem `CA-n` no pedido; as obrigações são as do escopo E1/E2 e os casos da seção 3 do lote B1 do desenho.

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1: PR mesclado com checks pendentes sai (caso P-N5) | `LacoDoPr.test_pr_mesclado_com_checks_pendentes_sai_na_segunda_volta` (OPEN, MERGED: `fim=MERGED`, rc 0, 2 leituras) | transição OPEN para terminal | passou |
| E1: PR fechado sai | `test_pr_fechado_sai` (`fim=CLOSED`, 1 leitura) | estado terminal CLOSED | passou |
| E1: checks 0 e 1 em OPEN | `test_checks_sem_pendencia_saem_com_o_codigo` | código diferente de 8 | passou |
| E1: teto de 17 leituras, rc diferente de 0 | `test_pendente_o_tempo_todo_sai_no_teto_depois_de_17_leituras` | teto exato (17) | passou |
| E1: `gh` que falha | `test_gh_que_falha_sai_com_erro` (`fim=erro`, 0 checks lidos) | falha do `gh` | passou |
| E1: sem `sh -c`, `timeout`, `--watch`, `run_in_background`; voltas x intervalo <= 540 | `TextoDaSkill.test_blocos_sem_espera_proibida_e_dentro_do_teto` | 17 x 30 = 510 <= 540 | passou |
| E1: sem palavra de marcador dos hooks | `test_skill_sem_palavra_de_marcador_dos_hooks` | n/a | passou |
| E1: frontmatter e tech-lead carrega a skill | `test_frontmatter_e_tech_lead_carrega` | n/a | passou |
| Blocos passam pelos hooks `parecer` e `conformidade` (papel tech-lead, Forge e projeto) | `BlocosPassamPelosHooks.test_blocos_saem_0_no_parecer_e_na_conformidade` | 4 x blocos casos, rc 0 | passou |
| E2: módulo no mapa e contagem | `test_testes_tocados` (31 módulos) | n/a | passou |

## Cenários e resultado real
- `python3 -m unittest tests.test_esperar_estado tests.test_testes_tocados` sobre 9e4eb2a: `Ran 90 tests ... OK` (carga de 1 min 2,97 antes da suíte).
- `scripts/validar-plugin.sh`: `Validation passed` (só o aviso ICON_MISSING, pré-existente e sem relação).
- Conferido: `gh pr checks --help` traz "8: Checks pending", como a skill cita; a skill tem 32 linhas (teto do desenho, 133); `bin/forge-testes` põe o módulo em FORGE_CHECK, em `hooks/` e na regra de `skills/esperar-estado` e `tech-lead.md`; fragmento de changelog presente; nenhuma guarda de código (`bin/`, `hooks/`) mudou além do mapa, então não há spec de mutantes.
- Mutação manual do laço da skill numa cópia em `$TMPDIR` (4 mutantes, todos mortos): 17 para 18 voltas (1 falha), `-eq 8` para `-eq 0` (3 falhas), remoção da saída fora de OPEN (2 falhas), remoção do `|| fim=erro` (1 falha).
- Vermelho antes do verde (`forge-testes --vermelho`): não rodei; a tentativa passou do prazo da ferramenta e saiu sem veredito (nunca vale como vermelho); a skill é arquivo novo, e os testes de laço leem a própria skill, provados pelos 4 mutantes acima.
- PA-7 (`docs/engineering/achados-recorrentes.md`): AR-1 a AR-10 conferidos contra o diff; nenhum se aplica (sem lista de mutantes, hook, `python` de decisão, `cd` nem limite antigo no texto).
- Observação sem bloqueio: o laço da skill não foi exercitado contra o `gh` real por este parecer (o autor registra o PR #370 real com `fim=MERGED`).
