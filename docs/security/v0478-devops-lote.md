---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0478-devops-lote
commit: f9356caf6fe937fd9d16d11e11c3d4588e4433e7
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-18
---
# Review de segurança: v0478 (E6.8, revalidação do lote de devops)

Revalidação por delta (`R-REVIEW`). A rodada anterior (E6.4, commit `d50b9cd0`, aprovado com A1 a A3 recomendados) está no git.

Gatilhos: dependência nova (o modo `--ferramentas` e o preparo completo baixam e executam binários e pacotes de terceiros na estação do dono).

## Delta lido
`forge-check parecer delta docs/security/v0478-devops-lote.md`, intervalo `d50b9cd0..f9356caf`. No domínio: `scripts/preparar-estacao.sh`, `agents/devops-engineer.md`, `skills/ci-cd/SKILL.md`. Fora do domínio (não relido): `changelog.d/v0478-devops-lote.md`, `tests/mutantes/v0478-devops-lote.json`, `tests/test_ferramentas_portoes.py` (só executado).

## Achados anteriores
- A1 corrigido: scripts/preparar-estacao.sh:77-79 fixa o sha256 de cada artefato ao lado da versão; o download só instala se bater com as somas da release e com a soma fixada (o segundo ramo vira `falta:`). Conferi as três somas fixadas contra os arquivos de somas publicados nas releases actionlint 1.7.12, gitleaks 8.30.1 e osv-scanner v2.7.1: as três batem. Teste `test_soma_fixada_no_script_errada_nao_instala`.
- A2 corrigido: `instalar_pipx` recebe `nome==versão` (zizmor 1.32.0, semgrep 1.186.0, scripts/preparar-estacao.sh:76 e :121-122); as duas versões existem no índice. Teste `test_pipx_recebe_a_versao_fixada`.
- A3 corrigido: extração e cópia dentro de `if ...; then ok=1; else ok=0; fi` (:97-98), e só `ok=1` grava "instalou"; falha vira `falta:`. Teste `test_falha_do_tar_vira_falta_e_nao_grava_instalou`.

## Verificado sem achado no delta
- Ordem das conferências: soma da release ausente ou diferente é recusada antes da fixada; nenhum ramo instala sem as duas iguais ao sha256 real.
- Textos de `agents/devops-engineer.md` e `skills/ci-cd/SKILL.md`: só redação ("quem instala é o script", ensaio de roteiro condensado mantendo "alvo provado descartável" e "recuse o valor padrão"); nenhuma regra com ID afrouxada.
- Recomendação informativa da rodada anterior (`curl --proto '=https'`) segue em aberto, sem achado: com a soma fixada, o binário já fica coberto mesmo que o arquivo de somas seja trocado.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas da skill (gitleaks, osv-scanner, semgrep, zizmor, actionlint, shellcheck) fora do PATH desta estação, lacuna registrada; revisão por leitura, `bash -n` do script e o teste `tests/test_ferramentas_portoes.py` rodado localmente (9 testes, OK). Suíte inteira: só no CI do PR, não rodada aqui (brief).
