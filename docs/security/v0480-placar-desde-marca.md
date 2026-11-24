---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-placar-desde-marca
commit: 6d13dbaede186e35dc70489bf443d599504c1d5e
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-23
---
# Review de segurança: v0478 (E139.13, placar desde a marca, PR #825)

Lido o diff inteiro `0e59c446..6d13dbae` (10 arquivos). De `19c1c2a6` a `6d13dbae` só mudaram `docs/qa/` e `docs/reviews/`: o código revisado é o de `19c1c2a6`.

Gatilhos: classe C por `bin/forge-changelog` (script da release); `scripts/placar-mutacao.py` vai junto (mede, não é portão).

## Só aperta ou neutro, por escrito
- `bin/forge-changelog:283-285` (**neutro**): a sugestão do `--desde` passa de `git describe` à marca (último commit do HEAD que mudou a versão do manifesto) e à tag apontada para ela. Os argumentos do `git` são fixos e em lista (sem shell); `marca[0]` vem de `--format=%H` (40 hex), não do usuário; o nome da tag segue em `shlex.quote` (o teste `test_tag_com_metacaractere_sai_citada_no_comando`, A3 da v046 E7, segue verde). A saída só é impressa, não executada, e nunca muda o rc da release.
- `scripts/placar-mutacao.py:53-61` (**neutro**): `aviso_do_desde` cala o aviso quando o commit do `--desde` é a marca. O aviso é informativo (o placar não é portão, sai 0 em ambos os casos); a marca é calculada pelo próprio script a partir do HEAD, não escolhida por quem chama. A validação do `--desde` (`:93-95`: recusa `-` inicial e usa `--end-of-options`) roda antes e não mudou.
- `scripts/placar-mutacao.py:95` (**neutro**): passa `base.stdout.strip()`, sha já resolvido e não vazio (o `rc` foi conferido na linha anterior).
- `tests/mutantes/*.json` (**neutro**): M7 e M10 alinhados à fonte nova; a isenção de `v0480-placar-desde-marca.json` cobre um trecho que saiu da fonte (`tag.returncode == 0 and tag.stdout.strip()`), cuja guarda passou a PDM4 e M10; não isenta código vivo.
- `tests/test_changelog.py`, `tests/test_forge_mutante.py`, `changelog.d/` (**neutro**): testes e fragmento.

Nada libera o que antes era recusado; nenhum caminho de ataque realista (o único insumo externo, o nome de tag, continua citado).

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum.
Ferramentas: leitura do diff. No head: `python3 -m unittest tests.test_changelog.ReleaseAvisaMedidasDaVersao tests.test_forge_mutante.PlacarDaRelease` deu 14 testes OK; `forge-mutante tests/mutantes/v0480-placar-desde-marca.json` deu 6 de 6 mortos (PDM1 a PDM6). Suíte inteira: CI do PR #825 no head 6d13dbae (run 45301720557), as cinco partes da suíte e o teto de pulados verdes; a `bateria (pareceres)` falhava por este parecer ainda ausente. Sem gitleaks/semgrep nesta passada: o diff não toca segredo nem dependência.
