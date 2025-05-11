from fastapi import FastAPI, Request 
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import random
import os

app = FastAPI()

static_path = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_path), name="static")
templates = Jinja2Templates(directory="templates")

# Liste de mots valides (non exhaustive...)
MOT = [
    "aimer", "abime", "acier", "actif", "adept", "aigle", "aimer", "alias", "amour", "angle",
    "anime", "appel", "arbre", "arche", "argon", "avion", "avert", "aube", "audit", "aussi",
    "balai", "banal", "barbe", "basil", "basse", "beaux", "beret", "berce", "bible", "bijou",
    "blanc", "bleue", "blocs", "boire", "bonne", "bouche", "boute", "brace", "bruit", "bravo",
    "cable", "cadre", "calme", "canon", "carre", "ceint", "celui", "chaud", "chien", "choix",
    "chute", "clair", "clown", "coeur", "colis", "corps", "creer", "crois", "cycle", "cible",
    "danse", "debut", "deuil", "diner", "donne", "douce", "drape", "droit", "durci", "echec",
    "eclat", "ecole", "ecrit", "effet", "elite", "email", "emile", "enjeu", "entre", "envie",
    "epice", "escal", "esprit", "etage", "etang", "etude", "evite", "exact", "exige", "exile",
    "fable", "facil", "faire", "femme", "ferme", "fiche", "filme", "fixer", "flanc", "fleur",
    "folie", "forme", "fouet", "franc", "frein", "front", "fuite", "gagne", "galop", "garde",
    "genre", "glace", "gomme", "grace", "grain", "grand", "grele", "guele", "gifle", "gland",
    "habit", "halte", "hardi", "herbe", "hiver", "homme", "hotel", "houle", "hurle", "hutte",
    "ideal", "image", "imite", "index", "inuit", "issue", "ivrog", "jaune", "jeton", "jeudi",
    "jouer", "jouet", "joyau", "jupon", "jurer", "karma", "lache", "lance", "large", "larme",
    "laser", "laver", "lente", "liane", "libre", "livre", "local", "loge", "lourd", "lueur",
    "luire", "lutte", "lutin", "magie", "maine", "major", "mande", "manie", "marie", "masse",
    "mater", "medit", "merle", "messe", "mieux", "mince", "miser", "mode", "mouet", "moule",
    "mulet", "munir", "murir", "naval", "neige", "nerfs", "niant", "niche", "noble", "noeud",
    "noire", "noyau", "nuage", "nuire", "obten", "occul", "ogive", "ombre", "oncle", "ordre",
    "otage", "outil", "ouvre", "ovale", "pagne", "palme", "panne", "paris", "paroi", "pause",
    "pelle", "perdu", "piano", "piste", "plage", "pluie", "plume", "poeme", "poids", "point",
    "pomme", "porte", "poser", "poule", "pours", "poutre", "prier", "prise", "prive", "pubis"
]

MOT_CIBLE = random.choice(MOT)


@app.get("/", response_class=HTMLResponse)
def serve_home(request: Request):
    return templates.TemplateResponse("wordle.html", {"request": request})


@app.post("/guess")
async def guess_word(data: dict):
    user_guess = data.get("guess", "").lower()
    if len(user_guess) != 5 or user_guess not in MOT:
        return JSONResponse({"error": "Mot invalide."}, status_code=400)

    result = []
    for i in range(5):
        if user_guess[i] == MOT_CIBLE[i]:
            result.append("correct")
        elif user_guess[i] in MOT_CIBLE:
            result.append("present")
        else:
            result.append("absent")

    win = user_guess == MOT_CIBLE
    return {"result": result, "win": win}

@app.get("/new-jeu")  # pour rejouer
def new_jeu():
    global MOT_CIBLE
    MOT_CIBLE = random.choice(MOT)
    return {"message": "Nouveau mot généré"}

@app.get("/get-mot-cible")  # afficher le mot cible
def get_mot():
    return {"mot": MOT_CIBLE}
