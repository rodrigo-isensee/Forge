---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-dir28-sandbox
commit: 4568c9b7276e6aa2edcbb4818e7ef09c08253aeb
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-24
---
# QA: v0478 E151.1 (DIR-28-SANDBOX-NO-JARVIS), PR #847

Escopo: `agents/jarvis.md` (regra da diretriz 28 na linha da diretriz 29), `skills/falar-com-o-dono/nao-trava.md` (detalhe), `tests/fixtures/diretrizes-do-dono.json` (28 de `pendente` para `fabrica`, com trecho), `tests/test_jarvis_nucleo.py` (classe `SandboxNoPrimeiroComando`, `MAX_PENDENTES` 8 para 7). Pedido de texto e teste; sem guarda de controle, sem `forge-mutante`. Sem gatilho de segurança.

## Critério → teste → resultado
Obrigação (E151.1): a diretriz 28 entra em `agents/jarvis.md`, dentro do teto, com teste num módulo existente que lê o agente; neutro.

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Regra no Jarvis, na linha que manda ler o detalhe | `SandboxNoPrimeiroComando.test_o_jarvis_traz_a_regra_na_linha_que_manda_ler_o_detalhe` | regra antes do ponteiro `nao-trava.md` | passou |
| Detalhe (conferir, modo automático, reabrir) na skill | `SandboxNoPrimeiroComando.test_o_detalhe_traz_o_modo_automatico_e_o_comando_de_reabrir` | 4 trechos exatos | passou |
| Diretriz 28 passa de pendente a fábrica | `PresencaDasRegrasEDasDiretrizes.test_cada_diretriz_tem_entrada_e_a_de_fabrica_aparece`, `..._cada_numero_do_arquivo_do_dono_tem_entrada` | trecho da fixture presente no Jarvis | passou |
| Dentro do teto | `OrcamentoDeInstrucao.*`, `NucleoCurtoDoJarvis.test_o_nucleo_ficou_curto...`, `test_orcamento_instrucao` | Jarvis 7883 de 12000 caracteres; núcleo no teto 37511 | passou |
| Teto de pendentes só desce | `MAX_PENDENTES = 7` | 7 pendentes | passou |
| Métricas de texto e clareza | `test_metricas_texto` (2), `test_clareza` (9), `test_skills_v0442` (4) | n/a | passou |

## Vermelho antes do verde
`bin/forge-testes --vermelho e15c8566d4d284909bf2459dedf36c59df5419c8 --modulos test_jarvis_nucleo` (base e15c8566), rc=0:
```
SandboxNoPrimeiroComando.test_o_detalhe_traz_o_modo_automatico_e_o_comando_de_reabrir · H=ok · B=falha · prova (asserção)
SandboxNoPrimeiroComando.test_o_jarvis_traz_a_regra_na_linha_que_manda_ler_o_detalhe · H=ok · B=falha · prova (asserção)
PresencaDasRegrasEDasDiretrizes.test_cada_diretriz_tem_entrada_e_a_de_fabrica_aparece · H=ok · B=falha · prova (asserção)
PresencaDasRegrasEDasDiretrizes.test_cada_numero_do_arquivo_do_dono_tem_entrada · H=ok · B=falha · prova (asserção)
contagem: não prova (passa na base)=41; prova (asserção)=4
```
Rodada sem `--modulos` caía na suíte completa (o mapa não conhece `agents/jarvis.md`); interrompida e restrita ao módulo tocado.

## Mutação à mão (cópia em `$TMPDIR`)
- M1, tirar a frase da regra de `agents/jarvis.md`: 3 testes caem (a nova classe e as 2 de presença). Morreu.
- M2, tirar `--permission-mode auto` da skill: o teste do detalhe cai. Morreu.
- M3, `MAX_PENDENTES` 7 para 8: passa (teto é limite superior; afrouxar é visível no diff e o 7 é o valor atual). Sem achado.

## Cenários e resultado real
- `python3 -I -m unittest discover -s tests -p test_jarvis_nucleo.py`: 45 testes OK.
- `test_orcamento_instrucao` 8 OK; `test_metricas_texto` 2 OK; `test_clareza` 9 OK; `test_skills_v0442` 4 OK.
- Suíte inteira: só no CI do PR (`R-QA`); a citar o check-run `bateria` do mesmo sha. Não rodada localmente.
- Diff conferido contra a obrigação: o commit tocou só os 5 arquivos acima; a linha 1 do passo "Registrar" e a linha das diretrizes 34 e 35 foram encurtadas para caber no teto, sem perder o ponteiro de leitura (testes de invariantes e de skill citada passam). Sem termo de projeto (neutro).
