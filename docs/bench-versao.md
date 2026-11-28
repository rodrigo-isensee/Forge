# Bench de versões com agentes (BENCH-VERSAO)

Mede se cada versão do Forge melhora ou piora: a mesma entrega pequena, feita pelo time de verdade, em cada tag
(ordem do dono de 24/11; desenho do arquiteto na etapa E175.1 do pedido v0478). Complementa o bench mecânico
(`docs/kanban/bench-versoes.md` do quadro), que mede o processo sem chamar agentes.

**Só o dono roda**, na máquina dele, num terminal comum e com a assinatura (`R-CUSTO`): o roteiro recusa com `CI`,
`GITHUB_ACTIONS` ou qualquer credencial ou provedor pago definido (`ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN`,
`ANTHROPIC_BASE_URL`, `CLAUDE_CODE_USE_BEDROCK`, `CLAUDE_CODE_USE_VERTEX`, `CLAUDE_CODE_USE_FOUNDRY`), recusa o
`--executar` dentro de uma sessão de agente (`CLAUDECODE` ou `CLAUDE_CODE_ENTRYPOINT`; nem pelo `!` do Claude Code) e
nunca entra no CI. A sessão não herda essas variáveis e é encerrada se o `init` dela trouxer `apiKeySource` diferente de
`none` (`apiKeyHelper`, chave): limite `api-paga`. Os testes do roteiro usam `claude` e `gh` falsos.

## Peças
| Peça | Onde | Por quê |
|---|---|---|
| Pedido de referência | `tests/bancada/romanos/pedido.md` | 5 critérios e as decisões respondidas; o sha256 vai para o registro de cada rodada |
| Resposta automática | `tests/bancada/romanos/resposta.md` | texto fixo para a sessão que para e pergunta |
| Testes escondidos | `~/.forge-bench/escondidos/romanos-v1/` (fora do repositório) | 28 casos caixa-preta; congelados pelo sha256 em `tests/bancada/versao.py`; mudança vira `romanos-v2` |
| Marca | `marca.txt` e um comentário no teste escondido | o hash está em `termos_proibidos_hash` (`tests/config.json`): se os testes vazarem para o Forge, o teste `Neutralidade` e o roteiro recusam; se aparecerem no projeto ou na sessão, a linha mostra onde |
| Roteiro | `tests/bancada/versao.py` | valida, estima, roda e grava a linha |
| Linha | `~/.forge-contrib/docs/kanban/bench-versao.md` | uma por rodada, com a fonte de cada medida no cabeçalho |

## Como roda
1. Repositório **público e descartável**, vazio, um por rodada (o roteiro recusa remoto que não está vazio).
2. `python3 tests/bancada/versao.py --tag <tag> --repo <dono>/<repositório>` valida e mostra a cota (nada é chamado).
3. Com `--executar`: a árvore da tag sai por `git archive` em `~/.forge-bench/rodadas/<tag>-<hora>/forge`; o projeto
   nasce em `.../projeto` pelo `forge-init` da tag (stack python, pronto `python3 -m unittest discover -s tests -t .`),
   sem o forge instalado nas configurações (só a árvore da tag carrega, por `--plugin-dir`), e envia `main` e `develop`.
4. Sessão `claude -p --agent forge:jarvis --plugin-dir <árvore> --permission-mode auto` (nunca bypass) com o pedido; a
   que termina sem PR é retomada (`--resume`) com a resposta fixa.
5. Avaliação: os testes escondidos rodam (`python3 -I`) no commit do PR (na `develop`, se integrado; sem PR, no HEAD).

## Limites (E175.1)
20 agentes (`Task`/`Agent`), 3 voltas (retomadas com a resposta fixa), 4 h e 80 M tokens processados; o que passa
encerra a sessão e fica na coluna `Limite`. Uma rodada por vez (trava em `rodadas/.trava`).

## Cota por rodada (E175.1)
Típico ~1,0 M tokens novos e 1h50 (~28 M processados com cache); mínimo ~0,5 M e 45 min; máximo ~2,5 M e 3h30. O dono
confere o `/usage` antes e depois. A carga da máquina vai junto (o time segue trabalhando): o tempo é indicativo, o
resto vale como medida.

## Leitura
Compare versões pelos testes escondidos (qualidade) e pelos tokens novos (custo); minutos só com carga parecida. Uma
rodada é uma amostra: diferença pequena entre duas versões não é tendência.
