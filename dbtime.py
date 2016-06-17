# -*- coding: utf-8 -*-
"""
Created on Tue May 24 15:42:14 2016
Author: Edouard Fouché
"""
import schiene
import datetime
import time
import os

def parse(req, time=False):
    """Extract relevant info from the connections"""
    res = []
    for s in req:
        res.append(s['departure'])
        if not s.get("canceled", False):
            if s.get("ontime", False):
                pass
            else:
                if "delay" in s:
                    res[-1] = res[-1] + "+%s"%s['delay']['delay_departure']
        else:
            res[-1] = res[-1] + "X"
        if time:
            res[-1] = res[-1] + " (" + s['time'][2:4] + "'')"
    return res

class DeutscheBahnTimeDisplay():
    def __init__(self, refresh=30):
        self.schiene = schiene.Schiene() # initialize crawler
        self.connections = [] # Contains the trips we are interested in
        self.display = [] # Contains the strings to display 
        self.refresh = refresh
        
    def add_connection(self, connection):
        """
        Add a streak to be displayed on the list.
        Each streak should be entered as a 3-tuple where:
        element 1: The prefix of the streak you want to show (to be printed)
        element 2: Start station (as on the DB website)
        element 3: Goal station (as on the DB website)
        """
        self.connections.append(connection)
                
    def run(self):   
        """Run the app and display the result, forever."""             
        while(True):
            self.display = [] # Erase information from last iteration 
            try:
                for connection in self.connections:
                    self.display.append(self._format_connections(connection[0], connection[1], connection[2]))
            except Exception as e: 
                print("ERROR: %s"%str(e))
            else: 
                self._print()
            
            self._animate()
            
    def _format_connections(self, pref, start, goal):
        """
        Parse and return the current string corresponding to next travel 
        possibiblities between start and goal.
        """
        now = datetime.datetime.now()
        time_now = datetime.datetime.strptime(now.strftime("%H:%M"),"%H:%M")
        
        conn = self.schiene.connections(start, goal, now)
        conn_dep = parse(conn) # Parse the raw data gained from the crawler

        if "ROTO" in pref: ### Add some restrain, just for ROTO (custom)
            conn_dep = [x for x in conn_dep if x[2:5] != ":00"] # This time is not relevant to go to roto
            
        conn_dep = conn_dep[:3]
        conn_time = [round(abs((datetime.datetime.strptime(x[:5],"%H:%M") - time_now)).seconds/60) for x in conn_dep]
        conn_time = [str(x) if x < 1000 else str(1440-x) for x in conn_time]  # Handle time after midnight
        conn_time = [x+y[5:] if len(y)>5 else x.zfill(2) for x,y in zip(conn_time,conn_dep)]
        
        if not conn_time:
            return "%s\tERROR: no data.\n"%(pref)
        elif len(conn_time) == 1:
            return "%s\t%s, the last one.\n"%(pref, conn_time[0])
        else:
            return "%s\t%s, next in %s\n"%(pref, conn_time[0], ",".join(conn_time[1:])) + " %s "%" | ".join(conn_dep)
        
    def _print(self):
        """Print the content of self.display on the terminal"""
        os.system('cls' if os.name == 'nt' else 'clear') # flush the terminal
        print("=========================" + "\n" + "\n\n".join(self.display))
            
    def _animate(self):
        """Just display an array of point as animation"""
        for i in range(25):
            print('.'*(i+1),end="\r")
            time.sleep(self.refresh/25)
        
def main():
    refresh = 30 # Number of seconds that we should wait before refreshing 
    app = DeutscheBahnTimeDisplay(refresh) # In the following lines, declare the trips your interested in 
    app.add_connection(("=HBF==>", 'Schwabstraße, Stuttgart', 'Stuttgart HbF'))
    app.add_connection(("=IBM==>", 'Schwabstraße, Stuttgart', 'Böblingen Zimmerschlag'))
    app.add_connection(("=ROTO=>", 'Schwabstraße, Stuttgart', 'Leinfelden Frank, Leinfelden-Echterdingen'))
    app.run()

if __name__ == '__main__': 
    main()