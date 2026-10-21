---
tipo: revisao-devops
contrato: 1
pedido: release-0.28.0
branch: melhoria/release-0.28.0
commit: 450d7fa27e133cddbafd9ce09f19f63548f86a31
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-10-21
---
# Review de devops: release-0.28.0

## Achados

## Parecer
Aprovado, sem bloqueantes. Escopo lido: o diff de `5e9b234` a `450d7fa` em `.github/`, `.githooks/` e `bin/forge-testes`, mais a versão e o `CHANGELOG`.

- `.github/workflows/ci.yml`: o passo de instalação do CLI passa a ter uma segunda tentativa só na instalação e confere a versão. Isso não é `continue-on-error` nem pula check, porque a segunda falha derruba o job (R-VERIFY). Os passos baratos (conferências de changelog, catraca e pareceres) agora rodam antes dos caros (testes, shellcheck, actionlint, zizmor, instalação de ponta a ponta). Nenhum passo foi removido; os mesmos passos pesados continuam com o mesmo gate. `permissions`, ações fixadas por SHA e checksums das ferramentas ficaram intactos.
- `.githooks/pre-push`: o caminho curto (só pareceres) falha fechada: exige uma ref de branch, ref existente, árvore limpa, HEAD igual ao enviado, árvore remota anotada como verde, ausência de apagamentos e delta só em `docs/{reviews,security,qa,devops}/` sem modelos. Qualquer dúvida roda a suíte inteira, e o CI repete tudo, então não afrouxa o processo. A prova fica fora do git, com `umask 077`, recusa link simbólico e exige dono.
- `bin/forge-testes`: as listas `FORGE_CHECK` e `CONTEUDO` ficaram mais completas (inclui `test_modelos_citados`), e o teste `MapaDoForgeCheck` as confere contra os arquivos.
- Versão: `plugin.json` em 0.28.0 e entrada `[0.28.0]` no `CHANGELOG` (`changelog.d` já juntado). `scripts/conferir-release.py --base 5e9b234` foi rodado.
- Ferramentas: o `actionlint` e o `shellcheck` não estão no PATH deste ambiente; lacuna registrada. O `ci.yml` foi lido por inspeção e carrega como YAML válido. O CI da PR roda o `actionlint`, o `zizmor` e o `shellcheck` do `pre-push`.

Recomendações (não bloqueiam):
- O pre-push cita a lista de classes do caminho curto no texto e no comando; manter as duas em sincronia ao mexer.
- Mudança em `.github/` exige o rótulo `afrouxa-regra` do dono na PR (catraca) e envio do workflow pelo dono, pois o token do bot não tem o escopo `workflow`.

## Custo e rollback
Sem custo novo (R-CUSTO): nenhum runner, serviço ou artefato adicionado; a segunda tentativa de instalação soma segundos só em falha de rede, e a reordenação falha mais cedo, o que tende a poupar minutos. Rollback: reverter o commit da release (ou reimplantar a tag `v0.27.0`); sem migração envolvida. Medição de minutos do CI do checkpoint (`gh run list`) fica para o `tech-lead` antes do PR `homolog` para `main`, pois não foi medida aqui.
