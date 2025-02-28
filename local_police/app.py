from flask import Flask, render_template, request, redirect, url_for, session
from supabase import create_client, Client
import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY")

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Authentication
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        response = supabase.from_('Agents').select("*").eq('email', email).eq('is_instructor', True).execute()
        instructor = response.data
        if instructor and instructor[0]['password'] == password:
            session['instructor_id'] = instructor[0]['id']
            session['instructor_name'] = instructor[0]['first_name']
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('instructor_id', None)
    session.pop('instructor_name', None)
    return redirect(url_for('login'))

# Agent Registration
@app.route('/register', methods=['GET', 'POST'])
def register_agent():
    if not session.get('instructor_id'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        nip = request.form['nip']
        section = request.form['section']
        group = request.form['group']
        email = request.form['email']
        phone_number = request.form['phone_number']

        new_agent = {
            'first_name': first_name,
            'last_name': last_name,
            'nip': nip,
            'section': section,
            'group': group,
            'email': email,
            'phone_number': phone_number
        }
        data, count = supabase.table("Agents").insert(new_agent).execute()

        if data:
            return render_template('register_agent.html', message='Agent registered successfully')
        else:
            return render_template('register_agent.html', error='Failed to register agent')

    return render_template('register_agent.html')

# Activity Scheduling
@app.route('/schedule', methods=['GET', 'POST'])
def schedule_activity():
    if not session.get('instructor_id'):
        return redirect(url_for('login'))

    activities_response = supabase.from_('Activities').select("*").execute()
    activities = activities_response.data
    instructors_response = supabase.from_('Agents').select("*").eq('is_instructor', True).execute()
    instructors = instructors_response.data

    if request.method == 'POST':
        activity_id = request.form['activity_id']
        date = request.form['date']
        shift = request.form['shift']
        instructor_id = request.form['instructor_id']

        new_scheduled_activity = {
            'activity_id': activity_id,
            'date': date,
            'shift': shift,
            'instructor_id': instructor_id
        }
        data, count = supabase.table("ScheduledActivities").insert(new_scheduled_activity).execute()

        if data:
            return render_template('schedule_activity.html', activities=activities, instructors=instructors, message='Activity scheduled successfully')
        else:
            return render_template('schedule_activity.html', activities=activities, instructors=instructors, error='Failed to schedule activity')

    return render_template('schedule_activity.html', activities=activities, instructors=instructors)

# Agent Assignment
@app.route('/assign', methods=['GET', 'POST'])
def assign_agent():
    if not session.get('instructor_id'):
        return redirect(url_for('login'))

    agents_response = supabase.from_('Agents').select("*").execute()
    agents = agents_response.data
    scheduled_activities_response = supabase.from_('ScheduledActivities').select("*, Activities(name), Agents(first_name, last_name)").execute()
    scheduled_activities = scheduled_activities_response.data

    if request.method == 'POST':
        agent_id = request.form['agent_id']
        scheduled_activity_id = request.form['scheduled_activity_id']

        new_agent_assignment = {
            'scheduled_activity_id': scheduled_activity_id,
            'agent_id': agent_id
        }
        data, count = supabase.table("AgentAssignments").insert(new_agent_assignment).execute()

        if data:
            return render_template('assign_agent.html', agents=agents, scheduled_activities=scheduled_activities, message='Agent assigned successfully')
        else:
            return render_template('assign_agent.html', agents=agents, scheduled_activities=scheduled_activities, error='Failed to assign agent')

    return render_template('assign_agent.html', agents=agents, scheduled_activities=scheduled_activities)

# Dashboard
@app.route('/dashboard')
def dashboard():
    if not session.get('instructor_id'):
        return redirect(url_for('login'))

    agents_response = supabase.from_('Agents').select("*").execute()
    agents = agents_response.data
    activities_response = supabase.from_('Activities').select("*").execute()
    activities = activities_response.data
    scheduled_activities_response = supabase.from_('ScheduledActivities').select("*, Activities(name), Agents(first_name, last_name)").execute()
    scheduled_activities = scheduled_activities_response.data
    agent_assignments_response = supabase.from_('AgentAssignments').select("*, Agents(first_name, last_name)").execute()
    agent_assignments = agent_assignments_response.data

    df_agents = pd.DataFrame(agents)
    df_activities = pd.DataFrame(activities)
    df_scheduled_activities = pd.DataFrame(scheduled_activities)
    df_agent_assignments = pd.DataFrame(agent_assignments)

    agent_courses = []
    for index, row in df_agent_assignments.iterrows():
        scheduled_activity_id = row['scheduled_activity_id']
        agent_id = row['agent_id']

        scheduled_activity = df_scheduled_activities[df_scheduled_activities['id'] == scheduled_activity_id]

        if not scheduled_activity.empty:
            activity_name = scheduled_activity['Activities']['name'].values[0]
            agent = df_agents[df_agents['id'] == agent_id]
            if not agent.empty:
                agent_name = f"{agent['first_name'].values[0]} {agent['last_name'].values[0]}"
                agent_courses.append({'Agent': agent_name, 'Activity': activity_name, 'Date': scheduled_activity['date'].values[0]})

    if agent_courses:
        df_agent_courses = pd.DataFrame(agent_courses)
        attendance_counts = df_agent_courses['Agent'].value_counts().reset_index()
        attendance_counts.columns = ['Agent', 'Number of Courses Attended']
        return render_template('dashboard.html', attendance_counts=attendance_counts.to_html(index=False))
    else:
        return render_template('dashboard.html', message='No courses attended by agents')

# Main route
@app.route('/')
def index():
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
