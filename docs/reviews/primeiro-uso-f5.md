---
tipo: review
contrato: 1
pedido: primeiro-uso-f5
branch: melhoria/primeiro-uso-f5
commit: d591c60
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-14
---
# Parecer de autor: primeiro uso F5 (atualização segura com ponto de retorno)

Autor e revisor são o mesmo papel aqui: este parecer é de autor e não substitui a review independente do PR.

## O que foi conferido
- **Fixação de versão:** `claude plugin marketplace add --help` não documenta ref. Teste local: `https://<host>/<repo>.git#v1.0.0` é aceito como fonte (a CLI tenta clonar sem o fragmento; a falha é só de rede no sandbox) e caminho local com `#` é recusado. O checkout da tag não pôde ser observado sem rede, então a troca é `remove` + `add <endereço>#vX.Y.Z` + `update`/`install`, com devolução ao endereço anterior se falhar; a versão nova é descoberta pelas tags (`git ls-remote`), não pela marketplace. Pendência: confirmar o checkout da tag na primeira atualização real.
- **Defesas da consulta** (`bin/forge_versoes.py`): só https sem usuário, `GIT_ALLOW_PROTOCOL=https`, `protocol.allow=never`, cwd vazio e neutro, sem senha, sem configuração do git do usuário. Local só com `FORGE_PERMITE_LOCAL=1` (testes). Testado com um `git` falso que registra cwd, protocolo e argumentos.
- **Segurança do usuário:** exige terminal; `forge-upgrade --simular` roda da cópia da tag antes de qualquer mudança; plugin só troca depois da simulação; falha na troca devolve o plugin e descarta o ponto; nenhum `reset`, `--force`, `branch -D` nem `rm` no projeto (teste por texto). `voltar-versao` não apaga branch nem arquivo novo (só lista).
- **Testes:** 28 novos (`tests/test_atualizar.py`), escritos antes (20 falhas e 4 erros sem a mudança): caminho feliz, recusa, sem terminal, em dia, sem rede, árvore suja, simulação que falha, doutor que falha (voltar e não voltar), troca do plugin que falha, voltar (não mesclada, mesclada, sem ponto, recusa, duas vezes), defesas, aviso do doutor. Suíte completa 431 verde, `validar-plugin.sh` ok.

## Riscos e pendências
- Altera `hooks/doutor.py` (consulta de rede no Stop, 3 s, cache diário): o PR precisa do rótulo `afrouxa-regra` do dono. `hooks.json` não mudou.
- Doutor com problema antigo e sem relação oferece voltar depois da atualização (a mensagem avisa que pode não ter relação).
- `forge-check` e os demais hooks intocados.
