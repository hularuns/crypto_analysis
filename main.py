import requests
from enum import Enum
from pprint import pprint
from datetime import datetime
import pytz


class CryptoNames(str, Enum):
    litecoin = "LTC"
    bitcoin = "BTC"
    ethereum = "ETH"
    solana = "SOL"

class CryptoAnalysis:
    def __init__(self ) -> None:
        pass
    
    def get_daily_prices(self, crypto:CryptoNames = CryptoNames.litecoin.value, days: int = 60):
        """ Gets daily prices of open and close at midnight in usd"""
        url = f"https://data-api.cryptocompare.com/index/cc/v1/historical/days?market=cadli&instrument={crypto}-USD&limit={days}&aggregate=1&fill=true&apply_mapping=true&response_format=JSON"
        request = requests.get(url).json()
        request_data = request.get('Data', None)
        return request_data
           
    def assign_weekdays(self, raw_data: dict) -> None:
        """ Assigns weekdays as day names and also week number as if from start of data, calendar week and formatted date. """
        weekdays = {0: "monday", 1: "tuesday", 2: "wednesday", 3: "thursday", 4: "friday", 5: "saturday", 6: "sunday"}      
        week_number = 1
        for day in raw_data:
            timestamp = day.get("TIMESTAMP", None)
            datetime_obj = datetime.fromtimestamp(timestamp=timestamp, tz = pytz.utc)   
            weekday = datetime_obj.weekday()
            
            if timestamp is not None:
                day.update({
                    "weekday": weekdays.get(weekday, None),
                    "week": week_number,
                    "calendar_week": datetime_obj.isocalendar()[1],
                    "date": datetime_obj.strftime('%Y-%m-%d')
                })
                week_number += 1 if weekday >= 6 else 0
        return raw_data
        
    def identify_buy_sell_days(self, raw_data: dict, purchase_day: str = "monday", sell_day: str = "friday"):
        """ Get rid of this and handle is entirely within simulation method... this is inefficient but works. """
        weekly_data = {} 
        pprint(raw_data)
        for day in raw_data:
            if day['weekday'] == purchase_day:

                weekly_data.setdefault(day['week'], {}).update({
                    "purchase": {
                    "low_price": day['LOW'],
                    "high_price": day['HIGH'],
                    "date": day['date'],
                    "weekday": day['weekday']
                }
            })
            elif day['weekday'] == sell_day:
                weekly_data.setdefault(day['week'], {}).update({
                        "sell": {
                        "low_price": day['LOW'],
                        "high_price": day['HIGH'],
                        "date" : day['date'],
                        "weekday": day['weekday']
                        }
                })

        return weekly_data
    
    def get_simulation_data(self, purchase_day: str ="monday", sell_day: str = "friday", crypto: CryptoNames.litecoin.value = "litecoin", days: int = 60):
        raw_data = self.get_daily_prices(crypto=crypto, days=days)
        week_day_data = self.assign_weekdays(raw_data=raw_data)
        filtered_data = self.identify_buy_sell_days(raw_data=week_day_data, purchase_day=purchase_day, sell_day=sell_day)
        return filtered_data
            
    def simulate_weekly_process(self, starting_usd=100, purchase_day:str = "monday", sell_day: str = "friday", crypto: CryptoNames.litecoin.value = "litecoin", days: int = 60, tx_tax: float = 0.004):
        """ purchase from usd into crypto funds """
        weekly_data = self.get_simulation_data(purchase_day=purchase_day.lower(), sell_day=sell_day.lower(), crypto=crypto, days=days)
 
        usd_funds = starting_usd
        previous_money = usd_funds
        weekly_price_diff = {}
        profit_week = 0
        loss_week = 0

        for week, data in weekly_data.items():
            
            if "purchase" in data and "sell" in data:
                purchase_price = data.get('purchase', {}).get('low_price', None)
                held_crypto = (usd_funds / purchase_price) * (1-tx_tax) #taxed purchase
                usd_funds = 0 # set to 0 as spent.

                #now sell crypto funds to usd on the sell day.
                sell_price = data.get('sell', {}).get('low_price', None)
                usd_funds = (held_crypto * sell_price ) * (1-tx_tax) # crypto coin in usd value now in usd funds for the weekend before monday buy.
                
                profit = usd_funds - previous_money
                
                if usd_funds > previous_money:
                    profit_or_loss = "profit"
                    profit_week += 1
                else:
                    profit_or_loss = "loss"
                    loss_week += 1

                weekly_price_diff.setdefault(week, {}).update({
                    "purchase_price (high)": purchase_price,
                    "sell_price (low)": sell_price,
                    "tax": f"{tx_tax*100}%",
                    "profit": profit,
                    "profit_or_loss": profit_or_loss,
                    "simulated_value_after_tax": usd_funds
                })
                previous_money = usd_funds
        print(f"Total number of profit weeks: {profit_week}, total number of loss weeks: {loss_week}")
        print(f"Starting with ${starting_usd}, after {days} days across {profit_week+loss_week} weeks with trading tax of: {tx_tax*100}%, held funds are now worth ${usd_funds:.2f} .")
        print(weekly_price_diff)
        return weekly_price_diff
    
if __name__ == "__main__":
    crypto_analysis = CryptoAnalysis()
    data = crypto_analysis.get_daily_prices()
    # crypto_analysis.price_difference_between_two_days()
    simulation = crypto_analysis.simulate_weekly_process(starting_usd = 100, purchase_day = "Monday", sell_day = "thursday",crypto=CryptoNames.litecoin.value, days = 10, tx_tax=0.004)
    pprint(simulation)
    # random_date = datetime.fromtimestamp(timestamp=1726704000, tz=pytz.utc).weekday()
    # print(random_date)
    

    # multipliers = [1.100616440404421, 0.8829632654336568, 1.168093659256931, 1.0619743890560547, 1.0112180576481031, 0.9825874677283922, 1.2173255800228566, 1.125256533279544, 1.0118842392659833, 1.0361003828429949, 1.0655112272008915, 1.0880866438854244, 1.0687939961260609]
    # funds = 100
    # for m in multipliers:
    #     funds = funds * m
    #     print(funds)