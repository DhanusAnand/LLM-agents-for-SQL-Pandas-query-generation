import os
import sqlite3
import pandas as pd

# Langchain imports
from langchain_openai import OpenAI
from sqlalchemy import create_engine
from langchain_openai import ChatOpenAI
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain.chains import create_sql_query_chain
from sqlalchemy.sql import text

# Loading variables from .env file
from dotenv import load_dotenv
load_dotenv()

PANDAS_AGENT_PROMPT = "Give me the pandas code to get answer to the query: {query}"
SQL_AGENT_PROMPT = "Give me the SQL code to get answer to the following query. Do not select specific columns unless I ask you to do so. If I do not specify the number of rows, then assume that I want all such rows i.e. DO NOT USE LIMIT UNLESS I SPECIFY A NUMBER: {query}"

def query_pandas_agent(df, query):
    if not isinstance(df, pd.core.frame.DataFrame):
        raise Exception("Invalid input. Please provide a pandas DataFrame")
    if not isinstance(query, str):
        raise Exception("Invalid input. Please provide a string query")
    
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
    """Converts a CSV file to an SQLite database table."""
    conn = sqlite3.connect(db_file)
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    conn.close()

def query_sql_agent(df, query):
    if not isinstance(df, pd.core.frame.DataFrame):
        raise Exception("Invalid input. Please provide a pandas DataFrame")
    if not isinstance(query, str):
        raise Exception("Invalid input. Please provide a string query")

    # convert to sqlite
    db_file = "temp_table.db"
    table_name = "temp_table"
    csv_to_sqlite(df, db_file, table_name)
    engine = create_engine(f"sqlite:///{db_file}")
    temp_db = SQLDatabase(engine)

    # run the query via langchain
    chain = create_sql_query_chain(ChatOpenAI(model="gpt-4o-mini"), temp_db)
    prompt = SQL_AGENT_PROMPT.format(query=query)
    print(prompt)
    sql_res = chain.invoke({"question": prompt}).split('SQLQuery: ')[1]
    # output_str = temp_db.run(sql_res)

    # for converting database result in string format to json format
    sql_query = text(sql_res)
    with engine.connect() as connection:
        result = connection.execute(sql_query) 
        rows = result.fetchall()               # Fetch all rows
        columns = result.keys()                # Get the column names

    json_output = {}    
    if len(rows) == 1 and len(columns) == 1:
        json_output['is_table'] = False
        table_json = rows[0][0]
    else:
        json_output['is_table'] = True
        table_json = [dict(zip(columns, row)) for row in rows]

    json_output['query'] = sql_res
    json_output['result'] = table_json
    os.remove(db_file)    

    return json_output
    

# Example Usage

df = pd.read_csv("https://raw.githubusercontent.com/pandas-dev/pandas/main/doc/data/titanic.csv")
# query = "filter rows where age > 21"
query = "how many people with age > 21?"
pandas_res = query_pandas_agent(df, query)
print(pandas_res['output'])
pandas_data = process_pandas_result_to_json(pandas_res)

sql_data = query_sql_agent(df, query)
print(sql_data['query'])