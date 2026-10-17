---
tipo: qa
contrato: 1
pedido: aq
branch: melhoria/aq
commit: c8acc52ededd96fb9c0159d19308feca63b95237
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-17
---
# QA - aq (criação do AQ, plugin forge-dev)

Sem UX nem API. Diff `0095d29...c8acc52` (implementação `efdd72e` e duas voltas: `e812309`, `679aaf1`, `96a21aa`/`c8acc52`). Não escrevi o diff. Review e segurança com `parecer: aprovado` e `commit: c8acc52ededd96fb9c0159d19308feca63b95237` (as revalidações "após a segunda volta"); os commits depois de `c8acc52` só trazem esses pareceres.

## Obrigação -> teste -> resultado
| ID | Obrigação (pedido, "Escopo" e "Critério de pronto") | Teste | Fronteira protegida | Resultado |
|---|---|---|---|---|
| Q-1 | `forge-dev` não vaza para `plugin.json` nem `marketplace.json` | `tests.test_forge.PluginDeDesenvolvimento` (6 testes); conferência à mão com `grep` nos dois manifestos | `dev/` só com manifesto e `agents/*.md`; agente de dev nunca listado no `forge` | passou |
| Q-2 | `jarvis-forge` só passa o 2º `--plugin-dir` quando `dev/` existe | `claude` falso no PATH, HOME falso, `--sem-tmux`, cinco casos: `--dev` sem `dev/`, `--dev` com `dev/` sem manifesto, `--dev` com `dev/`, vigente sem `dev/`, vigente com `dev/` | `dev/` ausente; `dev/` sem `.claude-plugin/plugin.json` | passou: só com manifesto vem `--plugin-dir ./dev` (ou `<vigente>/dev`) |
| Q-3 | AQ (opus, `tools: Read, Grep, Glob, Write, Edit`, sem Bash nem WebFetch) | `test_aq_tem_papel_e_lista_de_escrita_no_hook` | ferramenta proibida no frontmatter | passou |
| Q-4 | AQ grava só em `docs/propostas/` e `docs/arquitetura/` de cópias do Forge, sessão num projeto | 8 caminhos à mão com `CLAUDE_PROJECT_DIR` num projeto git: `docs/propostas/` 0; `src/`, `agents/`, `../x.md`, `docs/propostas/../../agents/` e `agents/` do Forge fora de `~/.forge-contrib` 2; worktree `wt/x/agents/` 2 | `..`, caminho relativo, outro repositório | passou |
| Q-5 | idem, sessão no Forge (pasta corrente em `~`, no clone e na worktree) | 15 caminhos à mão e as 5 fixtures `aq-sessao-forge-*` | pasta corrente fora de projeto; raiz do Forge | passou: `docs/propostas/` e `docs/arquitetura/` do clone e de `wt/x` 0; `agents/`, `.claude/`, `~/.bashrc`, `~/.forge-contrib/docs/pedidos/`, outro repositório 2 |
| Q-6 | Política malformada falha fechada | `test_escrita_permitida_malformada_bloqueia` (4 formas) e à mão: `{"aq":[]}`, `{"aq":"docs/"}`, `[1]` e JSON ilegível, nas sessões do Forge, de projeto e fora de projeto | lista vazia, tipo errado, JSON quebrado | passou: 2 em todos |
| Q-7 | Erro interno falha fechado para o AQ | `test_erro_interno_com_lista_de_permissao_falha_fechado` | exceção no hook | passou |
| Q-8 | Outros papéis não mudam | suíte completa; à mão `forge:dev` e `forge:tech-lead` gravam em `agents/` do Forge (0), como antes | papel sem lista | passou |
| Q-9 | Exploratório: link simbólico | à mão: link em `docs/propostas/` para `agents/`, link para `~/.bashrc`, e `docs/arquitetura` inteiro como link para `agents/` (absoluto e relativo) | caminho resolvido pelo disco | passou: 2 em todos |
| Q-10 | Exploratório: worktree fora de `~/.forge-contrib/wt/` | à mão: worktree em outra pasta, sessão no clone: 2; com a própria worktree como raiz da sessão: 0 (é a raiz declarada) | cópia fora de `~/.forge-contrib` | passou |
| Q-11 | `scripts/validar-plugin.sh` e `claude plugin validate dev --strict` | execução real | manifesto de `dev/` | passou nos três manifestos |

## Vermelho antes do verde
Cópia de `c8acc52` em `$TMPDIR` com `hooks/conformidade.py`, `hooks/conformidade.json` e `scripts/jarvis-forge` trocados pelos de `0095d29`: `python3 -m unittest tests.test_hooks -q` deu `Ran 16 tests` / `FAILED (failures=17)`: `test_erro_interno_com_lista_de_permissao_falha_fechado`, quatro subtestes de `test_escrita_permitida_malformada_bloqueia` e 12 fixtures `aq-*-bloqueia` (`aq-sessao-forge-agents-bloqueia`, `aq-sessao-forge-pedido-bloqueia`, `aq-sessao-forge-agents-em-worktree-bloqueia`, `aq-escreve-agents-bloqueia` etc.). As fixtures `*-libera` passam sem a mudança, como esperado (liberar é o comportamento antigo). `tests.test_forge.PluginDeDesenvolvimento` com o mesmo estado: `FAILED (errors=1)`. Com o código do diff, tudo verde.

## Execução
- `python3 -m unittest discover -s tests -q` na worktree, HEAD `164d5ca` (diferença para `c8acc52`: só `docs/reviews/aq.md` e `docs/security/aq.md`): `Ran 785 tests in 124.077s` / `OK`.
- Mutação: o repositório não tem ferramenta gratuita de mutação para Python/hook configurada; o vermelho antes do verde acima faz o papel de prova de que os testes pegam a mudança. Lacuna declarada.

## Observações (não são bugs; sem bug aberto)
1. Sessão num projeto (ou o Forge com a pasta corrente num projeto): o AQ grava em `docs/propostas/` e `docs/arquitetura/` do projeto (código 0). É a nota informativa da segurança; o AQ só é carregado pela sessão do Forge e não é instalado nos projetos. Recomendação já registrada: limitar as entradas relativas à raiz de um clone do Forge.
2. Raiz de sessão que não é repositório git (sem `.git`): o AQ passa em qualquer caminho (código 0), mas `forge:dev` também passa em `.claude/settings.json` nessa condição, então o comportamento já existia e não vem do diff. Projetos do Forge são repositórios git.
3. Do review: com `conformidade.json` malformado, o hook agora barra toda ferramenta de qualquer papel até em pasta fora de projeto (antes ficava calado). Conferido à mão, é falha fechada coerente com a seção 7 da ADR 0009; só ocorre com defeito no arquivo versionado, que a suíte pega.
4. Não testei o carregamento real do plugin `forge-dev` por uma sessão do Claude Code (exige modelo, `api.anthropic.com` está fora do sandbox); o script foi testado com `claude` falso e o manifesto, com `claude plugin validate`.

## Fora do escopo
E1.4 (integração), E3.1 (estudo do AQ), E3.2 (decisão do dono) e a segurança 7 (AQ-OPERACAO).
