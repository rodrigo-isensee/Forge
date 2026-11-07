---
tipo: qa
contrato: 1
pedido: versao-035
branch: melhoria/push-parecer-ja-no-remoto
commit: 2bc09a2b690a3c41cd1adb40b3285c9d8cd13b9d
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-06
---
# QA: versao-035 (E3, PUSH-PARECER-JA-NO-REMOTO)

## Achados
- A1 (recomendado) .githooks/pre-push:197 · url.insteadOf encadeado com pushInsteadOf desvia a consulta do ls-remote (A3 do review, A1 da segurança); falhar fechado se `ls-remote --get-url -- "$2"` diferir de $2, ou registrar residual no PR
- A2 (recomendado) .githooks/pre-push:191 · 8 guardas de defesa em profundidade (191, 192, 195 cntrl, 196, 199, 201 cat-file, 197 rc, 190 modo_suite) não têm teste que as isole: mutantes Q2, Q3, Q4, Q6, Q8, Q10, Q12 e Q15 sobrevivem, equivalentes hoje

## Critério → teste → resultado
Critérios: decisão do dono de 2026-11-05 15:20 e C-1 a C-11 do modelo de ameaças (sem CA-n em EARS neste pedido).
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Pula quando o remoto já tem o commit (igual, ou descendente) | test_pula_so_com_prova_positiva_no_destino: igual, ancestral, duas refs | ref igual / local ancestral | passou |
| Na dúvida roda a suíte (C-1): erro, timeout 20 s, credencial, destino inexistente | mesmo teste: inexistente, `-x`, pede credencial, lento (<24 s) | falha fechada | passou |
| Só branch já existente, tudo ou nada (C-3, C-4, C-6) | sha não ancestral, cauda, ref nova, objeto ausente, enviada+nova, +tag, +remoção | ref nova, tag, remoção, misto | passou |
| Destino real é $2 (A1 do review) | "pushurl sem o commit, url com ele" | url ≠ pushurl | passou |
| Recusas antes e sem consulta (C-5, T-5, T-6) | main, homolog, develop, não fast-forward, stdin vazio, `--suite`, `--status` | recusas intactas | passou |
| Pulo não pega trava nem anota prova (C-8) | mesmo teste: pasta de trava vazia após cada pulo | nenhuma prova nova | passou |
| Nenhuma variável liga o pulo (C-10) | mesmo teste: FORGE_* no ambiente e leitura estática | ambiente | passou |
| Segunda consulta depois da vez; solta fila e trava (C-7) | test_destino_ganha_a_ref_durante_a_espera_pula_e_solta_fila_e_trava | remoto que ganha a ref na fila | passou |

## Cenários e resultado real
- Suíte inteira de 2bc09a2: `/tmp/suite-e3-2bc09a2.log`: "Ran 2615 tests in 1564.306s (2 processos)", "OK (skipped=32)", `suite_rc=0 16:35:26` (rodada pelo hook, fora do QA, D-5).
- Módulo do E3 no head, load1 abaixo de 1: 2 testes OK.
- Vermelho (`forge-testes --vermelho d9b26bb`, árvore limpa, só o teste do E3 mantido): `test_destino_ganha_a_ref_durante_a_espera...` H=ok B=falha, "prova (asserção)". `test_pula_so_com_prova_positiva_no_destino` H=ok B=erro, que a ferramenta classifica "sem veredito" (rc 2; o restrito `--modulos test_pre_push_ja_no_remoto` dá o mesmo). Causa lida numa cópia da base: os subcasos "igual", "ancestral" e "duas refs" falham por asserção `(1, False, False) != (0, True, True)` (a suíte roda) e o erro é o `IndexError` da leitura estática de `ja_no_remoto`, função que a base não tem. O teste cai na base pelos motivos certos; o rc 2 vem de a ferramenta contar o erro final.
- Na rodada ampla do vermelho (suíte completa, pois `.githooks/pre-push` não tem mapa): `test_fechar_sinal.test_l5_int_e_hup...` H=erro e B=erro e `test_hooks` sem veredito (prazo). Nenhum é tocado pela branch (`git diff d9b26bb...HEAD` não os lista); o l5 passa isolado no head (OK, 0,5 s) e os dois passaram na suíte inteira de 2bc09a2. Ruído da rodada sob carga, não regressão.
- Mutação (`bin/forge-mutante` sobre 16 mutantes meus, um por linha de guarda mudada do hook, spec em scratchpad, rev 2bc09a2b690a): morreram Q1 (190 tudo-ou-nada), Q5 (195 tag), Q7 (198 nome inteiro), Q9 (201 ancestral), Q11 (197 timeout), Q13 (296 segunda consulta), Q14 (207 destino $2), Q16 (294 ordem da fila). Sobreviveram, rc 1: Q2 (191), Q3 (192), Q4 (195), Q6 (196), Q8 (199), Q10 (201), Q12 (197), Q15 (190).
- Justificativa dos sobreviventes, aceita como mutante equivalente (cada guarda é redundante com outra que o teste prova): Q2 vetor de mesmo tamanho (os dois vetores crescem na mesma linha do laço); Q3 destino `-x`: o `--` do ls-remote já o trata como repositório inexistente e o subcaso "destino que parece opção" roda a suíte com e sem a guarda; Q4 ref com cntrl: o ls-remote não devolve a linha e o sha vazio falha em `sha_valido`; Q6 e Q8 sha vindo do git ou do ls-remote já é hexadecimal; Q10 `merge-base --is-ancestor` com objeto ausente já falha; Q12 saída vazia já falha em `sha_valido`; Q15 no `--suite` o stdin é /dev/null, `n_envios` é 0 e a guarda `-gt 0` já devolve 1. Nenhuma abre o pulo sem prova positiva hoje; viram A2 (recomendado), não devolvem.
- Conferência da lista contra o diff: linhas de guarda mudadas 190, 191, 192, 195, 196, 197, 198, 199, 201, 207, 296 e a ordem do 294 têm mutante; a linha 135 só acumula o vetor.
- Fora do ambiente: `shellcheck` ausente (registrado pelo review e pela segurança).

## Parecer
Aprovado sobre 2bc09a2. Lido: E3 do pedido e decisões do dono, E3 do desenho, o diff `d9b26bb...2bc09a2`, os pareceres de review e segurança. Os comportamentos do afrouxamento autorizado (pula só com prova positiva no destino real, depois das recusas, sem anotar prova; na dúvida roda a suíte) têm teste que cai na base e passa no head, a suíte inteira está verde e os mutantes que mudam comportamento morreram. Os 8 sobreviventes são equivalentes justificados; A1 e A2 são recomendações que não devolvem. O rótulo `afrouxa-regra` e o residual do A10/A1 vão no corpo do PR.
