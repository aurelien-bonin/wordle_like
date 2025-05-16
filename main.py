from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List
import random
import string
import os

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


WORD_LIST = ["bleue", "rouge", "jaune", "verte", "rosee", "grise", "blanc", "grise", "mauve"]


SECRET_WORD = random.choice(WORD_LIST)

class GuessRequest(BaseModel):
    guess: str

class LetterResult(BaseModel):
    letter: str
    result: str  

class GuessResponse(BaseModel):
    result: List[LetterResult]
    is_correct: bool

@app.get("/new-game")
def new_game():
    global SECRET_WORD
    SECRET_WORD = random.choice(WORD_LIST)
    return {"message": "New game started!", "word_length": len(SECRET_WORD)}

@app.post("/guess", response_model=GuessResponse)
def make_guess(req: GuessRequest):
    guess = req.guess.lower()
    if len(guess) != len(SECRET_WORD):
        raise HTTPException(status_code=400, detail="Invalid word length.")

    result = []
    secret_word_copy = list(SECRET_WORD)
    

    for i in range(len(guess)):
        if guess[i] == SECRET_WORD[i]:
            result.append(LetterResult(letter=guess[i], result="correct"))
            secret_word_copy[i] = None  
        else:
            result.append(None)  


    for i in range(len(guess)):
        if result[i] is not None:
            continue
        if guess[i] in secret_word_copy:
            result[i] = LetterResult(letter=guess[i], result="present")
            secret_word_copy[secret_word_copy.index(guess[i])] = None
        else:
            result[i] = LetterResult(letter=guess[i], result="absent")

    return GuessResponse(result=result, is_correct=guess == SECRET_WORD)

@app.get("/word")
def reveal_word():
    return {"word": SECRET_WORD}  

@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Guess The Color</title>
        <style>
            .letter { display: inline-block; width: 40px; height: 40px; line-height: 40px; margin: 2px;
                      text-transform: uppercase; font-size: 24px; font-weight: bold; }
            .correct { background-color: green; color: white; }
            .present { background-color: orange; color: white; }
            .absent { background-color: grey; color: white; }
        </style>
    </head>
    <body>
        <h1>Guess The Color</h1>
        <h2>A Wordle inspired game</h2>
        <input type="text" id="guessInput" maxlength="5" autofocus>
        <button onclick="submitGuess()">Guess</button>
        <div id="results"></div>

        <script>
            let wordLength = 5;
            fetch('/new-game').then(res => res.json()).then(data => {
                wordLength = data.word_length;
                document.getElementById("guessInput").setAttribute("maxlength", wordLength);
            });

            function submitGuess() {
                const guess = document.getElementById('guessInput').value;
                fetch('/guess', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ guess })
                })
                .then(res => res.json())
                .then(data => {
                    const resultDiv = document.getElementById('results');
                    const row = document.createElement('div');
                    data.result.forEach(letter => {
                        const span = document.createElement('span');
                        span.className = 'letter ' + letter.result;
                        span.textContent = letter.letter;
                        row.appendChild(span);
                    });
                    resultDiv.appendChild(row);
                    document.getElementById('guessInput').value = '';
                    if (data.is_correct) alert("Congratulations! You guessed it!");
                })
                .catch(err => alert("Invalid guess."));
            }
        </script>
    </body>
    </html>
    """

