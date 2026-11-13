---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/release-0.47.0
commit: 72bb40084ec4b32d979dbbd8ba7379934aa5d055
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-13
---
# Review de segurança: release 0.47.0, delta da marca até 72bb4008 (E2.11)

branch: melhoria/release-0.47.0 · head revisado: 72bb40084ec4b32d979dbbd8ba7379934aa5d055

Escopo: delta `51c51139..72bb4008` (13 arquivos, +521/-16): a junção do PR 540 (testes de tempo pela carga da máquina), a linha do CHANGELOG, o placar regravado (`mortos=62 invalido=1`, com nota do M10) e os pareceres. Substitui, no head atual, o parecer da marca (51c51139), que continua válido para o que ele cobriu.

## Gatilhos
`R-SEGURANCA`: a release publica a versão dos projetos e o delta toca testes de guarda de hook de conformidade (limite de CPU do corpus e prazo do `gh` pendurado).

## Achados
- A1 (recomendado) tests/test_hooks.py:1011 · com carga 2x, o teto do teste do gh pendurado sobe a (limite-1)*2 e passa do prazo do hook; ainda pega o `sleep 30`, mas não atraso intermediário. Já registrado no parecer v047-teste-carga (A1); sem caminho de ataque, não bloqueia.
- A2 (recomendado) tests/apoio_volta_unica.py:43 · a carga vem de `os.getloadavg` do hospedeiro e os núcleos da afinidade; em contêiner com quota ele pode ficar sempre em 2x. O efeito é limitado ao teto de 2x. Já registrado no parecer v047-teste-carga (A2).

## Sondas

## Detalhe dos achados
Verificações estáticas e locais no head:
- Nenhum arquivo de `.github/`, `hooks/`, `bin/`, `scripts/`, `agents/`, `skills/` nem dependência muda no delta; só testes, docs e o CHANGELOG. Os `plugin.json` (raiz e `dev/`) não mudam desde a marca e seguem em 0.47.0, JSON válido.
- Afrouxamento: o teto do fator de carga é fixo em 2 (`tests/apoio_volta_unica.py:36`), carga ilegível dá 1 (`:44-45`) e `FORGE_NPROC` não entra na conta; defeito acima do dobro do limite continua falhando (teste `test_limite_do_corpus_escala_e_regressao_de_mais_do_dobro_ainda_falha`). O limite é lido antes do lote (`tests/test_hooks_volta_corpus.py:122`). Nenhuma guarda de produção é afrouxada; o `sleep 30` do teste do gh pendurado segue além do teto.
- Placar: `docs/engineering/placar-mutacao.md` só troca a linha e acrescenta a nota do M10; o A1 do parecer da marca (rc=2 por carga) foi tratado pela regravação.
- Varredura do diff por padrões de segredo (ghp_, AKIA, chave privada, password) e caminhos pessoais: sem ocorrência.
- Teste afetado rodado aqui: `python3 -m unittest test_medida_cpu` (12 testes, OK). A suíte inteira roda no CI do PR da release.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Lacuna: `gitleaks` ausente do PATH, substituído pela leitura do diff. Sem PR aberto para a release neste momento.
