# Weather Data

## Overview

Airplane pilots live in a world of weather.  It determines whether they can take off, which route they take, and if they'll get to their destination on time.

Weather data is published and available from a number of different sources, including METARS by the National Weather Service.  It's available in a number of different ways, but the basic text follows a strictly defined set of rules.  The data is similar to what you'd like to hear from the radio or TV station with a more direct look at cloud coverage and dewpoint.

It's published on the hour, every hour with additional updates for unusual weather patterns.

## Format

The raw text of a weather report is easily scannable by pilots:

`KMSP 270253Z 22005KT 10SM BKN250 M16/M20 A3022 RMK AO2 SLP256 T11561200 55012`

This starts with the station, in this case at the Minneapolis Saint Paul airport, the time stamp, and then a series of data points useful for flight, including:

- Windspeed
- Visibility
- Cloud Coverage
- Temperature
- Dew Point
- Altimeter Setting
- Various Remarks
