### Corrigido
- Vigia de prazo dos hooks (VIGIA-PRAZO-TRAVA, decisão do dono de 24/11): toda linha que chega a uma trava que pode recusar (`conformidade`, `parecer`) conta como crítica; o prazo vencido recusa, com ou sem o marcador crítico, e nunca libera. Antes, a linha sem o marcador (por exemplo, `"g"h repo create x --public`) liberava quando a decisão passava do prazo.
