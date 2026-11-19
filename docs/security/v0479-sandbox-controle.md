---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-sandbox-controle
commit: 64fca89083f7549aa5ea97ed4e716bec049f1306
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-19
---
# Review de segurança: v0479-sandbox-controle

Revalidação (E29.13) no head 64fca890, por delta: `forge-check parecer delta` de 1aaea973..64fca890. Lido no domínio: `hooks/_comum.py` (`gravar_json`, `:2561-2569`), `hooks/agentes.py` (`ler_estado`, docstring HOOK-ESTADO-ILEGIVEL-LIBERA), `docs/hooks.md:129`, as fixtures `tests/hooks/agentes/estado-ilegivel-vazio-bloqueia.json` (nova) e `estado-vazio-0byte-libera.json` (removida). Fora do domínio, lidos só para conferir A2: `tests/test_sandbox_controle.py:362-373` e `docs/devops/v0479-sandbox-controle.md:61`. A rodada anterior está no git (parecer de 1aaea973).

## Gatilhos
Gatilhos: configuração do sandbox do Bash (controle de escrita), estado dos hooks de R-TETO (registro de agentes, trava pesada), teste de controle.

## Resumo
- **A5 fechado.** `gravar_json` apaga a sobra (`os.path.lexists` + `unlink`, sem seguir link) e cria o temporário com `O_WRONLY|O_CREAT|O_EXCL|O_NOFOLLOW` (`hooks/_comum.py:2564-2566`). S1 refeita no head: o link plantado sai, `pesado.json` fica arquivo regular com a trava e o alvo do agente não é tocado. Modo `0o666` sob umask, igual ao `write_text` anterior: sem regressão. Resíduo (S2): replantar o link entre o `unlink` e o `open` dá `FileExistsError`, a gravação falha sem seguir o link e o hook `pesado` (não crítico) libera pelo ADR 0003; ganho igual ao do A2, exige vencer uma janela curta. Fica no cartão do A2.
- **Mudança de 0 byte no `agentes.json`:** `ler_estado` volta a tratar 0 byte como ilegível (falha fechada, R-TETO); `forge-init` e `doutor` criam o arquivo antes do primeiro Bash, então o ponto de montagem vazio não nasce no uso normal. Mais estrito que a rodada anterior; a fixture `estado-ilegivel-vazio-bloqueia` prova recusa e não regravação. `ler_trava` segue aceitando 0 byte e `null` como sem trava, coerente com `docs/hooks.md:129`.
- **A2 parcial:** o teste do rename como limite existe (`tests/test_sandbox_controle.py:365-373`: `mv .forge/run`, recria o registro, espera sucesso e cai se o runtime passar a recusar); `docs/hooks.md:129` cita `.forge` como pasta mãe de `.forge/config.json`. Falta a mesma citação em `docs/devops/v0479-sandbox-controle.md:61` (lá só `.forge/run` e `.git/forge`).
- Testes rodados no head: `tests.test_sandbox_controle` (14, OK, 2 pulados: bubblewrap aninhado negado aqui) e as fixtures `agentes/estado-ilegivel-{vazio,texto}-bloqueia` pelo executor do `tests/test_hooks.py` (2 verificadas, OK). Sem execução de CI no head (`gh run list --commit` vazio): a recusa dentro do bubblewrap só tem prova no CI do PR, obrigatório para o merge.

## Achados
- A2 (recomendado) docs/devops/v0479-sandbox-controle.md:61 · Estado: teste do rename e .forge em docs/hooks.md:129 feitos; falta citar .forge (pasta de .forge/config.json) na linha do limite do patch. Cartão da identidade da pasta absorve o resíduo do A5 (S2, corrida entre unlink e open).

## Sondas
- S1 · `python3 -I sonda.py <head>/hooks <tmp>`: link `pesado.json.<pid>.tmp` -> arquivo do agente, `gravar_json(pesado.json, {"pid":1,"desde":1})`, o agente grava `null` no alvo · espera: pesado.json regular com a trava · obtido: `link: False regular: True ler_trava: {'pid': 1, 'desde': 1}`, sobra apagada
- S2 · mesma sonda, `os.unlink` trocado para replantar o link logo após apagar · espera: não seguir o link · obtido: `FileExistsError`, alvo intacto, trava anterior preservada

## Detalhe dos achados
**A2.** Correção mínima que falta: em `docs/devops/v0479-sandbox-controle.md:61`, `.forge` (pasta de `.forge/config.json`, modelo) ao lado de `.forge/run` e `.git/forge`. Severidade baixa (documentação de limite já registrado), esforço P. Dono: tech-lead.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Suíte inteira: não rodada (brief); sem CI no head. Ferramentas: varredor de segredos e linters de workflow fora do PATH (lacuna; o delta não toca workflow nem segredo); bubblewrap aninhado negado (lacuna para sondar dentro do sandbox).
