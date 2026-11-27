---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-rotulo-pelo-time
commit: ab5871d1dedead9ff0021f4063b629794f6f9f00
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-26
---
# QA: v0481 ROTULO-PELO-TIME (#918, E24.3; 1ª rodada completa no ab5871d1)

Diff lido contra o merge-base com a `develop` (3c833f3f): `bin/forge_autorizacao.py`, emenda ROTULO-PELO-TIME da ADR 0018, changelog, `tests/test_autorizacao.py`, `tests/test_autorizacao_gravar.py` e as cinco specs de mutantes. O plano nasce da ordem do dono de 26/11 12:57 e das decisões R1 a R3 da emenda (não há UX nem API). Não escrevi teste novo: conferi o que os do autor provam.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| R1 ato `rotulo-pelo-time` sem prazo: alvo `fixo`, validade `fixa`, nunca vence, retirada o para | `RotuloPeloTime.test_ativo_so_com_o_origin_do_forge_e_sem_vencer`, `test_so_com_alvo_fixo_e_validade_fixa`; M1, M2 | alvo `pr:5`, uso único e prazo no ato novo (adulterada); 2036 sem vencer | passou |
| R1 termo `homologacao`; frase "autorizo o time ate a homologacao, fixo" nasce ativa; `rotulo` junto nasce pendente ("mais de um ato") | `test_autorizacao_gravar.AtosFixos.test_rotulo_pelo_time_grava_fixa_e_so_ativa_no_repositorio_do_forge`; M7 | duas palavras de ato; vocabulário fixo só com `homologacao` | passou |
| R1 `forge-check autorizacao ler --ato rotulo-pelo-time`: rc 0 com a ativa, rc 1 sem ela | `RotuloPeloTime.test_ler_ato_diz_a_ativa_e_sem_ela_rc_1`; M8, M9 | origin de outro repositório dá rc 1 e a saída exata | passou |
| R2 inativa fora do Forge: sem git/origin, origin outro, raiz com `.forge/versao` (mesmo com o origin do Forge) | `test_outro_origin_ou_projeto_deixa_inativo`, `test_ativo_so_com_o_origin_do_forge_e_sem_vencer`; M3 a M6 | origin `...-site`, projeto com origin do Forge, sem origin; maiúsculas e `.git` final valem | passou |
| R2 o manifesto que decide é o do plugin que lê, não o da raiz; manifesto ausente, não-objeto ou JSON quebrado: inativa | `test_plugin_sem_repositorio_nao_faz_o_forge` (3 subcasos); M10 | falha fechada | passou |
| Nenhum hook nem a catraca consome o ato (R3 vem no 2º PR) | `grep -rn "rotulo-pelo-time\|SO_NO_FORGE" bin hooks .githooks tests/catraca.py`: só `bin/forge_autorizacao.py` o cita | n/a | passou |
| Os outros atos não mudam (`corte-diario`, `so-aperta-com-seguranca`, `rotulo-afrouxa-regra`, `merge-main`) | testes antigos de `AtosFixos`, `Ler`, `ItemPresoAoCommit` verdes; `corte-diario` ativo no projeto com origin do Forge | n/a | passou |
| Specs antigas com o trecho de ajustado | `v0481-autorizacoes-fixas`, `-2`, `-3`: os `de` seguem o código novo (`SEM_PRAZO`, `== ato`); os 22 mutantes morrem | n/a | passou |

## Cenários e resultado real
- Módulos tocados: `bin/forge-testes --vermelho` rodou os dois módulos (63 testes avaliados) e o veredito foi saída 0. A suíte inteira ficou com o CI (G3).
- Vermelho antes do verde, colado:
```
vermelho: base=3c833f3f1ba1 head=ab5871d1dede módulos=test_autorizacao,test_autorizacao_gravar (restrito por --modulos)
revertidos à base: bin/forge_autorizacao.py, changelog.d/v0481-rotulo-pelo-time.md, docs/adr/0018-autorizacao-do-dono-gravada.md
tests.test_autorizacao.RotuloPeloTime.test_ativo_so_com_o_origin_do_forge_e_sem_vencer · H=ok · B=falha · prova (asserção)
tests.test_autorizacao.RotuloPeloTime.test_ler_ato_diz_a_ativa_e_sem_ela_rc_1 · H=ok · B=falha · prova (asserção)
tests.test_autorizacao.RotuloPeloTime.test_outro_origin_ou_projeto_deixa_inativo · H=ok · B=falha · prova (asserção)
tests.test_autorizacao.RotuloPeloTime.test_plugin_sem_repositorio_nao_faz_o_forge · H=ok · B=falha · prova (asserção)
tests.test_autorizacao.RotuloPeloTime.test_so_com_alvo_fixo_e_validade_fixa · H=ok · B=ok · não prova (passa na base)
tests.test_autorizacao_gravar.AtosFixos.test_rotulo_pelo_time_grava_fixa_e_so_ativa_no_repositorio_do_forge · H=ok · B=falha · prova (asserção)
contagem: não prova (passa na base)=58; prova (asserção)=5
```
`test_so_com_alvo_fixo_e_validade_fixa` passa na base de propósito: na base o ato novo cai em "Ato fora da lista" e já lê `adulterada`; o teste guarda que o limite continua assim depois da mudança (a fronteira do uso único, do alvo `pr:` e da validade com data).
- Mutantes: `bin/forge-mutante tests/mutantes/v0481-rotulo-pelo-time.json tests/mutantes/v0481-rotulo-pelo-time-2.json --processos 2`, saída 0, M1 a M10 todos `morreu` (M10 por erro do teste declarado sob o mutante, que passa sem ele, forma aceita pela regra). Specs antigas (`v0481-autorizacoes-fixas.json`, `-2`, `-3`, 22 mutantes): todos `morreu`.
- Lista contra o diff: `bin/forge-mutante --cobertura --base 3c833f3f` dá `coberta` para cada linha de guarda nova (242, 243, 245, 283, 284, 369, 473, 483, mais as linhas 123, 151, que a lista antiga cobre) e só avisa `spec editada` nas três specs antigas, que é a edição pedida. Nenhuma linha sem mutante.
- Sonda de segurança do limite (arquivo `sonda_slug.py`, rodado com `python3 -I`): `slug()` reduz a `dono/repo` as URLs https, ssh, com credencial, com `.git` e com barra final. Descoberta: a parte antes de `github.com` é descartada por `^.*`, então `https://evil.example/github.com/rodrigo-isensee/Forge` e um caminho local `/x/github.com/rodrigo-isensee/Forge` valem como o Forge (`https://github.com.evil.example/...` não vale).
- ci: ver a linha final.

## Para a segurança (limite ao repositório do Forge; o parecer de segurança é do `security-engineer`)
Do ponto de vista de teste, o limite se sustenta nos casos cobertos: um projeto com `.forge/versao` nunca é o Forge, mesmo com o origin dele; outro origin, ausência de origin e manifesto ilegível dão inativa (falha fechada); o manifesto da raiz não decide. O que o teste não cobre e a sonda mostrou: a conferência é sobre o texto do `remote.origin.url` da raiz, que é configuração local, e o `slug` não confere o host. Quem consegue escrever o `.git/config` de uma raiz sem `.forge/versao` a faz passar por Forge; ainda assim a concessão só nasce de mensagem do dono lida na transcrição pelo `forge-check autorizacao gravar`, e nenhum hook consome o ato neste PR. O risco cresce no 2º PR, quando o consumo existir: é quando o host deve ser exigido (A1).

## Achados
- A1 (recomendado) bin/forge_autorizacao.py:231 · `slug` descarta tudo antes de `github.com`: `https://evil.example/github.com/<dono>/<repo>` vale como o Forge. Exigir o host `github.com` (ou `ssh://`/`git@`) no início da URL, com teste; virar cartão antes do 2º PR, que passa a consumir o ato.

## Resultado
Aprovado no head ab5871d1: R1 e R2 cobertos, vermelho visto (5 testes provam; 1 guarda), 10 mutantes novos e 22 antigos mortos, módulos tocados verdes, nenhum hook consome o ato. Sem bug aberto; um achado recomendado.
- ci: ab5871d1dedead9ff0021f4063b629794f6f9f00 verde
- Leitura do CI (`gh pr checks 918`, run 45857943188, head conferido igual ao `Revisar-sha`): verdes a suíte 3.12 e 3.14 (partes 1 a 5), teto de pulados 3.14, `bateria (passos)`, `bateria (python 3.14)`, `bateria (verificações longas)`, instalação 3.14, árvore já provada e `catraca`. Vermelhos: `bateria (pareceres)` e `bateria`, os dois que esperam os pareceres (o brief os exclui); não consegui ler o log deles (o `gh run view --log` falhou: `/root/.cache/gh` é só leitura no sandbox), a causa é a dita pelo brief, inferida. A suíte 3.12 parte 1/5 estava `pending` na primeira leitura e fechou `pass` (6m59s) na seguinte.
