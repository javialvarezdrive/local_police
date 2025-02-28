import streamlit as st
from datetime import datetime
from utils import supabase, get_agents, get_activities, get_scheduled_activities, get_agent_assignments
import auth
import dashboard

def register_agent():
    st.subheader("Register Agent")
    first_name = st.text_input("First Name")
    last_name = st.text_input("Last Name")
    nip = st.text_input("NIP (6-digit number)")
    section = st.text_input("Section")
    group = st.text_input("Group")
    email = st.text_input("Email")
    phone_number = st.text_input("Phone Number")

    if st.button("Register"):
        if len(nip) != 6 or not nip.isdigit():
            st.error("NIP must be a 6-digit number.")
            return

        try:
            nip_int = int(nip)
        except ValueError:
            st.error("NIP must contain only digits.")
            return

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
            st.success("Agent registered successfully!")
        else:
            st.error("Failed to register agent.")

def schedule_activity():
    st.subheader("Schedule Activity")
    activities = get_activities()
    instructors = supabase.from_('Agents').select("*").eq('is_instructor', True).execute().data

    if not activities:
        st.warning("No activities available. Please add activities in the database.")
        return

    if not instructors:
        st.warning("No instructors available. Please add instructors in the database.")
        return

    activity_names = [activity['name'] for activity in activities]
    activity_name = st.selectbox("Activity", activity_names)
    date = st.date_input("Date", datetime.now())
    shift = st.selectbox("Shift", ["Morning Shift", "Afternoon Shift", "Night Shift"])
    instructor_name = st.selectbox("Instructor", [f"{i['first_name']} {i['last_name']}" for i in instructors])

    if st.button("Schedule"):
        activity_id = next(item['id'] for item in activities if item['name'] == activity_name)
        instructor_id = next(item['id'] for item in instructors if f"{item['first_name']} {item['last_name']}" == instructor_name)

        new_scheduled_activity = {
            'activity_id': activity_id,
            'date': date.strftime("%Y-%m-%d"),
            'shift': shift,
            'instructor_id': instructor_id
        }
        data, count = supabase.table("ScheduledActivities").insert(new_scheduled_activity).execute()

        if data:
            st.success("Activity scheduled successfully!")
        else:
            st.error("Failed to schedule activity.")

def assign_agent():
    st.subheader("Assign Agent to Activity")
    agents = get_agents()
    scheduled_activities = get_scheduled_activities()

    if not agents:
        st.warning("No agents registered.")
        return

    if not scheduled_activities:
        st.warning("No scheduled activities.")
        return

    agent_names = [f"{agent['first_name']} {agent['last_name']}" for agent in agents]
    scheduled_activity_details = [f"{sa['Activities']['name']} - {sa['date']} - {sa['shift']} - {sa['Agents']['first_name']} {sa['Agents']['last_name']}" for sa in scheduled_activities]

    agent_name = st.selectbox("Agent", agent_names)
    scheduled_activity_detail = st.selectbox("Scheduled Activity", scheduled_activity_details)

    if st.button("Assign"):
        agent_id = next(agent['id'] for agent in agents if f"{agent['first_name']} {agent['last_name']}" == agent_name)

        scheduled_activity_id = None
        for sa in scheduled_activities:
            activity_name = sa['Activities']['name']
            activity_date = sa['date']
            activity_shift = sa['shift']
            instructor_name = f"{sa['Agents']['first_name']} {sa['Agents']['last_name']}"

            formatted_activity_detail = f"{activity_name} - {activity_date} - {activity_shift} - {instructor_name}"

            if formatted_activity_detail == scheduled_activity_detail:
                scheduled_activity_id = sa['id']
                break

        if not scheduled_activity_id:
            st.error("Could not find the selected scheduled activity.")
            return

        new_agent_assignment = {
            'scheduled_activity_id': scheduled_activity_id,
            'agent_id': agent_id
        }
        data, count = supabase.table("AgentAssignments").insert(new_agent_assignment).execute()

        if data:
            st.success("Agent assigned to activity successfully!")
        else:
            st.error("Failed to assign agent to activity.")

def main():
    st.title("Local Police Gym Management")

    if 'instructor' not in st.session_state:
        auth_status = auth.login()
        if not auth_status:
            return

    auth.logout()

    menu = ["Register Agent", "Schedule Activity", "Assign Agent", "Dashboard"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Register Agent":
        register_agent()
    elif choice == "Schedule Activity":
        schedule_activity()
    elif choice == "Assign Agent":
        assign_agent()
    elif choice == "Dashboard":
        dashboard.show_dashboard()

if __name__ == "__main__":
    main()
