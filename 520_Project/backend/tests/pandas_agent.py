import pytest
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../app/Api')))
from llm_agent import *
import pandas as pd

# this should run without any exceptions
def test_query_pandas_agent():
    df = pd.read_csv("https://raw.githubusercontent.com/pandas-dev/pandas/main/doc/data/titanic.csv")
    query = "filter rows where age > 21"
    try:
        sql_data = query_pandas_agent(df, query)
    except Exception as e:
        assert False, f"Error: {e}"

# this should return an exception because the dataframe is not a pandas dataframe
def test_query_pandas_agent_fail1():
    df = {}
    query = "filter rows where age > 21"
    with pytest.raises(Exception):
        sql_data = query_pandas_agent(df, query)

# this should return an exception because the query is not a string
def test_query_pandas_agent_fail2():
    df = pd.read_csv("https://raw.githubusercontent.com/pandas-dev/pandas/main/doc/data/titanic.csv")
    query = 123
    with pytest.raises(Exception):
        sql_data = query_pandas_agent(df, query)