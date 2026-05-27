from flask import Flask, render_template_string, request, redirect, url_for, session
import os

app = Flask(__name__)
app.secret_key = "mood-game-fixed-v2"

# -----------------------------
# GIFS
# -----------------------------
GIF_YES = "https://media1.tenor.com/m/uvpSJ-foSuQAAAAd/me-if-u-even-care.gif"
GIF_NO = "https://media.tenor.com/7cdeCWXmOREAAAAm/bffr.webp"

# -----------------------------
# QUESTIONS
# -----------------------------
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
            "Very": {"elin": -3, "wengie": +3, "next": "Q3Y"}
        }
    },

    "Q3Y": {
        "text": "Do you want to talk it through with Wengie?",
        "options": {
            "Yes": {"elin": +2, "wengie": -2, "next": "Q4Y"},
            "No": {"elin": -1, "wengie": +2, "next": "Q4Y"}
        }
    },

    "Q4Y": {
        "text": "Do you know Wengie really loves you?",
        "options": {
            "Yes": {"elin": +3, "wengie": -2, "next": "Q5Y"},
            "Hmmph": {"elin": -1, "wengie": +1, "next": "Q5Y"}
        }
    },

    "Q5Y": {
        "text": "What made you upset?",
        "options": {
            "Forgot something": {"elin": -1, "wengie": +1, "next": "Q6Y"},
            "Didn't listen": {"elin": -2, "wengie": +2, "next": "Q6Y"},
            "Other": {"elin": -1, "wengie": +1, "next": "Q6Y"}
        }
    },

    "Q6Y": {
        "text": "Do you still love Wengie?",
        "options": {
            "Yes": {"elin": +3, "wengie": -3, "next": "Q7Y"},
            "No": {"elin": -4, "wengie": +4, "next": "Q7Y"},
            "IDK": {"elin": -1, "wengie": +2, "next": "Q7Y"}
        }
    },

    "Q7Y": {
        "text": "Will you forgive Wengie?",
        "options": {
            "Yes": {"elin": +4, "wengie": -3, "next": "END"},
            "No": {"elin": -3, "wengie": +3, "next": "END"},
            "Maybe": {"elin": +1, "wengie": +1, "next": "END"}
        }
    },

    "Q2N": {
        "text": "Was Wengie a good boyfriend today?",
        "options": {
            "Average": {"elin": 0, "wengie": 0, "next": "Q3N"},
            "Yes": {"elin": +2, "wengie": +2, "next": "Q3N"},
            "Very": {"elin": +3, "wengie": +3, "next": "Q3N"}
        }
    },

    "Q3N": {
        "text": "Did Wengie forget something today?",
        "options": {
            "Yes": {"elin": -2, "wengie": -2, "next": "Q4N"},
            "No": {"elin": +1, "wengie": +1, "next": "Q4N"}
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

    "Q5N": {
        "text": "Are you stressed about anything?",
        "options": {
            "Yes": {"elin": -2, "wengie": -1, "next": "Q6N"},
            "No": {"elin": +2, "wengie": +1, "next": "Q6N"}
        }
    },

    "Q6N": {
        "text": "How much do you love Wengie right now?",
        "options": {
            "A lot": {"elin": +3, "wengie": +3, "next": "END"},
            "Moderate": {"elin": +1, "wengie": +1, "next": "END"},
            "Little": {"elin": -3, "wengie": -2, "next": "END"}
        }
    }
}

# -----------------------------
# HELPERS
# -----------------------------
def clamp(v):
    return max(0, min(20, v))

def get_activity(score):
    if score <= 4:
        return "Talk / Give space"
    elif score <= 8:
        return "Talk / Watch something"
    elif score <= 12:
        return "Watch / Study together"
    elif score <= 16:
        return "Gaming / Chill"
    else:
        return "Fun activity / Date vibe 💖"

# -----------------------------
# TEMPLATE
# -----------------------------
TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<title>Elin & Wengie Mood Game</title>

<style>
body {
    font-family: Arial;
    margin: 0;
    background: #ffd6e7;
    color: #1f2937;
}

.topbar {
    position: fixed;
    top: 15px;
    right: 15px;
    width: 320px;
}

.row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 10px;
    gap: 10px;
}

.label {
    font-weight: bold;
    font-size: 12px;
    width: 150px;
}

.bar {
    background: #fff;
    height: 12px;
    border-radius: 10px;
    overflow: hidden;
    border: 1px solid #ddd;
    flex: 1;
}

.fill {
    height: 12px;
    background: #22c55e;
    transition: width 0.3s ease;
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

<div class="row">
    <div class="label">Elin's happiness</div>
    <div class="bar"><div class="fill" style="width: {{elin*5}}%"></div></div>
</div>

<div class="row">
    <div class="label">Wengie's panic level</div>
    <div class="bar"><div class="fill" style="width: {{wengie*5}}%"></div></div>
</div>

{% else %}

<div class="row">
    <div class="label">Elin</div>
    <div class="bar"><div class="fill" style="width: {{elin*5}}%"></div></div>
</div>

<div class="row">
    <div class="label">Wengie</div>
    <div class="bar"><div class="fill" style="width: {{wengie*5}}%"></div></div>
</div>

{% endif %}

</div>

<div class="container">
<div class="card">

{% if question %}

{% if gif %}
<img src="{{ gif }}" style="max-width:100%; border-radius:12px; margin-bottom:15px;">
{% endif %}

<h2>{{question}}</h2>

<form method="POST">
{% for opt in options %}
<button name="choice" value="{{opt}}">{{opt}}</button>
{% endfor %}
</form>

{% else %}

<h2>Final Result 💖</h2>
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

# -----------------------------
# ROUTES
# -----------------------------
@app.route("/", methods=["GET", "POST"])
def index():

    if not all(k in session for k in ["q", "elin", "wengie", "first_yes"]):
        session["q"] = "Q1"
        session["elin"] = 10
        session["wengie"] = 10
        session["first_yes"] = False

    qid = session["q"]

    if request.method == "POST":
        choice = request.form.get("choice")
        q = QUESTIONS[qid]

        if choice not in q["options"]:
            return redirect(url_for("index"))

        effect = q["options"][choice]

        session["elin"] = clamp(session["elin"] + effect["elin"])
        session["wengie"] = clamp(session["wengie"] + effect["wengie"])
        session["q"] = effect["next"]

        if qid == "Q1":
            session["first_yes"] = (choice == "Yes")

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
            first_yes=session["first_yes"],
            gif=None
        )

    q = QUESTIONS[qid]

    gif = None
    if qid != "Q1":
        gif = GIF_YES if session.get("first_yes") else GIF_NO

    return render_template_string(
        TEMPLATE,
        question=q["text"],
        options=q["options"].keys(),
        elin=session["elin"],
        wengie=session["wengie"],
        activity=None,
        first_yes=session["first_yes"],
        gif=gif
    )

@app.route("/reset")
def reset():
    session.clear()
    return redirect(url_for("index"))

# -----------------------------
# RENDER ENTRY POINT
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
