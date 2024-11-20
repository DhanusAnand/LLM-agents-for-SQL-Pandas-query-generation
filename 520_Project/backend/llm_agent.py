import os
import sqlite3
import pandas as pd

# Langchain imports
from langchain_openai import OpenAI
from sqlalchemy import create_engine
from langchain_openai import ChatOpenAI
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent

# Loading variables from .env file
from dotenv import load_dotenv
load_dotenv()

PANDAS_AGENT_PROMPT = "Give me the pandas code to get answer to the query: {query}"
SQL_AGENT_PROMPT = "Give me the SQL code to get answer to the following query. If I do not specify the number of rows, then assume that I want all such rows: {query}"

def query_pandas_agent(df, query):
    agent = create_pandas_dataframe_agent(OpenAI(temperature=0), df, verbose=False,  allow_dangerous_code= True,
                                     return_intermediate_steps=True)
    prompt = PANDAS_AGENT_PROMPT.format(query=query)
    print(prompt)
    res = agent.invoke(prompt)
    return res

def process_pandas_result_to_json(res):
    data = {
        "query": res["output"],
    }
    
    if(isinstance(res['intermediate_steps'][0][-1],pd.core.frame.DataFrame)):
        data["is_table"] = True
        data["result"] = res['intermediate_steps'][0][-1].to_json()
    else:
        data["is_table"] = False
        data["result"] = res['intermediate_steps'][0][-1]
    return data

def csv_to_sqlite(df, db_file, table_name):
    """Converts a CSV file to a SQLite database table."""
    conn = sqlite3.connect(db_file)
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    conn.close()

def query_sql_agent(df, query):
    db_file = "table_name.db"
    table_name = "table_name"
    # dummy dataframe for input to llm
    csv_to_sqlite(df[:5], db_file, table_name)      # create dummy dataframe with minimal rows for lesser context length
    engine = create_engine(f"sqlite:///{db_file}")
    db = SQLDatabase(engine)

    agent_executor = create_sql_agent(ChatOpenAI(model="gpt-3.5-turbo", temperature=0), db=db, agent_type="openai-tools", 
                                      verbose=True, agent_executor_kwargs = {"return_intermediate_steps": True})
    prompt = SQL_AGENT_PROMPT.format(query=query)
    print(prompt)
    res = agent_executor.invoke(prompt)
    
    sql_queries = []
    for (log, output) in res["intermediate_steps"]:
        if log.tool == 'sql_db_query':
            sql_queries.append(log.tool_input)

    # this time, create use dataframe for final output
    csv_to_sqlite(df, db_file, table_name) 
    engine = create_engine(f"sqlite:///{db_file}")
    db = SQLDatabase(engine)
    os.remove(db_file)

    if len(sql_queries) > 0:
        output = db.run(sql_queries[0]['query'])
        return output, sql_queries[0]['query']
    else:
        assert False, "No SQL query generated"

def process_sql_result_to_json(res, query):
    data = {
        "result": res,
        "query": query,
    }
    return data


# Example Usage

# df = pd.read_csv("https://raw.githubusercontent.com/pandas-dev/pandas/main/doc/data/titanic.csv")
# query = "filter rows where age > 21"
# pandas_res = query_pandas_agent(df, query)
# print(pandas_res['output'])
# pandas_data = process_pandas_result_to_json(pandas_res)

# sql_res, sql_query = query_sql_agent(df, query)
# sql_data = process_sql_result_to_json(sql_res, sql_query)
# print(sql_query)