from flask import Flask, render_template_string, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "mood-game-secret"

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

    # YES ROUTE
    "Q2Y": {
        "text": "How mad/upset are you, Elin?",
        "options": {
            "Slightly": {"elin": -1, "wengie": +1, "next": "Q3Y"},
            "Quite": {"elin": -2, "wengie": +2, "next": "Q3Y"},
            "Very": {"elin": -4, "wengie": +4, "next": "Q3Y"}
        }
    },

    "Q3Y": {
        "text": "Elin, do you want to talk it through with Wengie?",
        "options": {
            "Yes": {"elin": +2, "wengie": -2, "next": "Q4Y"},
            "No": {"elin": -1, "wengie": +2, "next": "Q4Y"}
        }
    },

    "Q4Y": {
        "text": "Elin, do you know Wengie really loves you?",
        "options": {
            "Yes": {"elin": +3, "wengie": -2, "next": "Q5Y"},
            "Hmmph": {"elin": -1, "wengie": +1, "next": "Q5Y"}
        }
    },

    "Q5Y": {
        "text": "Elin, what made you upset?",
        "options": {
            "Forgot something": {"elin": -1, "wengie": +1, "next": "Q6Y"},
            "Didn't listen": {"elin": -2, "wengie": +2, "next": "Q6Y"},
            "Other": {"elin": -2, "wengie": +1, "next": "Q6Y"}
        }
    },

    "Q6Y": {
        "text": "Elin, do you still love Wengie?",
        "options": {
            "Yes": {"elin": +3, "wengie": -3, "next": "Q7Y"},
            "No": {"elin": -4, "wengie": +4, "next": "Q7Y"},
            "IDK": {"elin": -1, "wengie": +2, "next": "Q7Y"}
        }
    },

    "Q7Y": {
        "text": "Elin, will you forgive Wengie?",
        "options": {
            "Yes": {"elin": +4, "wengie": -3, "next": "END"},
            "No": {"elin": -3, "wengie": +3, "next": "END"},
            "Maybe": {"elin": +1, "wengie": +1, "next": "END"}
        }
    },

    # NO ROUTE
    "Q2N": {
        "text": "Elin, was Wengie a good boyfriend today?",
        "options": {
            "Average": {"elin": 0, "wengie": 0, "next": "Q3N"},
            "Yes": {"elin": +2, "wengie": +2, "next": "Q3N"},
            "Very": {"elin": +4, "wengie": +4, "next": "Q3N"}
        }
    },

    "Q3N": {
        "text": "Elin, did Wengie forget something today?",
        "options": {
            "Yes": {"elin": -2, "wengie": -2, "next": "Q4N"},
            "No": {"elin": +1, "wengie": +1, "next": "Q4N"}
        }
    },

    "Q4N": {
        "text": "Elin, how happy are you right now?",
        "options": {
            "Very": {"elin": +4, "wengie": +2, "next": "Q5N"},
            "Average": {"elin": 0, "wengie": 0, "next": "Q5N"},
            "Not very": {"elin": -4, "wengie": -2, "next": "Q5N"}
        }
    },

    "Q5N": {
        "text": "Elin, are you stressed about anything?",
        "options": {
            "Yes": {"elin": -2, "wengie": -1, "next": "Q6N"},
            "No": {"elin": +2, "wengie": +1, "next": "Q6N"}
        }
    },

    "Q6N": {
        "text": "Elin, how much do you love Wengie right now?",
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
        return "Talk / Give space / Comfort Elin"
    elif score <= 8:
        return "Talk / Watch something together"
    elif score <= 12:
        return "Watch something / Study together"
    elif score <= 16:
        return "Gaming / Watch something / Chill together"
    else:
        return "Gaming / Fun activity / Date vibe 💖"

# -----------------------------
# UI
# -----------------------------
TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<title>Elin & Wengie Mood Game</title>
<style>
body {
    font-family: Arial;
    background: #0f172a;
    color: white;
    margin: 0;
}

.topbar {
    position: fixed;
    top: 10px;
    right: 10px;
    width: 220px;
}

.bar {
    background: #334155;
    height: 10px;
    border-radius: 5px;
    margin-bottom: 10px;
}

.fill {
    height: 10px;
    background: #38bdf8;
}

.container {
    max-width: 600px;
    margin: 120px auto;
    text-align: center;
}

.card {
    background: #1e293b;
    padding: 20px;
    border-radius: 12px;
}

button {
    margin: 8px;
    padding: 10px 15px;
    border-radius: 8px;
    border: none;
    cursor: pointer;
}

.option { background: #38bdf8; }
.reset { background: #ef4444; color: white; }
</style>
</head>

<body>

<div class="topbar">
    <div>Elin: {{elin}}/20</div>
    <div class="bar"><div class="fill" style="width: {{elin*5}}%"></div></div>

    <div>Wengie: {{wengie}}/20</div>
    <div class="bar"><div class="fill" style="width: {{wengie*5}}%"></div></div>
</div>

<div class="container">
<div class="card">

{% if question %}

<h2>{{question}}</h2>

{% for opt in options %}
<form method="POST">
    <input type="hidden" name="choice" value="{{opt}}">
    <button class="option">{{opt}}</button>
</form>
{% endfor %}

{% else %}

<h2>Recommended Activity for Elin & Wengie</h2>
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
    if "q" not in session:
        session["q"] = "Q1"
        session["elin"] = 10
        session["wengie"] = 10

    qid = session["q"]

    if qid == "END":
        activity = get_activity(session["elin"])

        return render_template_string(
            TEMPLATE,
            question=None,
            options=None,
            elin=session["elin"],
            wengie=session["wengie"],
            activity=activity
        )

    q = QUESTIONS[qid]

    if request.method == "POST":
        choice = request.form["choice"]
        effect = q["options"][choice]

        session["elin"] = clamp(session["elin"] + effect["elin"])
        session["wengie"] = clamp(session["wengie"] + effect["wengie"])
        session["q"] = effect["next"]

        return redirect(url_for("index"))

    return render_template_string(
        TEMPLATE,
        question=q["text"],
        options=q["options"].keys(),
        elin=session["elin"],
        wengie=session["wengie"],
        activity=None
    )

@app.route("/reset")
def reset():
    session.clear()
    return redirect(url_for("index"))

# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
