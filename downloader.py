import sqlite3
from datetime import datetime

import serial

LF = bytearray([10])
LFCR = bytearray([10, 13])
ACK = bytearray([6])
NAK = bytearray([33])
DMPAFT = bytearray([68, 77, 80, 65, 70, 84, 13])
ESC = bytearray([27])

CRC_TABLE = [
    0x0, 0x1021, 0x2042, 0x3063, 0x4084, 0x50a5, 0x60c6, 0x70e7,
    0x8108, 0x9129, 0xa14a, 0xb16b, 0xc18c, 0xd1ad, 0xe1ce, 0xf1ef,
    0x1231, 0x210, 0x3273, 0x2252, 0x52b5, 0x4294, 0x72f7, 0x62d6,
    0x9339, 0x8318, 0xb37b, 0xa35a, 0xd3bd, 0xc39c, 0xf3ff, 0xe3de,
    0x2462, 0x3443, 0x420, 0x1401, 0x64e6, 0x74c7, 0x44a4, 0x5485,
    0xa56a, 0xb54b, 0x8528, 0x9509, 0xe5ee, 0xf5cf, 0xc5ac, 0xd58d,
    0x3653, 0x2672, 0x1611, 0x630, 0x76d7, 0x66f6, 0x5695, 0x46b4,
    0xb75b, 0xa77a, 0x9719, 0x8738, 0xf7df, 0xe7fe, 0xd79d, 0xc7bc,
    0x48c4, 0x58e5, 0x6886, 0x78a7, 0x840, 0x1861, 0x2802, 0x3823,
    0xc9cc, 0xd9ed, 0xe98e, 0xf9af, 0x8948, 0x9969, 0xa90a, 0xb92b,
    0x5af5, 0x4ad4, 0x7ab7, 0x6a96, 0x1a71, 0xa50, 0x3a33, 0x2a12,
    0xdbfd, 0xcbdc, 0xfbbf, 0xeb9e, 0x9b79, 0x8b58, 0xbb3b, 0xab1a,
    0x6ca6, 0x7c87, 0x4ce4, 0x5cc5, 0x2c22, 0x3c03, 0xc60, 0x1c41,
    0xedae, 0xfd8f, 0xcdec, 0xddcd, 0xad2a, 0xbd0b, 0x8d68, 0x9d49,
    0x7e97, 0x6eb6, 0x5ed5, 0x4ef4, 0x3e13, 0x2e32, 0x1e51, 0xe70,
    0xff9f, 0xefbe, 0xdfdd, 0xcffc, 0xbf1b, 0xaf3a, 0x9f59, 0x8f78,
    0x9188, 0x81a9, 0xb1ca, 0xa1eb, 0xd10c, 0xc12d, 0xf14e, 0xe16f,
    0x1080, 0xa1, 0x30c2, 0x20e3, 0x5004, 0x4025, 0x7046, 0x6067,
    0x83b9, 0x9398, 0xa3fb, 0xb3da, 0xc33d, 0xd31c, 0xe37f, 0xf35e,
    0x2b1, 0x1290, 0x22f3, 0x32d2, 0x4235, 0x5214, 0x6277, 0x7256,
    0xb5ea, 0xa5cb, 0x95a8, 0x8589, 0xf56e, 0xe54f, 0xd52c, 0xc50d,
    0x34e2, 0x24c3, 0x14a0, 0x481, 0x7466, 0x6447, 0x5424, 0x4405,
    0xa7db, 0xb7fa, 0x8799, 0x97b8, 0xe75f, 0xf77e, 0xc71d, 0xd73c,
    0x26d3, 0x36f2, 0x691, 0x16b0, 0x6657, 0x7676, 0x4615, 0x5634,
    0xd94c, 0xc96d, 0xf90e, 0xe92f, 0x99c8, 0x89e9, 0xb98a, 0xa9ab,
    0x5844, 0x4865, 0x7806, 0x6827, 0x18c0, 0x8e1, 0x3882, 0x28a3,
    0xcb7d, 0xdb5c, 0xeb3f, 0xfb1e, 0x8bf9, 0x9bd8, 0xabbb, 0xbb9a,
    0x4a75, 0x5a54, 0x6a37, 0x7a16, 0xaf1, 0x1ad0, 0x2ab3, 0x3a92,
    0xfd2e, 0xed0f, 0xdd6c, 0xcd4d, 0xbdaa, 0xad8b, 0x9de8, 0x8dc9,
    0x7c26, 0x6c07, 0x5c64, 0x4c45, 0x3ca2, 0x2c83, 0x1ce0, 0xcc1,
    0xef1f, 0xff3e, 0xcf5d, 0xdf7c, 0xaf9b, 0xbfba, 0x8fd9, 0x9ff8,
    0x6e17, 0x7e36, 0x4e55, 0x5e74, 0x2e93, 0x3eb2, 0xed1, 0x1ef0]

dmp_data = []


def calc_checksum(data):
    crc = 0

    for b in data:
        crc = CRC_TABLE[(crc >> 8) ^ b] ^ (crc << 8)
        crc = crc & 65535  # we only want the low 16 bytes

    low = crc & 255
    high = crc >> 8

    return low * 256 + high  # swap the low and high byte


def date_data_with_crc(latest_date):
    date_int = (latest_date.year - 2000) * 512 + latest_date.month * 32 + latest_date.day
    time_int = latest_date.hour * 100 + latest_date.minute
    date_data = date_int.to_bytes(2, 'little')
    time_data = time_int.to_bytes(2, 'little')

    combined = list(date_data) + list(time_data)
    check_sum = calc_checksum(combined)
    lst = combined + list(check_sum.to_bytes(2, 'little'))
    return bytearray(lst)


def write_and_check_return(port, bytes_to_write, response, error_message, bytes_to_read):
    if bytes_to_write:

        try:
            num = port.write(bytes_to_write)
            assert num == len(bytes_to_write), f"Didn't write {num} chars"

        except AssertionError as e:
            print(e)
            return False

        except Exception as e:
            print(e)
            print(f'Got an exception. bytes_to_write: {bytes_to_write}')
            return False

    try:
        returned_value = port.read(size=bytes_to_read)

        if bytes_to_write:
            assert returned_value == response, error_message

        else:
            assert len(returned_value) == response, error_message

    except AssertionError as e:
        print(f'returned_Value was: {returned_value}')
        print(e)
        return False

    else:
        print(f'returned value after sending {repr(bytes_to_write)} was: {list(returned_value)}')
        return list(returned_value)


def download_weather_data(date_data):
    raw_data = bytes()

    with serial.Serial('/dev/cu.usbserial-0001', 19200, timeout=1) as ser:

        params = [[LF, LFCR, "Didn't get a lfcr after waking console", 2],
                  [DMPAFT, ACK, "Didn't get Ack back after sending DMPAFT", 1],
                  [date_data, ACK, "Didn't get Ack back after sending date_data", 1],
                  [None, 6, "didn't get 6 bytes of page and first record data", 6]]

        for lst in params:
            result = write_and_check_return(ser, *lst)
            if not result: return

        num_pages = (result[1] << 8) + result[0]
        first_record = (result[3] << 8) + result[2]
        print(f'No. of pages: {num_pages}  First Record: {first_record}')

        if num_pages == 0:
            print("There were no new pages of data")
            return

        else:
            ser.write(ACK)
            print(f'\nDownloading Page Number: ', end='')
            for i in range(num_pages):
                print(i, end=' ')

                try:
                    page_read = ser.read(size=267)
                    assert len(page_read) == 267, "Didn't get 267 bytes of data"

                except AssertionError as e:
                    print(e)

                else:
                    valid = validateChecksum(page_read, ser)
                    if valid:
                        raw_data += page_read[1:261]
                        ser.write(ACK)
                    else:
                        print("Got an invalid checksum")
                        return

            print(f"\nDone receiving {num_pages} pages of data")

    now = datetime.now()
    month, day, year = now.month, now.day, now.year
    with open(f'weather_download_{month}_{day}_{year}.txt', 'wb') as f:
        f.write(raw_data)
        print('done writing to file')

    return first_record, raw_data


def validateChecksum(page, serial_port):
    crc = 0
    retries = 0

    for byte in page:
        crc = CRC_TABLE[(crc >> 8) ^ byte] ^ (crc << 8)
        crc = crc & 65535

    if crc == 0:
        dmp_data.append(list(page))
        return True

    else:
        retries += 1
        print("Got a bad checksum, sending NAK")
        if retries < 6:
            serial_port.write(NAK)
        else:
            print("Didn't get a valid checksum after 5 tries.")
            return False


def download():
    conn = sqlite3.connect("/Users/ricdelmar/Complete-Python-3-Bootcamp-master/weather4.sqlite")
    c = conn.cursor()
    c.execute("SELECT max(datetime) from timepointdata")
    conn.commit()
    date_string = c.fetchone()[0]
    print(f'Last date in database is: {date_string}\n')
    conn.close()
    date = datetime.fromisoformat(date_string)
    #date = datetime(2021,10,12,0,0,0)
    data = date_data_with_crc(date)
    return download_weather_data(data)


def parse(data):
    def get_bytes(length):

        if length == 2:
            return data.pop(1) * 256 + data.pop(0)

        else:
            return data.pop(0)

    date_stamp = get_bytes(2)
    year = date_stamp // 512
    month = (date_stamp % 512) // 32
    day = (date_stamp % 512) % 32

    timestamp = get_bytes(2)
    date = datetime(year + 2000, month, day, timestamp // 100, timestamp % 100)
    temp = get_bytes(2) / 10
    hi_temp = get_bytes(2) / 10
    low_temp = get_bytes(2) / 10
    rain = get_bytes(2) / 100
    hi_rain_rate = get_bytes(2) / 100
    pressure = get_bytes(2) / 1000

    data = data[7:]  # remove unwanted indoor data

    humidity = get_bytes(1)
    avg_wind = get_bytes(1)
    hi_wind = get_bytes(1)

    dirs = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    indx = get_bytes(1)
    hi_wind_dir = dirs[indx] if indx < 16 else None

    indx = get_bytes(1)
    prevail_wind_dir = dirs[indx] if indx < 16 else None

    return [avg_wind, date, hi_rain_rate, hi_temp, hi_wind, humidity, low_temp,
            pressure, rain, 0.0, temp, hi_wind_dir, prevail_wind_dir]


def download_Starter():
    index, raw_data = download()
    lst = [raw_data[i:i + 52] for i in range(0, len(raw_data), 52)][index:]
    new_data = [parse(list(row)) for row in lst]
    last_good_data = max(new_data, key=lambda lst: lst[1])
    new_data = new_data[0:new_data.index(last_good_data) + 1]
    return new_data