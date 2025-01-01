import pandas as pd
import streamlit as st
from datetime import datetime

# charging the data from the excel file
@st.cache_data
def load_data():
    # on va transformmer chaque feuille en data_qcm a une dataframe
    excel_file = "qcm_data.xlsx"
    users_df = pd.read_excel(excel_file, sheet_name="users")
    history_df = pd.read_excel(excel_file, sheet_name="history")
    questions_df = pd.read_excel(excel_file, sheet_name="questions")
    return users_df, history_df, questions_df

# our main function
def main():
    st.title("Application de QCM Informatique 📘")

    # charging the data
    users_df, history_df, questions_df = load_data()

    # le debut de la page 
    st.header("Connexion utilisateur")
    username = st.text_input("Entrez votre nom :").strip()

    if username:
        # verifying if the user actually exists
        user = users_df[users_df['name'] == username]

        if not user.empty:
            st.success(f"Bienvenue, {username} ! 🎉")

            # getting the user id
            user_id = user.iloc[0]['id']

            # displaying the user's history (displaying the database : history)
            st.subheader("Historique des QCM")
            user_history = history_df[history_df['user_id'] == user_id]
            if user_history.empty:
                st.info("Aucun historique trouvé pour cet utilisateur.")
            else:
                st.dataframe(user_history)

            # strating a new qcm
            if st.button("Commencer un nouveau QCM"):
                run_quiz(user_id, questions_df, history_df)

        else:
            st.error("Utilisateur non trouvé. Veuillez vérifier votre nom ou créer un nouvel utilisateur.")

            # option to create a new user
            if st.checkbox("Créer un nouvel utilisateur"):
                new_id = users_df['id'].max() + 1
                new_user = pd.DataFrame({"id": [new_id], "name": [username]})
                users_df = pd.concat([users_df, new_user], ignore_index=True)
                with pd.ExcelWriter("qcm_data.xlsx", engine="openpyxl", mode="a", if_sheet_exists="overlay") as writer:
                    users_df.to_excel(writer, sheet_name="users", index=False)
                st.success("Utilisateur créé avec succès ! Rechargez l'application.")

    else:
        st.info("Entrez votre nom pour continuer.")

# the function that excutes the qcm
def run_quiz(user_id, questions_df, history_df):
    st.header("QCM en cours 🗃️")

    if "current_question" not in st.session_state:
        st.session_state.current_question = 0
        st.session_state.score = 0

    total_questions = len(questions_df)

    if st.session_state.current_question < total_questions:
        row = questions_df.iloc[st.session_state.current_question]
        st.subheader(f"Question {st.session_state.current_question + 1}/{total_questions} : {row['question']}")

        options = {
            "a": row['option_a'],
            "b": row['option_b'],
            "c": row['option_c']
        }
        for key, value in options.items():
            st.write(f"{key}) {value}")

        selected_option = st.radio("Choisissez une option :", list(options.keys()), key=f"question-{st.session_state.current_question}")

        if st.button("Valider votre réponse", key=f"validate-{st.session_state.current_question}"):
            if selected_option == row['answer']:
                st.success("Bonne réponse ! ✅")
                st.session_state.score += 1
            else:
                st.error(f"Mauvaise réponse ❌. La bonne réponse était ({row['answer']}) {options[row['answer']]}.")

            st.session_state.current_question += 1
            st.experimental_rerun()
    else:
        st.write(f"Votre score final : {st.session_state.score}/{total_questions}")

        # saving the results
        new_entry = pd.DataFrame({
            "user_id": [user_id],
            "date": [datetime.now().strftime("%Y-%m-%d")],
            "score": [f"{st.session_state.score}/{total_questions}"]
        })
        history_df = pd.concat([history_df, new_entry], ignore_index=True)
        with pd.ExcelWriter("qcm_data.xlsx", engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
            history_df.to_excel(writer, sheet_name="history", index=False)

        st.success("Résultat sauvegardé avec succès !")
        st.balloons()

# launching the app
if __name__ == "__main__":
    main()
