from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/genre-rock', methods=['GET'])
def connect():
  print("Successfully Connected!")
  return render_template('public/genre-rock.html')