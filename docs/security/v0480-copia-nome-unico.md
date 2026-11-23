---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-copia-nome-unico
commit: 2f16f0175ef1a657ad21031e493e079cdce06b41
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-23
---
# Review de segurança: v0478 (E111.7, volta por delta do CLONE-NOME-UNICO)

Delta lido (`forge-check parecer delta`): `95011540..2f16f017`; no domínio só `bin/forge-copia` (`ocupado`, +2 linhas); fora do domínio, também lidos: `tests/test_forge_copia_nome.py`, `tests/mutantes/v0480-copia-nome-unico.json`, `changelog.d/v0480-copia-nome-unico.md`. Já lido na rodada anterior (commit `0e11bc4a`, parecer sobre `95011540`): o restante do `bin/forge-copia` e as sondas de caminho, opção e controle.

Gatilhos: controle do Forge (caminho de escrita das cópias na pasta liberada do sandbox).

## Conferência
- **A1 (anterior, recomendado): corrigido.** `bin/forge-copia:79-80` trata `os.path.islink` como ocupado antes de seguir o link; `nome_unico` (`:88`) pula o link e sugere o próximo nome. Sonda S1 refeita pelo teste novo `test_link_com_o_nome_sugerido_nao_e_oferecido` (`tests/test_forge_copia_nome.py:86-94`): link `b-qa` para pasta vazia fora da pasta de cópias · espera: sugere `b-qa-2`, rc 2, pasta de fora vazia · obtido: igual (9 testes, OK). Mutante M6 (`if False:`) aplicado numa cópia: o teste novo falha (morto).
- **Só aperta: sim.** A mudança só faz `ocupado` devolver `True` em mais casos (nunca `False` onde antes era `True`). No destino explícito, `ocupado` recebe `realpath` (`:109`, `:114`), que já resolveu os links: o comportamento não muda (laço de links já era ocupado por `lexists` e não ser pasta). Na sugestão, só deixa de oferecer link como livre. Nenhuma recusa foi afrouxada, nenhum caminho novo de escrita.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática, teste novo e mutante rodados localmente; varredor de segredos, SAST e auditor de dependências ausentes no PATH (lacuna; o delta não traz dependência nem segredo). Suíte inteira: não rodada (brief: sem suíte local); o portão de merge segue dependendo do CI verde do PR.
