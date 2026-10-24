Agente destino: forge:dev-exemplo

## Objetivo
Entregar o recurso A (exemplo sintético).

## Ler
- docs/pedidos/pedido-sintetico.md: Escopo.

## Entregar
- Recurso A no módulo de exemplo, em um commit (E1, E1.1).
- Documentação do recurso A (E2).

## Fora do escopo
- "E2.1 (dev-exemplo): texto da documentação." · etapa do mesmo papel em outra delegação; continua no pedido.
- "E3.1 (revisor): revisão de código da branch. E3.2 (qa): validação de qualidade da branch. E3.3 (dono): merge final na branch principal." · etapa de outro papel ou do dono; continua no pedido.

## Decisões e restrições
- DECISÃO DO DONO (2026-01-01): "A".
- DECISÃO DO DONO (2026-01-02): "sem custo".
- NÃO tocar: hooks/.

## Pronto quando
- PQ-1 (sha): `git log -1 --format=%h` da branch · espera: o hash do commit entregue.
- PQ-2 (cmd): `grep -c recurso docs/a.md` · espera: contém 'recurso'
- PQ-3 (push): `git ls-remote origin refs/heads/melhoria/a` igual ao head local.

## Relatório
Até 8 linhas, resultado real, depois o bloco `Provas:`.
