---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-aviso-versao-parada
commit: 063a2d567e8500d6fcaa23d1ec4cae15adcb1c98
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: v0478 (aviso de versão parada), revalidação

Etapa E69.10 do pedido v0478. Volta por delta (`R-REVIEW`): a rodada anterior (E69.4, commit `1d47aa8e`, aprovado) fica no git.

## Gatilhos
Gatilhos: hook de controle do Forge (`hooks/doutor.py`), leitura de estado fora do projeto (`~/.claude/plugins`), escrita em `.forge/run/`.

Confirmação: só aperta. O delta `1d47aa8e..063a2d56` não toca código executável nem guarda: em `bin/forge_versoes.py:168` só muda a docstring de `texto_de_versao_parada` (tira o caminho de `docs/propostas/`), e `docs/hooks.md:16` só acrescenta à linha do `doutor` a descrição do aviso de versão parada, fiel ao código (limiar constante de 2 dias, `hooks/doutor.py:41`; um aviso por dia e outro só se a causa mudar, `hooks/doutor.py:260`; estado em `.forge/run/versao-parada` e medida em `.forge/run/versao-parada.log`, `hooks/doutor.py:224` e `:268`). Nenhuma recusa, teto, `O_NOFOLLOW` ou normalização da rodada anterior saiu.

## Revalidação
- Delta lido: `forge-check parecer delta docs/security/v0479-aviso-versao-parada.md`, intervalo `1d47aa8e..063a2d56`; no domínio, `bin/forge_versoes.py` (1 linha de docstring) e `docs/hooks.md` (1 linha da tabela); fora do domínio, `tests/test_doutor.py` (1 linha de comentário, sem mudança de teste).
- Já lido na rodada anterior e sem mudança: `hooks/doutor.py` e o resto de `bin/forge_versoes.py`.
- Achados anteriores: nenhum.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Suíte: a inteira roda no CI; o delta é só texto e não pede teste local, nenhum rodado. Ferramentas: leitura estática do delta.
