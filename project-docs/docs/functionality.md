# Functionality
## 1. Flight Search
- Searches for available flights based on user preferences.
- API used: **Amadeus Flight Search API**.

## 2. Hotel Search
- Uses the **Amadeus Hotel List API**.
- Returns hotel options based on destination, check-in/check-out dates, and price range.

## 3. Weather Forecast
- Fetches real-time weather data for the travel location.
- API used: **WeatherAPI/OpenWeather**.

## 4. Currency Conversion
- Converts between different currencies.
- API used: **ExchangeRatesAPI**.

## 5. News Reporting
- Report the news based on queried location.
- API used: **NewsAPI**.

## 6. LLM-based Decision Making
- The LLM determines which tool to use based on the input query.

---

## How to Run the Project

To run the **Customer Service Assistant**, follow these steps:

### **1. Setup the Environment**

Clone the repository and install the dependencies:

```bash
git clone https://github.com/AkshayJadhav96/Travel-_Planning_Assistant.git
```
Before running following command Please ensure just is already installed in your system 
```bash
just setup  
```

### **2. Running the Application**

#### Run the Backend

Start the backend server using FastAPI:
```bash
just run-fastapi
```
This will start the backend server, which powers the core functionality of the system.

#### Run the Frontend

Start the frontend interface using Streamlit:
```bash
just run-gui
```
This will launch the Streamlit frontend, allowing you to interact with the system via a web interface.


#### Run MkDocs for Documentation

To view the project documentation locally, run MkDocs:
```bash
just run-mkdocs
```
This will start a local server where you can view the project documentation in your browser.

#### Run Ruff for Linting

To check the code for linting issues using Ruff:
```bash
just run-ruff
```
This will analyze the codebase and report any linting errors or warnings.
```