# Kairós

## Descripción del problema

Kairós es una herramienta integral capaz de definir y eficientar los recursos necesarios para el Departamento Omnicanal de El Corte Inglés. Utiliza un modelo dinámico y escalable para facilitar la toma de decisiones y mejorar la productividad alineada con las necesidades reales del negocio. En términos operativos, la herramienta prevé la demanda a partir de datos reales y automatiza la planificación de la plantilla, distribuyendo las horas según el volumen de trabajo proyectado y las habilidades de cada trabajador.

Esta solución resuelve el problema combinatorio de asignar tareas, turnos y días, minimizando simultáneamente la sobrecobertura y la infracobertura de personal.

## Arquitectura y tecnologías

Kairós se sostiene sobre tres capas principales

- Base de Datos: Diseñada en MySQL con un modelo relacional para garantizar la integridad referencial entre trabajadores, contratos, tareas, turnos y periodos de disponibilidad.
- Backend: Desarrollado en Python utilizando el framework Flask. En esta capa se ejecutan los tres modelos analíticos de la herramienta:
  - Previsión de demanda: Modelo de series temporales utilizando la librería Prophet para proyectar las líneas diarias.
  - Optimización de horas: Programación lineal entera mixta implementada con la librería PuLP.
  - Calendarización: Asignación nominal mediante programación con restricciones utilizando Google OR-Tools.
- Frontend: Desarrollado con HTML, CSS y JavaScript. El código de la interfaz mantiene separadas la estructura, el diseño y el comportamiento, ubicando las plantillas HTML, las hojas de estilo y los ficheros JavaScript en directorios independientes.

## Módulos de la aplicación

- La interfaz se organiza en distintas secciones accesibles desde un menú lateral:
  - Dashboard: Ofrece una vista agregada del estado general de los datos cargados mediante tarjetas resumen e indicadores clave.
  - Gestión de datos: Administra la información estable del centro, incluyendo catálogos de contratos, tareas, perfiles de trabajadores y sus disponibilidades o restricciones horarias.
  - Datos históricos: Gestiona el histórico de líneas y el registro de promociones que alimentan el modelo predictivo. La carga masiva de información se resuelve mediante plantillas de Excel descargables que se importan desde la propia aplicación.
  - Predicción: Presenta los resultados del modelo de demanda diaria (Prophet) a través de gráficas de evolución temporal y tablas con intervalos de confianza.
  - Planificación: Muestra la calendarización final en dos vistas complementarias, una semanal por tarea y turno, y otra vista mensual de calendarios por trabajador.
 
## Configuración y Despliegue

- Seguridad y Credenciales: Los parámetros de conexión con la base de datos se gestionan mediante variables de entorno externas al código fuente, de forma que las credenciales de acceso no se exponen en el repositorio.
- Importación de datos: La herramienta valida la estructura y el contenido de los archivos Excel mediante la librería Pandas antes de escribir en la base de datos, garantizando la integridad de la información.


## Impacto y sostenibilidad

El diseño de Kairós tiene un impacto directo alineado con la Agenda 2030 de Naciones Unidas:
- ODS 8 (Trabajo decente y crecimiento económico): Convierte las condiciones pactadas en el convenio y las circunstancias personales en restricciones que el modelo debe satisfacer necesariamente, garantizando su cumplimiento por construcción algorítmica.
- ODS 3 (Salud y bienestar): La previsión anticipada facilita la organización personal de la plantilla, reduciendo la incertidumbre al conocer los turnos con antelación.
- ODS 10 (Reducción de las desigualdades): El algoritmo aplica los mismos criterios a toda la plantilla en cada ejecución, evitando desigualdades y ofreciendo un registro trazable y objetivo de las asignaciones.
