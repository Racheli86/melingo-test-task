# Smart Grocery Order Agent

An AI-powered agent built with **LangGraph** and **LangChain** that processes free-text grocery orders, matches them against a product catalog, handles stock availability, and calculates totals.

## Features
* **Natural Language Processing**: Extracts items and quantities from unstructured text.
* **Fuzzy Matching**: Maps customer requests to catalog products.
* **Stock Management**: Handles out-of-stock items and partial fulfillment (ORD08 logic).
* **Automated Calculations**: Calculates subtotals, 10% tax, and grand totals.
* **Code Quality**: Formatted with `black` and `isort`.
* **Conditional Workflow Routing**: Implemented smart termination logic in the graph to handle failed extractions efficiently.
* **Production-Ready Error Handling**: Graceful degradation and logging for robustness against API failures.

## Setup & Installation

1. **Clone the repository**:
   ```bash
   git clone <your-repository-url>
   cd melingo-test-task

2. **Set up environment variables**:
   ```bash
    Create a .env file in the root directory and add your OpenAI API key:
    OPENAI_API_KEY=your_actual_key_here

3. **Install dependencies**:
   ```bash
    pip install -r requirements.txt

## Running the Project:
   ```bash
   To process the test orders and see the output:
   python test_run.py

Docker Support
If you have Docker installed, you can run the agent in a containerized environment:

1. Build the Docker image:
   docker build -t grocery-agent .

2. Run the container:
    (This will use the API key from your local .env file)
    docker run --env-file .env grocery-agent
