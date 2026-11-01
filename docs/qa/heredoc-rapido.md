---
tipo: qa
contrato: 1
pedido: heredoc-rapido
branch: melhoria/heredoc-rapido
commit: c51715f222eb6d6b9ec0c990f5db6e5bceea4c10
parecer: reprovado
escopo: completo
revisor: forge:qa-engineer
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-01
---
# QA: heredoc-rapido

Etapa E1.4. Diff lido: `c454ccb..c51715f` (`hooks/conformidade.py` +8/-2, `tests/test_hooks.py` +21, fragmento de changelog). Entrega o item E1 do pedido, passo 1 do desenho: `Guarda._regras` e `Guarda._raiz_home` guardam por decisão o manifesto e o par realpath(raiz)/realpath(home). Passo 2 fora do diff. Cumpre a M14 (agents/tech-lead.md:19): 31 linhas contáveis (limite 150), um comportamento, uma classe em `hooks/`. O limite de 5,0 s do teste não mudou.

## Critério → teste → resultado
| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1: a recusa de R-MAIN com 3000 heredocs não muda | `Hooks.test_muitos_heredocs_recusam_dentro_do_orcamento` (duas formas) | 3000 heredocs, limite 5,0 s de parede e de CPU | passou |
| E1: decisão igual em todo o corpo de fixtures | `Hooks.test_fixtures` (corpo de fixtures dos hooks) | `so_forge`, home, projeto, papéis | passou |
| C-1/C-5 (e): uma leitura do manifesto e um home por decisão, sem cache entre decisões | `Hooks.test_regras_e_raiz_sao_calculadas_uma_vez_por_decisao` | 4 instâncias × 50 destinos | passou |
| C-5 (a),(b): 2 destinos protegidos, com e sem manifesto | `test_fixtures`: `protegido-claude-plugin-*`, `protegido-github-*`, `politica-de-conformidade-so-em-melhoria` | `so_forge` vale só com manifesto | passou (H1, H3, H4 mortos) |
| C-5 (c): sessão de projeto com manifesto forjado, `so_forge` não vale | nenhuma fixture | `externo` não nulo | sem teste: H5 sobreviveu (A1) |
| C-5 (d): home e raiz resolvidos (ordem e realpath) | `test_fixtures`: `vigor-claude-md-*`, `home-claude-*` | ordem `raiz, home` | passou para a ordem (H8); o realpath do home sem teste (H9, A2) |

## Execução (head c51715f; a worktree está à frente só com pareceres e a spec)
- `python3 -m unittest tests.test_hooks.Hooks.test_fixtures ...test_muitos_heredocs_recusam_dentro_do_orcamento ...test_regras_e_raiz_sao_calculadas_uma_vez_por_decisao`: `Ran 3 tests in 85.265s` `OK`.
- Vermelho antes do verde: `bin/forge-testes --vermelho c454ccbb7b76c9148023ff66d04e43895ffcb308`, rc=0, `contagem: não prova (passa na base)=1358; prova (asserção)=1; pulado=26` (o único que prova é o teste novo; os 26 pulados são subtestes do lançador, pulados na base e no head).
- Cobertura de mutação: `bin/forge-mutante --cobertura --base c454ccb...` rc=0 (antes da spec, rc=1 com as linhas 440 e 492 sem mutante): `coberta · hooks/conformidade.py:440 · H1, H2` e `coberta · hooks/conformidade.py:492 · H6, H7`, ambas "declarado, não provado". Conferi a lista contra o diff: linhas 440, 441, 492, 493 e 494 têm mutante; a linha 441 (condição `externo is None and ...`) e a 493 (realpath) não são condição Python mudada, e tive de acrescentar H3 a H5 e H9.
- Mutantes (`bin/forge-mutante tests/mutantes/heredoc-rapido.json`, 16 min, rc≠0): H1, H2, H3, H4, H6, H7, H8, H10, H11 morreram; H5 e H9 sobreviveram (A1 e A2). H2 e H7 são o M3 do desenho (sem cache), mortos pelo teste de contagem, não pela parede. H10 e H11 (cache de classe) provam o C-1 entre decisões.
```
H5 · sobreviveu · hooks/conformidade.py:441   (self._regras = tem_manifesto_do_forge(self.h.raiz), sem o externo)
H9 · sobreviveu · hooks/conformidade.py:493   (Path(Path.home()), sem o realpath do home)
```
- Fixture que mata o H5, provada numa cópia de c51715f em `$TMPDIR` (head: código 0; com H5: código 2): `arquivos` com `src/app.js`, `.forge/versao` e `.claude-plugin/plugin.json` `{"name": "forge"}`; `git` branch `melhoria/x`; `env` `HOME={tmp}/home` e `CLAUDE_PROJECT_DIR={tmp}/proj`; Write de `{raiz}/.github/x.yml` por `forge:node-backend`; esperado código 0 (um projeto não herda os caminhos `so_forge` só por escrever o manifesto).

## Medida de tempo do hook (3000 heredocs, parede em s, WSL, load 2,5 a 3,7; 5 medidas)
| Forma | Base c454ccb | Head c51715f |
|---|---|---|
| um por linha | 2,02 1,90 1,90 2,00 1,92 | 1,41 1,41 1,40 1,41 1,43 |
| `&&` | 1,96 1,97 1,98 1,96 1,97 | 1,47 1,49 1,49 1,51 1,50 |
Redução de cerca de 27%. A razão CI/local do pedido (2,6 a 3,1) dá, no head, 3,6 a 4,7 s no runner (pior caso 1,51 × 3,1), abaixo de 5,0 s, mas o pior caso passa dos 4,5 s em que o Jarvis abriu o passo 2. A medida do runner sai do CI do PR (E1.5) e decide: acima de 4,5 s, o passo 2 vira PR próprio.

## Achados
- A1 (bloqueante) hooks/conformidade.py:441 · H5 sobreviveu: sem o `externo is None`, o `so_forge` valeria em projeto com manifesto forjado e nenhum teste cai (C-5 c, R-SEGURANCA). Criar a fixture descrita no parecer; H5 precisa morrer em `forge-mutante`.
- A2 (bloqueante) hooks/conformidade.py:493 · H9 sobreviveu: tirar o `realpath` do home não derruba teste (C-3); com HOME em symlink a proteção de `~/` falha. Fixture ou teste com HOME por symlink; H9 precisa morrer.
- A3 (recomendado) tests/hooks/conformidade/:1 · corpo de fixtures sem os casos C-5 (c) e (d) do modelo de ameaças (sessão de projeto, HOME trocado na linha); A1 e A2 já trazem o essencial.

## Parecer
Reprovado, só por prova de mutação (R-QA): o código revisado cumpre o item E1 e a M14, o hook recusa igual, o tempo cai 27% (1,4 a 1,5 s local) e os testes passam, mas dois mutantes das linhas mudadas (441 e 493) sobrevivem. Devolve ao tech-lead: duas fixtures (a de A1 está pronta acima) e nova rodada de `bin/forge-mutante tests/mutantes/heredoc-rapido.json` com todos mortos. Nenhum defeito de produção encontrado (bugs 0).
