Agente destino: forge:dev-exemplo

## Objetivo
Entregar o recurso A (exemplo sintético).

## Ler
- docs/pedidos/pedido-sintetico.md: Escopo.

## Entregar
- Recurso A no módulo de exemplo, em um commit (E1).

## Fora do escopo
- Retira do escopo original: "E2. Atualizar a documentação do recurso A." · justificativa: a documentação espera o recurso estável · consequência: o recurso fica sem texto até a próxima entrega · decisão: DECISÃO DO DONO (2026-01-02): "sem custo".
- "validação de qualidade da branch" é de outro papel.
- "E3.1 (revisor): revisão de código da branch." e "E3.3 (dono): merge final na branch principal." · outras etapas do pedido; continuam nele.

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
