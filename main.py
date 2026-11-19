from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import psycopg2

app = FastAPI(title="API Geovisor Armenia - Laura Karina")

# Configuración CORS más permisiva para desarrollo local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False, # Cámbialo a False si usas "*"
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_CONFIG = {
    "host": "localhost",
    "database": "Armenia_Riesgo",
    "user": "postgres",
    "password": "TU_CONTRASEÑA_AQUI", # <-- Cámbialo aquí
    "port": "5432"
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

@app.get("/comunas")
def get_comunas():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id_comuna, nombre, ST_AsGeoJSON(geom)::json FROM public.comuna;')
    rows = cur.fetchall()
    cur.close()
    conn.close()
    
    features = [{
        "type": "Feature",
        "properties": {"id": row[0], "nombre": row[1]},
        "geometry": row[2]
    } for row in rows]
    return {"type": "FeatureCollection", "features": features}

@app.get("/comunas/{id_comuna}/manzanas")
def get_manzanas_comuna(id_comuna: int):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM manzana WHERE id_comuna = %s;", (id_comuna,))
    total = cur.fetchone()[0]
    cur.close()
    conn.close()
    return {"comuna_id": id_comuna, "total_manzanas": total}

# CONSULTA DE RIESGO (Corregida para traer Categoría Específica)
@app.get("/riesgo")
def consultar_riesgo(lon: float, lat: float):
    conn = get_db_connection()
    cur = conn.cursor()
    
    # 1. Buscamos en qué comuna está el punto
    cur.execute("""
        SELECT id_comuna, nombre 
        FROM public.comuna 
        WHERE ST_Covers(geom, ST_SetSRID(ST_MakePoint(%s, %s), 4326))
        LIMIT 1;
    """, (lon, lat))
    comuna = cur.fetchone()
    
    if not comuna:
        cur.close()
        conn.close()
        return {"en_riesgo": False, "comuna":"", "mensaje": "El punto está fuera de los límites de Armenia."}

    id_comuna, nombre_comuna = comuna

    # 2. Buscamos si esa comuna tiene una amenaza asociada
    # Nota: Hacemos JOIN por id_comuna ya que creamos la llave foránea antes
    cur.execute("""
        SELECT "NOMBRE_VOLCAN", "GRADO_AMENAZA", "CATEGORIA_ESPECIFICA_FENOMENO" 
        FROM public.amenaza 
        WHERE id_comuna = %s 
        LIMIT 1;
    """, (id_comuna,))
    amenaza = cur.fetchone()
    
    cur.close()
    conn.close()
    
    if amenaza:
        return {
            "en_riesgo": True, 
            "comuna": nombre_comuna,
            "volcan": amenaza[0], 
            "nivel": amenaza[1], 
            "fenomeno": amenaza[2]
        }
    else:
        return {
            "en_riesgo": False, 
            "comuna": nombre_comuna,
            "mensaje": "Esta comuna no tiene zonas de amenaza volcánica registradas."
        }

# CONSULTA DE BARRIOS (Blindada contra errores de texto)
@app.get("/barrios/{id_comuna}")
def get_barrios(id_comuna: int):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Usamos una expresión regular para asegurarnos de que solo convertimos a entero si es un número válido
        # Si NOCOMUNA tiene espacios, hacemos TRIM primero.
        cur.execute("""
            SELECT "NOMBRE" FROM public.barrio 
            WHERE TRIM("NOCOMUNA") ~ '^[0-9]+$' 
            AND CAST(TRIM("NOCOMUNA") AS INTEGER) = %s;
        """, (id_comuna,))
        barrios = [row[0] for row in cur.fetchall()]
    except Exception as e:
        print(f"Error en barrios: {e}")
        barrios = []
    finally:
        cur.close()
        conn.close()
        
    return {"comuna_num": id_comuna, "total_barrios": len(barrios), "lista_barrios": barrios}

@app.get("/amenazas")
def get_amenazas():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id_amenaza, "NOMBRE_VOLCAN", "GRADO_AMENAZA", "CATEGORIA_ESPECIFICA_FENOMENO", ST_AsGeoJSON(geom)::json FROM public.amenaza;')
    rows = cur.fetchall()
    cur.close()
    conn.close()
    
    features = [{
        "type": "Feature",
        "properties": {
            "id": row[0], 
            "volcan": row[1],
            "nivel": row[2], 
            "fenomeno": row[3]
        },
        "geometry": row[4]
    } for row in rows]
    return {"type": "FeatureCollection", "features": features}