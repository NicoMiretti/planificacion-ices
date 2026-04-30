# Actores

| Actor | Tipo | Descripción | Casos de uso (previstos) |
|---|---|---|---|
| **Moderadora (Secretaría Académica)** | Primario | Abre instancias, recibe planificaciones, valida formato, marca tardías, archiva oficiales, hace correcciones leves. Única en su rol. | CU-01 Crear instancia, CU-02 Tablero de revisión, CU-03 Aprobar (parte moderadora), CU-04 Rechazar, CU-05 Aplicar corrección leve, CU-13 Reemplazar oficial |
| **Coordinador** | Primario | Aprueba en conjunto con la moderadora; ve histórico de rechazos de su carrera. | CU-03 Aprobar (parte coordinador), CU-04 Rechazar, CU-12 Cerrar revisión por consenso |
| **Profesor titular** | Primario | Recibe aviso, completa plantilla, envía y reenvía versiones, ve observaciones. | CU-06 Ver instancias asignadas, CU-07 Cargar planificación, CU-08 Enviar planificación, CU-09 Ver observaciones, CU-10 Reenviar nueva versión, CU-14 Clonar oficial previa |
| **Alumnado** | Secundario | Consulta la planificación oficial vigente de cada materia. | CU-11 Consultar oficial vigente |
| **Secretarías generales / Equipo de gestión** | Secundario | Consulta y descarga oficiales para gestión / auditorías / homologaciones. | CU-11 Consultar oficial vigente, CU-15 Reporte de cumplimiento |
| **Administrador** | Secundario | Alta de carreras, materias, profesores, plantillas, materiales. (Puede recaer en la moderadora). | CU-16 Gestionar catálogos |
| **Sistema de notificaciones** | Soporte | Envía mails al abrir instancias, ante cambios de estado y recordatorios. | (participa en múltiples CU) |
| **Validador automático de campos** | Soporte | Verifica los 7 campos obligatorios y rechaza automáticamente si falta alguno. | (participa en CU-08) |
