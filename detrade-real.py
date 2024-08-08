
import time
import platform
import asyncio 
import aiohttp 
from aiohttp.client import ClientSession
import requests
import pyautogui
from pynput.keyboard import *
from threading import Thread,local

if platform.system() == 'Windows' :
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

session = requests.Session()


_XRP        = {"name" : "XRP",  "multi" : 10000}    # !
api_url     = "https://fapi.binance.com/fapi/v1/depth?symbol=" + _XRP["name"] + "USDT"


is_first = 1

time_last = 0.0
now_option = 0
last_option = 0
is_place = 0

limit_stop = 0
limit_gap = 3
limit_step = 0
jump_gap = 2

net_state = 200
last_input = 0



def check_algo_1 (input): 
    global last_input, is_place, now_option, limit_stop, limit_gap, limit_step, jump_gap, net_state

    gap = input - last_input 
    if(gap != 0):
        print(input)

    if(last_input == 0):
        last_input = input
        return
    
    if(is_place):
        if(now_option):
            if(input >= limit_stop):
                if(input > (limit_stop + limit_gap)):
                    limit_stop += limit_gap
                    limit_step+=1
                    print("+ place updated -- " + str(limit_step))
            else:
                t1 = Thread(target=stop_round, args=(1,))
                t1.start()
                print("place has beed stoped -- " + str(limit_stop) + "    " + str(input))
                limit_stop = 0 
                is_place = 0
                limit_step = 0
                time.sleep(5)   
        else:
            if(input <= limit_stop):
                if(input < (limit_stop - limit_gap)):
                    limit_stop -= limit_gap
                    limit_step+=1
                    print("+ place updated -- " + str(limit_step))
            else:
                t1 = Thread(target=stop_round, args=(0,))
                t1.start()
                print("place has beed stoped -- " + str(limit_stop) + "    " + str(input))
                limit_stop = 0 
                is_place = 0
                limit_step = 0
                time.sleep(5)

    else:
        if(net_state != 500):
            if (gap >= jump_gap):
                is_place = 1
                limit_stop = input
                now_option = 1
                t1 = Thread(target=start_round, args=(now_option,))
                t1.start()
                print("up start")
            elif (gap <= (jump_gap * -1)):
                is_place = 1
                limit_stop = input
                now_option = 0
                t1 = Thread(target=start_round, args=(now_option,))
                t1.start()
                print("down start")
            
    last_input = input

def check_algo_2 (input): 
    global last_data, now_option, is_first, release, max, min, up_place, down_place


    new_data = int(input * 1000000) 

    if(last_data == 0):
        last_data = new_data
        min = new_data
        return
    
    gap = new_data - last_data
    last_data = new_data
    # print(input)

    if(gap):
        print(new_data)

        # checking history
        if(is_first):
            if(min > new_data):
                min = new_data
            elif(new_data >= (min * 1.005)):
                is_first = 0
                print("it can be start")
            
        # checking 
        else:
            if(down_place):
                if(new_data >= down_place):
                    t1 = Thread(target=stop_round, args=(0,))
                    t1.start()
                    print("Down place has beed stoped -- " + str(down_place) + "    " + str(new_data))
                    release = 2
                    down_place = 0

                    if(up_place):
                        t1 = Thread(target=stop_round, args=(1,))
                        t1.start()
                        print("Up place has beed stoped -- " + str(up_place) + "    " + str(new_data))
                        release = 2
                        up_place = 0

                    if(new_data >= max):
                        max = new_data

                if(up_place): 
                    if(new_data <= up_place):
                        t1 = Thread(target=stop_round, args=(1,))
                        t1.start()
                        print("Up place has beed stoped -- " + str(up_place) + "    " + str(new_data))
                        release = 2
                        up_place = 0

                    elif(new_data > int(up_place * 1.005)):
                        # ---- close all
                        print ("  -------  close all")
                        
                        t1 = Thread(target=stop_round, args=(1,))
                        t1.start()
                        print("Up place has beed stoped -- " + str(up_place) + "    " + str(new_data))
                        up_place = 0
                        
                        t1 = Thread(target=stop_round, args=(0,))
                        t1.start()
                        print("Down place has beed stoped -- " + str(down_place) + "    " + str(new_data))
                        down_place = 0
                        release = 2

                else:
                    if(new_data <= min):
                        # min = new_data
                        if(release):
                            release -= 1
                        elif(gap >= 20):
                            t1 = Thread(target=start_round, args=(1,))
                            t1.start()
                            print("Up place start !!!")
                            # up_place = (new_data - gap ) + 10      
                            up_place = new_data - 10

            # watching
            else:
                if(new_data >= max):
                    max = new_data
                elif(release):
                    release -= 1
                else:
                    if(gap <= -20):
                        t1 = Thread(target=start_round, args=(0,))
                        t1.start()
                        print("Down place start !!!")
                        # down_place = (new_data + gap ) + 10
                        down_place = new_data + 10
                        min = int(down_place * 0.995)



# real place round function
def place_round():
    print("place round")
    pyautogui.click(x=1565, y=625, button="left", clicks=1)


def option_round(option):
    global last_option
    if(last_option != option):
        print("option changed", option)
        if(option):
            pyautogui.click(x=1450, y=250, button="left", clicks=5)     # up button
        else:
            pyautogui.click(x=1330, y=250, button="left", clicks=5)     # down button
        last_option = option


def claim_round():
    for x in range(3):
        # claim button
        pyautogui.click(x=1715, y=950, button="left", clicks=1)
        time.sleep(0.2)


def check_balance():
    error_rate = 0
    auth = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJtaW5BbW91bnQiOiIxLjAwMDAwIiwib3BlbklkIjoiMzQyODc5NzgiLCJhY2NvdW50VHlwZSI6MSwiaXNUZW1wb3JhcnkiOmZhbHNlLCJwbGF0Zm9ybUlkIjoiMSIsInByb2ZpbGVzQWN0aXZlIjoicHJvZCIsInVzZXJJZCI6OTc5NTU5OTE5MDQ2NCwiY291bnRyeUNvZGUiOiJKUCIsImN1cnJlbmN5IjoiVVNEVCIsIm1heEFtb3VudCI6IjMwLjAwMDAwIiwicGxhdGZvcm1OYW1lIjoiYmMiLCJleHAiOjE3MTUyNTExNzYsImlhdCI6MTcxNDY0NjM3Nn0.ubPO-0CcTdx40PUhQBqO3ujC9olWVdVl__IdqCYIt5g'
    
    headers = {
            'Origin': 'https://bc.game', 
            'Referer':'https://bc.game/',
            'Sec-Ch-Ua':'"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
            'Authorization':auth,
            'Content-Type':'application/json',
            }
    session.headers.update(headers)

    url_get_id = "https://api.detrade.com/api/transaction/contractOrder/list?status=0&accountType=1&direction=&symbol=&sort=PNL&timeType=DAY&currency=&page=1&pageSize=100"
    url_close = "https://api.detrade.com/api/transaction/contractOrder/close"
    url_get_result = "https://api.detrade.com/api/transaction/contractOrder/list?status=-1&accountType=1&direction=&symbol=&sort=PNL&timeType=DAY&currency=&page=1&pageSize=100"

    res_check = session.get(url_get_id)
    res_json = res_check.json()
    
    
    if(int(res_json['data']['total'])):
        print (int(res_json['data']['total']))
        claim_round()           #   click cash out button again
        res_id = res_json['data']['items'][0]['id']
        data_claim = '{"id":"' + res_id + '", "token":"' + auth + '"}'
        session.post(url_close, data = data_claim) 

        # error_rate += 60
        print("Error : its not claimed yet. just trying again.")
        check_balance()
        return


    res = session.get(url_get_result)
    result_check = res.json()
    
    roi = result_check['data']['items'][0]['roi']
    if(int(roi) < -30):
        error_rate = 60 * 20
        print("!!! ROI is REALLY LOW !!!")
    elif(int(roi) < -10):
        error_rate = 60 * 5
        print("!!! ROI is LOW !!! " )
    
    print("Check balance is passed. Need to sleep for " + str(error_rate))
    time.sleep(error_rate)
    



def start_round(option):
    option_round(option)
    place_round()

def stop_round(option):
    claim_round()
    # check_balance()


def net_speed_check():
    global time_last
    time_now = time.time()
    time_gap = time_now - time_last

    if(time_last != 0.0 and time_gap > 0.8):
        print("b Net speed is not enough ---  " + str(time_gap))
        time_last = time.time()
        return 500  # Error : server connection is too slow or failed

    elif(time_gap <= 0.08):    
        time.sleep(0.08 - time_gap)
        time_last = time.time()

        return 300  # Error : server connection is too fast
    else:    
        time_last = time_now
        return 200 # Successed


async def download_link(session:ClientSession):
    async with session.get(api_url) as response:
            global net_state
        # try:
            result = await response.json()
            depth_asks = round(float(result['asks'][0][0]) * _XRP["multi"])
            depth_bids = round(float(result['bids'][0][0]) * _XRP["multi"])
            if(depth_asks):
                check_algo_1(depth_asks)
                # check_algo_2(depth_asks)
                net_state = net_speed_check()
        # except:
        #     if(is_place):
        #         stop_round()
        #         is_place = 0



async def download_all(times):
    my_conn = aiohttp.TCPConnector(limit=1)
    async with aiohttp.ClientSession(connector=my_conn) as session:
        tasks = []
        for x in range(times):
            task = asyncio.ensure_future(download_link(session=session))
            tasks.append(task)
        await asyncio.gather(*tasks,return_exceptions=True) # the await must be nest inside of the session


while(True):
    asyncio.run(download_all(5000)) 
    print("finished" )    

while(True): 
    print(pyautogui.position()) 

