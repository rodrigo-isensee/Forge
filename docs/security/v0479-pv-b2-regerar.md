---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-pv-b2-regerar
commit: c5815650ef8c81b24ca7d466b7a23f04239458b6
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: v0479-pv-b2-regerar (PR-VERDE B2, v0478 E57.45)

Primeira rodada. Lido o diff `ed5bfa02..c5815650`: no domínio, `bin/forge-testes` (`--regerar`: `link_no_caminho`, `fotografia`, `regerar`, validação de opções); fora do domínio, só lidos por alto: `tests/test_testes_tocados.py` (classe `Regerar`), `tests/mutantes/v0479-pv-b2-regerar*.json`, `changelog.d/v0479-pv-b2-regerar.md`. Riscos do desenho (`docs/propostas/v0479-pr-verde-de-primeira.md:66`): escrita fora da lista fechada, seguir link, regerar arquivo de controle.

## Gatilhos
Gatilhos: ferramenta do envio do Forge (`bin/forge-testes`), execução de geradores por subprocesso, escrita em arquivo versionado.

## Conferência dos riscos do desenho
- Lista fechada: `DERIVADOS` em `bin/forge-testes:987` (índice do Forge e `tests/pesos-d4.json`); o que mudou fora dela no `git status` sai 2 (`:1030`). `tests/config.json` e `docs/regras/` são versionados, logo cobertos. Teste: `Regerar.test_escrita_fora_da_lista_fechada_sai_2`, `test_lista_fechada_sem_arquivo_de_controle_e_geradores_que_existem`.
- Link: o destino e as pastas dele são conferidos antes de qualquer gerador (`:991-996`, `:1017`), recusa com 2 sem rodar. Teste: `test_link_no_derivado_ou_na_pasta_recusa_sem_rodar_o_gerador`.
- Geradores: argv fixo, sem shell, `python -I`, ambiente sem `GIT_*`/`FORGE_*` (`:1022-1023`); o nome do módulo medido casa `tests/(test_[a-z0-9_]+)\.py` (`:286`), não vira opção. A busca da base reaproveita `buscar_base` do B1, já aprovada (`docs/security/v0479-pv-b1-registros.md`).
- Sem veredito (git ou pesos ilegíveis, antes e depois) sai 2, nunca verde (`:1012-1015`, `:1024-1028`).

## Achados
- A1 (recomendado) bin/forge-testes:1001 · `fotografia` usa `git status` sem `--ignored`: escrita do gerador em caminho ignorado (`.forge/`, `.claude/hooks` etc.) não é vista e sai 0; o texto de ajuda (`:30`) promete "nunca escreve arquivo de controle". Incluir ignorados ou limitar a promessa.

## Sondas

## Detalhe dos achados
A1. Evidência: `bin/forge-testes:1001` (o `git status --porcelain` sem `--ignored`) e `:30` (a ajuda). Sonda local: repositório de brinquedo com `/.forge` no `.gitignore`, `fotografia()` antes e depois de gravar `.forge/agentes.json` devolve `{}` nas duas, sem diferença. Caminho de ataque: só com um gerador ou módulo de teste medido que grave fora da lista em caminho ignorado; quem roda é o autor sobre o próprio código, a mesma confiança da suíte, e a trava de escrita do sandbox (A3) e o hook `conformidade` seguem protegendo os arquivos de controle da sessão. Sem atacante realista, por isso recomendado, não bloqueante. Severidade: baixa. Correção mínima (uma das duas): somar `--ignored=matching` à chamada de `fotografia` (com `PYTHONDONTWRITEBYTECODE` já no ambiente dos geradores, o ruído de `__pycache__` fica pequeno; conferir o teste), ou trocar a ajuda e o fragmento do changelog para "sai 2 se mudou caminho versionado ou novo fora da lista". Esforço: P. Dono: tech-lead (autor do B2).

## Riscos aceitos e ferramentas
Sem risco aceito. Suíte: não rodada aqui (brief: sem suíte local); a branch ainda não tem PR nem CI, e o portão de merge confere o CI verde no head. Rodei só a classe nova: `python3 -m unittest tests.test_testes_tocados.Regerar`, 11 testes, OK, árvore limpa. Ferramentas ausentes no PATH: varredor de segredos, SAST e linter de workflow (lacuna registrada, `R-CUSTO`); o diff não traz segredo nem workflow.
