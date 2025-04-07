# **Functionality**
## 1. Flight Search
- Searches for available flights based on user preferences.
- API used: **Amadeus Flight Search API**.
- This functionality gives the rates and flights for the src destination/airport,target destination/airport,date of travel (not in past) (required).
- Also you can get the rates and flights for number of adults you want and in the currency you want.

## 2. Hotel Search
- Uses the **Amadeus Hotel List API**.
- Returns hotel options based on destination, check-in/check-out dates, and price range.
- This functionality requires the city,radius,radius unit and also suggests hotels based on ammenities and ratings.

## 3. Weather Forecast
- Fetches real-time weather data for the travel location. 
- API used: **WeatherAPI/OpenWeather**.
- The weather is forecasted for a given city for a given number of days in future starting from today onwards but less tha 14.

## 4. Currency Conversion
- Converts between different currencies.
- API used: **ExchangeRatesAPI**.
- Converts the amount from one currency to another

## 5. News Reporting
- Report the news based on queried location.
- API used: **NewsAPI**.

## 6. LLM-based Decision Making
- The LLM determines which tool to use based on the input query.
