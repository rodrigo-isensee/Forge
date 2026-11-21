---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-dir31-focus
commit: 0d5826f9ce401e259e888080149cef3d4ed37218
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: v0479-dir31-focus (DIR-31, visão de foco), head 0d5826f9

Primeira rodada (E67.3) sobre `bead3e53..0d5826f9` (9 arquivos, +250 −3). Arquivos lidos: `scripts/jarvis`, `templates/projeto/.claude/settings.json`, `tests/test_sessao_automatica.py` (classes `AtalhoAbreNaVisaoDeFoco` e `ModeloELinguagem`), `README.md:39`, `agents/jarvis.md` e o desenho `docs/arquitetura/visao-de-foco.md` (seção 2.1).

Gatilhos: execução de comando no atalho (`scripts/jarvis`, novo argumento `--settings` na abertura da sessão em modo automático), arquivo de configuração do modelo de projeto copiado a todos os projetos (`templates/projeto/.claude/settings.json`).

## Achados

## Sondas

## Detalhe dos achados
Sem achados. O que sustenta o parecer:
- **`--settings` não carrega entrada:** `scripts/jarvis:70-94` monta o JSON só com literais (`{"viewMode":"focus"}` e `{"tui":"fullscreen"}`) por `json.dumps`; nenhum valor lido dos arquivos é impresso nem repassado (o `env` do usuário, que pode ter credencial, nunca sai). O argumento vai como elemento do array `args` e o `exec claude "${args[@]}"` não passa por shell: sem injeção. O stderr do auxiliar vai a `/dev/null` (`:93`) e a falha dele (`|| foco=""`) só tira o argumento, sem barrar a abertura (teste `test_python_que_falha_nao_impede_a_abertura`).
- **A camada nova não mexe em controle:** o `--settings` é a camada `flagSettings` do Claude Code; só as chaves `viewMode` e `tui` entram nela, então `sandbox`, `permissions.deny`/`ask` e `defaultMode` dos arquivos do projeto e do usuário seguem valendo, e a camada gerenciada continua acima. O aviso de sandbox desligado (`:65-67`) e o `--permission-mode auto` (`:51`) não mudam.
- **Leitura dos arquivos:** `python3 -I` (sem `PYTHONPATH` nem diretório do script no caminho de import), só `json`; arquivo ilegível (inclusive aninhamento fundo, que vira `RecursionError`, subclasse de `Exception`) encerra sem saída, ou seja, não decide pelo dono (teste `test_arquivo_ilegivel_nao_decide_pelo_dono`, 3 casos). Os caminhos lidos são os mesmos que o Claude Code já lê na abertura; arquivo apontado para dispositivo infinito trava os dois, e o padrão já existia em `sandbox_ligado` (`:53-64`): não é superfície nova.
- **Modelo de projeto:** `templates/projeto/.claude/settings.json:3` só acrescenta `"viewMode": "focus"` no nível de cima; o bloco `sandbox` e as listas de `permissions` ficam idênticos. Conferido no Claude Code 2.1.224 instalado: o esquema declara `viewMode` como enum com `.catch(void 0)`, então valor estranho é descartado sem invalidar o arquivo (e com ele o sandbox e os `deny`). O modelo não leva `tui` (teste `test_modelo_de_projeto_liga_a_visao_sem_trocar_o_renderizador`).
- **Não passa `--verbose`** (teste `test_sem_nenhum_arquivo_liga_a_visao_e_a_tela_cheia`); a escolha do dono em qualquer dos três arquivos vence (`test_viewmode_em_qualquer_arquivo_do_dono_nao_e_passado`, `test_arquivo_local_vence_o_projeto`).
- **Segredo:** nas linhas acrescidas de `bead3e53..0d5826f9`, nenhum casamento de padrão de token, chave de acesso nem chave privada. Nenhum workflow nem dependência tocados.
- **Testes rodados:** `python3 -m unittest tests.test_sessao_automatica` no head: 22 testes, OK. A suíte inteira é do CI do PR, ainda não aberto; o merge exige o CI verde.

## Riscos aceitos e ferramentas
Nenhum risco aceito nem pendente de aceite. Lacuna: gitleaks, osv-scanner, semgrep, zizmor e actionlint não estão no PATH; o item não toca workflow nem dependência, e a busca de segredo foi feita por padrão nas linhas acrescidas.
