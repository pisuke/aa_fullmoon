#!/usr/bin/env python3

# Calculating the Moon position for Hooke Park
# More example calculations here: https://rhodesmill.org/skyfield/examples.html

LOCATION_NAME = "Hooke Park, UK"
YEAR = 2020
MONTH = 3
DAY = 7
HOUR = 20
MIN = 0
VERBOSE = False
DEBUG = False

from datetime import datetime
import ephem
from geopy.geocoders import Nominatim
from math import degrees as deg
from skyfield.api import load, Topos
from skyfield.trigonometry import position_angle_of
import argparse
from pyfiglet import Figlet


def human_moon(home):
	# Human-readable names for phases of the moon, taken from:
	# https://stackoverflow.com/questions/26702144/human-readable-names-for-phases-of-the-moon-with-pyephem/26707918
	target_date_utc = home.date
	target_date_local = ephem.localtime(target_date_utc).date()
	next_full = ephem.localtime(ephem.next_full_moon(target_date_utc)).date()
	next_new = ephem.localtime(ephem.next_new_moon(target_date_utc)).date()
	next_last_quarter = ephem.localtime(ephem.next_last_quarter_moon(target_date_utc)).date()
	next_first_quarter = ephem.localtime(ephem.next_first_quarter_moon(target_date_utc)).date()
	previous_full = ephem.localtime(ephem.previous_full_moon(target_date_utc)).date()
	previous_new = ephem.localtime(ephem.previous_new_moon(target_date_utc)).date()
	previous_last_quarter = ephem.localtime(ephem.previous_last_quarter_moon(target_date_utc)).date()
	previous_first_quarter = ephem.localtime(ephem.previous_first_quarter_moon(target_date_utc)).date()
	if target_date_local in (next_full, previous_full):
		return 'Full'
	elif target_date_local in (next_new, previous_new):
		return 'New'
	elif target_date_local in (next_first_quarter, previous_first_quarter):
		return 'First quarter'
	elif target_date_local in (next_last_quarter, previous_last_quarter):
		return 'Last quarter'
	elif previous_new < next_first_quarter < next_full < next_last_quarter < next_new:
		return 'Waxing crescent'
	elif previous_first_quarter < next_full < next_last_quarter < next_new < next_first_quarter:
		return 'Waxing gibbous'
	elif previous_full < next_last_quarter < next_new < next_first_quarter < next_full:
		return 'Waning gibbous'
	elif previous_last_quarter < next_new < next_first_quarter < next_full < next_last_quarter:
		return 'Waning crescent'

def main():
	global LOCATION_NAME, YEAR, MONTH, DAY, HOUR, MIN, VERBOSE, DEBUG
	fig = Figlet(font='standard')
	print(fig.renderText('FullMoon'))

	parser = argparse.ArgumentParser(description="Full moon calculations")
	group = parser.add_mutually_exclusive_group()
	group.add_argument("-v", "--verbose", action="store_true")
	parser.add_argument("--debug", action="store_true")
	parser.add_argument("-l","--location", default=LOCATION_NAME, help="name of location")
	parser.add_argument("-y","--year", default=YEAR, help="year")
	parser.add_argument("-m","--month", default=MONTH, help="month")
	parser.add_argument("-d","--day", default=DAY, help="day")
	parser.add_argument("--hour", default=HOUR, help="hour")
	parser.add_argument("--min", default=MIN, help="minutes")

	args = parser.parse_args()

	VERBOSE = args.verbose
	DEBUG = args.debug

	LOCATION_NAME = args.location
	YEAR = int(args.year)
	MONTH = int(args.month)
	DAY = int(args.day)
	HOUR = int(args.hour)
	MIN = int(args.min)

	if DEBUG:
		print(args)

	time_t = datetime(YEAR, MONTH, DAY, HOUR, MIN)
	print(time_t)

	geolocator = Nominatim(user_agent="moon_sim")
	location = geolocator.geocode(LOCATION_NAME)

	format = "%Y-%m-%d %H:%M"

	if location:
	   print(location.address)
	   print((location.latitude, location.longitude))
	   #print(location.raw)

	   time_t = datetime(YEAR, MONTH, DAY, HOUR, MIN)

	   home = ephem.Observer()
	   home.lat, home.lon = location.latitude, location.longitude

	   home.date = time_t
	   #datetime.datetime.utcnow()

	   #print(dir(ephem))

	   moon = ephem.Moon()
	   moon.compute(home)
	   print()
	   print("Moon: ", moon.alt, moon.az)
	   moon_azimuth  = round(deg(float(moon.az)),1)
	   moon_altitude = round(deg(float(moon.alt)),1)
	   moon_illum = round(moon.phase,1)
	   moonrise = ephem.localtime(home.next_rising(moon)).strftime(format)
	   moonset  = ephem.localtime(home.next_setting(moon)).strftime(format)
	   full_moon = ephem.localtime(ephem.next_full_moon(home.date)).strftime(format)
	   moon_phase = human_moon(home)
	   print("moon azimuth / altitude", moon_azimuth, moon_altitude)
	   print("moon illumination", moon_illum)
	   print("next moon rise / full moon", moonrise, full_moon)
	   print("phase: ", moon_phase)

	   print()

	   sun = ephem.Sun()
	   sun.compute(home)
	   print("Sun: ", sun.alt, sun.az)
	   sun_azimuth  = round(deg(float(sun.az)),1)
	   sun_altitude = round(deg(float(sun.alt)),1)
	   sunrise  = home.previous_rising(sun)
	   sunset   = home.next_setting(sun)
	   print(sunrise, sunset)
	   print("sun  azimuth / altitude", sun_azimuth, sun_altitude)


	   ts = load.timescale()
	   t = ts.utc(YEAR, MONTH, DAY, HOUR, MIN)

	   eph = load('de421.bsp')
	   sun, moon, earth = eph['sun'], eph['moon'], eph['earth']
	   hooke_park = earth + Topos(home.lat, home.lon)

	   hp = hooke_park.at(t)
	   m = hp.observe(moon).apparent()
	   s = hp.observe(sun).apparent()

	   print()
	   print(position_angle_of(m.altaz(), s.altaz()))
	   print("Moon: ", m.altaz())
	   print("Sun:  ", s.altaz())


if __name__ == '__main__':
	main()
