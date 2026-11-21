---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-k152-prepush-sem-deps
commit: ce1d79bd030ae0c1d33b4443d91bd311ad043155
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-21
---
# QA: K152, cópia nova sem dependências no pre-push (v0478 E81.4)

O patch do `pre-push.local` do modelo é proposta (`docs/propostas/k152-pre-push.md`): testei-o numa cópia temporária, sem gravar em `.githooks`.

## Achados
- A1 (bloqueante) docs/propostas/k152-pre-push.md:47 · `trechos//||/;` e `trechos//|/;` (guardas mudadas) sem mutante e sem teste: apagadas, 8 testes seguem verdes. Programa após `||` ou `|` nunca é checado. Declare 2 mutantes e teste com `a || b` e `a | b`.
- A2 (recomendado) tests/test_prepush_k152.py:177 · `EnvioDaCopiaNova` faz skipTest se ruff/mypy estiverem no PATH da máquina: o ambiente decide o que testa; falta fixar o PATH do envio num diretório sem as ferramentas.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Comando de instalar gravado por stack | `test_cada_stack_grava_o_comando_do_instalar_json` | stack sem instalar.json | passou |
| Sem `instalar.json`, mensagem genérica | `test_stack_sem_instalar_json_...` | vazio | passou |
| Aspa simples no comando vira vazio | `test_comando_com_aspa_simples_fica_vazio` | caractere especial | passou |
| Nada instalado barra sem rodar o pronto | `test_sem_nenhuma_ferramenta_...` | todas faltando | passou |
| Falta uma só: nomeia só ela | `test_falta_so_uma_...` | uma faltando | passou |
| Tudo instalado: pronto roda | `test_com_as_ferramentas_...` | tudo presente | passou |
| Pronto reprovado lembra o comando | `test_pronto_reprovado_...` | rc 1 do pronto | passou |
| Ponta a ponta (worktree + push) | `EnvioDaCopiaNova` | PATH mínimo | passou |
| Separadores `\|\|`, `\|`, `;` do pronto rápido | nenhum | n/a | sem teste (A1) |

## Cenários e resultado real
- Testes: `test_prepush_k152` 8 de 8 verdes; `test_forge.PreEnvioDoModelo` 18 de 18 verdes (TMPDIR, sem suíte).
- Vermelho antes do verde (`forge-testes --vermelho adc52def... --modulos test_prepush_k152,test_reval_delta`): os 8 testes do K152 `H=ok · B=erro · prova (API ausente)`; `test_reval_delta...test_caminho_de_texto_so_e_citado_como_a_lista_conhece` `B=falha · prova (asserção)`; contagem: não prova (passa na base)=9; prova (API ausente)=8; prova (asserção)=1.
- Sonda antes (modelo sem patch, `env -i`, PATH `/usr/bin:/bin`): `bash: line 1: ruff: command not found` e "o pronto rápido reprovou (ou falta a ferramenta no PATH)", rc=1. Depois (patch aplicado numa cópia): `falta no PATH: ruff mypy (cópia nova, sem as dependências instaladas?)...` com o comando `python3 -m venv .venv && ... pip install ...`, rc=1. Confere a proposta.
- Mutantes (`bin/forge-mutante tests/mutantes/v0479-k152-prepush-sem-deps.json`, rev=ce1d79bd030a): M1..M8 `morreu`. `--cobertura --base adc52def...`: `não coberto: bin/forge-init` (shell) e `tests/pesos-d4.json`. Mutantes meus fora da spec, em cópia: remover `trechos//||/;` e remover `trechos//|/;` sobreviveram (8 testes OK nos dois).
- Merge do remoto (pareceres de review e segurança) trazido antes do parecer; código intacto.
