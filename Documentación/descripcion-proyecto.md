# Sistema Inteligente de Control de Hábitos y Productividad

## 1. Descripción General
El **Sistema Inteligente de Control de Hábitos** es una solución móvil diseñada para acompañar a estudiantes universitarios y jóvenes en la construcción y consolidación de rutinas positivas (estudio, salud, hidratación y descanso)[cite: 3, 5]. Superando las agendas pasivas y las listas estáticas tradicionales, la plataforma incorpora persistencia relacional transaccional en PostgreSQL, gestión de metas por porcentaje, recordatorios automáticos configurables y un asistente inteligente que analiza patrones de cumplimiento para prevenir el abandono de hábitos[cite: 5, 9].

---

## 2. Alcance del Avance 2 (70% del Sistema)
En esta fase el sistema evoluciona de un registro básico a una plataforma integral con analítica e inteligencia contextual[cite: 5]:
* **Base de Datos V2:** Migración de esquema e incorporación de las entidades `metas` y `recordatorios`, vinculadas a `usuarios` y `habitos` mediante integridad referencial (`ON DELETE CASCADE`)[cite: 8, 9].
* **Persistencia Transaccional:** Conexión mediante pool en PostgreSQL con restricción de unicidad para evitar duplicidad de registros diarios (`UNIQUE(id_habito, fecha)`)[cite: 5, 9].
* **Servicio de Analítica y Rachas:** Cálculo automatizado de rachas vigentes, rachas máximas y porcentaje de avance de metas[cite: 5, 9].
* **Módulo Inteligente de Detección:** Algoritmo auditor de los últimos 7 a 14 días para identificar hábitos en riesgo de deserción (< 50% de completitud)[cite: 5].
* **Asistente Contextual:** Motor de recomendaciones oportunas para reajuste de metas y motivación guiada[cite: 4, 5].
* **Expansión Frontend (KivyMD):** Nuevas pantallas para Metas (`MDProgressBar`), Recordatorios (`MDSwitch`, TimePicker) y la interfaz interactiva del Asistente[cite: 4, 9].

---

## 3. Modelo de Datos Relacional (PostgreSQL V2)
El modelo relacional implementado en PostgreSQL garantiza integridad referencial (ACID) sobre cinco tablas normalizadas[cite: 5, 8, 9]:

1. **`usuarios`**: `id_usuario` (PK), `nombre`, `correo` (UNIQUE), `contraseña` (hash bcrypt), `fecha_registro`[cite: 8, 9].
2. **`habitos`**: `id_habito` (PK), `id_usuario` (FK), `nombre`, `categoria`, `frecuencia`[cite: 8, 9].
3. **`registros_habitos`**: `id_registro` (PK), `id_habito` (FK), `fecha`, `completado`, `comentario`[cite: 8, 9].
4. **`metas`**: `id_meta` (PK), `id_usuario` (FK), `id_habito` (FK), `titulo`, `progreso_porcentaje`, `fecha_limite`, `estado`[cite: 8, 9].
5. **`recordatorios`**: `id_recordatorio` (PK), `id_habito` (FK), `hora`, `dias_semana`, `activo`, `mensaje`[cite: 8, 9].

---

## 4. Distribución del Equipo de Desarrollo
El proyecto se distribuye entre cuatro integrantes bajo control de versiones formal en Git/GitHub[cite: 4]:

| Integrante | Rol Oficial | Módulos y Responsabilidades (Avance 2) |
| :--- | :--- | :--- |
| **Diego Manuel Mio Purizaca**[cite: 4] | **Integrante 1:** Backend + IA[cite: 4] | Arquitectura en capas, lógica del sistema, cálculo de rachas e integración del servicio de inferencia/IA[cite: 4, 5]. |
| **Edickson Joel Salvador García**[cite: 4] | **Integrante 2:** Base de Datos + Funcionalidades[cite: 4] | Modelo relacional V2 en PostgreSQL, consultas transaccionales, persistencia de `metas` y `recordatorios`[cite: 4, 9]. |
| **Manuel David Tineo Esquerre**[cite: 4] | **Integrante 3:** Frontend + UX[cite: 4] | Diseño y maquetación en Kivy/KivyMD de pantallas: Dashboard, Metas, Recordatorios e interfaz del Asistente[cite: 4, 9]. |
| **José Luis Silva Silupu**[cite: 4] | **Integrante 4:** Inteligencia + Pruebas[cite: 4] | Algoritmo de detección de bajo cumplimiento, evaluación de riesgos de abandono y suite de pruebas unitarias[cite: 4, 5]. |

---

## 5. Estructura del Proyecto
```text
Sistema-de-habitos/
│
├── .gitignore                      # Filtro de entornos (.venv), __pycache__ y temporales
├── requirements.txt                # Dependencias (Kivy, KivyMD, psycopg2-binary, bcrypt)
├── main.py                         # Punto de entrada y navegación global
│
├── config/
│   └── settings.py                 # Conexiones seguras y variables de entorno
│
├── database/                       # [Integrante 2]
│   ├── connection.py               # Pool de conexiones a PostgreSQL
│   ├── schema.sql                  # DDL de tablas V2
│   └── models/                     # Modelos y consultas SQL aisladas
│       ├── usuario_model.py
│       ├── habito_model.py
│       ├── meta_model.py
│       └── recordatorio_model.py
│
├── services/                       # [Integrantes 1 y 4]
│   ├── habito_service.py           # Cálculo formal de rachas y consistencia
│   ├── meta_service.py             # Lógica de progreso de metas
│   ├── tracking_service.py         # Detección de bajo cumplimiento / abandono
│   └── ai_service.py               # Motor de inferencia y recomendaciones
│
├── screens/                        # [Integrante 3]
│   ├── kv/                         # Vistas en Kivy Lang
│   │   ├── login_screen.kv
│   │   ├── registro_screen.kv
│   │   ├── inicio_screen.kv        # Dashboard unificado
│   │   ├── metas_screen.kv         # Barras de avance
│   │   ├── recordatorios_screen.kv # Configuración de horarios
│   │   └── asistente_screen.kv     # Interfaz del asistente inteligente
│   └── *.py                        # Controladores de pantalla asociados
│
└── tests/                          # [Integrante 4]
    ├── test_database.py            # Validación de operaciones CRUD e integridad
    └── test_tracking.py            # Validación del algoritmo de deserción
