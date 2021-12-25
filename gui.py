from tkinter import Tk, Canvas, Label, ttk
from tkmacosx import Button, SFrame
from main import retrieve_daily_summaries, retrieve_day_data
from datetime import datetime, timedelta
import re
from math import sin, cos, radians

CELL_BG = '#ffffcc'
WINDOW_BG = '#b1d1dd'
DIRS = ("N","NNE","NE","ENE","E","ESE","SE","SSE","S","SSW","SW","WSW","W","WNW","NW","NNW")
ANGLES = dict(zip(DIRS, [num*22.5 for num in range(16)]))

def combo_changed(b):
    print(f'combo date selected is: {combo.get()}')

    for widget in content.winfo_children():
        widget.destroy()

    if combo.get() == 'Current Month':

        curent_year,current_month = datetime.now().year, datetime.now().month
        start_date = datetime(curent_year, current_month, 1)
        end_date = datetime(curent_year if current_month <12 else curent_year+1, current_month+1 if current_month <12 else 1, 1)

    elif combo.get() == 'Year to Date':
        curent_year = datetime.now().year
        start_date = datetime(curent_year, 1, 1)
        end_date = datetime(curent_year, 12, 31)

    elif combo.get() == "Rain Year to Date":
        date = datetime.now()
        start_date = datetime(date.year if date.month > 6 else date.year-1, 7, 1)
        end_date = datetime(date.year, date.month, date.day-1)

    elif combo.get() == "Previous Rain Year":
        curent_year = datetime.now().year
        start_date = datetime(curent_year - 1, 7, 1)
        end_date = datetime(curent_year, 6, 30)

    elif combo.get() == "Previous Month":
        curent_year,current_month = datetime.now().year, datetime.now().month
        start_date = datetime(curent_year if current_month !=1 else curent_year-1, current_month-1 if current_month !=1 else 12, 1)
        end_date = (start_date + timedelta(days = 40)).replace(day=1)


    data = retrieve_daily_summaries(start_date, end_date)

    tups = [obj.data_tup() for obj in data]
    print(len(tups))
    for tup in tups:
        c = DataCell(tup)
        c.pack(pady=10)

    rain_label['text'] = f'Total Rainfall:  {sum(tup[5] for tup in tups):0.2f}"'
    rainy_days_lo['text'] = f'Number of Rainy Days with <= 0.02":  {sum(1 for tup in tups if 0 < tup[5] <= 0.02)}'
    rainy_days_hi['text'] = f'Number of Rainy Days with > 0.02":   {sum(1 for tup in tups if tup[5] >0.02)}'



class DataCell(Canvas):

    def __init__(self, args):

        super().__init__(content, background=CELL_BG,width=1380, height=150, highlightbackground='#71a1cc')

        self.create_line(260,5,260,145, fill=WINDOW_BG)
        self.create_line(550,5,550,145, fill=WINDOW_BG)
        self.create_line(990,5,990,145, fill=WINDOW_BG)

        c = Canvas(self, background=CELL_BG,width=70, height=70, bd=0, highlightthickness=0)
        c.place(x=850,y=77)
        c.create_oval(4,4,68,68, outline='black', width=2)

        c.create_polygon(32,4,40,4,36,10, fill='black')
        c.create_polygon(32,68,40,68,36,62, fill='black')
        c.create_polygon(4,32,4,40,10,36, fill='black')
        c.create_polygon(68,32,68,40,62,36, fill='black')
        lst = re.findall(r'\D+\d+', args[12])
        r = [(re.match(r'\D+',val).group(0), int(re.search(r'\d+',val).group(0))) for val in lst]
        max_wind = max(r, key = lambda tup:tup[1])[1]
        scaler = 30/max_wind
        for tup in r:
            xc = sin(radians(ANGLES[tup[0]])) * tup[1] * scaler + 36
            yc = -cos(radians(ANGLES[tup[0]])) * tup[1] * scaler + 36
            c.create_line(36,36,xc,yc, fill='red')

        dl = Button(self,text=args[0].strftime("%m/%d/%y"), borderless=True, bg=CELL_BG, height=25, font=('Arial Bold',14), width=95)

        hi_temp = Label(self,text=f'hi_temp:  {args[1]}  @{args[2].strftime("%H:%M")}', bg=CELL_BG, foreground='red', height=1)
        lo_temp = Label(self,text=f'lo_temp:   {args[3]}  @{args[4].strftime("%H:%M")}', bg=CELL_BG,foreground='blue', height=1)

        rain_amt = '-' if args[5] == 0 else f'{round(args[5], 2)} inches'
        rain_total = Label(self,text=f'Rain Total:  {rain_amt}', bg=CELL_BG, height=1)
        rate_amt = '-' if args[6]==0 else f'{round(args[6], 2)} in/hr'
        rate_time = '' if rate_amt=='-' else f'@{args[7].strftime("%H:%M")}'
        hi_rain_rate = Label(self,text=f'High Rain Rate: {rate_amt}  {rate_time}', bg=CELL_BG, height=1)

        pressure = Label(self,text=f'Pressure Range: {args[13]}', bg=CELL_BG, height=1)
        pressure_trend = Label(self,text='6 hr Pressure Trend:', bg=CELL_BG, height=1)

        hi_wind_speed = Label(self,text=f'High wind Speed: {args[9]} mph   @{args[10].strftime("%H:%M")} from the {args[11]}', bg=CELL_BG, height=1)
        avg_wind = Label(self,text=f'Avg. Windspeed: {args[8]} mph', bg=CELL_BG, height=1)
        wind_dirs = Label(self,text='Wind Directions:', bg=CELL_BG, height=1)

        solar_production = Label(self,text=f'Solar Power Production (KWh): 0', bg=CELL_BG, height=1)

        dl.place(x=5, y=5)
        dl.place(x=5, y=5)
        dl.place(x=5, y=5)
        hi_temp.place(x=5,y=40)
        lo_temp.place(x=5,y=65)
        rain_total.place(x=5,y=100)
        hi_rain_rate.place(x=5,y=125)
        pressure.place(x=265,y=40)
        pressure_trend.place(x=265,y=100)
        hi_wind_speed.place(x=555, y=40)
        avg_wind.place(x=555, y=100)
        wind_dirs.place(x=730, y=100)
        solar_production.place(x=995, y=40)

root = Tk()
root.title("Daily Summary")
root.geometry('1500x900')
root['background'] = WINDOW_BG

rain_label = Label(root, text='', bg=WINDOW_BG)
rain_label.place(x=5,y=5)

rainy_days_hi = Label(root, text='', bg=WINDOW_BG)
rainy_days_lo = Label(root, text='', bg=WINDOW_BG)
rainy_days_hi.place(x=230,y=5)
rainy_days_lo.place(x=230,y=30)

date_ranges = ["Current Month", "Previous Month","Year to Date", "Rain Year to Date", "Previous Rain Year", "Custom"]
combo = ttk.Combobox(root, values = date_ranges, background=WINDOW_BG)
combo.bind("<<ComboboxSelected>>", combo_changed)
combo.current(newindex=0)
combo.place(x=570, y=18)

summary_btn = Button(root, text='Summary Graph', borderless=True, bg=WINDOW_BG)
rain_btn = Button(root, text='Rain Graph', borderless=True, bg=WINDOW_BG)
summary_btn.place(x=870, y=18)
rain_btn.place(x=1070, y=18)

content = SFrame(root, background='#b1d1dd', scrollbarwidth=10)

content.configure(width=1400, height=820)
content.grid_propagate(0)
content.place(x=0,y=80)

combo.bind("<<startup>>", combo_changed)
combo.event_generate("<<startup>>")


root.mainloop()