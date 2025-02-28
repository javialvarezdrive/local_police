import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from utils import supabase

def show_dashboard():
    st.header("Dashboard")

    agents = supabase.from_('Agents').select("*").execute().data
    activities = supabase.from_('Activities').select("*").execute().data
    scheduled_activities = supabase.from_('ScheduledActivities').select("*, Activities(name), Agents(first_name, last_name)").execute().data
    agent_assignments = supabase.from_('AgentAssignments').select("*, Agents(first_name, last_name)").execute().data

    if not agents or not activities or not scheduled_activities or not agent_assignments:
        st.warning("No data available to display.")
        return

    df_agents = pd.DataFrame(agents)
    df_activities = pd.DataFrame(activities)
    df_scheduled_activities = pd.DataFrame(scheduled_activities)
    df_agent_assignments = pd.DataFrame(agent_assignments)

    start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=30))
    end_date = st.date_input("End Date", value=datetime.now())

    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    df_scheduled_activities['date'] = pd.to_datetime(df_scheduled_activities['date'])
    filtered_scheduled_activities = df_scheduled_activities[(df_scheduled_activities['date'] >= start_date) & (df_scheduled_activities['date'] <= end_date)]

    if filtered_scheduled_activities.empty:
        st.warning("No scheduled activities found within the specified date range.")
        return

    st.subheader("Courses Attended by Agents")

    agent_courses = []
    for index, row in df_agent_assignments.iterrows():
        scheduled_activity_id = row['scheduled_activity_id']
        agent_id = row['agent_id']

        scheduled_activity = filtered_scheduled_activities[filtered_scheduled_activities['id'] == scheduled_activity_id]

        if not scheduled_activity.empty:
            activity_name = scheduled_activity['Activities']['name'].values[0]
            agent = df_agents[df_agents['id'] == agent_id]
            if not agent.empty:
                agent_name = f"{agent['first_name'].values[0]} {agent['last_name'].values[0]}"
                agent_courses.append({'Agent': agent_name, 'Activity': activity_name, 'Date': scheduled_activity['date'].values[0]})

    if agent_courses:
        df_agent_courses = pd.DataFrame(agent_courses)
        st.dataframe(df_agent_courses)

        st.subheader("Attendance Monitoring")
        attendance_counts = df_agent_courses['Agent'].value_counts().reset_index()
        attendance_counts.columns = ['Agent', 'Number of Courses Attended']
        st.dataframe(attendance_counts)
    else:
        st.warning("No courses attended by agents within the specified date range.")
