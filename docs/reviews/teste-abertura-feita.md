---
tipo: review
contrato: 1
pedido: teste-abertura-feita
branch: melhoria/teste-abertura-feita
commit: da445ba433c3d9548d834e72d40ee6073b2c4714
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-15
---
# Parecer: `ambiente_limpo()` sem as variáveis `FORGE_*` (cartão jarvisforge-abrir-falhas)

Escopo: `develop..da445ba`, um arquivo de teste e o CHANGELOG. Sem mudança em código de produção.

## Garantido por ferramenta
- `python3 -m unittest discover -s tests` com `FORGE_ABERTURA_FEITA=1` exportada: `Ran 561 tests`, `OK`.

## Por leitura
- Nenhum teste dependia de herdar `FORGE_*`: `test_atualizar.py`, `test_doutor.py` e `test_sugerir.py` montam o próprio ambiente a partir de `os.environ` (sem `ambiente_limpo`) e definem `FORGE_HOJE`, `FORGE_REPO_URL` etc. de propósito. `test_hooks.py` usa `ambiente_limpo()` e depois define `FORGE_PROC` (e já removia `FORGE_GUARDA_ABERTA`), então a ordem (limpar, depois definir) está correta. Os testes de `test_forge.py` que chamam `ambiente_limpo()` não definem `FORGE_*`.
- Não esconde bug: a variável é estado de sessão externo ao que os testes verificam; os 7 testes de `JarvisForgeAbrir` passam a controlar a entrada. Se algum deles precisar de `FORGE_ABERTURA_FEITA`, define de propósito.
- CHANGELOG: entrada em `### Corrigido` de `[Não publicado]`, descreve causa e escopo ("só testes"). Adequada.

## Observação (não bloqueia)
- `test_sugerir.py:53` e `test_atualizar.py` filtram o ambiente por conta própria; hoje coerentes. Um filtro único compartilhado seria melhoria futura.

Sem achado de segurança, pipeline ou contêiner.
