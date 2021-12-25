from sqlalchemy import Column, String, Float, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class WeatherDatum(Base):
    __tablename__ = 'timepointdata'

    avg_wind = Column(Float)
    datetime = Column(DateTime, primary_key=True)
    hi_rain_rate = Column(Float)
    hi_temp = Column(Float)
    hi_wind = Column(Float)
    humidity = Column(Float)
    low_temp = Column(Float)
    pressure = Column(Float)
    rain = Column(Float)
    solar = Column(Float)
    temp = Column(Float)
    hi_wind_dir = Column(String)
    prevailing_dir = Column(String)

    def __init__(self, args):
        self.avg_wind = args[0]
        self.datetime = args[1]
        self.hi_rain_rate = args[2]
        self.hi_temp = args[3]
        self.hi_temp = self.hi_temp if 0 < self.hi_temp < 120 else None

        self.hi_wind = args[4]
        self.humidity = args[5]
        self.low_temp = args[6]
        self.low_temp = self.low_temp if 0 < self.low_temp < 120 else None

        self.pressure = args[7]
        self.rain = args[8]
        self.solar = args[9]
        self.temp = args[10]
        self.temp = self.temp if 0 < self.temp < 120 else None

        self.hi_wind_dir = args[11]
        self.prevailing_dir = args[12]


    def data_tup(self):
        return (self.avg_wind, self.datetime, self.hi_rain_rate, self.hi_temp, self.hi_wind,
                self.humidity, self.low_temp, self.pressure, self.rain, self.solar, self.temp, self.hi_wind_dir,
                self.prevailing_dir)


    def __str__(self):
        return f"""
        datetime = {self.datetime}
        temp: {self.temp}
        high temp: {self.hi_temp} degrees
        low temp: {self.low_temp} degrees
        rain: {self.rain} inches
        high rain rate: {self.hi_rain_rate} inches
        pressure: {self.pressure}
        humidity: {self.humidity}
        avg windspeed: {self.avg_wind} mph
        high windspeed: {self.hi_wind} mph
        high wind direction: {self.hi_wind_dir}
        prevailing wind direction: {self.prevailing_dir}
        """

# Base.metadata.create_all(engine)