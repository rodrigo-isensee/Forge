---
tipo: qa
contrato: 1
pedido: primeiro-uso-f6
branch: melhoria/primeiro-uso-f6
commit: e0d6d1c
parecer: aprovado
revisor: forge:qa-engineer
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 2
aceite_usuario: sim
data: 2026-10-14
---

# QA - primeiro uso do Forge, entrega F6 (`forge sugerir`, PR #112)

Testado no HEAD e0d6d1c (PR #112), em worktree temporária. Sem o `gh` real: PATH com links para as ferramentas do sistema e um `gh` falso (grava os argumentos e o corpo recebido; com `GH_FAIL=1` simula falta de rede). HOME, XDG e git temporários; nada tocou o GitHub. Projeto fictício `Acme-Pagamentos` (remoto `acmecorp/Acme-Pagamentos`, `.forge/novo-projeto.json`, `CLAUDE.md` com cliente "Banco Zeta" e servidor `db01.acme.local`). A linha de sandbox sobre `api.anthropic.com` na saída é do ambiente. Fontes: F6 em `docs/propostas/primeiro-uso/arquitetura.md`, P1 = A em `decisoes.md`, vereditos de `docs/reviews/primeiro-uso-f6.md` (4 reviews, a quarta aprova).

## Resultado da suíte
`python3 -m unittest discover -s tests`, com `CLAUDECODE` removida e PATH sem o `gh` real: **496 testes, OK**. Na primeira tentativa, com um PATH mínimo demais (sem as demais ferramentas do sistema), 30 testes falharam por ferramenta ausente, nenhum de `sugerir`; com o PATH completo (menos o `gh`), tudo passa. Não houve teste pulado nem instável.

## Matriz
| Critério (F6 / P1) | Teste | Resultado |
|---|---|---|
| Problema vira sugestão sem dados do projeto | E1 texto realista | passou: caminho Unix e Windows, e-mail, token `ghp_`, `API_KEY=sk-`, `senha:`, URLs e IP, host `.local`, nome do projeto em 3 grafias (hífen, espaço, `_`, camelCase) e usuário saíram; só a URL do próprio Forge ficou |
| Pessoa vê o texto exato e confirma | E2 | passou: o corpo recebido pelo `gh` (+ rodapé) está contido, igual, no texto mostrado; título igual ao mostrado |
| Aviso de que aparece com o nome de usuário do GitHub | E1 | passou: aviso antes do texto, em português |
| Recusa vai para a fila | E1 (`n`) | passou: saída 0, `gh` não chamado, arquivo 600 em pasta 700 |
| Sem rede vai para a fila | E3 | passou: saída 1, texto guardado, mensagem diz como reenviar |
| `--fila` no terminal envia | E2 (`CLAUDECODE` removida, pty, `s`) | passou: issue criada pelo `gh` falso, arquivo removido da fila |
| Dentro do Claude o envio é recusado | E4, E4b, E4c | passou: `--fila` sai 2, mesmo com pty e "s"; texto solto com pty e "s" só guarda; `gh` nunca chamado |
| `--guardar` grava com 600, sem enviar nem perguntar | E4d | passou: 600, texto anonimizado, saída 0 |
| `--guardar` só como primeiro argumento | E4e | passou (não envia), com mensagem ruim: bug F6-02 |
| Sem terminal guarda na fila | E5 | passou: guarda, saída 0 |
| Entradas inválidas (vazio, opção desconhecida, arquivo ausente, `--fila` com texto) | E6, E4f | passou: saída 2, mensagem em português |
| Mensagens em português claro | todas | passou, com um trecho em inglês: bug F6-01 |

## Exploratórios
1. Recusa: `n` no pty. Nada enviado, fila com 600/700.
2. `--fila` com `s`: enviou; diferença mostrado x enviado: nenhuma; varredura do corpo por `Acme`, `maria`, `hunter2`, `ghp_`, `sk-`, `wiki`, `10.0.0`, `db01` e `C:\`: nada.
3. `gh` falho: `Não consegui enviar (error connecting to api.github.com). Guardei em ...`, saída 1 (bug F6-01).
4. Dentro do Claude: itens 4 a 4f da matriz.

## Limites conhecidos (não são bugs deste parecer)
- **Nome de cliente em texto livre não é removido** ("Banco Zeta" ficou no texto e no título). Não há como o script saber; o aviso mostra isso e pede conferência antes do "s", como a P1 prevê.
- Recomendações abertas da review final: palavra do subcomando montada por variável ou ofuscação escapa do hook `conformidade` (a variável `CLAUDECODE` é a segunda camada e cai com `env -i`); `bin/forge-sugerir` relativo liberado pela lista branca; heurísticas de segredo (dupla codificação de URL, `key=`/`pass=` soltos). Não testadas de novo aqui; seguem como risco aceito pela review.

## Bugs
| ID | Severidade | Resumo |
|---|---|---|
| F6-01 | baixa | motivo da falha de envio sai em inglês (`docs/qa/bugs/F6-01-motivo-da-falha-de-envio-em-ingles.md`) |
| F6-02 | baixa | `--guardar` fora da primeira posição diz "opção desconhecida" (`docs/qa/bugs/F6-02-guardar-fora-da-primeira-posicao-diz-opcao-desconhecida.md`) |

## Parecer
**Aprovado.** Nenhum bug crítico, alto ou médio. Dois baixos abertos (texto de mensagem) exigem o aceite do usuário. As garantias centrais valem nos testes: nenhum dado do projeto vazou no corpo enviado, nada é enviado sem o "s" da pessoa, e dentro do Claude só se guarda na fila.
