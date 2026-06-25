import datetime

class date_utils:
    
    def today():
        return datetime.datetime.now().strftime('%Y-%m-%d')