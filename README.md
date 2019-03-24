##My REST Application

## Description about the app
This Flask application enables you to get the weather of a certain city and it also has a currency converter.

The application uses two REST API's, available publicly for free but requires registration.

You can type a city/town, and the result will give you a summary of the current weather i.e "Clear Sky" and the temperature.

You can also check the current currency exchange rate for any two given world currencies.


## Setup
How to check it out, install and get the application running


External API Registration
1.
Weather - https://openweathermap.org/api 
select "Current weather data" option and register to optain API key

Currency - https://openexchangerates.org
select "Free Plan" option and sign-up to optain API key



Initial setup
2. Create a folder called "instance"
  2.1 Within instance folder, create a file called "config.py"
  2.2 Edit the file and add the following - replacing the API key from above step after registering.

DEBUG = False
API_KEY_WEATHER = "Weather API Key"
API_KEY_CURRENCY = "Currency API Key"

3. Create a file called "config.py" in the root folder.
  3.1 Edit the file and add 

DEBUG = False

  3.2 during development, you can change this DEBUG to "True"
