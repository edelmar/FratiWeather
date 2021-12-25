from sqlalchemy import Column, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


# noinspection SpellCheckingInspection
class DailySummary(Base):
    __tablename__ = 'summary'

    datetime = Column(DateTime, primary_key=True)

    hi_temp = Column(Float)
    hi_temp_time = Column(DateTime)
    low_temp = Column(Float)
    low_temp_time = Column(DateTime)

    rain = Column(Float)
    hi_rain_rate = Column(Float)
    hi_rain_rate_time = Column(DateTime)

    avg_wind = Column(Float)
    hi_wind = Column(Float)
    hi_wind_time = Column(DateTime)
    hi_wind_dir = Column(String)
    prevailing_dir = Column(String)

    pressure_range = Column(String)
    solar = Column(Float)

    def __init__(self, args):
        self.datetime = args[0]

        self.hi_temp = args[1]
        self.hi_temp_time = args[2]
        self.low_temp = args[3]
        self.low_temp_time = args[4]

        self.rain = args[5]
        self.hi_rain_rate = args[6]
        self.hi_rain_rate_time = args[7]

        self.avg_wind = args[8]
        self.hi_wind = args[9]
        self.hi_wind_time = args[10]
        self.hi_wind_dir = args[11]
        self.prevailing_dir = args[12]

        self.pressure_range = args[13]
        self.solar = args[14]

    @classmethod
    def summary_from_timepoints(cls, day_data: list):
        z = list(zip(*day_data))

        avg_wind_speed = round(sum(z[0]) / len(z[0]), 1)
        dt = z[1][0]
        hirain = max(z[2])
        hiraintime = [tup[1] for tup in day_data if tup[2] == hirain][0]
        hitemp = max([num for num in z[3] if num != None], default=0)
        if hitemp == 0:
            hitemptime = dt
        else:
            hitemptime = [tup[1] for tup in day_data if tup[3] == hitemp][0]
        hiwind = max(z[4])
        hiwinddir = [tup[11] for tup in day_data if tup[4] == hiwind][0]
        hiwindtime = [tup[1] for tup in day_data if tup[4] == hiwind][0]
        lowtemp = min([num for num in z[6] if num != None], default=100)
        if lowtemp == 100:
            lowtemptime = dt
        else:
            lowtemptime = [tup[1] for tup in day_data if tup[6] == lowtemp][0]
        pressurerange = f'{min(z[7]):1.2f}-{max(z[7]):1.2f}'
        rain = sum(z[8])
        solar = sum(z[9])

        d = dict()
        for direc in ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW",
                      "NNW"]:
            d[direc] = z[12].count(direc)
        prevailwind = ''.join(f'{k}{v}' for k, v in d.items())

        return DailySummary((dt, hitemp, hitemptime, lowtemp, lowtemptime, rain,
                             hirain, hiraintime, avg_wind_speed, hiwind, hiwindtime,
                             hiwinddir, prevailwind, pressurerange, solar))

    def data_tup(self):
        return (self.datetime, self.hi_temp, self.hi_temp_time, self.low_temp, self.low_temp_time,
                self.rain, self.hi_rain_rate, self.hi_rain_rate_time, self.avg_wind, self.hi_wind,
                self.hi_wind_time, self.hi_wind_dir, self.prevailing_dir, self.pressure_range)

    def __str__(self):
        return f"""
           datetime = {self.datetime.month}/{self.datetime.day}/{self.datetime.year}
           high temp: {self.hi_temp} degrees
           high temp time: {self.hi_temp_time.hour}:{self.hi_temp_time.minute}
           low temp: {self.low_temp} degrees
           low temp time: {self.low_temp_time.hour}:{self.low_temp_time.minute}
           rain: {self.rain} inches
           high rain rate: {self.hi_rain_rate} inches/hour
           high rain rate time: {self.hi_rain_rate_time.hour}:{self.hi_rain_rate_time.minute}
           avg windspeed: {self.avg_wind} mph
           high windspeed: {self.hi_wind} mph
           high windspeed time: {self.hi_wind_time.hour}:{self.hi_wind_time.minute}
           high wind direction: {self.hi_wind_dir}
           prevailing wind direction: {self.prevailing_dir}
           pressure range: {self.pressure_range}
           """

