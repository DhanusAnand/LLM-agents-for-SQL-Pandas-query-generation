# LLM Agent for Database Query Generation

This is a web-based tool to translate natural language inputs into SQL/Pandas queries for data analysis. Our tool aims to simplify complex data operations for non-technical users and to streamline workflows for data analysts.

---

## Features  
- **Natural Language Interface**: Accepts queries in everyday language.  
- **Query Generation**: Converts user inputs into SQL or Pandas queries using LLMs.  
- **Data Processing**: Supports Excel/CSV uploads and query-based operations on the uploaded files.  
- **Results Visualization**: Displays processed data and generates visualizations like line charts and pie charts.  
- **Cloud Deployment**: Scalable architecture using AWS/GCP.  
- **User Spaces**: Allows saving preferences and securely storing files.  
- **Export Options**: Enables downloading processed data or visualization charts in formats like `.xlsx` or `.csv`.  

<!-- ---

## Use Cases  
### 1. Upload Data  
- Upload Excel/CSV files via the web interface.  
- Validates the file format and processes it accordingly.  

### 2. Enter Natural Language Query  
- Users provide queries in natural language (e.g., "Show the top 5 sales regions").  
- LLM interprets the query and translates it into SQL/Pandas commands.  

### 3. Generate and Execute Query  
- Prompts LLM with user input and sample data to generate queries.  
- Automatically checks query safety before execution.  

### 4. Visualize Results  
- Users can view the LLM-generated query and processed results.  
- Create charts by selecting columns and visualization types.  

### 5. Export Results  
- Export processed data as XLSX, CSV, or other formats.  
- Download visualization charts.   -->

---

## Technologies Used
- **Frontend**: `Angular` for an interactive user interface.  
- **Backend**: `Flask` for handling the backend, and `LangChain` for interfacing with the LLM.  
- **Database**: `AWS DynamoDB` for scalable cloud data storage.  
<!-- - **Deployment**: Docker for containerization and AWS/GCP for cloud deployment.   -->

---

## Installation  

### Frontend Setup  
1. Install Node.js: [Download here](https://nodejs.org/).  
2. Run the following commands:  
   ```bash  
   npm install -g @angular/cli  
   cd csv-query-app  
   npm install crypto-js  
   ```

### Backend Setup  
Install dependencies:
```bash
    pip install Flask boto3 Flask-CORS requests  
```

## Running
```bash
    cd csv-query-app  
    ng serve
```
