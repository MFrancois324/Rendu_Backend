let essais = 0;
let maxEssais = 6;
let score = 0;


async function submitGuess() {
    const input = document.getElementById("guess-input");
    const guess = input.value;

    if (guess.length !== 5) {
        alert("Veuillez entrer un mot de 5 lettres.");
        return;
    }

    const reponse = await fetch("/guess", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ guess: guess })
    });

    const data = await reponse.json();

    if (data.error) {
        alert(data.error);
        return;
    }

    essais++;
    document.getElementById("essais").textContent = `${essais}`;  

    const feedbackDiv = document.getElementById("feedback");
    const nouvelle_ligne = document.createElement("div");
    nouvelle_ligne.className = "feedback-nouvelle_ligne";

    data.result.forEach((status, i) => {
        const span = document.createElement("div");
        span.className = `lettre ${status}`;
        span.textContent = guess[i];
        nouvelle_ligne.appendChild(span);
    });

    feedbackDiv.appendChild(nouvelle_ligne);


    if (data.win) {
        score++;
        document.getElementById("score").textContent = score;
        setTimeout(() => {
            alert("Bravo, tu as trouvé le mot !");
            document.getElementById("replay-container").style.display = "block";
        }, 200);
    } else if (essais >= maxEssais) {
        const reveal = document.createElement("div");
        reveal.textContent = `Mot à trouver : ${await getCurrentWord()}`;
        reveal.style.marginTop = "10px";
        reveal.style.fontWeight = "bold";
        feedbackDiv.appendChild(reveal);
        document.getElementById("replay-container").style.display = "block";
        setTimeout(() => {
            alert("Tu as déjà utilisé tous tes essais !");
            document.getElementById("replay-container").style.display = "block";
        }, 200);
    }

    input.value = "";
}

async function replayGame() {

    essais = 0;
    document.getElementById("essais").textContent = essais;
    document.getElementById("feedback").innerHTML = "";
    document.getElementById("guess-input").value = "";

    // Affiche un message temporaire
    const messageDiv = document.getElementById("message");
    messageDiv.textContent = "Nouveau mot chargé !";
    setTimeout(() => {
        messageDiv.textContent = "";
    }, 2000);

    // Appelle le backend pour générer un nouveau mot
    await fetch("/new-jeu");
}

window.replayGame = replayGame;

async function getCurrentWord() {
    // Ce n’est pas sécurisé, mais utile ici pour démo. Tu peux améliorer cela côté serveur.
    // Pour une vraie appli, ne révèle jamais le mot côté client ainsi !
    const res = await fetch("/get-mot-cible");
    const data = await res.json();
    return data.word;
}
