import os

from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
# loading variables from .env file
load_dotenv()


import pandas as pd
from langchain_openai import OpenAI

# df = pd.read_csv(
#     "https://raw.githubusercontent.com/pandas-dev/pandas/main/doc/data/titanic.csv"
# )

# agent = create_pandas_dataframe_agent(OpenAI(temperature=0), df, verbose=True,  allow_dangerous_code= True,
#                                      return_intermediate_steps=True)

# res = agent.invoke("how many rows are there?")
# print(res)

PANDAS_AGENT_PROMPT = "give me the pandas code to get answer to the query: {query}"

def query_pandas_agent(df, query):
    agent = create_pandas_dataframe_agent(OpenAI(temperature=0), df, verbose=True,  allow_dangerous_code= True,
                                     return_intermediate_steps=True)

    prompt = PANDAS_AGENT_PROMPT.format(query=query)
    print(prompt)
    res = agent.invoke(prompt)
    print(res)
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

# query = "filter the data where age >=21"
# res = query_pandas_agent(df, query)
# print(process_pandas_result_to_json(res))