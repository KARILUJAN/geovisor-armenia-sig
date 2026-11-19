# Geovisor SIG Web - Armenia, Quindío

**Autora:** Laura Karina Luján Arias  
**Asignatura:** Programación para SIG  
**Universidad:** Universidad del Quindío  
**Programa:** Ingeniería Topográfica y Geomática

## 1. Objetivo y Alcance
Desarrollar un visor geográfico web que permita visualizar, consultar e interactuar con las comunas de Armenia y las zonas de amenaza volcánica del Cerro Machín. El sistema permite hacer consultas espaciales para identificar en qué comuna se encuentra un punto y qué categoría específica de amenaza la afecta, así como listar los barrios y contar las manzanas pertenecientes a cada comuna.

## 2. Fuentes de Información
Los datos utilizados en este geovisor provienen exclusivamente de fuentes oficiales del Estado colombiano:

- **Datos Espaciales (Geometrías):** Los polígonos de comunas, manzanas y las zonas de amenaza volcánica fueron descargados de la plataforma **Colombia en Mapas** (Infraestructura Colombiana de Datos Espaciales - ICDE).
- **Datos Alfanuméricos (Atributos):** La tabla con los nombres de los barrios fue obtenida del **SIG Quindío** (Sistema de Información Geográfica Departamental).
- **Integración de datos:** La relación entre las manzanas y los barrios se realizó mediante consultas SQL (`JOIN` con conversión de tipo `CAST`) directamente en el backend (FastAPI + Psycopg2), permitiendo unir la información geográfica con los atributos alfanuméricos sin depender de cruces manuales en QGIS.

## 3. Arquitectura de la Aplicación
El proyecto sigue una arquitectura cliente-servidor:

- **Frontend:** HTML, CSS, JavaScript y la librería Leaflet.js.
- **Backend:** Python con FastAPI.
- **Base de Datos:** PostgreSQL con la extensión espacial PostGIS.
- **Conexión:** Psycopg2 para conectar FastAPI con PostgreSQL.
- **Comunicación:** Peticiones HTTP que devuelven JSON/GeoJSON.

## 4. Requisitos e Instrucciones de Ejecución

### Requisitos previos:
- Tener instalado PostgreSQL y PostGIS.
- Tener instalado Python 3.x.

### Pasos:

#### *1.* **Clonar el repositorio:**
```bash
git clone [https://github.com/TU_USUARIO/TU_REPOSITORIO.git](https://github.com/TU_USUARIO/TU_REPOSITORIO.git)
cd TU_REPOSITORIO
```

#### *2.* **Instalar dependencias de Python:**
Ejecuta el siguiente comando en la terminal para instalar las librerías necesarias:
```bash
pip install -r requirements.txt
```

#### *3.* **Configurar la Base de Datos:**
- Crea una base de datos en PostgreSQL (ej. `Armenia_Riesgo`).
- Ejecuta el script `geodatabase.sql` que se encuentra en este repositorio para crear la estructura y relaciones de las tablas.
- Abre el archivo `main.py` y ajusta la variable `DB_CONFIG` con tu usuario, contraseña y puerto de PostgreSQL.

#### *4.* **Ejecutar el Backend (FastAPI):**
En una terminal, ubícate en la carpeta del proyecto y ejecuta:
```bash
python -m uvicorn main:app --reload
```

#### *5.* **Ejecutar el Frontend:**
Abre el archivo `index.html` con un servidor local (por ejemplo, la extensión **Live Server** de VS Code en el puerto `5500`).

## 5. Funcionalidades Implementadas y Endpoints

- **F1. Visualización de Comunas:** `GET /comunas` — Devuelve un `GeoJSON` con los polígonos de las 10 comunas coloreados.
- **F2. Conteo de Manzanas:** `GET /comunas/{id_comuna}/manzanas` — Devuelve el total de manzanas en una comuna.
- **F3. Consulta Espacial de Riesgo:** `GET /riesgo?lon={lon}&lat={lat}` — Usa `ST_Covers` para identificar si el punto está en Armenia y `JOIN` para devolver el nombre del volcán y la categoría específica de amenaza.
- **F4. Consulta de Barrios:** `GET /barrios/{id_comuna}` — Lista los barrios pertenecientes a una comuna mediante conversión de tipos de datos.
- **Capa de Amenaza:** `GET /amenazas` — Devuelve el `GeoJSON` de las zonas de amenaza.

## 6. Demostración del Flujo Completo

Ejemplo de flujo de una consulta:

1. El usuario hace clic en una zona vacía del mapa.
2. El Frontend captura las coordenadas (`lat`, `lng`) y hace una petición HTTP a `GET /riesgo?lon=...&lat=...`.
3. FastAPI recibe los datos y ejecuta la consulta SQL en PostGIS (`ST_Covers`).
4. PostGIS responde si el punto está dentro de los límites y qué amenaza le corresponde.
5. El Backend formatea el resultado en `JSON` y lo devuelve.
6. Leaflet recibe el `JSON` y renderiza un popup (chincheta) con los datos exactos: *"Comuna: Quimbaya, Amenaza Alta, Categoría: Flujo de piroclastos"*.

## 7. Evidencias Técnicas
Las capturas de pantalla que demuestran el funcionamiento del visor se encuentran en la carpeta [`evidencias/`](./evidencias) de este repositorio. 

Allí podrá encontrar:
1. Visualización de la capa de comunas y consulta de barrios en la barra lateral.
2. Popup con la consulta espacial de amenaza volcánica (Volcán Cerro Machín).
3. Validación de puntos fuera de los límites del municipio.
4. Diagrama Entidad-Relación (ERD) demostrando las llaves foráneas.
5. Consulta SQL directa en PostgreSQL verificando las llaves primarias y foráneas.
