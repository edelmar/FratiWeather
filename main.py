import downloader
from updater import WeatherDatum
from daily_summary_creator import DailySummary
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

engine = create_engine('sqlite:////Users/ricdelmar/Complete-Python-3-Bootcamp-master/weather4.sqlite')


def update_database():
    session = sessionmaker(bind=engine)()

    results = downloader.download_Starter()
    print()
    print(*results[:5], sep='\n')
    print('.', '.', '.', '.', sep='\n')
    print(*results[-5:], sep='\n')

    for tup in results:  # Update the WeatherDatum table with the latest data
        wd = WeatherDatum(tup)
        try:
            session.add(wd)
            session.commit()

        except Exception as e:
            print(e)
            print(f'This WeatherDatum object caused an error: {wd}')



    max_ = session.query(func.max(DailySummary.datetime))
    dt = max_[0][0]  # last date in the DailySummary table
    start_date = dt + timedelta(days=1)


    for day in range(100):

        day_to_search = start_date + timedelta(days=day)
        if day_to_search.date() == datetime.now().date():
            break

        r = session.query(WeatherDatum).filter(WeatherDatum.datetime >= day_to_search,
                                               WeatherDatum.datetime < day_to_search + timedelta(days=1))
        tuple_list = [obj.data_tup() for obj in r]
        if tuple_list:
            ds = DailySummary.summary_from_timepoints(tuple_list)
            session.add(ds)
        else:
            break

    session.commit()
    session.close()

    with open('/Users/ricdelmar/Desktop/z_test/test_write.txt', 'a') as f:
        f.write(f'Updated FratiWeather on {datetime.now()}\n')



def retrieve_daily_summaries(start, end):
    session = sessionmaker(bind=engine)()
    result = session.query(DailySummary).filter(DailySummary.datetime >= start, DailySummary.datetime < end)
    session.close()
    return result


def retrieve_day_data(date):
    session = sessionmaker(bind=engine)()
    print(date)
    session.close()



if __name__ == '__main__':
    update_database()
