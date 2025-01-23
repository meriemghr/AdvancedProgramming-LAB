# Project Overview
This project is designed to create an interactive **Questionnaire à Choix Multiples (QCM) application**. We use an Excel file to store the database, and the application is built with Python using the following technologies:

- **Pandas**: We use **Pandas** to load, manipulate, and transform data from the Excel file into /*DataFrames**. This allows us to handle structured data such as users, question histories, and answers efficiently.

- **Streamlit**: Streamlit is used to create a simple yet interactive web interface for the QCM application. It allows users to take quizzes, view scores in real-time, and interact with the app with minimal code.

## Project Features
- **User Management**: Users can log in, create new profiles, and view their quiz history.
- **Questionnaire Interface**: Users can answer questions, get immediate feedback, and see their progress.
- **Timer**: A countdown timer is included for each question to simulate a time-constrained environment.
- **Export Results**: After completing the quiz, users can download their results in different formats (CSV, TXT).

## Requirements
To run the project locally, you need the following:

- **Python**: Make sure you have **Python 3.7+** installed.
- **Dependencies**: Install the necessary libraries using the following command:
  
***pip install requirement***

This will install all the required Python libraries such as Pandas and Streamlit.

## Running the Project
Once the dependencies are installed, you can start the application:

- Open your terminal and navigate to the project directory.
- Run the following command to launch the Streamlit app:

***streamlit run app.py***

## Data Storage
The app uses an **Excel** file named ***qcm_data.xlsx*** to store:
- User Information (sheet: users)
- Quiz History (sheet: history)
- Questions and Answers (sheet: questions)
  
## Conclusion
This project demonstrates how to use **Python** explicitally **Pandas** for data manipulation and **Streamlit** for building an interactive application. It allows users to engage with quizzes, track their performance, and manage data efficiently.

