# Sistema de Gestión de Planificaciones Docentes

Sistema para que profesores envíen planificaciones mensuales y un moderador (coordinador académico) las apruebe o rechace, con versionado y registro de la versión oficial.

## Estructura de la documentación

```
docs/
├── README.md                       ← este archivo (índice + metodología)
├── 01-vision/
│   ├── vision-del-producto.md      ← propósito, alcance, objetivos
│   ├── glosario.md                 ← términos del dominio
│   └── stakeholders.md             ← interesados y necesidades
├── 02-relevamiento/
│   ├── guia-entrevista-moderador.md
│   ├── protocolo-entrevistas.md
│   └── actas/
│       └── acta-YYYY-MM-DD-<rol>.md
├── 03-requerimientos/
│   ├── requerimientos-funcionales.md
│   ├── requerimientos-no-funcionales.md
│   └── reglas-de-negocio.md
├── 04-casos-de-uso/
│   ├── actores.md
│   ├── diagrama-casos-de-uso.md
│   └── CU-XX-<nombre>.md
├── 05-modelo/
│   ├── modelo-dominio.md
│   ├── diagrama-estados-planificacion.md
│   └── diagrama-secuencia.md
└── 06-decisiones/
    └── ADR-XXXX-<titulo>.md        ← decisiones de arquitectura/diseño
```

## Metodología sugerida (rol analista)

1. **Visión** — Definir problema, alcance y objetivos antes de tocar requerimientos.
2. **Stakeholders** — Identificar todos los roles (profesor, moderador, secretaría, autoridades, alumno indirecto).
3. **Relevamiento** — Entrevistas (1 por rol mínimo), validar con observación de proceso actual.
4. **Modelado** — Casos de uso, modelo de dominio y diagrama de estados de la planificación.
5. **Requerimientos** — Funcionales (qué hace), no funcionales (cómo: rendimiento, seguridad, usabilidad), reglas de negocio.
6. **Validación** — Devolver al usuario lo entendido (prototipos en papel / mockups) antes de construir.
7. **Trazabilidad** — Cada requerimiento referencia la entrevista y el caso de uso que lo origina.

## Convenciones

- IDs: `CU-01`, `RF-001`, `RNF-001`, `RN-01`, `ADR-0001`.
- Toda decisión que cambie el alcance se registra como ADR.
- Las actas se firman (digitalmente o por mail) por el entrevistado.
