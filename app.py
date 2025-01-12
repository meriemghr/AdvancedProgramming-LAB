import pandas as pd
import streamlit as st
from datetime import datetime

# Charging the data from the excel file
@st.cache_data
def load_data():
    # Transform each sheet into a DataFrame
    excel_file = "qcm_data.xlsx"
    users_df = pd.read_excel(excel_file, sheet_name="users")
    history_df = pd.read_excel(excel_file, sheet_name="history")
    questions_df = pd.read_excel(excel_file, sheet_name="questions")
    return users_df, history_df, questions_df

# Function to save data to the Excel file
def save_data(users_df, history_df, questions_df):
    with pd.ExcelWriter("qcm_data.xlsx", engine="openpyxl") as writer:
        users_df.to_excel(writer, sheet_name="users", index=False)
        history_df.to_excel(writer, sheet_name="history", index=False)
        questions_df.to_excel(writer, sheet_name="questions", index=False)

# Main function
def main():
    st.title("Application de QCM Informatique 📘")

    # Charging the data
    users_df, history_df, questions_df = load_data()

    # Start of the page
    st.header("Connexion utilisateur")
    username = st.text_input("Entrez votre nom :").strip()

    if username:
        # Verify if the user exists
        user = users_df[users_df['name'] == username]

        if not user.empty:
            st.success(f"Bienvenue, {username} ! 🎉")

            # Get the user id
            user_id = user.iloc[0]['id']

            # Display the user's history
            st.subheader("Historique des QCM")
            user_history = history_df[history_df['user_id'] == user_id]

            if user_history.empty:
                st.info("Aucun historique trouvé pour cet utilisateur.")
            else:
                # Display all attempts in a user-friendly format
                st.write("Voici votre historique complet :")
                for index, row in user_history.iterrows():
                    st.write(f"📅 Date: {row['date']}, Score: {row['score']}")

            # Start a new QCM
            if st.button("Commencer un nouveau QCM"):
                st.session_state.quiz_started = True
                st.session_state.current_question = 0
                st.session_state.score = 0

        else:
            st.error("Utilisateur non trouvé. Veuillez vérifier votre nom ou créer un nouvel utilisateur.")

            # Option to create a new user
            if st.checkbox("Créer un nouvel utilisateur"):
                new_id = users_df['id'].max() + 1
                new_user = pd.DataFrame({"id": [new_id], "name": [username]})
                users_df = pd.concat([users_df, new_user], ignore_index=True)
                save_data(users_df, history_df, questions_df)
                st.success("Utilisateur créé avec succès ! Rechargez l'application.")

    else:
        st.info("Entrez votre nom pour continuer.")

    # Run the quiz if it has started
    if st.session_state.get("quiz_started", False):
        run_quiz(user_id, questions_df, history_df, users_df)

# Function that executes the QCM
def run_quiz(user_id, questions_df, history_df, users_df):
    st.header("QCM en cours 🗃️")

    total_questions = len(questions_df)

    # Initialize session state variables if they don't exist
    if "current_question" not in st.session_state:
        st.session_state.current_question = 0
        st.session_state.score = 0

    # Display the current question
    if st.session_state.current_question < total_questions:
        row = questions_df.iloc[st.session_state.current_question]
        st.subheader(f"Question {st.session_state.current_question + 1}/{total_questions} : {row['question']}")

        options = {
            "a": row['option_a'],
            "b": row['option_b'],
            "c": row['option_c']
        }

        # Display options as buttons
        selected_option = st.radio(
            "Choisissez une option :",
            list(options.keys()),
            key=f"question-{st.session_state.current_question}"
        )

        # Validate the answer
        if st.button("Valider votre réponse", key=f"validate-{st.session_state.current_question}"):
            if selected_option == row['answer']:
                st.success("Bonne réponse ! ✅")
                st.session_state.score += 1
            else:
                st.error(f"Mauvaise réponse ❌. La bonne réponse était ({row['answer']}) {options[row['answer']]}.")

            # Move to the next question
            st.session_state.current_question += 1

            # Rerun the app to refresh the question
            st.experimental_rerun()

    else:
        # Quiz is finished
        st.write(f"Votre score final : {st.session_state.score}/{total_questions}")

        # Save the results
        new_entry = pd.DataFrame({
            "user_id": [user_id],
            "date": [datetime.now().strftime("%Y-%m-%d")],
            "score": [f"{st.session_state.score}/{total_questions}"]
        })
        history_df = pd.concat([history_df, new_entry], ignore_index=True)
        save_data(users_df, history_df, questions_df)

        st.success("Résultat sauvegardé avec succès !")
        st.balloons()

        # Reset quiz state
        st.session_state.quiz_started = False
        st.session_state.current_question = 0
        st.session_state.score = 0

        # Force reload the data
        st.cache_data.clear()

# Launch the app
if __name__ == "__main__":
    main()
