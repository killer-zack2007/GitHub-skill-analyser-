GitHub Pulse — Skill Evolution Analyzer

A student-friendly GitHub analytics web app built with Streamlit.
Features
Public GitHub profile analysis
Activity-based proficiency estimate
Project, language, collaboration and community signals
Repository creation timeline
Dataset collector
Optional Random Forest model
GitHub activity is not the same as actual programming ability. The score is an activity-based estimate.
Run
python -m venv .venv
Windows:
.venv\Scripts\activate
macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
Copy .env.example to .env, add your GitHub token, then:
streamlit run app.py

Collect data
Start small:
python src/collect_dataset.py --pages 1 --per-page 10 --output data/raw/github_users.csv
Train ML
For supervised ML, add a skill_level column using an independently defined labeling process:
python src/train_model.py --input data/raw/github_users.csv --output models/github_skill_model.joblib
The app automatically uses the saved model if present; otherwise it uses the transparent rubric.

Structure

github-skill-analyzer/

├── app.py

├── requirements.txt

├── .env.example

├── .gitignore

├── README.md

├── data/raw/

├── models/

└── src/

    ├── __init__.py
    
    ├── github_api.py
    
    ├── analyzer.py
    
    ├── collect_dataset.py
    
    └── train_model.py
