---
tipo: review
contrato: 1
pedido: contrib-externa-so-propoe
branch: melhoria/contrib-externa-so-propoe
commit: d6cc1a6
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-13
---
# Parecer de autor: sessão de outro projeto só propõe ao Forge (`R-CONTRIB`)

Escopo: `origin/develop..d6cc1a6` (1 commit): `docs/regras/R-CONTRIB.md`, `skills/contribuir-com-o-forge/SKILL.md`, `agents/jarvis.md`, `hooks/conformidade.py`, `tests/config.json`, 23 fixtures em `tests/hooks/conformidade/` e `CHANGELOG.md`. O autor é o próprio `tech-lead`: este parecer é de autoria e exige o rótulo `afrouxa-regra` do dono (toca `hooks/conformidade.py` e `docs/regras/`), que é o portão independente.

Aperta a regra, não afrouxa: nenhum invariante saiu; cinco entraram em `tests/config.json`. A política `hooks/conformidade.json` não mudou.

## Garantido por hook
Só em sessão cuja raiz não é o Forge (`e_clone_do_forge` falso), e só quando o alvo é o Forge (pasta em `~/.forge-contrib/` ou `--repo`/`GH_REPO`/endpoint com o slug do Forge):
- `git push` para branch fora de `melhoria/<projeto>-` (`<projeto>` = nome da raiz da sessão), incluindo `HEAD` estando em branch alheia;
- `gh pr merge`, `gh pr edit`, `gh pr close` e `gh label`;
- `gh api` mutante em `pulls/<n>`, `issues/<n>`, `issues/<n>/labels` e `labels`, e mutações GraphQL equivalentes. Criar o PR (`POST pulls`), ler e comentar continuam livres. PR e API de outro repositório (o do projeto) não são afetados.

## Só regra (limites do hook)
- Commitar em branch alheia e resolver conflito ou revalidar parecer de PR alheio: o hook não vê a intenção; o efeito (o push) é barrado, então o dano não chega ao Forge.
- Sessão iniciada com `cwd` dentro do clone de contribuição: o clone do Forge não tem `.forge/versao`, e o `conformidade` só age em projeto com ele (ADR 0009). Não há como distinguir com segurança "outro projeto" de "o Forge" nesse caso; o limite já existia e fica documentado aqui.
- `git push` com `--tags` ou `gh` por script (`python -c`, arquivo `.sh`): o Bash é lido como texto (limite já documentado no hook).
- Vale a identificação por raiz do projeto; uma sessão que se passe pelo Forge criando `.claude-plugin/plugin.json` falso na raiz é um dolo que o hook não cobre (o sandbox e o ruleset do GitHub são a garantia).

## Checklist
1. Pedido atendido, sem extras: sim.
2. Regras e ADRs: `R-CONTRIB` é texto único; skill e `jarvis` citam o ID sem repetir o texto (ADR 0002); `R-CUSTO` e `R-NEUTRO` intactas.
3. Legível: `alvo_do_forge` e `gh_contrib` pequenos, constantes nomeadas.
4. Erros: política e falha fechada inalteradas; o marcador `CRITICO` ganhou `edit|close|label` para falhar fechado em erro interno.
5. Testes: fixtures escritas antes. Vermelho: 14 falhas em `test_hooks` sem a mudança no hook (todas as `bloqueia` de `contrib-*`). Verde: `python3 -m unittest discover -s tests`, 271 testes, e `scripts/validar-plugin.sh` passa.
6. Commits: um commit coerente, `git add` explícito.

Parecer: **aprovado**, condicionado ao rótulo `afrouxa-regra` do dono.
