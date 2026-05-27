from flask import Flask, render_template_string, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "mood-game-secret"

QUESTIONS = {
    "Q1": {
        "text": "Elin, are you mad or upset at Wengie?",
        "options": {
            "Yes": {"elin": -3, "wengie": +3, "next": "Q2Y"},
            "No": {"elin": +2, "wengie": +2, "next": "Q2N"}
        }
    },
    "Q2Y": {
        "text": "How mad/upset are you, Elin?",
        "options": {
            "Slightly": {"elin": -1, "wengie": +1, "next": "Q3Y"},
            "Quite": {"elin": -2, "wengie": +2, "next": "Q3Y"},
            "Very": {"elin": -4, "wengie": +4, "next": "Q3Y"}
        }
    },
    "Q3Y": {
        "text": "Do you want to talk it through with Wengie?",
        "options": {
            "Yes": {"elin": +2, "wengie": -2, "next": "Q4Y"},
            "No": {"elin": -1, "wengie": +2, "next": "Q4Y"}
        }
    },
    "Q4N": {
        "text": "How happy are you right now, Elin?",
        "options": {
            "Very": {"elin": +4, "wengie": +2, "next": "Q5N"},
            "Average": {"elin": 0, "wengie": 0, "next": "Q5N"},
            "Not very": {"elin": -4, "wengie": -2, "next": "Q5N"}
        }
    },
}

def clamp(v):
    return max(0, min(20, v))

def get_activity(score):
    if score <= 4:
        return "Talk / Give space / Comfort Elin"
    elif score <= 8:
        return "Talk / Watch something together"
    elif score <= 12:
        return "Watch something / Study together"
    elif score <= 16:
        return "Gaming / Chill together"
    else:
        return "Gaming / Fun activity / Date vibe 💖"

# ---------------- UI ----------------
TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<title>Elin & Wengie Mood Game</title>

<style>
body {
    font-family: Arial;
    margin: 0;
    background: #ffd6e7; /* 💗 light pink */
    color: #1f2937;
}

.topbar {
    position: fixed;
    top: 15px;
    right: 15px;
    width: 260px;
}

.label {
    font-weight: bold;
    margin-top: 10px;
}

.bar {
    background: #f3f4f6;
    height: 12px;
    border-radius: 10px;
    overflow: hidden;
}

.fill {
    height: 12px;
    background: #22c55e; /* 🟢 green */
    transition: width 0.4s ease;
}

.container {
    max-width: 600px;
    margin: 120px auto;
    text-align: center;
}

.card {
    background: white;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

button {
    margin: 8px;
    padding: 10px 15px;
    border-radius: 10px;
    border: none;
    cursor: pointer;
    background: #f472b6;
    color: white;
    font-weight: bold;
}

.reset {
    background: #ef4444;
}
</style>

</head>

<body>

<div class="topbar">

{% if first_yes %}

<div class="label">Elin's happiness: {{elin}}/20</div>

{% else %}

<div class="label">Elin: {{elin}}/20</div>

{% endif %}

<div class="bar">
<div class="fill" style="width: {{elin*5}}%"></div>
</div>

{% if first_yes %}

<div class="label">Wengie's panic level: {{wengie}}/20</div>

{% else %}

<div class="label">Wengie: {{wengie}}/20</div>

{% endif %}

<div class="bar">
<div class="fill" style="width: {{wengie*5}}%"></div>
</div>

</div>

<div class="container">
<div class="card">

{% if question %}

<h2>{{question}}</h2>

{% for opt in options %}
<form method="POST">
<input type="hidden" name="choice" value="{{opt}}">
<button>{{opt}}</button>
</form>
{% endfor %}

{% else %}

<h2>Result for Elin & Wengie 💖</h2>
<h3>{{activity}}</h3>

<form action="/reset">
<button class="reset">Restart</button>
</form>

{% endif %}

</div>
</div>

</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    if "q" not in session:
        session["q"] = "Q1"
        session["elin"] = 10
        session["wengie"] = 10
        session["first_yes"] = False

    qid = session["q"]

    if request.method == "POST":
        choice = request.form["choice"]
        q = QUESTIONS[qid]
        effect = q["options"][choice]

        session["elin"] = clamp(session["elin"] + effect["elin"])
        session["wengie"] = clamp(session["wengie"] + effect["wengie"])
        session["q"] = effect["next"]

        if qid == "Q1" and choice == "Yes":
            session["first_yes"] = True

        return redirect(url_for("index"))

    if qid == "END":
        activity = get_activity(session["elin"])
        return render_template_string(
            TEMPLATE,
            question=None,
            options=None,
            elin=session["elin"],
            wengie=session["wengie"],
            activity=activity,
            first_yes=session.get("first_yes", False)
        )

    q = QUESTIONS[qid]

    return render_template_string(
        TEMPLATE,
        question=q["text"],
        options=q["options"].keys(),
        elin=session["elin"],
        wengie=session["wengie"],
        activity=None,
        first_yes=session.get("first_yes", False)
    )

@app.route("/reset")
def reset():
    session.clear()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
