import os
from typing import List, Tuple
from utils.load_config import LoadConfig
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain import hub
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from operator import itemgetter
from sqlalchemy import create_engine
from langchain_community.agent_toolkits import create_sql_agent
from langchain.schema import SystemMessage, HumanMessage, AIMessage

import langchain
langchain.debug = True

APPCFG = LoadConfig()


class ChatBot:
    """
    A ChatBot class capable of responding to messages using different modes of operation.
    It can interact with SQL databases, leverage language chain agents for Q&A,
    and use embeddings for Retrieval-Augmented Generation (RAG) with ChromaDB.
    """
    @staticmethod
    def respond(chatbot: List, message: str) -> Tuple:
        """
        Respond to a message based on the given chat and application functionality types.

        Args:
            chatbot (List): A list representing the chatbot's conversation history.
            message (str): The user's input message to the chatbot.
            chat_type (str): Describes the type of the chat (interaction with SQL DB or RAG).
            app_functionality (str): Identifies the functionality for which the chatbot is being used (e.g., 'Chat').

        Returns:
            Tuple[str, List, Optional[Any]]: A tuple containing an empty string, the updated chatbot conversation list,
                                             and an optional 'None' value. The empty string and 'None' are placeholder
                                             values to match the required return type and may be updated for further functionality.
                                             Currently, the function primarily updates the chatbot conversation list.
        """

        if os.path.exists(APPCFG.stored_csv_xlsx_sqldb_directory):
            engine = create_engine(
                f"sqlite:///{APPCFG.stored_csv_xlsx_sqldb_directory}")
            db = SQLDatabase(engine=engine)
        else:
            chatbot.append(
                (message, f"SQL DB from the stored csv/xlsx files does not exist. Please first execute `src/prepare_csv_xlsx_sqlitedb.py` module."))
            return "", chatbot, None
        print(db.dialect)
        print(db.get_usable_table_names())

        print('this is the message:', message)

        # Agent One: parses for topics 
        messages = [
            SystemMessage(content="You are an assistant that will be given a query asking for information about a specfific topic.\n"
                          "Your goal is to extract key topics from the query and provide an array of topics."),
            HumanMessage(content="Give me information about acute bronchitis"),
            AIMessage(content="[acute bronchitis]"),
            HumanMessage(content=message),
        ]

        topics = APPCFG.langchain_llm.invoke(messages)
        print('this is TOPICS CONTENT:', topics.content)
        print(topics.content)

        agent_executor = create_sql_agent(
        APPCFG.langchain_llm, db=db, agent_type="openai-tools", verbose=True, top_k=APPCFG.top_k)
        response = agent_executor.invoke({"input": topics.content})
        response = response["output"]

        if response:
            chatbot.append(
        (message, response))


        # Agent Three: LangChain SQL Agent      

        # Get the current study status and feed it in as extra information
        time_messages = [
            SystemMessage(content="You are an assistant that will be given a query asking for information about clinical trials.\n"
                          "during a specific period of time and you will return an array of corresponding time periods in the query."),
            HumanMessage(content="Give me information about current acute bronchitis trials"),
            AIMessage(content="[Not yet recruiting, Recruiting, Active, not recruiting, Enrolling by invitation]"),
            HumanMessage(content="Give me information about completed acute bronchitis trials"),
            AIMessage(content="[Completed, Suspended, Terminated, Withdrawn]"),
            HumanMessage(content="Give me information about completed pneumonia trials that went wrong"),
            AIMessage(content="[Suspended, Terminated, Withdrawn]"),
            HumanMessage(content="List clinical trials that are currently recruiting"),
            HumanMessage(content="Recruiting, Enrolling by invitation"),
            HumanMessage(content=message),
        ]

        time_periods = APPCFG.langchain_llm.invoke(time_messages)
        print('this is TIME PERIODS CONTENT:', time_periods.content)
        if time_periods: 
            message = message + " with the following possible study status " + time_periods.content      

        template = '''Given an input question, first create a syntactically correct {dialect} query to run, then look at the results of the query and return the answer.
        Use the following format:

        Question: "Question here"
        SQLQuery: "SQL Query to run"
        SQLResult: "Result of the SQLQuery"
        Answer: "Final answer here"

        Only use the following tables:

        {table_info}.

        Question: {input}'''
        prompt = PromptTemplate.from_template(template)
        agent_executor = create_sql_agent(
            APPCFG.langchain_llm, db=db, agent_type="openai-tools", verbose=True, top_k=APPCFG.top_k)
        response = agent_executor.invoke({"input": message})
        response = "This is the response taking the time frame into consideration: " + response["output"]



        # Get the `response` variable from any of the selected scenarios and pass it to the user.
        if response:
            chatbot.append(
            (message, response))


       # Agent Three: LangChain SQL Agent      
        agent_executor = create_sql_agent(
            APPCFG.langchain_llm, db=db, agent_type="openai-tools", verbose=True, top_k=APPCFG.top_k)
        response = agent_executor.invoke({"input": message})
        response = response["output"]

        # Get the `response` variable from any of the selected scenarios and pass it to the user.
        if response:
            chatbot.append(
            (message, response))
        return "", chatbot
