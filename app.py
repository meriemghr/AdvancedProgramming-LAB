import pandas as pd
import streamlit as st
import time
from datetime import datetime

# Function to load data
@st.cache_data
def load_data():
    excel_file = "qcm_data.xlsx"
    users_df = pd.read_excel(excel_file, sheet_name="users")
    history_df = pd.read_excel(excel_file, sheet_name="history")
    questions_df = pd.read_excel(excel_file, sheet_name="questions")
    return users_df, history_df, questions_df

# Function to save data
def save_data(users_df, history_df, questions_df):
    with pd.ExcelWriter("qcm_data.xlsx", engine="openpyxl") as writer:
        users_df.to_excel(writer, sheet_name="users", index=False)
        history_df.to_excel(writer, sheet_name="history", index=False)
        questions_df.to_excel(writer, sheet_name="questions", index=False)

# Display user history
def user_history(user_id, history_df):
    st.subheader("Historique des QCM")
    history_user = history_df[history_df['user_id'] == user_id]
    if history_user.empty:
        st.info("Aucun historique trouvé pour cet utilisateur.")
    else:
        st.write("Voici votre historique complet :")
        for index, row in history_user.iterrows():
            st.write(f"📅 Date: {row['date']}, Score: {row['score']}")


def export_results_to_file(history_user):
    
    csv_file = "quiz_results.csv"
    history_user.to_csv(csv_file, index=False)
    with open(csv_file, "rb") as f:
        st.download_button(
            label="📥 Télécharger les résultats en CSV",
            data=f,
            file_name=csv_file,
            mime="text/csv"
        )
    
    txt_file = "quiz_results.txt"
    with open(txt_file, "w") as f:
        for _, row in history_user.iterrows():
            f.write(f"User ID: {row['user_id']}, Date: {row['date']}, Score: {row['score']}\n")
    with open(txt_file, "rb") as f:
        st.download_button(
            label="📥 Télécharger les résultats en TXT",
            data=f,
            file_name=txt_file,
            mime="text/plain"
        )

def run_quiz(user_id, questions_df, history_df, users_df):
    st.header("QCM en cours 🗃️")
    if "current_question"  in st.session_state:
     st.write(st.session_state.current_question)
    st.header("Choisissez une catégorie pour commencer le QCM 🗂️")
    categories = questions_df['category'].unique()  # Get unique categories from the questions
    selected_category = st.selectbox("Sélectionner une catégorie", categories)

    if selected_category:
        # Store the selected category in session state
        st.session_state.selected_category = selected_category
        st.session_state.quiz_started = True

        # Filter the questions based on the selected category
        questions_category_df = questions_df[questions_df['category'] == selected_category]
        st.session_state.questions_category_df = questions_category_df
    total_questions = len(questions_category_df)

    # Initialisation des variables d'état de session si elles n'existent pas
    if "current_question" not in st.session_state:
        st.session_state.current_question = 0
        st.session_state.score = 0
    if "answer_validated" not in st.session_state:
        st.session_state.answer_validated = False
    if "start_time" not in st.session_state:
        st.session_state.start_time = None  # Initialise start_time à None

    # Définir start_time seulement si ce n'est pas encore défini
    if st.session_state.start_time is None:
        st.session_state.start_time = time.time()

    # Afficher la question actuelle
    if st.session_state.current_question < total_questions:
        row = questions_category_df.iloc[st.session_state.current_question]
        st.subheader(f"Question {st.session_state.current_question + 1}/{total_questions} : {row['question']}")

        options = {
            "a": row['option_a'],
            "b": row['option_b'],
            "c": row['option_c']
        }

        # Afficher les options comme des boutons radio
        selected_option = st.radio(
            "Choisissez une option :",
            list(options.values()),
            key=f"question-{st.session_state.current_question}"
        )

        # Gestion du timer pour la question actuelle
        elapsed_time = time.time() - st.session_state.start_time
        remaining_time = 5 - int(elapsed_time)
        mins, secs = divmod(remaining_time, 60)

        if remaining_time > 0:
            st.write(f"⏳ Temps restant : {mins:02d}:{secs:02d}")
        else:
            # Si le temps est écoulé, valider automatiquement la réponse comme incorrecte
                st.session_state.answer_validated = True
                st.write("Temps écoulé ❌. La bonne réponse était" + str(row['answer']) + " car " + str(row['explication']))
                st.session_state.answer_validated = True  # Marquer la réponse comme validée automatiquement

        # Valider la réponse si l'utilisateur clique sur le bouton avant que le temps ne soit écoulé
        if remaining_time > 0 and st.button("Valider votre réponse", key=f"validate-{st.session_state.current_question}"):

            if selected_option == row['answer']:
                st.success("Bonne réponse ! ✅")
                st.session_state.score += 1
            else:
                st.write("Mauvaise réponse ❌. La bonne réponse était " + str(row['answer']) + " car " + str(row['explication']) )
            st.session_state.answer_validated = True  # La réponse est validée

        if st.session_state.answer_validated:
            if st.session_state.current_question < total_questions - 1:
                next_question_button = st.button("Question suivante")
                if next_question_button:
                    st.session_state.current_question += 1  # Passer à la question suivante
                    st.session_state.answer_validated = False  # Réinitialiser la validation
                    st.session_state.start_time = None  # Réinitialiser le timer pour la prochaine question
                    st.rerun()  # Forcer le rechargement de la prochaine question
            else:
                # Fin du quiz
                st.success("Vous avez terminé le QCM ! 🎉")
                st.write(f"🎉 **Votre score final : {st.session_state.score}/{total_questions}**")

                # Enregistrer les résultats dans l'historique
                new_entry = pd.DataFrame({
                    "user_id": [user_id],
                    "date": [datetime.now().strftime("%Y-%m-%d")],
                    "score": [f"{st.session_state.score}/{total_questions}"]
                })
                history_df = pd.concat([history_df, new_entry], ignore_index=True)
                save_data(users_df, history_df, questions_df)

                st.success("Résultat sauvegardé avec succès !")
                st.balloons()

                # Réinitialiser l'état pour un nouveau quiz
                st.session_state.quiz_started = False
                st.session_state.current_question = 0
                st.session_state.score = 0
                st.session_state.start_time = None  
                
                user_history(user_id, history_df)
                history_user = history_df[history_df['user_id'] == user_id]
                st.cache_data.clear()
                export_results_to_file(history_user)
                st.session_state.page = "login" 

# Login page logic
def login_page(users_df, history_df):
    # If no user is logged in, initialize session state
    if "current_user" not in st.session_state:
        st.session_state.current_user = None
    if "quiz_started" not in st.session_state:
        st.session_state.quiz_started = False
    if "current_question" not in st.session_state:
        st.session_state.current_question = 0
    if "score" not in st.session_state:
        st.session_state.score = 0

    st.header("Connexion utilisateur")
    username = st.text_input("Entrez votre nom :").strip()

    if username:
        # Check if the username exists in the users_df
        user = users_df[users_df['name'] == username]

        if not user.empty:
            st.success(f"Bienvenue, {username} ! 🎉")

            # Get the user id
            user_id = user.iloc[0]['id']
            st.session_state.user_id = user_id  # Set the user_id in session state

            # Display the user's history
            user_history(user_id, history_df)

            # Start a new quiz
            if st.button("Commencer un nouveau QCM"):
                st.session_state.quiz_started = True
                st.session_state.current_question = 0
                st.session_state.score = 0
                st.session_state.page = "quiz"  # Set the page to "quiz" to navigate to the quiz page

                # Refresh to load the quiz
                st.rerun()

        else:
            st.error("Utilisateur non trouvé. Veuillez vérifier votre nom ou créer un nouvel utilisateur.")

            # Option to create a new user
            if st.checkbox("Créer un nouvel utilisateur"):
                new_id = users_df['id'].max() + 1
                new_user = pd.DataFrame({"id": [new_id], "name": [username]})
                users_df = pd.concat([users_df, new_user], ignore_index=True)
                save_data(users_df, history_df, questions_df)
                st.success("Utilisateur créé avec succès ! Rechargez l'application.")
                user_id = new_id
                st.session_state.user_id = user_id  # Set the user_id in session state

                if st.button("Commencer un nouveau QCM"):
                    st.session_state.quiz_started = True
                    st.session_state.current_question = 0
                    st.session_state.score = 0
                    st.session_state.page = "quiz"  # Navigate to the quiz page
                    st.rerun()

    else:
        st.info("Entrez votre nom pour continuer.")


# Main entry point for the Streamlit app
st.title("Application de QCM Informatique 📘")
users_df, history_df, questions_df = load_data()

# Ensure all session states are initialized
if "page" not in st.session_state:
    st.session_state.page = "login"

if st.session_state.page == "login":
        login_page(users_df, history_df)
elif st.session_state.page == "quiz":
    run_quiz(st.session_state.user_id, questions_df, history_df, users_df)
