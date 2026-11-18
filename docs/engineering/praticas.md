# Práticas de engenharia do Forge

Propósito: as regras que o review de uma melhoria do Forge confere e quem decide cada uma (COBERTURA-ESTUDO P5, decisão do dono de 2026-11-16). Público: o `tech-lead` e os revisores no repositório do Forge. Revisão: 2026-11-16.

As práticas padrão vêm da skill `engineering-practices`; aqui fica só o que é do Forge. O fluxo e a contribuição seguem `R-FLUXO`, `R-REVIEW` e `R-CONTRIB`; decisão estrutural fica em ADR.

## Regras e quem as decide
Cada regra diz quem a decide: uma **ferramenta** (o comando abaixo, que roda no CI do PR ou no envio do autor) ou a **leitura** (o revisor lê o diff). O review não refaz o que a ferramenta decide: cita a saída do comando, ou o CI verde do PR. Regra "ferramenta" sem comando configurado é pendência a registrar, não revisão manual.

| Regra | Decidida por |
|---|---|
| Testes passam | `scripts/suite-partes.py` (o job "suíte" do CI do PR; local, `.githooks/pre-push --suite`) |
| Script de shell sem aviso do shellcheck (os arquivos vêm do shebang, P6) | o passo "shellcheck (scripts e hooks)" do `.github/workflows/ci.yml` |
| Plugin válido | `scripts/validar-plugin.sh` (no CI, `claude plugin validate . --strict`) |
| Arquivo de produção do diff tem teste | a catraca no CI do PR (`tests/catraca.py --modo pr-texto`, T1): sem teste mudado ou novo, `## Sem teste` cita cada arquivo pelo caminho inteiro, com o motivo dele na mesma linha (20 caracteres por arquivo além dos caminhos), ou o PR fica vermelho; local, `bin/forge-check pr <pedido>` (linha `sem teste:`). O mérito da justificativa: leitura |
| Guarda mudada tem mutante declarado e morto | `bin/forge-mutante` (com `--cobertura --base <Base-sha>`) e a catraca `tests/catraca.py` |
| Cobertura por arquivo não cai | pendência: sem comando por PR até a decisão C3 do COBERTURA-ESTUDO (piso que só sobe, só se não aumentar o tempo do CI do PR); hoje `scripts/cobertura.py` só mede no push na `main`, no job "cobertura (informativa)", sem reprovar. Registrada aqui uma vez, não em cada parecer |
| Neutralidade e invariantes da fábrica | `tests/test_forge.py` (classes `Neutralidade` e `NeutralidadeDoNucleo`) e `tests/config.json` |
| Nomes, tamanho das funções, duplicação | leitura |
| Segue as regras com ID (`docs/regras/`) e os ADRs | leitura |
| Segurança: segredos, injeção, comando montado | leitura (parecer do `security-engineer`, `R-SEGURANCA`) |
