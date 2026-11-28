---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-k152-prepush-sem-deps
commit: ef43fe5a10e4fd15f8f6d9c7f224f9af7339fb0b
parecer: aprovado
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
- A2 (recomendado) tests/test_prepush_k152.py:169 · `EnvioDaCopiaNova` faz skipTest se ruff/mypy estiverem no PATH da máquina: o ambiente decide o que testa; falta fixar o PATH do envio num diretório sem as ferramentas.

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

## Revalidação no head ef43fe5a (v0478 E81.6)
A1 fechou: os testes `test_programa_depois_de_ou_logico_tambem_e_checado` e `test_programa_depois_de_pipe_tambem_e_checado` cobrem as guardas de `||` e `|`; sem a guarda caem (mutantes mortos). `tests/test_prepush_k152.py`: 10 testes, OK. A2 segue aberto como recomendado (`skipTest` na linha 193).
```
forge-mutante: pedido=v0479-k152-prepush-sem-deps rev=ef43fe5a10e4 spec=75a750539f47b86c92e6c2c9c5e33a8f2eeef38f0dd7b884cd28c306ac046bf4
M9 · morreu · docs/propostas/k152-pre-push.md:47
M10 · morreu · docs/propostas/k152-pre-push.md:47
```
