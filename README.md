## General structure of the projects:

```
Project-folder
  ├── README.md           <- The top-level README for developers using this project.
  ├── .env                <- dotenv file for local configuration.
  ├── configs             <- Holds yml files for project configs
  ├── data                <- Contains clinical trial data
  ├── src                 <- Contains the source code(s) for executing the project.
  |   └── utils           <- Contains all the necessary project modules.
```

## Instructions to Run Application:

1. Create your venv with the following command: python -m venv your_env_name
2. Create an .env file inside the Q&A and RAG with SWL Tabular Data folder with with your OPENAI_API_KEY and get_deployment_name set to your model name (i.e gpt-4o-mini) 
3. Activate your venv with the command: pip install -r requirements.txt
4. Run the application with the following command:

**Database:**

- sql/csv_slsx_sqldb.db

**Table:**

- clinical_trials
