---
tipo: review
contrato: 1
pedido: jarvis-forge-ao-abrir
branch: melhoria/jarvis-forge-ao-abrir
commit: 55f8be6
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-13
---
# Parecer de autor: `jarvis-forge` atualiza a cópia vigente e consulta a fonte de harness ao abrir

Escopo: `origin/develop..55f8be6` (1 commit): `scripts/jarvis-forge`, `bin/forge-check` (subcomando `fontes`), `tests/test_forge.py`, ADR 0009 (ajuste), README, `docs/fontes-de-praticas.md` e `CHANGELOG.md`. O autor é o próprio `tech-lead`: parecer de autoria; `bin/forge-check` é protegido, então o PR exige o rótulo `afrouxa-regra` do dono, que é o portão independente.

## O que muda
- Atualização automática só por `fetch` + `merge --ff-only` na cópia vigente, nunca `reset`. Recusa com aviso de uma linha (e abre com a cópia atual) se houver mudança local, commit local, branch diferente da `develop` ou falta de rede. Não atualiza sob sessão tmux já aberta (`FORGE_ABERTURA_FEITA` evita repetir dentro do tmux). `--dev` não atualiza.
- `forge-check fontes` lê `~/.forge-contrib/fontes/fontes.json`, usa `git ls-remote -- <url> HEAD`, compara por prefixo com `commit_revisado`; sem registro, silêncio; sem resposta, saída 3 (o `jarvis-forge` não grava o cache e tenta na abertura seguinte). URL começando com `-` é ignorada. Nome e URL da fonte não entram no repositório (`R-NEUTRO`).

## Verificação
- Testes novos escritos antes e falhando sem a mudança: fast-forward, mudança local, commit local, sem rede, cache diário, `fontes` com versão nova, sem novidade, sem registro e fonte inalcançável. Repositórios bare locais e HOME temporário, sem rede.
- Um teste existente foi ajustado: a segunda abertura agora toca a cópia vigente (só fetch e merge), mas continua sem clone nem reset.
- Suíte completa, `shellcheck scripts/jarvis-forge` e `scripts/validar-plugin.sh` passam.

## Riscos e limites
- `R-CUSTO`: só `git ls-remote` e `git fetch`, sem API paga.
- O cache é por data local; arquivos `fontes-<data>` se acumulam (vazios, um por dia); o script não apaga nada.
- `ls-remote` consulta `HEAD` da fonte, não uma branch fixa: acompanha a branch padrão dela.
