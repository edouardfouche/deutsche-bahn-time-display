# -*- coding: utf-8 -*-
"""
Created on Tue May 24 15:42:14 2016
Author: Edouard Fouché
"""
from __future__ import print_function
import schiene
import datetime
import time
import os
import sys, getopt

def sanitize(req):
    """Enhance the information content"""
    # get current time
    now = datetime.datetime.now()
    time_now = datetime.datetime.strptime(now.strftime("%H:%M"),"%H:%M")

    for i,s in enumerate(req):        
        if s.get("ontime", False):
            req[i]['status'] = "+0"
        elif "delay" in s:
            req[i]['status'] = "+%s"%s['delay']['delay_departure']
        elif s.get("canceled", False):
            req[i]['status'] = "X"
        else:
            req[i]['status'] = ""

        time_to_wait = round(abs((datetime.datetime.strptime(s['departure'],"%H:%M") - time_now)).seconds/60)
        if time_to_wait < 1000:
            req[i]['time_to_wait'] = str(time_to_wait)
        else:
            req[i]['time_to_wait'] = str(1440-time_to_wait)
    return req

class DeutscheBahnTimeDisplay():
    def __init__(self, refresh=30):
        self.schiene = schiene.Schiene() # initialize crawler
        self.trips = [] # Contains the trips we are interested in
        self.display = [] # Contains the strings to display 
        self.refresh = refresh
        
    def add_trip(self, start, goal, prefix=None, only_direct=False):
        """
        Add a streak to be displayed on the list.
        Each streak should be defined by a start, a goal and optional a prefix
        
        Arguments
        ---------
            start: str
                Start station (as on the DB website)
            goal: str
                Goal station (as on the DB website)
            prefix: str, optional
                The prefix of the streak you want to show (to be printed)
                We recommend a string of 7 characters of the shape "=XXXX=>",
                where X can be either additional "=" or an abbreviation for
                your trip/destination.
                If no prefix is given, it will be set to "=XX===>" where XX are
                the first 2 capitalized letters of the destination of the trip. 
            only_direct: bool, default: False
                If True, return only direct connections. 
        """
        if prefix is None: 
            prefix = "=%s===>"%(goal[0:2].upper())

        self.trips.append({"start":start, "goal":goal, "prefix":prefix, 
                           "only_direct":only_direct})
                
    def run(self):   
        """Run the app and display the result, forever."""  
        j = 0           
        while(True):
            self.get_data()
            
            #print the content of each trip in self.display on the terminal              
            for i in range(25):
                os.system('cls' if os.name == 'nt' else 'clear') 
                if i % 5 == 0: # change displayed trip every 5 units 
                    j = (j+1)%len(self.display)    
                
                print("%s/%s======================"%(j+1,len(self.display))) # just esthetic 
                print(self.display[j])
                    
                print('.'*(i+1))#,end="\r")
                time.sleep(self.refresh/25)

    def get_data(self):
        self.display = [] # Erase information from last iteration 
        for trip in self.trips:
            self.display.append(self.format_information(trip))
            
    def format_information(self, trip):
        """
        Parse and return the current string to be printed corresponding to next 
        travel possibiblities between start and goal.
        """

        # get current time
        now = datetime.datetime.now()

        start = trip['start']
        goal = trip['goal']
        prefix = trip['prefix']

        try:
            conn = self.schiene.connections(start, goal, now,
                                           only_direct=trip['only_direct'])
        except Exception as e:
            raise e
        else: 
            conn = sanitize(conn) # Parse the raw data gained from the crawler
            
            time_to_wait_list = [str(int(float(x['time_to_wait']))) for x in conn]
            product_list = [','.join(x['products']) for x in conn]
            departure_list = [x['departure'] for x in conn]
            time_list = [x['time'] for x in conn]
            status_list = [x['status'] for x in conn]

            max_product_length = max([len(x) for x in product_list])
            output = "%s %s"%(prefix, ",".join(time_to_wait_list))
            for i, el in enumerate(product_list):
                output += "\n"
                prod = product_list[i]
                if len(prod) < max_product_length: # esthetic tuning
                    prod = prod + " "*(max_product_length - len(prod))
                output += "%s | %s | %s %s"%(prod, departure_list[i], 
                                            time_list[i], status_list[i])
        
            return output
        
def main(argv):
    """
    Each trip are characterized by 4 Arguments
    - The first one: Start
    - The second one: Destination
    - The third one: prefix (7 letters zith an arrow is better, e.g; =WORK=>)
    - The fourth one: If we should onlw consider direct connections (True) or not (False)
    """
    #python dbtime.py "Stuttgart HbF" "Karlsruhe HbF" "==KA==>" True "Schwabstraße, Stuttgart" "Leinfelden Frank, Leinfelden-Echterdingen" "=ROTO=>" False
    refresh = 30 # Number of seconds that we should wait before refreshing 
    app = DeutscheBahnTimeDisplay(refresh) 
    
    # In the following lines, declare the trips you are interested in 
    if len(argv) == 0:
        app.add_trip(start='Karlsruhe HbF', goal='Stuttgart HbF', prefix= "=HOME=>", only_direct=True)
    else:
        if len(argv)%4 != 0:
            raise ValueError("Arguments need to be composed of 4 terms, see documentation.")

        for x in range(int(len(argv)/4)):
            app.add_trip(start=argv[4*x], goal=argv[4*x+1], prefix= argv[4*x+2], only_direct=argv[4*x+3] == "True")
    

    #app.add_trip(start='Stuttgart HbF', goal='Karlsruhe HbF', prefix= "=KA===>")
    #app.add_trip(start='Schwabstraße, Stuttgart', goal='Leinfelden Frank, Leinfelden-Echterdingen', prefix="=ROTO=>")
    while(True):
        try:
            app.run()
        except Exception as e:
            for i in range(25):
                os.system('cls' if os.name == 'nt' else 'clear')
                print("Error: %s"%str(e))
                print("Restarting in 1 minute") 
                print('.'*(i+1))#,end="\r")
                time.sleep(60/25)


if __name__ == '__main__': 
    main(sys.argv[1:])
