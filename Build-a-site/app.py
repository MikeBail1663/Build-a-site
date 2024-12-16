from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

client = MongoClient("mongodb://localhost:27017/")
db = client['health_tracker']
goals_collection = db['goals']
progress_collection = db['progress']

@app.route('/')
def index():
    # Check if there's an existing goal for today
    goal = goals_collection.find_one()
    return render_template('index.html', goal=goal)

@app.route('/goals', methods=['GET', 'POST'])
def goals():
    if request.method == 'POST':
        existing_goal = goals_collection.find_one()
        now = datetime.now()
        if existing_goal:
            goal_date = datetime.strptime(existing_goal['date'], '%Y-%m-%d')
            if goal_date == now.date():
                return render_template('goals.html', message="Goal already set for today!")

        goal_steps = int(request.form['goal_steps'])
        goal_water = int(request.form['goal_water'])
        goals_collection.delete_many({})  # Delete any existing goal
        goals_collection.insert_one({
            "steps": goal_steps,
            "water": goal_water,
            "date": now.strftime('%Y-%m-%d')
        })
        return redirect(url_for('tracker'))
    
    return render_template('goals.html')

@app.route('/tracker', methods=['GET', 'POST'])
def tracker():
    now = datetime.now()
    today = now.strftime('%Y-%m-%d')

    goal = goals_collection.find_one()
    if not goal:
        return redirect(url_for('goals'))

    progress = progress_collection.find_one({"date": today})
    if not progress:
        progress = {"date": today, "steps": 0, "water": 0}
        progress_collection.insert_one(progress)

    if request.method == 'POST':
        steps = int(request.form['steps'])
        water = int(request.form['water'])

        progress['steps'] += steps
        progress['water'] += water
        progress_collection.update_one({"date": today}, {"$set": progress})

        # Check if the goal is achieved
        if progress['steps'] >= goal['steps'] and progress['water'] >= goal['water']:
            message = "Congratulations! You have achieved your goals today!"
            # Delete the goal and progress data after achievement
            goals_collection.delete_many({})
            progress_collection.delete_many({"date": today})
        else:
            message = None

        return render_template('tracker.html', progress=progress, goal=goal, message=message)
    
    remaining_steps = max(goal['steps'] - progress['steps'], 0)
    remaining_water = max(goal['water'] - progress['water'], 0)
    completed_steps = goal['steps'] - remaining_steps
    completed_water = goal['water'] - remaining_water

    if now.hour == 0 and (progress['steps'] < goal['steps'] or progress['water'] < goal['water']):
        message = "Sorry, you did not achieve your fitness goals yesterday."
    else:
        message = None

    return render_template('tracker.html', progress=progress, goal=goal, message=message)

@app.route('/tips')
def tips():
    return render_template('tips.html')

if __name__ == "__main__":
    app.run(debug=True)
