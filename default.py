# Random episode selecter
# Massive thanks to the developers of the script.randommovie addon, which this is entirely based off of. 
# From the developer of script.randommovie goes massive thanks to the developers of the script.randommitems addon, 
# without whom this would not have been possible. 
#
# Author - stafio
# Website - https://github.com/elParaguayo/
# Version - 0.1
# Compatibility - pre-Eden
#

import xbmc
import xbmcgui
from urllib import quote_plus, unquote_plus
import re
import sys
import os
import random
import simplejson as json

# let's parse arguments before we start
try:
  # parse sys.argv for params
  params = dict( arg.split( "=" ) for arg in sys.argv[ 1 ].split( "&" ) )
except:
  # no params passed
  params = {}
# set our preferences
filterSeries = params.get( "filterseries", "" ) == "True"
promptUser = params.get( "prompt" , "" ) == "True"


def getAllEpisodes():
  # get the raw JSON output
  try:
    episodesstring = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetEpisodes", "params": { "fields": ["showtitle", "file", "playcount"], "sort": { "method": "random" } }, "id": 1}')    
    episodesstring = unicode(episodesstring, 'utf-8', errors='ignore')
    episodes = json.loads(episodesstring)
    # older "pre-Eden" versions accepted "fields" parameter but this was changed to "properties" in later versions.
    # the next line will throw an error if we're running newer version
    testError = episodes["result"]
  except:
    episodesstring = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetEpisodes", "params": { "properties": ["showtitle", "file", "playcount"], "sort": { "method": "random" } }, "id": 1}')
    episodesstring = unicode(episodesstring, 'utf-8', errors='ignore')
    episodes = json.loads(episodesstring)
  # and return it
  return episodes

def getRandomEpisode(filterWatched, filterseries, series):
  # set up empty list for movies that meet our criteria
  episodeList = []
  # loop through all movies
  for episode in episodesJSON["result"]["episodes"]:
    # reset the criteria flag
    meetsCriteria = False
    # check if the episode meets the criteria
    # Test #1: Does the series match our selection (also check whether the playcount criteria are satisfied)
    if ( filterseries and series == episode["showtitle"] ) and (( filterWatched and episode["playcount"] == 0 ) or not filterWatched):
      meetsCriteria = True
    # Test #2: Is the playcount 0 for unwatched episodes (when not filtering by series)
    if ( filterWatched and episode["playcount"] == 0 and not filterseries ):
      meetsCriteria = True
    # Test #3: If we're not filtering series or unwatched movies, then it's added to the list!!
    if ( not filterWatched and not filterseries ):
      meetsCriteria = True

    # if it meets the criteria, let's add the file path to our list
    if meetsCriteria:
      episodeList.append(str(item.get('episodeid')))
  # Make a random selection      
  randomEpisode = random.choice(episodeList)
  # return the filepath
  return randomEpisode
  
def selectSeries(filterWatched):
  success = False
  selectedSeries = ""
  mySeries = []
  
  for episode in episodesJSON["result"]["episodes"]:
    # Let's get the episode series names
    # If we're only looking at unwatched episodes then restrict list to those movies
    if ( filterWatched and episode["playcount"] == 0 ) or not filterWatched:
      series = episode["showtitle"]
      # check if the series is a duplicate
      if not series in mySeries:
        # if not, add it to our list
        mySeries.append(series)
  # sort the list alphabetically
  mySortedSeries = sorted(mySeries)
  # prompt user to select series
  selectSeries = xbmcgui.Dialog().select("Select series:", mySortedSeries)
  # check whether user cancelled selection
  if not selectSeries == -1:
    # get the user's chosen series
    selectedSeries = mySortedSeries[selectSeries]
    success = True
  else:
    success = False
  # return the series and whether the choice was successfull
  return success, selectedSeries
  
def getUnwatched():
  # default is to select from all episodes
  unwatched = False
  # ask user whether they want to restrict selection to unwatched episodes
  a = xbmcgui.Dialog().yesno("Watched shows", "Restrict selection to unwatched shows only?")
  # deal with the output
  if a == 1: 
    # set restriction
    unwatched = True
  return unwatched
  
def askSeries():
  # default is to select from all series
  selectSeries = False
  # ask user whether they want to select a series
  a = xbmcgui.Dialog().yesno("Select series", "Do you want to select a series to watch?")
  # deal with the output
  if a == 1: 
    # set filter
    selectSeries = True
  return selectSeries  

# get the full list of movies from the user's library
episodesJSON = getAllEpisodes()
  
# ask user if they want to only play unwatched movies  
unwatched = getUnwatched()  

# is skin configured to use one entry?
if promptUser and not filterSeries:
  # if so, we need to ask whether they want to select series
  filterSeries = askSeries()

# did user ask to select genre?
if filterSeries:
  # bring up genre dialog
  success, selectedSeries = selectSeries(unwatched)
  # if not aborted
  if success:
    # get the random episdoe...
    randomEpisode = getRandomEpisode(unwatched, True, selectedSeries)
    # ...and play it!
    xbmc.executeJSONRPC('{ "jsonrpc": "2.0", "method": "Player.Open", "params": { "item": { "episodeid": %d }, "options":{ "resume": false } }, "id": 1 }' % int(randomEpisode))
else:
  # no genre filter
  # get the random episode...
  randomEpisode = getRandomEpisode(unwatched, False, "")
  # ...and play it
  xbmc.executeJSONRPC('{ "jsonrpc": "2.0", "method": "Player.Open", "params": { "item": { "episodeid": %d }, "options":{ "resume": false } }, "id": 1 }' % int(randomEpisode))
