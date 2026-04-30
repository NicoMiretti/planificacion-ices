# Diagrama de Estados — Planificación (preliminar)

```mermaid
stateDiagram-v2
    [*] --> Borrador: Profesor crea
    Borrador --> Enviada: Profesor envía
    Enviada --> EnRevision: Moderador toma
    EnRevision --> Aprobada: Moderador aprueba
    EnRevision --> Rechazada: Moderador rechaza (con observaciones)
    Rechazada --> Borrador: Profesor inicia nueva versión
    Aprobada --> [*]: Queda como oficial del período
```

## Notas
- "Tomar" la revisión podría ser implícito (no requerir acción) — validar.
- Una **versión** rechazada queda en histórico; la "nueva versión" es un registro nuevo, no una edición.
- Solo la versión **Aprobada** se considera **oficial**.
