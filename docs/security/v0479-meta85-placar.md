---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-meta85-placar
commit: 97ef4fd1e6c99380646ad2f52dbe291f2168d27b
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-19
---
# Review de segurança: v0479-meta85-placar, revalidação (v0478 E36.7)

Volta por delta (R-REVIEW): `forge-check parecer delta docs/security/v0479-meta85-placar.md`, intervalo 87aff761..97ef4fd1. No domínio, só `bin/forge-placar` (`paradas_do_historico`, :658-673); fora, `tests/evals/test_placar.py` e dois mutantes. A rodada anterior (87aff761, aprovado com A1 recomendado) fica no git.

## Gatilhos
Gatilhos: nenhum (ferramenta local de leitura; sem autenticação, segredo, dependência, CI, rede nem controle do Forge).

## Sondas
- S5 · `PARADA sessão` com mês 13, hora 25 e ano 0000, mais uma válida 10:00-10:30 · espera: 3 avisos que citam o arquivo e 30 min · obtido: 3 vezes `PARADA com data impossível em docs/pedidos/p1.md; linha ignorada`, `sessão` = 30, rc 0
- S7 · pedido só com a linha impossível · espera: `sessão` sai `-` (None), nunca 0 · obtido: `min: None`, rc 0

## Detalhe
- A1 (anterior, recomendado): **resolvido** em bin/forge-placar:666-672. O `ValueError` de `fromisoformat` é captado por linha; o aviso vai ao stderr com texto fixo e só o nome do pedido (`arq.stem` de `docs/pedidos/*.md`), nada do texto da linha ecoado; as demais linhas seguem (S5). Sem intervalo legível, devolve None em vez de 0 (S7), coerente com "fonte ausente sai -".
- O resto do delta não muda superfície: a regex `PARADA` (:102) e `minutos_recortados` são os mesmos; `momento` deixa de ser usado nesse caminho, sem perda de validação (a regex já exige só dígitos).

## Riscos aceitos e ferramentas
Sem risco aceito. Ferramentas: leitura do delta e sondas locais em `$TMPDIR` com `python3 -I`. Suíte: não rodada localmente (brief: sem suíte local); a suíte inteira fica com o CI do PR. Varredor de segredos e SAST não estão no PATH: lacuna registrada; o delta não traz credencial.
