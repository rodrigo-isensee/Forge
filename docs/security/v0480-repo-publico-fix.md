---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-repo-publico-fix
commit: eebdfef67bdc1a2357ab54e65acd937484853afc
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-24
---
# Review de segurança: v0480-repo-publico-fix (PR #829, 3ª volta E141.15, v0478 E141.17)

Revalidação por delta. `forge-check parecer delta`: intervalo `708c4bb0..eebdfef6`; no domínio, `hooks/conformidade.py` (`CRITICO` :63, `GRAPHQL_SEM_TEXTO` :348, `graphql_publica` :3502 e :3504, relidos com `executar`, `marcado` e `prazo_vencido` de `hooks/_comum.py`, onde o marcador roda sob o vigia), as 14 fixtures novas e `tests/test_hooks.py:3073`; fora do domínio, os mutantes, `docs/hooks-fixtures.md` e o fragmento do changelog. A rodada anterior fica no git (`789a1174`). Método igual: o hook rodado direto com o JSON de PreToolUse num projeto descartável (`.forge/versao`, branch `feature/x`), prazo de produção, `PATH=/usr/bin:/bin`, o gh nunca executado; papéis: um papel de desenvolvimento, `forge:tech-lead` e a sessão principal. Para comparar, a base `216413c9` e o head anterior `708c4bb0` por `git archive`, rodados igual.

**Só aperta ou neutro: sim, contra a base e contra `708c4bb0`.** No conjunto de 31 entradas (S8 a S18, 8 de tempo, 9 legítimas curtas e 3 legítimas longas), toda entrada que a base ou `708c4bb0` barram o head também barra. O head barra a mais: S18 e a string aberta de 40 KB dentro da própria consulta (eram 0 em `708c4bb0`, em 3,2 s), e a continuação de 4000 linhas com a mutação (agora crítica, cai no teto de palavras). O delta só soma recusas: a string sem fechamento e o `query` repetido retornam antes da busca (:3502, :3504), e o marcador novo (:63) só liga recusas. As leituras de `gh api` que passam a recusar (sondas do review, A1 do `tech-lead` no mesmo head) apertam: custo de uso, não de segurança.

**Sondas S8 a S18 refeitas no head:** todas saem 2 com `R-CONFORMIDADE: tornar o repositório público` nos três papéis, S18 em 0,6 a 0,8 s. Legítimas que saem 0 nos três papéis, como em `708c4bb0`: literal `visibility:PRIVATE`, a mutação por variável com `i[visibility]=PRIVATE`, a privada com string escapada (`\"`), consulta com string e escape, `gh repo new novo --private`, REST com `private=true`, `gh issue list`, `gh api repos/dono/proj/pulls`, `gh repo view`.

**Sonda de tempo nas formas que a volta tocou.** O léxico ficou linear: isolado, 100 KB em cada forma adversarial (`"` e `\"`, só `"`, bloco aberto com `\"""`, bloco com `"a`, barras, `"""a"` repetido, blocos abertos) decidem em até 0,06 s. No hook, com a mutação e `i[visibility]=PUBLIC`: string aberta na mesma consulta, 40 KB num campo que não é `query`, bloco aberto de 40 KB e 20000 pares `""` saem 2 em até 0,9 s. O marcador novo (:63) não é linear (A9): sem casar, custa da ordem de (ocorrências de `gh`) × (de `repo` ou `api`) × tamanho da linha; `gh repo ` repetido leva 1,1 s em 2 KB, 8,4 s em 4 KB e 84 s em 8 KB (`708c4bb0`: 0,05 s). Conferi que não abre caminho: o `re` cede ao alarme (interrompido em 1,0 s numa busca de 84 s), o marcador roda sob o vigia, e o prazo vencido com o marcador desconhecido recusa (`prazo_vencido`, `hooks/_comum.py:2853`); a criação pública com lixo à frente casa cedo ou vence o prazo e recusa: 200 KB de `gh repo ` com `--public` saem 2 em 3,3 s. O custo cai sobre o uso: `echo` com `gh api ` 290 vezes, `gh repo ` 300 vezes e um `gh issue create` com corpo de 30 KB citando `repo` a cada 15 caracteres saem 0, mas em 3,2 s em vez de 0,3 s.

**A8 fechado.** S18 sai 2 no prazo de produção; as três correções pedidas estão no código: string sem fechamento falha fechado (:348, :3504), mais de um `query` falha fechado (:3502), as formas de visibilidade no marcador (:63). Fixtures `trava-graphql-s18-prazo-bloqueia`, `-string-aberta-prazo-bloqueia`, `-query-repetida-bloqueia`, as nove `trava-prazo-*-bloqueia` e o controle `-comentario-grande-prazo-libera`.

Suíte: rodados `tests.test_hooks.Hooks.test_fixtures_do_repo_publico` e `test_prazo_do_merge` (as fixtures de prazo de produção): OK, 2 testes, 38 s. CI do PR na leitura (run sobre `67cc41cb`, que só soma o parecer do review): suíte parte 3/5 vermelha nas duas versões por `test_nucleo_sem_termos_de_stack` em `docs/security/v0480-repo-publico-fix.md` (nome de papel de stack no meu parecer anterior; este texto não o cita), `bateria` e `catraca` à espera dos pareceres; as outras partes verdes, uma pendente.

## Gatilhos
Gatilhos: controle de acesso do agente (hook de conformidade), exposição de código e histórico, ação irreversível no GitHub.

## Achados
- A9 (recomendado) hooks/conformidade.py:63 · O marcador novo tem custo cúbico sem casar (`gh repo ` repetido: 1,1 s em 2 KB, 84 s em 8 KB); falha fechado pelo vigia, sem caminho de ataque, mas atrasa até o prazo linhas legítimas longas que citam `gh` e `repo` ou `api`.

## Detalhe dos achados
**Estado dos anteriores.** A1, A2, A3, A6, A7: seguem fechados (S8 a S12, S16, S17 e os endpoints não canônicos saem 2). A4: S13 a S15 saem 2; reaberta só pela A8, agora fechada. A5: como antes (GraphQL fechado; REST fora com razão). A8: fechado (acima). Cartões C1 a C3 da rodada anterior seguem cartões.

**A9: custo do marcador crítico.** Evidência: `hooks/conformidade.py:63`, três `(?:[^\n]|\\\n)*` em sequência atrás de `\bgh\b` e de `repo\b`/`api\b`; medidas isoladas e no hook (acima). Caminho de ataque: nenhum; o prazo vencido com marcador desconhecido recusa, então o pior caso é recusa ou espera de 3 s numa linha legítima longa. Severidade baixa. Correção mínima: busca linear, por exemplo a checagem em dois passos no código (`gh` na linha, depois as rotas) ou grupo atômico ou possessivo, se a versão mínima suportada do interpretador o tiver, com uma fixture de tempo de `gh repo ` repetido em 4 KB decidindo abaixo de metade do prazo. Pode vir junto da correção da A1 do review: o estreitamento que o `tech-lead` sugere serve à segurança desde que o marcador do prazo (no `CRITICO` ou só em `MarcadorDaPolitica.marca`, :4400) siga cobrindo todas as formas que decidem a visibilidade: `gh repo create`, `gh repo new`, `gh repo edit` (já crítico pelo `edit`), `gh api` com `graphql` (ao menos com `mutation`, `createRepository`, `cloneTemplateRepository` ou `updateRepository` na linha, e com a consulta fora da linha: `-F query=@arq`, `--input`), `user/repos`, `orgs/<o>/repos`, `repos/<o>/<r>/generate` e `repos/<o>/<r>` com PATCH ou PUT; e S18 siga saindo 2 sob o prazo de produção. Esforço P. Dono: o autor do E141.15. Pelo brief (última volta do item), vira cartão.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: o hook rodado localmente com projeto descartável; a base e o head anterior por `git archive`; as expressões medidas isoladas e o alarme do vigia reproduzido fora do hook; o gh fora do PATH das sondas e nunca executado. gitleaks, semgrep e zizmor não foram usados (não se aplicam a este diff).
