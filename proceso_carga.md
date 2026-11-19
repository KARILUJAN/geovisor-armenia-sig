# Proceso de Construcción de la Geodatabase

## 1. Obtención de insumos oficiales
* **Geometrías espaciales:** Se descargaron las capas de comunas, manzanas y amenaza volcánica desde la plataforma oficial "Colombia en Mapas" (ICDE).
* **Tabla de atributos de barrios:** Se descargó la capa de barrios desde el portal del "SIG Quindío". Esta fuente aportó los nombres de los barrios, pero no contaba con una geometría asociada ni una llave foránea directa con las manzanas.

## 2. Preparación y estandarización en QGIS
* Se cargaron las capas espaciales en QGIS para verificar su integridad geométrica (herramienta "Comprobar validez").
* Se aseguró que todas las capas estuvieran proyectadas en el sistema de referencia EPSG:4326 (WGS 84), requisito indispensable para su uso en Leaflet.
* Se exportaron las capas espaciales a la base de datos PostgreSQL/PostGIS (base de datos "Armenia_Riesgo").

## 3. Modelo relacional e integridad en PostGIS
* Una vez en PostGIS, se ejecutó el script `geodatabase_armenia.sql` para crear las llaves foráneas formales entre las tablas:
  * Tabla `manzana` relacionada con `comuna` (campo `id_comuna`).
  * Tabla `amenaza` relacionada con `comuna` (campo `id_comuna`).

## 4. Integración de la tabla de barrios mediante programación (Backend)
* La tabla `barrio` quedó alojada en PostGIS como una tabla puramente alfanumérica (sin columna geom).
* Para resolver la consulta de barrios por comuna, se implementó una lógica en el backend (FastAPI + Psycopg2) que realiza un cruce por atributos. Específicamente, en el endpoint `/barrios/{id_comuna}`, se ejecuta un `JOIN` utilizando `CAST(TRIM("NOCOMUNA") AS INTEGER) = id_comuna`. 
* Esta decisión técnica demuestra la capacidad de integrar datos de diferentes fuentes y resolver relaciones espaciales/alfanuméricas mediante el uso de SQL avanzado y programación en Python.
