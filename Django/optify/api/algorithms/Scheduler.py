import datetime as dt
import numpy as np
import random
import pytz
import math
import matplotlib.pyplot as pyplot
# from api.models import ActivitySchedule
#Weighted Majority integer programming, linear programming, deterministic optimization,priority-basedsearchheuristics,greedyalgo rithms,randomizedalgorithms,localsearchmethods,meta heuristics, tabu search, evolutionary algorithms, genetic algorithms, simulated annealing, agent-based algorithms, portfoliooptimization,simulation,stochasticoptimization, forecastinganalysis

class Frame:

    def __init__(self,frame_time_start,frame_time_end,frame_date_start,frame_date_end,start_time,end_time,duration,inc_minutes = 5):
        self.frame_time_start = frame_time_start
        self.frame_time_end = frame_time_end
        self.frame_date_start = frame_date_start
        self.frame_date_end =frame_date_end
        self.start_time = start_time
        self.end_time = end_time
        self.duration = duration        
        self.increment = dt.timedelta(minutes=inc_minutes)
        self.current = start_time
    def rand(self):
        date_size = (self.frame_date_end - self.frame_date_start).days
        time_size = (dt.datetime.combine(time=self.frame_time_end,date=dt.date.today())-dt.datetime.combine(time=self.frame_time_start,date=dt.date.today())-self.duration)
        time_size = time_size/self.increment
        off_date =  dt.timedelta(days=random.randrange(date_size+1))if date_size!=0 else dt.timedelta(days=0)
        off_time =  random.randrange(time_size) * self.increment if time_size!=0 else dt.timedelta(hours=0)
        self.current = self.start_time + off_time + off_date
        return self.current             
    def nextoffset(self,count):
        count = int(count)                    
        neg = False
        if count <0:
            neg = True
            count = count * (-1)
        try:
            for c in range(count):
                if neg:
                   self.__prev__()   
                else:
                    self.__next__()  
        except:
            return self.current
        return self.current            
        
    def __iter__(self):
        return self
    def __next__(self): # Python 2: def next(self)                                   
        self.current += self.increment
        end = self.current + self.duration
        if self.end_time < end:
            self.current -= self.increment            
            raise StopIteration
        if self.isInFrame(self.current,end):            
            return self.current       
        date = self.current.date()+dt.timedelta(days=1)               
        self.current = dt.datetime.combine(time=self.frame_time_start,date=date,tzinfo=self.current.tzinfo)
        return self.current
    def __prev__(self):
        self.current -= self.increment
        end = self.current + self.duration
        if self.start_time > self.current:
            self.current += self.increment            
            raise StopIteration
        if self.isInFrame(self.current,end):            
            return self.current       
        date = self.current.date()-dt.timedelta(days=1)               
        self.current = dt.datetime.combine(time=self.frame_time_end,date=date,tzinfo=self.current.tzinfo)
        return self.current   
    def isInFrame(self,start,end):
        """ Return 1 if I am in the frame 0 if I am not. start and end datetimes"""
        if start.date() < self.frame_date_start or end.date() > self.frame_date_end:
            return 0
        if start.time() < self.frame_time_start or end.time() > self.frame_time_end:
            return 0
        return 1        

class SchedulerAI:
    """ Base Abstract class for all Schedule AI Algorithms """
    def __init__(self,start_time,end_time,start_date,end_date,duration,schedule,timezone="UTC"):
        self.timezone = pytz.timezone(timezone)
        self.start_time = dt.datetime.combine(date=start_date,time=start_time,tzinfo=self.timezone)
        self.end_time = dt.datetime.combine(date=end_date,time=end_time,tzinfo=self.timezone)
        self.frame = Frame(start_time,end_time,start_date,end_date,self.start_time,self.end_time,duration)
        self.duration = duration
        self.schedule = schedule
        s = dt.timedelta(days=1)        
        self.activities = schedule.activities.filter(activity__start_times__0__gte=self.start_time-s,activity__end_times__0__lte=self.end_time+s)        
    def Search(self):
        """ Function to search for the best possible timeslot """
        pass
    def Overlap(self,activity,header,footer):
        """ Function that returns the portion of overlap with the activity  """
        if activity.end_times[0] < header or activity.start_times[0] > footer:
            return 0
        portion =1            
        if activity.start_times[0]<header and activity.end_times[0] < footer:
            portion = (activity.end_times[0]-header)/activity.durations[0]
        elif activity.start_times[0] > header and activity.end_times[0] > footer:
            portion = (footer-activity.start_times[0])/activity.durations[0] 
        return portion

    def linearPriorityFunction(self,time):
        """ Returns the sum of all the priorities of all activities within the schedule at a timepoint """
        priority = 0 
        for activity in self.activities:
            if activity.activity.start_times[0] < time and activity.activity.end_times[0] > time:
                priority += activity.priority
        return priority                
    def plotConvolution(self,increment=60):
        time = self.start_time
        end_time = self.end_time
        inc = dt.timedelta(hours=0,minutes=increment)
        priority = list()
        dates = list()
        current_one = list()
        while(time < end_time):
            dates.append(time)
            current_one.append(self.stepFunction(time,delta=self.start_time))
            priority.append(self.linearPriorityFunction(time))
            time += inc
        pyplot.figure(figsize=(20,10))
        pyplot.plot_date(dates, priority)        
        pyplot.savefig('test_1.png')
        # current_one = np.roll(current_one,shift=200)
        pyplot.figure(figsize=(20,10))
        pyplot.plot_date(dates, current_one)        
        pyplot.savefig('test_1_2.png')
        conv = np.convolve(priority,current_one,mode="same")
        pyplot.figure(figsize=(20,10))
        pyplot.plot_date(dates, conv)        
        pyplot.savefig('test_1_3.png')


    def stepFunction(self,t,delta=None):
        """ Returns a step function in some distance of self.duration  """        
        if not delta:
            delta = dt.datetime(year=0,month=0,day=0,hour=0,minute=0,second=0,tzinfo=self.timezone)
        if t<delta:
            return 0
        elif t>delta and t<delta+self.duration:
            return 1
        return 0            

    def plotlinearPriority(self,increment=60):
        """ Outputs the graph of priorities vs time for a given schedule """
        time = self.start_time
        end_time = self.end_time
        inc = dt.timedelta(hours=0,minutes=increment)
        values = list()
        dates = list()
        while(time < end_time):
            dates.append(time)
            values.append(self.linearPriorityFunction(time))
            time += inc          

        pyplot.figure(figsize=(20,10))
        pyplot.plot_date(dates, values)        
        pyplot.savefig('calendar_priority_%d.png'%self.schedule.id)
    def exportWeeklyCalendarasPng(self,week_offset = 0,y=1440,x=200,img=[]):       
        """ Exports the Calendar for a given week as well as any further weeks with certain offset """
        if len(img)==0:                       
            img = self.exportWeeklyCalendar(week_offset=week_offset,y=y,x=x)                                
        fig=pyplot.figure(figsize=(20,10))    
        pyplot.imshow(img,extent=(1, 24, 24, 0),vmin=0,vmax=255)
        fig.tight_layout()
        pyplot.savefig('calendar_schedule_%d.png'%self.schedule.id)
    def exportWeeklyCalendar(self,week_offset=0,y=1440,x=200,additional=[]):
        today = dt.datetime.now(tz=self.timezone).date()
        start = today - dt.timedelta(days=today.weekday(),weeks=-week_offset)
        end = start + dt.timedelta(days=6,weeks=week_offset)        
        week = [np.zeros(shape=(y,x)),np.zeros(shape=(y,x)),np.zeros(shape=(y,x)),np.zeros(shape=(y,x)),np.zeros(shape=(y,x)),np.zeros(shape=(y,x)),np.zeros(shape=(y,x))]
        for activity in self.activities:            
            date_of = activity.activity.start_times[0].date()
            duration = activity.activity.durations[0]
            if date_of>=start and date_of <=end:
                index = date_of.weekday()
                tmp =dt.datetime.combine(date=date_of,time=dt.time(hour=0,minute=0),tzinfo=self.timezone)
                minutes = (activity.activity.start_times[0] - tmp).total_seconds()/60
                offset = int((minutes / (24*60))*y)
                length = int(duration.total_seconds()/(24*60*60)*y)
                week[index][offset:offset+length,10:x-10] += 150 * (activity.priority/100)
        for tup in additional:
            if not additional:
                break
            date_of = tup[0].date()
            duration = tup[1]
            if date_of>=start and date_of <=end:
                index = date_of.weekday()                
                tmp =dt.datetime.combine(date=date_of,time=dt.time(hour=0,minute=0),tzinfo=self.timezone)
                minutes = (tup[0] - tmp).total_seconds()/60 
                offset = int((minutes / (24*60))*y)
                length = int(duration.total_seconds()/(24*60*60)*y)
                week[index][offset:offset+length,10:x-10] += 150
        img = np.hstack(week)
        hour = int(y/24)
        day = x
        for i in range(y):
            if i%hour==0 and i!=0:
                img[i-2:i+2] = 255 
        for i in range(7*x):
            if i%x==0 and i!=0:
                img[:,i-2:i+2] = 255   
        return img
    class Meta:
        abstract = True


    
class BruteForceAI(SchedulerAI):
    """ AI That finds the Minimal value of PerformanceFunction using BruteForce Search by some increments"""
    increment = dt.timedelta(minutes=5) # 5 minutes increment each time
    def Distance(self,activity,priority,header,footer):
        if activity.end_times[0] < header:
            # This activity is finishing before our timeslot                
            return (header-activity.end_times[0]).total_seconds()/60            
        elif activity.start_times[0] > footer:
            #This activity is starting after our activity finished
            return (activity.start_times[0]-footer).total_seconds()/60        
        return 0            
    def Exponential(self,x,a=1000,b=-0.03):
        return a * math.pow(math.e,(b) * x)
    def Sigmoid(self,x):
        return 3*0.8/(1+math.pow(math.e,50-x))+1
    def normal(self,x,myu=16,sig=1.7):
        return (4.3)*(1/(sig*math.sqrt(2*math.pi)))*pow(math.e, (-1/2)*pow( ((x-myu)/(sig)) ,2))    
    def PerformanceFunction(self,header,footer):       
        loss = 0
        for activityschedule in self.activities:
            activity = activityschedule.activity
            loss += self.Exponential(x=self.Distance(activity=activity,priority=activityschedule.priority,header=header,footer=footer))* self.Sigmoid(activity.durations[0].total_seconds()/60)
        
        tmp1 = header.time()
        tmp1 = tmp1.hour + tmp1.minute/60
        loss = loss*self.normal(x=tmp1)    
        return loss    
    def Search(self):
        #super(BruteForceAI,self).plotlinearPriority(increment=3)
        #super(BruteForceAI,self).plotConvolution(increment=3)
        super(BruteForceAI,self).exportWeeklyCalendarasPng()
        # return "SALAM"
        best_measure = float('inf')  
        best_header = None
        for header in self.frame:            
            footer = header + self.duration
            print("Considering HEADER:"+str(header))
            measure = self.PerformanceFunction(header,footer)                           
            if (measure < best_measure ):
                best_measure = measure
                best_header = header
            print("Total Loss "+str(measure))   
            print("-----------------------------------")
        #img = super(BruteForceAI,self).exportWeeklyCalendar(additional=[(best_header,self.duration)])
        #super(BruteForceAI,self).exportWeeklyCalendarasPng(img=img)        
        return {"start_time":best_header,"end_time":best_header+self.duration,"duration":str(self.duration)}


class GradientDecentAI(SchedulerAI):
    def Distance(self,activity,priority,header,footer):
        if activity.end_times[0] < header:
            # This activity is finishing before our timeslot                
            return (header-activity.end_times[0]).total_seconds()/60            
        elif activity.start_times[0] > footer:
            #This activity is starting after our activity finished
            return (activity.start_times[0]-footer).total_seconds()/60        
        return 0            
    def Exponential(self,x,a=1000,b=-0.03):
        return a * math.pow(math.e,(b) * x)
    def Sigmoid(self,x):
        return 3*0.8/(1+math.pow(math.e,50-x))+1
    def PerformanceFunction(self,header,footer):       
        loss = 0
        for activityschedule in self.activities:
            activity = activityschedule.activity
            loss += self.Exponential(x=self.Distance(activity=activity,priority=activityschedule.priority,header=header,footer=footer))* self.Sigmoid(activity.durations[0].total_seconds()/60)
        return loss
    def gradient(self,prev_measure,header,sec=10):
        delta = dt.timedelta(seconds=sec)
        header = header + delta
        footer = header + self.duration
        measure = self.PerformanceFunction(header,footer)
        return measure/sec



    def Search(self):     
        best_measure = float("inf") 
        best_header = None
        rate = self.frame.increment
        learn_rate=0.01
        header = self.frame.rand()
        print(header)
        stop = 1000
        i = 1
        while i<stop:                                 
            footer = header + self.duration
            if not self.frame.isInFrame(header,footer):
                header = self.frame.rand()
                continue
            measure = self.PerformanceFunction(header,footer)
            if (measure < best_measure ):
                best_measure = measure
                best_header = header
            grad = self.gradient(measure,header)
            header = self.frame.nextoffset(grad*learn_rate) 
            i = i + 1                      

        return {"start_time":best_header,"end_time":best_header+self.duration}                              

class AnotherAI(SchedulerAI):
    def Overlap(self,activity,header,footer):
        """ Function that returns the portion of overlap with the activity  """
        if activity.end_times[0] <= header or activity.start_times[0] >= footer:
            return 0
        portion =1            
        if activity.start_times[0]<header and activity.end_times[0] < footer:
            portion = (activity.end_times[0]-header)/activity.durations[0]
        elif activity.start_times[0] > header and activity.end_times[0] > footer:
            portion = (footer-activity.start_times[0])/activity.durations[0] 
        return portion
    def Distance(self,activity,header,footer):
        if activity.end_times[0] < header:
            # This activity is finishing before our timeslot                
            return (header-activity.end_times[0]).total_seconds()/60/60            
        elif activity.start_times[0] > footer:
            #This activity is starting after our activity finished
            return (activity.start_times[0]-footer).total_seconds()/60/60       
        return 0 #Over lap       
    def DagumDistribution(self,x,a=0.5,p=1,b=1):
        return (a*p/x)*(( pow(x/b,a*p) ) / ( pow(pow(x/b,a)+1,p+1)))
    def exponential(self,x,l=-4.3):
        return pow(math.e,l*x)
    def tanh(self,x):
        return (pow(math.e,x)-pow(math.e,-x))/(pow(math.e,x)+pow(math.e,-x))    
    def sigmoid(self,x):
        return 1/(1+pow(math.e,-4.5*x)) 
    def normal(self,x,myu=16,sig=1.7):
        return (4.3)*(1/(sig*math.sqrt(2*math.pi)))*pow(math.e, (-1/2)*pow( ((x-myu)/(sig)) ,2))
    def PerformanceFunction(self,header,footer):
        today = header.date()
        tmp1 = dt.time(hour=5,minute=0,tzinfo=header.tzinfo)
        tmp1 = dt.datetime.combine(today,tmp1)
        today = today + dt.timedelta(days=1)
        tmp2 = dt.time(hour=3,minute=0,tzinfo=header.tzinfo)
        tmp2 = dt.datetime.combine(today,tmp2)
        activites = self.activities.filter(activity__start_times__0__gte=tmp1,activity__end_times__0__lte=tmp2)
        selection_probability = 1
        for activityschedule in activites:
            activity = activityschedule.activity
            dst = self.Distance(activity,header,footer)#Distance in hours 
            dr = activity.durations[0].total_seconds()/60/60 # Durations in hours
            if dst:
                selection_probability = selection_probability*self.tanh(3*dst/dr)
            else:
                overlap = self.Overlap(activity,header,footer)
                selection_probability = selection_probability*self.tanh((3/12)/dr)*self.sigmoid(1-overlap)*self.sigmoid(1-(activityschedule.priority/100))

        tmp1 = header.time()
        tmp1 = tmp1.hour + tmp1.minute/60
        selection_probability = selection_probability*self.normal(x=tmp1)
        return selection_probability
   
    def Search(self):      
        best_measure = 0 
        best_header = None
        for header in self.frame:            
            footer = header + self.duration
            # print("Considering HEADER:"+str(header))
            measure = self.PerformanceFunction(header,footer)                           
            if (measure > best_measure ):
                best_measure = measure
                best_header = header
            # print("Total Loss "+str(measure))   
            # print("-----------------------------------")
        return {"start_time":best_header,"end_time":best_header+self.duration,"duration":str(self.duration)}
class AnotherGradientAI(SchedulerAI):
    def Overlap(self,activity,header,footer):
        """ Function that returns the portion of overlap with the activity  """
        if activity.end_times[0] <= header or activity.start_times[0] >= footer:
            return 0
        portion =1            
        if activity.start_times[0]<header and activity.end_times[0] < footer:
            portion = (activity.end_times[0]-header)/activity.durations[0]
        elif activity.start_times[0] > header and activity.end_times[0] > footer:
            portion = (footer-activity.start_times[0])/activity.durations[0] 
        return portion
    def Distance(self,activity,header,footer):
        if activity.end_times[0] < header:
            # This activity is finishing before our timeslot                
            return (header-activity.end_times[0]).total_seconds()/60/60            
        elif activity.start_times[0] > footer:
            #This activity is starting after our activity finished
            return (activity.start_times[0]-footer).total_seconds()/60/60       
        return 0 #Over lap  
    def DagumDistribution(self,x,a=0.5,p=1,b=1):
        return (a*p/x)*(( pow(x/b,a*p) ) / ( pow(pow(x/b,a)+1,p+1)))
    def exponential(self,x,l=-4.3):
        return pow(math.e,l*x)
    def tanh(self,x):
        return (pow(math.e,x)-pow(math.e,-x))/(pow(math.e,x)+pow(math.e,-x))    
    def sigmoid(self,x):
        return 1/(1+pow(math.e,-4.5*x)) 
    def normal(self,x,myu=16,sig=1.7):
        return (4.3)*(1/(sig*math.sqrt(2*math.pi)))*pow(math.e, (-1/2)*pow( ((x-myu)/(sig)) ,2))
    def PerformanceFunction(self,header,footer):
        today = header.date()
        tmp1 = dt.time(hour=5,minute=0,tzinfo=header.tzinfo)
        tmp1 = dt.datetime.combine(today,tmp1)
        today = today + dt.timedelta(days=1)
        tmp2 = dt.time(hour=3,minute=0,tzinfo=header.tzinfo)
        tmp2 = dt.datetime.combine(today,tmp2)
        activites = self.activities.filter(activity__start_times__0__gte=tmp1,activity__end_times__0__lte=tmp2)
        selection_probability = 1
        for activityschedule in activites:
            activity = activityschedule.activity
            dst = self.Distance(activity,header,footer)#Distance in hours 
            dr = activity.durations[0].total_seconds()/60/60 # Durations in hours
            if dst>1/12:
                selection_probability = selection_probability*self.tanh(3*dst/dr)
            else:
                overlap = self.Overlap(activity,header,footer)
                selection_probability = selection_probability*self.tanh((3/12)/dr)*self.sigmoid(1-overlap)*self.sigmoid(1-(activityschedule.priority/100))

        tmp1 = header.time()
        tmp1 = tmp1.hour + tmp1.minute/60
        selection_probability = selection_probability*self.normal(x=tmp1)
        return selection_probability
    def TestPerformanceFunction(self,header,footer):
        today = header.date()
        tmp1 = dt.time(hour=5,minute=0,tzinfo=header.tzinfo)
        tmp1 = dt.datetime.combine(today,tmp1)
        today = today + dt.timedelta(days=1)
        tmp2 = dt.time(hour=3,minute=0,tzinfo=header.tzinfo)
        tmp2 = dt.datetime.combine(today,tmp2)
        activites = self.activities.filter(activity__start_times__0__gte=tmp1,activity__end_times__0__lte=tmp2)
        selection_probability = 1
        for activityschedule in activites:
            activity = activityschedule.activity
            dst = self.Distance(activity,header,footer)#Distance in hours 
            dr = activity.durations[0].total_seconds()/60/60 # Durations in hours
            if dst:
                selection_probability = selection_probability*self.tanh(3*dst/dr)
            else:
                continue
                overlap = self.Overlap(activity,header,footer)
                selection_probability = selection_probability*self.tanh((3/12)/dr)*self.sigmoid(1-overlap)*self.sigmoid(1-(activityschedule.priority/100))
    def TestGradient(self,header,footer):
        today = header.date()
        tmp1 = dt.time(hour=5,minute=0,tzinfo=header.tzinfo)
        tmp1 = dt.datetime.combine(today,tmp1)
        today = today + dt.timedelta(days=1)
        tmp2 = dt.time(hour=3,minute=0,tzinfo=header.tzinfo)
        tmp2 = dt.datetime.combine(today,tmp2)
        activites = self.activities.filter(activity__start_times__0__gte=tmp1,activity__end_times__0__lte=tmp2)
        selection_probability = 1
        for activityschedule in activites:
            activity = activityschedule.activity
            dst = self.Distance(activity,header,footer)#Distance in hours 
            dr = activity.durations[0].total_seconds()/60/60 # Durations in hours
            if dst:
                selection_probability = selection_probability*self.tanh(3*dst/dr)
            else:
                continue
                overlap = self.Overlap(activity,header,footer)
                selection_probability = selection_probability*self.tanh((3/12)/dr)*self.sigmoid(1-overlap)*self.sigmoid(1-(activityschedule.priority/100))

    def gradient(self,prev_measure,header,sec=10):
        delta = dt.timedelta(seconds=sec)
        header = header + delta
        footer = header + self.duration
        measure = self.PerformanceFunction(header,footer)                                      
        return (measure-prev_measure)/(sec/60/60)



    def Search(self):                 
        best_measure = 0 
        best_header = None
        rate = self.frame.increment
        learn_rate=0.01
        header = self.frame.rand()
        stop = 1000
        grad= 2
        i = 1
        while i<stop and (grad > 1 or grad <-1):                                 
            footer = header + self.duration
            print(header)
            if not self.frame.isInFrame(header,footer):
                header = self.frame.rand()
                continue
            measure = self.PerformanceFunction(header,footer)
            if (measure > best_measure ):
                best_measure = measure
                best_header = header
            grad = self.gradient(measure,header)*500
            header = self.frame.nextoffset(grad) 
            print(grad)
            
            i = i + 1           

        return {"start_time":best_header,"end_time":best_header+self.duration}     
