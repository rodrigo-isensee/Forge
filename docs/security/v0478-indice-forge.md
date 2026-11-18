---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0478-indice-forge
commit: 35a78d7408bc3940e034e94e3b6983d3adc3e1da
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-18
---
# Review de segurança: v0478 (E8.13, índice do Forge, revalidação)

Revalidação por delta (`R-REVIEW`): `forge-check parecer delta` de `bf97d62a..35a78d74`, sem o que veio da base (`develop`, merge `be429378`). No domínio: `bin/forge-testes`, lido inteiro no diff. Fora do domínio (não relido como controle): `tests/test_indice_forge.py`. As rodadas anteriores (aprovado em `7bd4913e` e em `bf97d62a`, sem achados) ficam no git.

## Gatilhos
Gatilhos: nenhum da lista da R-SEGURANCA; o delta toca `bin/forge-testes` (sensível em `tests/catraca.py`), nenhum caminho protegido.

## Detalhe
Achados anteriores: nenhum. Sem achado novo. O que o delta muda:

- **`bin/forge-testes:183`: só acrescenta teste ao plano.** A entrada do `MAPA` para `scripts/preparar-estacao.sh` ganha `test_ferramentas_portoes` (módulo existe em `tests/`). Não remove módulo, não muda o desvio para a suíte completa nem lê entrada externa; o efeito máximo é rodar um teste a mais. Sem caminho de ataque.
- **`tests/test_indice_forge.py:15-16` (fora do domínio, lido por ser curto):** troca `from tests.ambiente_git` por `sys.path.insert` do próprio `tests/` e `from ambiente_git`, no padrão da suíte; o caminho inserido é fixo (diretório do arquivo), sem entrada externa.
- **Prova executada.** `bin/forge-testes --listar scripts/preparar-estacao.sh`: dirigido, com `test_ferramentas_portoes` no plano. Suíte inteira: no CI do PR (não rodada aqui, por regra).

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Ferramentas: leitura estática do delta e o planejador de testes. Lacuna: varredor de segredos e SAST fora do PATH (não instalados, `R-CUSTO`); o delta não traz credencial, dependência nem configuração.
