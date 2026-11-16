# HabitPulse — Guía de Desarrollo y Distribución de Tareas del Equipo

Este documento contiene la guía técnica detallada para que cada integrante del equipo desarrolle sus funcionalidades en ramas dedicadas, respetando la arquitectura, la base de datos y evitando conflictos en Git.

---

## 👥 Resumen de Ramas Oficiales

| Integrante | Rol Oficial | Rama de Trabajo en Git |
| :--- | :--- | :--- |
| **Manuel David Tineo Esquerre** | Integrante 3 (Frontend & UX) | `feature/configuracion-perfil-temas` |
| **Diego Manuel Mio Purizaca** | Integrante 1 (Backend & IA) | `feature/backend-ia-gemini-asistente` |
| **Edickson Joel Salvador García** | Integrante 2 (Base de Datos) | `feature/database-sqlite-fallback-docker` |
| **Jose Luis Silva Silupu** | Integrante 4 (Pruebas & QA) | `feature/qa-suite-pruebas-ci` |

---

## 1. Guía para Diego Manuel Mio Purizaca (Backend + IA)
**Objetivo:** Conectar el módulo de IA con la interfaz del Asistente y permitir recomendaciones predictivas inteligentes.

### 🌿 Rama de trabajo:
```bash
git checkout -b feature/backend-ia-gemini-asistente
```

### 📁 Archivos a Modificar / Crear:
1. **`AI/ai_service.py` (Crear o actualizar):**
   - Implementar la clase `AIService` que unifique `habit_analyzer.py` y `recommendation_engine.py`.
   - Incorporar la función `generar_respuesta_asistente(pregunta_usuario, habitos_en_riesgo, usuario_info)`:
     - Si está configurada la variable `GEMINI_API_KEY` en `.env`, realizar la consulta con el prompt de `AI/prompts.py`.
     - Si no hay conexión o no hay clave, aplicar el motor de reglas offline de `AI/recommendation_rules.py`.
2. **`proyecto/screens/asistente_screen.py` (Modificar):**
   - En el método `enviar_mensaje()`, reemplazar las respuestas fijas por una llamada asíncrona o directa a `AIService.generar_respuesta_asistente`.
   - Vincular los hábitos en riesgo detectados por `auditar_habitos_desercion()` como contexto para las respuestas.
3. **`proyecto/.env.example` (Actualizar):**
   - Añadir la variable de entorno:
     ```env
     GEMINI_API_KEY=tu_api_key_de_google_gemini
     ```

### 🧪 Cómo probarlo:
1. Entrar a la app, ir a la pestaña **Asistente**.
2. Escribir en el chat: *"¿Qué hábito tengo en riesgo de abandono y cómo puedo mejorarlo?"*.
3. El asistente debe responder mencionando el hábito con bajo porcentaje y recomendando una micro-rutina específica.

---

## 2. Guía para Edickson Joel Salvador García (Base de Datos + Persistencia)
**Objetivo:** Garantizar persistencia automática (con fallback a SQLite local) y despliegue rápido con Docker.

### 🌿 Rama de trabajo:
```bash
git checkout -b feature/database-sqlite-fallback-docker
```

### 📁 Archivos a Modificar / Crear:
1. **`proyecto/database.py` (Modificar):**
   - Implementar un fallback automático: si la conexión a PostgreSQL con `psycopg2` falla (`OperationalError` / servidor apagado), la clase `BaseDatos` debe inicializar automáticamente una base de datos local SQLite (`habitpulse.db`).
   - Crear las tablas en SQLite con el mismo esquema V2 (`usuarios`, `habitos`, `registros_habitos`, `metas`, `recordatorios`).
   - Esto asegura que la aplicación guarde datos reales y funcione en cualquier máquina sin necesidad de configurar PostgreSQL.
2. **`docker-compose.yml` (Crear en la raíz del repositorio):**
   - Configurar el contenedor oficial de PostgreSQL:
     ```yaml
     version: '3.8'
     services:
       db:
         image: postgres:15-alpine
         container_name: habitpulse_db
         restart: always
         environment:
           POSTGRES_USER: postgres
           POSTGRES_PASSWORD: postgrespassword
           POSTGRES_DB: habitpulse_db
         ports:
           - "5432:5432"
         volumes:
           - postgres_data:/var/lib/postgresql/data
           - ./Documentación/base-datos/seed.sql:/docker-entrypoint-initdb.d/seed.sql:ro
     volumes:
       postgres_data:
     ```
3. **`Documentación/base-datos/seed.sql` (Verificar / Actualizar):**
   - Asegurar que contenga datos de prueba iniciales: 1 usuario demo con password bcrypt, 4 hábitos con diferentes categorías y registros históricos de la última semana.

### 🧪 Cómo probarlo:
1. Apagar cualquier servicio de PostgreSQL y abrir la app: debe funcionar guardando en `habitpulse.db`.
2. Ejecutar `docker compose up -d` y verificar que la app se conecte a PostgreSQL en el puerto 5432 sin errores.

---

## 3. Guía para Jose Luis Silva Silupu (Inteligencia + Pruebas Unitarias & QA)
**Objetivo:** Crear la suite formal de pruebas unitarias con `pytest` y configurar la integración continua (CI/CD).

### 🌿 Rama de trabajo:
```bash
git checkout -b feature/qa-suite-pruebas-ci
```

### 📁 Archivos a Crear:
1. **`tests/__init__.py`:** Archivo vacío para declarar el paquete de pruebas.
2. **`tests/test_gamificacion.py`:**
   - Test 1: Verificar que un usuario con 0 XP comience en Nivel 1 ("Novato Constante").
   - Test 2: Verificar que con 950 XP alcance el Nivel 4 ("Titán de la Rutina").
   - Test 3: Verificar que un hábito con 7 días de racha desbloquee la insignia *"Racha de Fuego"*.
3. **`tests/test_tracking.py`:**
   - Test 1: Validar `calcular_tasa_cumplimiento` con 7 días de registros (ej. 5 días cumplidos de 7 = 71.43%).
   - Test 2: Validar `detectar_riesgo_abandono` devolviendo `True` cuando el cumplimiento es menor al 50%.
4. **`tests/test_database.py`:**
   - Test 1: Validar que `encriptar_contrasena` genere un hash válido con `bcrypt`.
   - Test 2: Validar que `verificar_contrasena` retorne `True` para la contraseña correcta y `False` para una errónea.
5. **`.github/workflows/ci.yml` (Integración Continua):**
   - Configurar GitHub Actions para que en cada Pull Request a `main` ejecute:
     ```yaml
     name: CI Testing
     on: [push, pull_request]
     jobs:
       test:
         runs-on: ubuntu-latest
         steps:
           - uses: actions/checkout@v3
           - name: Set up Python
             uses: actions/setup-python@v4
             with:
               python-version: '3.12'
           - name: Install dependencies
             run: |
               pip install -r requirements.txt pytest
           - name: Run tests
             run: pytest tests/ -v
     ```

### 🧪 Cómo probarlo:
1. En la terminal ejecutar:
   ```bash
   pytest tests/ -v
   ```
2. Todos los tests deben pasar en verde (`PASSED`).

---

## 4. Trabajo en Nuestra Rama (Manuel David Tineo Esquerre)
**Rama activa:** `feature/configuracion-perfil-temas`
- Unificación del Navigation Rail de escritorio en las pantallas secundarias (`Metas`, `Recordatorios`, `Asistente`, `Perfil`).
- Mantenimiento del sistema de temas claro/oscuro y paletas reactivas.
- Sincronización de los módulos de presentación con los servicios del backend.

---

## 🚀 Flujo para Subir Cambios y Crear Pull Requests
Cada integrante debe seguir este procedimiento en su terminal:
1. Guardar y confirmar sus cambios:
   ```bash
   git add .
   git commit -m "feat(modulo): descripción clara de la funcionalidad"
   ```
2. Subir su rama al repositorio remoto de GitHub:
   ```bash
   git push -u origin <nombre-de-su-rama>
   ```
3. Ir a GitHub y abrir el **Pull Request** hacia la rama `main`.
