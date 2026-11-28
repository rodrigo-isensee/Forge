---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-custo-por-agente
commit: b2a1470ae35196c6df3be1fb8c8c00046c42a6c7
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-16
---
# Review de segurança: v047-custo-por-agente

Item CUSTO-MEDIA-POR-AGENTE (v047 E2.312; parecer E2.353), diff `1b88640e..b2a1470a`: `bin/forge-check` (opção e despacho), `bin/forge_transcricao.py` (`ler_entregas`, `tokens_por_agente`, `cmd_media_por_agente`), testes em `tests/test_medidas_m14b.py`, mutantes e fragmento do changelog. Instância que não fez a entrega.

## Gatilhos
Nenhum gatilho de `R-SEGURANCA` tocado: sem autenticação, dado pessoal, segredo, dependência nova (só biblioteca padrão), rede, banco, CI/CD, Docker nem controle do Forge (`hooks/`, `docs/regras/`, `tests/catraca.py`, `tests/config.json` intactos). É um leitor de relatório, só leitura de um arquivo local, sem escrita, sem subprocesso e sem decisão de portão. Parecer pedido pelo brief como portão da classe.

## Achados
- A1 (recomendado) bin/forge_transcricao.py:377 · CONTROLE cobre só C0, DEL e C1; bidi e largura zero (Cf, ex. U+202E) do nome do agente saem crus na saída lida pelo dono; usar e_controle/CATEGORIAS_DE_CONTROLE do forge-check (Cc, Cf, Zl, Zp), como no resto da ferramenta.
- A2 (recomendado) bin/forge_transcricao.py:382 · is_symlink olha só o último componente: docs/kanban como link para fora é seguido e lido; risco baixo (só sai agente e soma de tokens de tabela); se quiser coerência, conferir a pasta resolvida dentro da raiz.

## Sondas

## Detalhe dos achados
**A1.** Evidência: `bin/forge_transcricao.py:377` e `:405`; a convenção da casa está em `bin/forge-check:1936` (`CATEGORIAS_DE_CONTROLE`, com Cf). Sonda local: célula de agente `a` + U+202E + `gnp.exe` sai na linha `custo: agente a‮gnp.exe: ...` sem escape (od mostra os bytes `342 200 256`); U+200B idem. Caminho de ataque: quem escreve `docs/kanban/entregas.md` (um agente do projeto ou um PR) faz o nome exibido ao dono parecer outro agente no terminal. Não há escape de terminal (C0/C1 já são trocados, o teste `test_controle_no_nome_do_agente_nao_sai_na_linha` prova) nem quebra de linha (U+2028 já separa linha no `splitlines`). Severidade: baixa (só apresentação, sem decisão automática sobre o valor). Correção mínima: trocar o regex pelo critério de `e_controle` (passar por `ctx` ou repetir as quatro categorias Cc, Cf, Zl, Zp). Esforço P. Dono: autor do item (tech-lead).

**A2.** Evidência: `bin/forge_transcricao.py:382` e `:417`. Sonda local: `docs/kanban` como link simbólico para uma pasta fora da raiz; o comando leu `entregas.md` de lá (rc 0). Caminho de ataque: repositório hostil com o link; o ganho é nulo na prática, porque só saem nomes e somas de células de tabelas com colunas `agente` e `tokens`, sem conteúdo arbitrário do arquivo. Severidade: informativa. Correção mínima (opcional): `resolve()` do arquivo e conferir que fica sob a pasta da raiz. Esforço P. Dono: autor do item.

Conferido sem achado: teto de 2 MB antes da leitura (`stat`), FIFO e pasta recusados por `is_file` (sonda: FIFO sai rc 1 sem travar); entrada patológica de 2 MB só de `|` e 200 000 linhas válidas terminam em segundos (custo linear, sem regex com retrocesso; `\d{1,15}` em `fullmatch`); combinação com alvo, `--entregas`, `--pedido`, `--desde` e `--ate` recusada com rc 2; nada de rede, subprocesso nem escrita; a corrida entre `is_symlink` e `read_text` exige escrita local na raiz, já fora da fronteira. Arquivo sem permissão de leitura não foi sondado (sessão como root).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Testes do item: `python3 -m unittest tests.test_medidas_m14b` na raiz do clone, 73 testes OK. A suíte inteira roda no CI do PR (não citado aqui: sem PR ainda; o brief pede só o parecer). Sem `gitleaks`, `semgrep` nem `zizmor` aplicáveis ao diff (sem segredo, sem workflow); revisão manual e sondas locais.
