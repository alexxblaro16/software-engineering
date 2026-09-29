# BACKLOG DEL PRODUCTO

**Proyecto:** Base de datos clave-valor ultraligera en Python
**Asignatura:** Ingeniería de Software — UDIT
**Metodología:** Scrum / Ágil (Historias de Usuario según criterios INVEST)
**Versión del documento:** 1.0

---

## 1. Visión del producto

Una base de datos clave-valor **mínima y fiable**, escrita en Python, pensada por y para programadores. Ofrece operaciones `set`, `get` y `delete` sobre un **registro append-only** en disco, con un **índice hash en memoria** que guarda la posición de cada clave en el archivo y permite recuperarla con `f.seek()` sin recorrer el log.

## 2. Requisitos del cliente y trazabilidad

| ID | Requisito del cliente | Historias asociadas |
|----|-----------------------|---------------------|
| R1 | Volumen y rendimiento: gran cantidad de datos, respuestas garantizadas por debajo de 500 ms | US-01, US-02 |
| R2 | Disponibilidad y seguridad: datos muy importantes, operación 24/7 (incluidos turnos nocturnos) y alta fiabilidad ante fallos | US-03, US-04 |
| R3 | Trazabilidad: auditoría del flujo de trabajo mediante log histórico, con modificaciones y borrados por lápidas | US-05 |
| R4 | Perfil de usuario: programadores Python, flujo ágil de leer/escribir/modificar con la BD clave-valor más sencilla posible | US-06 |
| R5 | Compatibilidad: varios sistemas operativos, equipos antiguos y clientes internacionales (ej. Rusia) con codificación robusta | US-07 |

## 3. Supuestos a validar con el cliente

El enunciado usa términos cualitativos ("masivo", "extremadamente importante"). Para poder probarlos se proponen valores medibles, que deben confirmarse con el cliente:

- **Volumen de referencia:** 1.000.000 de claves y un archivo de log de varios cientos de MB.
- **Latencia:** el límite de 500 ms se toma como máximo para el **percentil 99 (p99)** de cada operación.
- **Seguridad:** se interpreta como **integridad y fiabilidad ante fallos** (no perder ni corromper datos). El cifrado o el control de acceso **no** figuran en los requisitos y quedan fuera de este backlog.
- **Equipo antiguo de referencia:** por ejemplo, 2 núcleos, 4 GB de RAM y disco HDD (a confirmar).
- **Versiones de Python soportadas:** se fijarán en la Sprint 0 (a confirmar).

---

## 4. Definición de Hecho (DoD)

Una historia se considera terminada cuando:

1. El código está integrado en la rama principal mediante Pull Request revisado por al menos un compañero.
2. Todos los criterios de aceptación están cubiertos por pruebas automatizadas que pasan.
3. Las pruebas no reducen la cobertura global por debajo del umbral acordado por el equipo.
4. El código sigue la guía de estilo PEP 8.
5. La documentación (README y docstrings) está actualizada.
6. El Product Owner ha validado la historia en la revisión del sprint.

---

## 5. Resumen del backlog

| ID | Historia | Requisito | Prioridad (MoSCoW) | Puntos | Sprint sugerido |
|----|----------|-----------|--------------------|--------|-----------------|
| US-06 | API sencilla para programadores Python | R4 | Must | 3 | 1 |
| US-01 | Respuesta en menos de 500 ms | R1 | Must | 5 | 1 |
| US-05 | Registro histórico append-only y lápidas | R3 | Must | 5 | 1 |
| US-02 | Índice hash en memoria para grandes volúmenes | R1 | Must | 5 | 2 |
| US-03 | Operación continua 24/7 y recuperación tras reinicio | R2 | Must | 5 | 2 |
| US-04 | Fiabilidad ante fallos y protección de integridad | R2 | Must | 8 | 3 |
| US-07 | Multiplataforma, equipos antiguos y codificación UTF-8 | R5 | Must | 5 | 3 |

*Estimación en puntos de historia (escala Fibonacci), a refinar en la sesión de Planning Poker.*

---

## 6. Historias de Usuario

### US-01 — Respuesta en menos de 500 ms

**Requisito:** R1 (Volumen y rendimiento)

> **Como** programador que integra la base de datos en una aplicación,
> **quiero** que las operaciones `get`, `set` y `delete` respondan en menos de 500 ms aun con un gran volumen de datos,
> **para** que mi aplicación ofrezca respuestas instantáneas a sus usuarios.

**Criterios de aceptación**

- **CA-01.1 — Lectura rápida con carga grande**
  - **Dado** una base de datos con 1.000.000 de claves,
  - **cuando** se ejecuta `get(clave)` sobre una clave existente,
  - **entonces** la respuesta llega en menos de 500 ms (p99 medido sobre al menos 1.000 lecturas).
- **CA-01.2 — Escritura rápida con carga grande**
  - **Dado** una base de datos con 1.000.000 de claves,
  - **cuando** se ejecuta `set(clave, valor)`,
  - **entonces** la operación se confirma en menos de 500 ms (p99 medido sobre al menos 1.000 escrituras).
- **CA-01.3 — Clave inexistente**
  - **Dado** una clave que no existe,
  - **cuando** se ejecuta `get(clave)`,
  - **entonces** se devuelve el resultado "no encontrada" también en menos de 500 ms.
- **CA-01.4 — Prueba automatizada**
  - **Dado** el conjunto de pruebas de rendimiento,
  - **cuando** se ejecutan en el entorno de integración continua,
  - **entonces** fallan si algún p99 supera los 500 ms.

**Análisis INVEST**

| Criterio | Cumplimiento |
|----------|--------------|
| Independent | Depende solo de tener un núcleo `set/get`; puede probarse aislada. |
| Negotiable | El umbral de volumen y el percentil son negociables con el cliente. |
| Valuable | Es un requisito explícito del cliente (respuesta instantánea). |
| Estimable | Es una prueba de rendimiento con umbral claro (5 puntos). |
| Small | Cabe en un sprint. |
| Testable | Verificable con cronometraje automatizado. |

---

### US-02 — Índice hash en memoria para grandes volúmenes

**Requisito:** R1 (Volumen y rendimiento)

> **Como** programador que almacena una cantidad masiva de datos,
> **quiero** que la base de datos mantenga un mapa hash en memoria con la posición de cada clave en el archivo,
> **para** leer cualquier valor con un único `f.seek()` sin recorrer todo el log.

**Criterios de aceptación**

- **CA-02.1 — Acceso directo por posición**
  - **Dado** un log con 1.000.000 de registros,
  - **cuando** se ejecuta `get(clave)`,
  - **entonces** el sistema consulta el mapa hash, obtiene el desplazamiento y lee el valor con `f.seek()` sin escanear el archivo.
- **CA-02.2 — Índice actualizado en escritura**
  - **Dado** una clave existente,
  - **cuando** se ejecuta `set(clave, nuevo_valor)`,
  - **entonces** el índice apunta al nuevo registro y `get(clave)` devuelve el valor más reciente.
- **CA-02.3 — Coste de lectura independiente del tamaño**
  - **Dado** dos bases de datos, una de 10.000 y otra de 1.000.000 de claves,
  - **cuando** se mide `get(clave)` en ambas,
  - **entonces** el tiempo no crece de forma proporcional al número de registros.
- **CA-02.4 — Reconstrucción del índice**
  - **Dado** un archivo de log existente,
  - **cuando** se abre la base de datos,
  - **entonces** el mapa hash se reconstruye leyendo el log y refleja el último valor de cada clave.

**Análisis INVEST**

| Criterio | Cumplimiento |
|----------|--------------|
| Independent | Se desarrolla sobre el formato de log definido en US-05, sin depender del resto. |
| Negotiable | La estructura del índice (`dict`) y su contenido pueden ajustarse. |
| Valuable | Es la razón de que la lectura sea rápida con datos masivos. |
| Estimable | Diseño conocido: `dict` de clave a desplazamiento (5 puntos). |
| Small | Cabe en un sprint. |
| Testable | Se comprueba con pruebas de correctitud y de escalado. |

---

### US-03 — Operación continua 24/7 y recuperación tras reinicio

**Requisito:** R2 (Disponibilidad y seguridad)

> **Como** responsable de operaciones de un sistema que trabaja 24/7, incluidos los turnos nocturnos,
> **quiero** que la base de datos funcione de forma continua y se recupere sola tras un reinicio o una caída,
> **para** no depender de intervención manual y no interrumpir el servicio por la noche.

**Criterios de aceptación**

- **CA-03.1 — Funcionamiento prolongado**
  - **Dado** la base de datos en funcionamiento con operaciones continuas,
  - **cuando** transcurren al menos 24 horas de prueba de estabilidad,
  - **entonces** no se producen caídas ni un aumento sostenido del consumo de memoria (sin fugas).
- **CA-03.2 — Recuperación automática**
  - **Dado** que el proceso se interrumpe y se vuelve a lanzar,
  - **cuando** se abre la base de datos,
  - **entonces** el índice se reconstruye desde el log sin intervención manual y los datos previos siguen disponibles.
- **CA-03.3 — Tiempo de arranque acotado**
  - **Dado** un log con 1.000.000 de registros,
  - **cuando** se reinicia el servicio,
  - **entonces** el tiempo de recuperación se mide, se documenta y queda dentro del objetivo acordado con el cliente.
- **CA-03.4 — Errores controlados**
  - **Dado** un error de E/S (por ejemplo, disco lleno),
  - **cuando** ocurre durante una operación,
  - **entonces** el sistema informa con una excepción clara y no queda en un estado inconsistente.

**Análisis INVEST**

| Criterio | Cumplimiento |
|----------|--------------|
| Independent | Se apoya en el log de US-05, pero puede desarrollarse en paralelo con un contrato claro. |
| Negotiable | El tiempo de arranque y la duración de la prueba son negociables. |
| Valuable | Responde al requisito de operación continua 24/7. |
| Estimable | Alcance acotado (5 puntos). |
| Small | Cabe en un sprint. |
| Testable | Prueba de estabilidad y simulación de reinicios. |

---

### US-04 — Fiabilidad ante fallos y protección de integridad

**Requisito:** R2 (Disponibilidad y seguridad)

> **Como** responsable de datos extremadamente importantes,
> **quiero** que un corte de energía o un fallo del proceso nunca corrompa ni haga perder los datos ya confirmados,
> **para** confiar en que la información almacenada es íntegra y fiable.

**Criterios de aceptación**

- **CA-04.1 — Escritura confirmada es escritura persistida**
  - **Dado** que `set` devuelve confirmación,
  - **cuando** el proceso se interrumpe inmediatamente después,
  - **entonces** el dato está en disco y se recupera al reiniciar.
- **CA-04.2 — Registro final incompleto**
  - **Dado** que el proceso se cortó a mitad de una escritura y el último registro quedó truncado,
  - **cuando** se abre la base de datos,
  - **entonces** el registro incompleto se detecta y se ignora, y todos los registros anteriores permanecen intactos.
- **CA-04.3 — Detección de corrupción**
  - **Dado** un registro cuyo contenido fue alterado,
  - **cuando** se lee o se reconstruye el índice,
  - **entonces** se detecta mediante una comprobación de integridad (por ejemplo, una suma de verificación por registro) y se informa del error sin devolver datos falsos.
- **CA-04.4 — Sin modificaciones sobre lo ya escrito**
  - **Dado** un registro ya grabado,
  - **cuando** se realizan operaciones posteriores,
  - **entonces** el archivo solo crece por el final y los datos anteriores no se sobrescriben.
- **CA-04.5 — Prueba de fallos**
  - **Dado** un conjunto de pruebas que simulan interrupciones en distintos puntos de la escritura,
  - **cuando** se ejecutan,
  - **entonces** ninguna produce pérdida de datos confirmados ni corrupción.

**Análisis INVEST**

| Criterio | Cumplimiento |
|----------|--------------|
| Independent | Se basa en el formato de log, con criterios verificables por separado. |
| Negotiable | El mecanismo (suma de verificación, política de sincronización a disco) se decide en el sprint. |
| Valuable | Cubre "alta seguridad/fiabilidad ante fallos" para datos críticos. |
| Estimable | Tiene incertidumbre técnica media; se estima en 8 puntos. |
| Small | Puede dividirse en dos si el equipo lo considera necesario (persistencia / detección de corrupción). |
| Testable | Verificable con inyección de fallos y pruebas de truncado. |

---

### US-05 — Registro histórico append-only con lápidas

**Requisito:** R3 (Trazabilidad)

> **Como** auditor del flujo de trabajo,
> **quiero** que cada alta, modificación y borrado quede registrado en un log histórico de solo escritura al final, con los borrados marcados mediante lápidas,
> **para** poder reconstruir y revisar en cualquier momento qué ocurrió con cada dato.

**Criterios de aceptación**

- **CA-05.1 — Alta registrada**
  - **Dado** una clave nueva,
  - **cuando** se ejecuta `set(clave, valor)`,
  - **entonces** se añade un registro al final del log con la clave, el valor y el orden de la operación.
- **CA-05.2 — Modificación conserva el historial**
  - **Dado** una clave existente,
  - **cuando** se ejecuta `set(clave, otro_valor)`,
  - **entonces** se añade un nuevo registro sin borrar el anterior, y `get` devuelve el más reciente.
- **CA-05.3 — Borrado mediante lápida**
  - **Dado** una clave existente,
  - **cuando** se ejecuta `delete(clave)`,
  - **entonces** se añade un registro de tipo lápida (tombstone) al log, la clave deja de estar disponible en `get` y el historial anterior permanece en el archivo.
- **CA-05.4 — Reconstrucción respetando lápidas**
  - **Dado** un log con altas, modificaciones y borrados,
  - **cuando** se reconstruye el índice al abrir la base de datos,
  - **entonces** las claves cuyo último registro es una lápida no aparecen en el índice.
- **CA-05.5 — Orden auditable**
  - **Dado** el archivo de log,
  - **cuando** se recorre de principio a fin,
  - **entonces** las operaciones aparecen en el orden exacto en que se realizaron.

**Análisis INVEST**

| Criterio | Cumplimiento |
|----------|--------------|
| Independent | Es la base del formato de datos; no depende de otras historias. |
| Negotiable | El formato del registro es negociable dentro de las restricciones del cliente. |
| Valuable | Cubre directamente el requisito de auditoría constante. |
| Estimable | Diseño claro: alta, modificación y lápida (5 puntos). |
| Small | Cabe en un sprint. |
| Testable | Se verifica inspeccionando el log tras secuencias de operaciones. |

---

### US-06 — API sencilla para programadores Python

**Requisito:** R4 (Perfil de usuario y tecnologías)

> **Como** programador Python,
> **quiero** leer, escribir y modificar datos con una API mínima e intuitiva (`set`, `get`, `delete`),
> **para** integrar la base de datos en mi proyecto en pocos minutos y sin aprender un sistema complejo.

**Criterios de aceptación**

- **CA-06.1 — Uso básico en pocas líneas**
  - **Dado** un proyecto Python con la librería instalada,
  - **cuando** se escriben `db.set("clave", "valor")` y `db.get("clave")`,
  - **entonces** el valor se guarda y se recupera correctamente sin configuración adicional.
- **CA-06.2 — Modificación y borrado**
  - **Dado** una clave existente,
  - **cuando** se usa `set` con un nuevo valor o `delete`,
  - **entonces** el cambio se refleja inmediatamente en las lecturas posteriores.
- **CA-06.3 — Sin dependencias externas**
  - **Dado** un entorno Python limpio,
  - **cuando** se instala y se usa la librería,
  - **entonces** funciona solo con la biblioteca estándar de Python.
- **CA-06.4 — Documentación con ejemplo**
  - **Dado** el README del repositorio,
  - **cuando** un programador lo lee,
  - **entonces** encuentra un ejemplo completo de uso que puede ejecutar de inmediato.
- **CA-06.5 — Errores comprensibles**
  - **Dado** un uso incorrecto (por ejemplo, un tipo de clave no admitido),
  - **cuando** se ejecuta la operación,
  - **entonces** se lanza una excepción con un mensaje claro.

**Análisis INVEST**

| Criterio | Cumplimiento |
|----------|--------------|
| Independent | Es la capa pública sobre el núcleo; puede desarrollarse con una implementación provisional. |
| Negotiable | Los nombres de método y la firma pueden ajustarse. |
| Valuable | Cumple la exigencia de la BD clave-valor más sencilla posible para programadores. |
| Estimable | API pequeña y conocida (3 puntos). |
| Small | Cabe en un sprint. |
| Testable | Se valida con pruebas unitarias y con el ejemplo del README. |

---

### US-07 — Multiplataforma, equipos antiguos y codificación robusta

**Requisito:** R5 (Compatibilidad y entorno)

> **Como** responsable de despliegue con clientes internacionales (por ejemplo, en Rusia),
> **quiero** que la base de datos funcione en distintos sistemas operativos y en equipos antiguos, y que guarde y recupere texto en cualquier idioma sin errores,
> **para** poder instalarla en el entorno de cada cliente y no perder ni deformar sus datos.

**Criterios de aceptación**

- **CA-07.1 — Varios sistemas operativos**
  - **Dado** las pruebas automatizadas,
  - **cuando** se ejecutan en Windows, Linux y macOS,
  - **entonces** todas pasan sin cambios en el código.
- **CA-07.2 — Versiones de Python soportadas**
  - **Dado** las versiones de Python definidas como soportadas (incluidas las más antiguas acordadas con el cliente),
  - **cuando** se ejecuta la suite de pruebas en cada una,
  - **entonces** todas pasan.
- **CA-07.3 — Recursos limitados**
  - **Dado** un equipo antiguo de referencia (por ejemplo, 2 núcleos y 4 GB de RAM),
  - **cuando** se ejecutan las pruebas de rendimiento de US-01,
  - **entonces** se cumple el límite de 500 ms o se documenta el volumen máximo admitido en ese equipo.
- **CA-07.4 — Codificación explícita UTF-8**
  - **Dado** que el archivo se abre siempre con codificación UTF-8 explícita, independiente de la configuración regional del sistema,
  - **cuando** se guarda el valor `"Привет, мир"` (cirílico) con la clave `"cliente_Москва"`,
  - **entonces** `get` devuelve exactamente el mismo texto, en Windows, Linux y macOS.
- **CA-07.5 — Desplazamientos correctos con caracteres multibyte**
  - **Dado** valores con caracteres de varios bytes (cirílico, tildes, emojis),
  - **cuando** se leen mediante `f.seek()`,
  - **entonces** los desplazamientos se calculan en **bytes** (no en caracteres) y el valor se recupera sin truncarse ni corromperse.
- **CA-07.6 — Saltos de línea consistentes**
  - **Dado** que el mismo archivo de log se crea en un sistema operativo y se abre en otro,
  - **cuando** se reconstruye el índice,
  - **entonces** los datos se leen correctamente sin diferencias por el formato de fin de línea.

**Análisis INVEST**

| Criterio | Cumplimiento |
|----------|--------------|
| Independent | Se valida como conjunto de pruebas transversales, sin depender de una funcionalidad concreta. |
| Negotiable | La lista de sistemas operativos y versiones de Python se acuerda con el cliente. |
| Valuable | Cubre el requisito de compatibilidad e internacionalización. |
| Estimable | Alcance definido en 5 puntos. |
| Small | Cabe en un sprint. |
| Testable | Se verifica con integración continua en varios sistemas y con datos en cirílico. |

---

## 7. Orden de trabajo propuesto

| Sprint | Historias | Objetivo |
|--------|-----------|----------|
| Sprint 0 | — | Repositorio, estructura del proyecto, herramientas de pruebas, CI y decisiones sobre versiones de Python y sistemas operativos |
| Sprint 1 | US-06, US-05, US-01 | Núcleo funcional: API, log append-only con lápidas y primera medición de rendimiento |
| Sprint 2 | US-02, US-03 | Índice hash con `f.seek()`, reconstrucción y recuperación continua |
| Sprint 3 | US-04, US-07 | Robustez ante fallos y compatibilidad multiplataforma con UTF-8 |

## 8. Riesgos identificados

| Riesgo | Impacto | Mitigación |
|--------|---------|------------|
| El log crece indefinidamente por su naturaleza append-only | Mayor uso de disco y arranques más lentos | Registrar como historia futura la compactación, siempre que no vaya contra la auditoría del cliente (R3) |
| El índice completo debe caber en memoria | Límite en equipos antiguos | Documentar el volumen máximo admitido (CA-07.3) |
| Garantizar persistencia puede afectar a la latencia | Riesgo para los 500 ms | Medir ambos objetivos juntos en las pruebas de US-01 y US-04 |
| Requisitos cualitativos poco definidos | Retrabajo | Validar los supuestos de la sección 3 en la primera revisión con el cliente |
