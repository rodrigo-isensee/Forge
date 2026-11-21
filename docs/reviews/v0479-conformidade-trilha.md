---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-conformidade-trilha
commit: dd1fc980fa57547c88dbf3d98fe35577b05fe522
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-21
---
# Review: v0478 (E63.25, revalidação da trilha CONFORMIDADE-SEGURANCA no head dd1fc980)

Revalidação (H3, `R-REVIEW`) do parecer aprovado no head a247ae11. Li só o delta de
`forge-check parecer delta docs/reviews/v0479-conformidade-trilha.md`: intervalo `a247ae11..dd1fc980`, domínio "código e
testes"; no domínio, só `docs/hooks.md`. Os pareceres de QA e segurança do intervalo ficam fora do domínio e não foram relidos.

## Delta lido
- `docs/hooks.md:56` (A18 da segurança E63.20): uma frase nova declara o limite do link criado por cópia na mesma linha
  (`cp -a`, `cp -P`, `cp -d`, `cp -r`, `cp --no-dereference`, `rsync -a`, `tar -x`, `os.symlink` no `python3 -c`) e o
  remete ao cartão CONFORMIDADE-LINK-POR-COPIA (registrado no Histórico do pedido, 03:59 e 08:33).
- Conferido contra o código: a recusa do link na mesma linha casa só `ln` e `cp` com `-[^-]*[ls]\w*|--(link|symbolic-link)`
  (`hooks/conformidade.py:2403` e `:2415`); nenhuma das formas listadas casa esse padrão, então o texto agora diz o que o
  hook faz, nem mais nem menos. A frase final do item ("o link criado na mesma linha recusa (A17)") segue válida para as
  formas do A17 (`ln`, `cp -s`, `cp -l`).
- Só documentação: sem guarda nova, sem mutante a declarar, sem teste a rodar.

## Ferramentas (citadas, não refeitas)
- Suíte inteira: fica com o CI do PR (sem PR nesta etapa; o brief pede revisão sem suíte local).

## Parecer
Aprovado no head dd1fc980. O delta é a declaração do limite pedida pelo A18; nenhum comportamento muda.
