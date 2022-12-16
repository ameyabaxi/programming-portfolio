# Ameya Baxi (some collaboration with lab team members)
# COMP SCI 320: Data Science Programming II, Fall 2022
# Project 4: Building a Data Website

# building a website, A/B testing
# project instructions: https://github.com/cs320-wisc/f22/tree/main/p4

# project: p4
# submitter: abaxi
# partner: none
# hours: 10

# main.py
# objective: building a data website

# data source: Chicago Transit Authority
# https://data.cityofchicago.org/Transportation/CTA-System-Information-List-of-L-Stops/8pix-ypme
# dataset containing information about each L stop and the train lines that stop there

# import statements
import pandas as pd, os, csv, re, matplotlib.pyplot as plt
from flask import Flask, request, jsonify

# create pandas DataFrame from CTA CSV data
df = pd.read_csv("main.csv") # data was downloaded locally

# create HTML representation of DataFrame for use in browse.html page
html_df = df.to_html()

# create index.html page
with open("index.html", "w") as f:
    f.write('''
    <html><head>
    <script src="https://code.jquery.com/jquery-3.4.1.js"></script>
    <script>
      function subscribe() {
        var email = prompt("What is your email?", "????");

        $.post({
          type: "POST",
          url: "email",
          data: email,
          contentType: "application/text; charset=utf-8",
          dataType: "json"
        }).done(function(data) {
          alert(data);
        }).fail(function(data) {
          alert("POST failed");
        });
      }
    </script>
  </head><body>
            <h1>CTA L Stations</h1>
            <p>Enjoy exploring the rail lines!</p>
            <a href="browse.html">Browse</a>
            <p></p>
            <a href="donate.html?from=A">Donate</a>            
            <p></p>
            <button onclick="subscribe()">SUBSCRIBE</button>
            <img src="dashboard_1.svg"><br><br>
            <img src="dashboard_1.svg?bins=100"><br><br>
            <img src="dashboard_2.svg"><br><br>
        </body>
    </html>
    ''')

    
app = Flask(__name__)


# variables to count number of times home page has been visited
count_total = 0
count_A = 0
count_B = 0

# open index.html as home page
@app.route("/")
def home():
    global count_total, count_A, count_B
    count_total += 1
    with open("index.html") as f:
        html = f.read()
    html_v2 = html.replace("<a href=\"donate.html?from=A\">Donate</a>", "<a href=\"donate.html?from=B\" style=\"color: red\">Donate</a>")
    if count_total > 10:
        if count_A > count_B:
            return html
        else:
            return html_v2
    elif count_total <= 10:
        if count_total % 2 == 0: # even numbers
            return html
        else: # odd numbers
            return html_v2           


# variable to count number of emails subscribed
num_subscribed = 0

# response to clicking email button on index.html
@app.route("/email", methods=["POST"])
def email():
    global num_subscribed
    email = str(request.data, "utf-8")
    if len(re.findall(r"^\w+@{1}\w+\.+\w{3}$", email)) > 0:
        with open("emails.txt", "a") as f: # open file in append mode
            f.write(email + "\n")
            num_subscribed += 1
        return jsonify(f"thanks, you're subscriber number {num_subscribed}!")
    return jsonify("bad input!!")


# open browse.html page, displaying data in a table
@app.route("/browse.html")
def browse():
    return "<html><h1>Browse</h1>{}</html>".format(html_df)

# open browse.json page, displaying data as a dict
@app.route("/browse.json")


# open visitors.json page, displaying list of client IPs
@app.route("/visitors.json")


# open donate.html page, asking users to make a donation
@app.route("/donate.html")
def donate():
    global count_total, count_A, count_B
    if count_total <= 10:
        query = request.args.get("from")
        if query == "A":
            count_A += 1
        elif query == "B":
            count_B += 1
    return "<html><h1>Donate</h1><p>Please donate to help keep our trains running!</p></html>"


if __name__ == "__main__":
    app.run(host = "0.0.0.0", debug = True, threaded = False)   
# cannot define functions after this because app.run never returns