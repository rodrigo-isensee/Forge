---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-copia-nome-unico
commit: d8e71e215ae0f8c19f99cc1ca6565e5063f9ecff
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-23
---
# Review de segurança: v0478 (E111.18, volta por delta do CLONE-NOME-UNICO após a volta de CI E111.13)

Delta lido (`forge-check parecer delta`): `2f16f017..d8e71e21`, sem o que veio da base (develop); no domínio só `bin/forge-testes`, e nele só a linha nova do `MAPA` (`bin/forge-testes:210`, commit `f6f1eaf1`): `bin/forge-copia` leva a `test_forge_copia`, `test_forge_copia_nome` e `test_forge`. As demais linhas do `MAPA` no diff vieram da develop (merge `d2288045`). Fora do domínio: `tests/pesos-d4.json` e os pareceres de QA e review. Já lido nas rodadas anteriores (parecer `6a1a8ce8` sobre `2f16f017` e o de `95011540`): o `bin/forge-copia` inteiro, o A1 (corrigido) e as sondas de caminho, opção e controle.

Gatilhos: controle do Forge (caminho de escrita das cópias na pasta liberada do sandbox; mapa de testes dirigidos do envio).

## Conferência
- **Mapa de testes (`bin/forge-testes:210`).** A linha só acrescenta módulos à seleção dirigida quando `bin/forge-copia` é tocado; os dois módulos existem (`tests/test_forge_copia.py`, `tests/test_forge_copia_nome.py`) e `forge-testes --listar bin/forge-copia` os lista. Não remove regra, não muda a ordem de casamento de outro caminho (o padrão `bin/forge-copia` não casa outro script do `bin/`) e não toca o portão: a suíte inteira continua só no CI.
- **Só aperta: sim.** O item segue só apertando: o `bin/forge-copia` não mudou desde `2f16f017` (a análise de `ocupado` do parecer anterior vale), e a mudança nova só faz o envio rodar mais testes quando o script é tocado. Nenhuma recusa afrouxada, nenhum caminho novo de escrita ou execução.
- Testes dos arquivos tocados: `python3 -m unittest tests.test_forge_copia tests.test_forge_copia_nome tests.test_testes_tocados` → 271 testes, OK (skipped=1).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática e os testes dos arquivos tocados rodados localmente; varredor de segredos, SAST e auditor de dependências ausentes no PATH (lacuna; o delta não traz dependência nem segredo). Suíte inteira: não rodada (brief: sem suíte local); o portão de merge segue dependendo do CI verde do PR.
