from copy import deepcopy
import time
from uuid import uuid4
from fastapi import Cookie, FastAPI, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app=FastAPI()
app.add_middleware(CORSMiddleware, 
                   allow_origins=["*","http://localhost:8000"],
                   allow_credentials=True
                   )

class PixelChange(BaseModel):
    x: int
    y: int
    r: int
    g: int
    b: int

class UserInfo:
    last_edited_time_nanos: int 
    last_seen_map: list[list[tuple[int,int,int]]]
    def __init__(self,carte):
        self.last_seen_map= deepcopy(carte)
        self.last_edited_time_nanos= 0

class Carte:
    keys : set[str]
    users: dict[str,]
    nx: int
    ny: int
    data: list[list[tuple[int,int,int]]]
    timeout_nanos: int  # en nanosecondes
    def __init__(self, nx, ny, timeout_nanos=10000000000):
        self.keys=set()
        self.users={}
        self.nx=nx
        self.ny=ny
        self.data=[
            [ (0,0,0) for _ in range(ny)]
            for _ in range(nx)]  #tableau nx lignes ny colonnes
        self.timeout_nanos=timeout_nanos

    def create_new_key(self):
        key=str(uuid4())
        self.keys.add(key)
        return key
    
    def is_valid_key(self,key):
        return key in self.keys
    
    def create_new_user_id(self):
        user_id=str(uuid4())
        self.users[user_id]=UserInfo(self.data)
        return user_id
    
    def is_valid_user_id(self, user_id):
        return user_id in self.users
    pass

Cartes: dict[str, Carte]= {"0000": Carte(nx=10,ny=10),}

@app.get('/api/v1/{nom_carte}/preinit')  # crée la clé
async def preinit(nom_carte: str):
    carte=Cartes[nom_carte]
    
    key=carte.create_new_key()  #créer une clé universelle unique
    res = JSONResponse({"key":key})
    res.set_cookie("key", key, httponly=True, samesite="none", max_age=3600)
    return res

@app.get('/api/v1/{nom_carte}/init')  #crée l'identifiant via la clé
async def init(nom_carte: str, 
               query_key: str = Query(alias="keys"),
               cookie_key: str= Cookie(alias="key")
               ):
    carte=Cartes[nom_carte]
    if not carte:
        return {"error":"Je n'ai pas trouvé le nom de la carte"}
    if query_key != cookie_key:
        return {"error":"Les clés ne correspondent pas"}
    if not carte.is_valid_key(cookie_key):
        return {"error":"La clé n'est pas valide"}
    user_id=carte.create_new_user_id()
    res=JSONResponse( {"id": user_id,
            "nx": carte.nx,
            "ny": carte.ny,
            "timeout": carte.timeout_nanos,
            "data": carte.data})
    res.set_cookie("id", user_id, httponly=True, samesite="none", max_age=3600)
    return res

@app.get('/api/v1/{nom_carte}/deltas')  #renvoie les tableau position + RGB des pixels qui ont changés depuis la dernière fois
async def deltas(nom_carte: str, 
               query_user_id: str = Query(alias="id"),
               cookie_user_id: str= Cookie(alias="id"),
               cookie_key: str= Cookie(alias="key")
               ):
    carte=Cartes[nom_carte]
    if not carte:
        return {"error":"Je n'ai pas trouvé le nom de la carte"}
    if not carte.is_valid_key(cookie_key):
        return {"error":"La clé n'est pas valide"}
    if query_user_id != cookie_user_id:
        return {"error":"Les id utilisateurs ne correspondent pas"}
    if not carte.is_valid_user_id(query_user_id):
        return {"error":"L'id n'est pas valide"}
    
    user_info = carte.users[query_user_id]
    user_carte=user_info.last_seen_map
    deltas=[]
    for x in range(carte.nx):
        for y in range(carte.ny):
            if carte.data[x][y]!=user_carte[x][y]:
                r,g,b=carte.data[x][y]
                deltas.append([x,y,r,g,b])

    return {"id": query_user_id,
            "nx": carte.nx,
            "ny": carte.ny,
            "deltas": deltas,
            }



@app.post("/api/v1/{nom_carte}/set_pixel")  # pour mettre à jour les pixels
async def set_pixel(nom_carte: str,
                    pixel: PixelChange,
                    user_id: str = Cookie(alias="id"),
                    key: str = Cookie(alias="key")):
    
    carte = Cartes.get(nom_carte)
    if not carte:
        return {"error": "Carte non trouvée."}
    
    if not carte.is_valid_key(key):
        return {"error": "Clé invalide."}
    
    if not carte.is_valid_user_id(user_id):
        return {"error": "ID utilisateur invalide."}
    
    if not (0 <= pixel.x < carte.nx and 0 <= pixel.y < carte.ny):
        return {"error": "Coordonnées hors limites."}
    
    if not all(0 <= v <= 255 for v in (pixel.r, pixel.g, pixel.b)):
        return {"error": "Valeurs RGB invalides."}
    
    user = carte.users[user_id]
    now = time.time_ns()

    if now - user.last_edited_time_nanos < carte.timeout_nanos:   # check un écart minimum
        wait_ms = (carte.timeout_nanos - (now - user.last_edited_time_nanos)) // 1_000_000
        return {"error": f"Trop rapide. Attendez {wait_ms} ms."}
    
    # Tout est valide : mise à jour du pixel
    carte.data[pixel.x][pixel.y] = (pixel.r, pixel.g, pixel.b)
    user.last_edited_time_nanos = now

    return {"success": True, "x": pixel.x, "y": pixel.y, "color": (pixel.r, pixel.g, pixel.b)}
