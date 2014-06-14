#!/usr/bin/env python

#*************************************************************
#Author:        Damiano Barboni <barboni@meeo.it>, Alan Beccati <beccati@meeo.it>
#Version:       2.1
#Description:   Functions for date conversion
#Changelog:     Feb 2012 - Alan
#               First version includes conversions from ANSI or Julian <--> Gregorian adapded from online resources @ http://www.astro.ruhr-uni-bochum.de/middelberg/
#                
#               Tue Feb  5 10:38:51 CET 2013 - Damiano
#               Manage different temporal resolution
#
#               Thu Jun 13 12:31:56 CEST 2013
#               Manage Gap Between Product Start Date And Year 0
#
#FIXME:         Julian/ANSI <--> Gregorian dates do not work correctly for years 2100+ and 1800-
#
#*************************************************************


import string
import math
import traceback
import sys


#::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
#::::::::::: List of managed regular temporal resolution ::::::::::::
#::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
regular_temporal_resolution = {"D" : 86400,
                               "H" : 3600,
                               "M" : 60,
                               "S" : 1
                              }

def isRegularTimeAxis(k):
    return regular_temporal_resolution.has_key(k)


#::::::::::::::::::::::::::::::::::
#::::::::::: Exception ::::::::::::
#::::::::::::::::::::::::::::::::::

class DateError(Exception):
    def __init__(self, error):
        self.message=error
    def __str__(self):
        return repr(self.message)




"""
#    ANSI Date origin January 1, 1601, Monday (as Day 1) 
#    Calculated as floor (JD - 2305812.5)    JD=Julian Day
#     The origin of COBOL integer dates
#    defined at: http://en.wikipedia.org/wiki/Julian_day
#    Takes ANSI date as input and outputs gregorian date in same format
#    as julian2gregorian: yyyy:MM:dd hh:mm:ss
"""
def ANSI2gregorian(ansidate):
    return julian2gregorian(ansidate + 2305812.5)


"""
# Adapted from: http://www.astro.ruhr-uni-bochum.de/middelberg/python/jd2gd.py
# task to convert a list of julian dates to gregorian dates
# description at http://mathforum.org/library/drmath/view/51907.html
# Original algorithm in Jean Meeus, "Astronomical Formulae for Calculators"
#    Takes Julian date as input and outputs gregorian date in format:
#    yyyy:MM:dd hh:mm:ss
"""
def julian2gregorian(julian, dof=None) :
    """
    if len(sys.argv)==1:
        print "\n Task to convert a list of julian dates to gregorian dates."
        print " Written by Enno Middelberg 2002"
        print "\n Usage: jd2gd.py [-f] date1 date2 date3 ...\n"
        sys.exit()
    """

    x=julian
    try:
        jd=float(x)
    except ValueError:
        return None
    jd=jd+0.5
    Z=int(jd)
    F=jd-Z
    alpha=int((Z-1867216.25)/36524.25)
    A=Z + 1 + alpha - int(alpha/4)

    B = A + 1524
    C = int( (B-122.1)/365.25)
    D = int( 365.25*C )
    E = int( (B-D)/30.6001 )

    dd = B - D - int(30.6001*E) + F

    if E<13.5:
        mm=E-1

    if E>13.5:
        mm=E-13

    if mm>2.5:
        yyyy=C-4716

    if mm<2.5:
        yyyy=C-4715

    #months=["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    daylist=[31,28,31,30,31,30,31,31,30,31,30,31]
    daylist2=[31,29,31,30,31,30,31,31,30,31,30,31]

    h=int((dd-int(dd))*24)
    min=int((((dd-int(dd))*24)-h)*60)
    sec=86400*(dd-int(dd))-h*3600-min*60

    # Now calculate the fractional year. Do we have a leap year?
    if (yyyy%4 != 0):
        days=daylist2
    elif (yyyy%400 == 0):
        days=daylist2
    elif (yyyy%100 == 0):
        days=daylist
    else:
        days=daylist2

    if dof is not None:
        daysum=0
        for y in range(mm-1):
            daysum=daysum+days[y]
        daysum=daysum+dd-1

        if days[1]==29:
            fracyear=yyyy+daysum/366
        else:
            fracyear=yyyy+daysum/365
        print str(x)+" = "+`fracyear`
    else:
        return string.zfill(yyyy,4) + "-"+ string.zfill(mm,2)+"-"+ string.zfill(int(dd),2) + " " \
        +string.zfill(h,2)+":"+string.zfill(min,2)+":"+string.zfill(int(sec),2)


"""
#    ANSI Date origin January 1, 1601, Monday (as Day 1) 
#    Calculated as floor (JD - 2305812.5)    JD=Julian Day
#     The origin of COBOL integer dates
#    defined at: http://en.wikipedia.org/wiki/Julian_day
"""
def toANSI(date,time=None):
    return int((toJulian(date, time) - 2305812.5))


"""
#adapted from: www.astro.ruhr-uni-bochum.de/middelberg/python/gd2jd.py
# converts a gregorian date to julian date
# expects one or two arguments, first is date in yyyy:mm:dd,
# second optional is time in hh:mm:ss. If time is omitted,
# 00:00:00 is assumed
"""
def toJulian(date,time=None):
    date = date.replace("-",":")
    date=string.split(date, ":")
    dd=int(date[2])
    mm=int(date[1])
    yyyy=int(date[0])
        
    if time == None :
        time="0:0:0"

    time=string.split(time, ":")
    hh=float(time[0])
    mins=float(time[1])
    sec=float(time[2])

    UT=hh+mins/60+sec/3600
    #print "UT="+`UT`
    
    #total_seconds=hh*3600+mins*60+sec
    #fracday=total_seconds/86400

    #print "Fractional day: %f" % fracday
    #print dd,mm,yyyy, hh,mins,sec, UT

    if (100*yyyy+mm-190002.5)>0:
        sig=1
    else:
        sig=-1

    JD = 367*yyyy - int(7*(yyyy+int((mm+9)/12))/4) + int(275*mm/9) + dd + 1721013.5 + UT/24 - 0.5*sig +0.5
    
    #months=["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    #print "\n"+months[mm-1]+" %i, %i, %i:%i:%i UT = JD %f" % (dd, yyyy, hh, mins, sec, JD),

    # Now calculate the fractional year. Do we have a leap year?
    daylist=[31,28,31,30,31,30,31,31,30,31,30,31]
    daylist2=[31,29,31,30,31,30,31,31,30,31,30,31]
    if (yyyy%4 != 0):
        days=daylist2
    elif (yyyy%400 == 0):
        days=daylist2
    elif (yyyy%100 == 0):
        days=daylist
    else:
        days=daylist2
    
    daysum=0
    for y in range(mm-1):
        daysum=daysum+days[y]
    daysum=daysum+dd-1+UT/24

    if days[1]==29:
        fracyear=yyyy+daysum/366
    else:
        fracyear=yyyy+daysum/365
    #print " = " + `fracyear`+"\n"
    return JD


def getTimeIndexFromDatasetName(name):
    
    """
        Extracts the ansi date from a dataset name
        DATE.TIME.TEMPORALRESOLUTION where
        - DATE is the date of image acquisition, in YYYYMMDD format;
        - TIME is the time of image acquisition, in HHMMSS format (Optional Parameter). If omitted, data is intended as a daily composite.
        - TEMPORALRESOLUTION define temporal resolution (Optional Parameter). If omitted, data is intended as a daily composite.
    """
    
    #parse date
    try:
        date = name.split("_")[2].split(".")[0]
        if len(date) >= 8 :
            date=date[-8:]
        formattedDate = date[0:4] + "-" + date[4:6] + "-" + date[6:8]
    
    except (ValueError, IndexError) as e:
        error_mess = "Unexpected filename: "+name+", date not recognized: " + e.message
        raise DateError(error_mess)
    
    #parse time and temporal resolution - NB not mandatory parameters
    try:
        imagetime     = name.split("_")[2].split(".")[1]
        if len(imagetime) != 6:
            raise
        formattedTime = imagetime[0:2] + ":" + imagetime[2:4] + ":" + imagetime[4:6]
        
    except:
        formattedTime = "00:00:00"
    
    #obtain rasdaman temporal index basing on the ansi_date_seconds and the temporal resolution
    try:        
        temporal_resolution = name.split("_")[2].split(".")[2]
    except:
        #set default daily temporal resolution
        temporal_resolution = "1D"
        
    try:
        temporal_index = getTimeIndexFromDate(formattedDate, formattedTime, temporal_resolution)
        return temporal_index
    except:
        error_mess = "Unexpected filename: "+name+", daaaate not recognized"
        raise DateError(error_mess)
        


def getTimeIndexFromDate(date, time="00:00:00", temporal_resolution="1D", gap=0):
    secondsFromMidnight = int(time.split(":")[0],10) * 3600 + int(time.split(":")[1],10) * 60 + int(time.split(":")[2],10)
    try:
        ansi_date         = toANSI(date) - gap
        ansi_date_seconds = (ansi_date * 86400) + secondsFromMidnight
        frequency_number  = int(temporal_resolution[:-1])
        frequency_letter  = temporal_resolution[-1].upper()
        
        frequency         = regular_temporal_resolution[frequency_letter] * frequency_number
        temporal_index    = int(ansi_date_seconds / frequency)
    except:
        #check if temporal resolution is a managed irregular value
        if temporal_resolution == "10MERMGVI":
            year         = int(date.split("-")[0], 10)
            month        = int(date.split("-")[1], 10)
            day          = int(date.split("-")[2], 10)
            if day <= 10:
                month_period = 0
            elif day > 10 and day <= 20:
                month_period = 1
            else:
                month_period = 2                
            temporal_index = (year * 36) + (((month -1)*3) + month_period) 
        
        else:
            error_mess = "Unexpected temporal resolution: " + temporal_resolution
            raise DateError(error_mess)
            
    return temporal_index




def getDateFromTimeIndex(index, temporal_resolution="1D", gap=0):
    try:
        frequency_number    = int(temporal_resolution[:-1])
        frequency_letter    = temporal_resolution[-1].upper()
        frequency           = regular_temporal_resolution[frequency_letter] * frequency_number
        ansi_date_seconds   = index * frequency
        secondsFromMidnight = ansi_date_seconds % 86400 
        ansi_date           = ((ansi_date_seconds - secondsFromMidnight) / 86400 ) + gap
        date                = ANSI2gregorian(ansi_date).split(" ")[0]
        time                = ("0" + str(secondsFromMidnight / 3600))[-2:] + ":" + ("0" + str((secondsFromMidnight % 3600)/60))[-2:] + ":" + ("0" + str((secondsFromMidnight % 3600) % 60))[-2:]
                
    except:
        #check if temporal resolution is a managed irregular value
        if temporal_resolution == "10MERMGVI":
            year         = index / (36)
            month        = ((index % (12 * 3)) / 3) + 1
            month_period = index % 3
            
            if month_period == 0:
                day = "01"
            elif month_period == 1:
                day = "11"
            else:
                day = "21"
            
            date = str(year) + "-" + ("0" + str(month))[-2:] + "-" + day
            time = "00:00:00"
                    
        else:
            error_mess = "Unexpected temporal resolution: " + temporal_resolution
            raise DateError(error_mess)
            
    return date + " " + time


def getGapBetweenProductStartDateAndOrigin(start_date, temporal_resolution="1D"):
    # convert index to date starting from start date and not from year 0
    # mandatory for products with temporal resolution > 1D    
    index_for_start_date_daily_resolution = getTimeIndexFromDate(start_date,           time="00:00:00", temporal_resolution="1D")
    index_for_start_date                  = getTimeIndexFromDate(start_date,           time="00:00:00", temporal_resolution=temporal_resolution)
    date_starting_from_0                  = getDateFromTimeIndex(index_for_start_date,                  temporal_resolution=temporal_resolution).split(" ")[0]
    index_for_start_date_starting_from_0  = getTimeIndexFromDate(date_starting_from_0, time="00:00:00", temporal_resolution="1D")
    gap = index_for_start_date_daily_resolution - index_for_start_date_starting_from_0
    return gap



def getDateFromFilename(name):
        #parse date
    try:
        date = name.split("_")[2].split(".")[0]
        if len(date) >= 8 :
            date=date[-8:]
        formattedDate = date[0:4] + "-" + date[4:6] + "-" + date[6:8]
    
    except (ValueError, IndexError) as e:
        error_mess = "Unexpected filename: "+name+", date not recognized: " + e.message
        raise DateError(error_mess)
    
    #parse time and temporal resolution - NB not mandatory parameters
    try:
        imagetime     = name.split("_")[2].split(".")[1]
        if len(imagetime) != 6:
            raise
        formattedTime = imagetime[0:2] + ":" + imagetime[2:4] + ":" + imagetime[4:6]
        
    except:
        formattedTime = "00:00:00"
    
    return formattedDate + " " +formattedTime
    
    


    
    

if __name__ == "__main__":
    if len( sys.argv[ 1 ].split( "-" ) ) > 2:
        print getTimeIndexFromDate( sys.argv[ 1 ], time="00:00:00", temporal_resolution="1D")
    else:
        print getDateFromTimeIndex( int( sys.argv[ 1 ], 10 ) )


