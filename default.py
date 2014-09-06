'''
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program. If not, see <http://www.gnu.org/licenses/>.
'''

'''
    Random Episode script
    by stafio

    Plays a random TV Show episode from user's video library.
    
    Based off of Random Movie script by elParaguayo

    Version: 0.2.0
'''

import sys
import random

if sys.version_info >=  (2, 7):
    import json as json
else:
    import simplejson as json

import xbmc
import xbmcgui
import xbmcaddon

_A_ = xbmcaddon.Addon()
_S_ = _A_.getSetting

# let's parse arguments before we start
try:
    # parse sys.argv for params
    params = dict( arg.split( "=" ) for arg in sys.argv[ 1 ].split( "&" ) )
except:
    # no params passed
    params = {}
# set our preferences
filterSeries = params.get("filterseries", "").lower() == "true"

# The filter by series prompt can be set via the skin...
skinprompt = params.get("promptSeries", "").lower() == "true"

# ... or via the script settings
scriptprompt = _S_("promptSeries") == "true"

# If the skin setting is set to true this overrides the script setting
promptUser = skinprompt or scriptprompt

def localise(id):
    '''Gets localised string.

    Shamelessly copied from service.xbmc.versioncheck
    '''
    string = _A_.getLocalizedString(id).encode( 'utf-8', 'ignore' )
    return string

def getEpisodeLibrary():
    '''Gets the user's full video library.

    Returns dictionary object containing episodes.'''

    # Build our JSON query
    jsondict = {"jsonrpc": "2.0",
                "method": "VideoLibrary.GetEpisodes",
                "params": {"properties": ["showtitle", "playcount", "file"]},
                "id": 1}

    # Submit our JSON request and get the response
    episodestring = unicode(xbmc.executeJSONRPC(json.dumps(jsondict)), 
                          errors='ignore')
    
    # Convert the response string into a python dictionary
    episodes = json.loads(episodestring)


    # Return the "episodes" part of the response, or None if no episodes are found
    return episodes["result"].get("episodes", None)

def getRandomEpisode(filterWatched, filterBySeries, series=None):
    '''Takes the user's video library, filters it by the criteria
       requested by the user and then selects a random episode from the filtered 
       list.

       Returns the filepath of the random episode.
    '''

    # set up empty list for episodes that meet our criteria
    episodeList = []

    # loop through all episodes
    # episodesJSON is global variable, it's not being modified
    for episode in episodesJSON:

        # reset the criteria flag
        meetsCriteria = False

        # Does the show title match the selected series?
        seriesmatch = series == episode["showtitle"]
        
        # Is the episode currently unwatched?
        isUnwatched = episode["playcount"] == 0 

        # Test the episode against the criteria

        # If we are filtering both by series and watched status...
        if filterBySeries and filterWatched:

            # ...we need both of these to be True
            meetsCriteria = seriesmatch and isUnwatched

        # If we're just filtering by series...
        elif filterBySeries:

            # ... only this needs to be True
            meetsCriteria = seriesmatch

        # If we're fitering by watched status...
        elif filterWatched:

            # ... only this one needs to be True
            meetsCriteria = isUnwatched

        # And if we're not filtering by either...
        else:

            # ... we can add it to our list!
            meetsCriteria = True

        # If the film passes the tests... 
        if meetsCriteria:

            # ... let's add the filepath to our list.
            episodeList.append(episode["file"])
    
    # return a random episode filepath
    try:
        return random.choice(episodeList)

    # Will be empty if no results
    except IndexError:

        return None
    
def selectSeries(filterWatched):
    '''Displays a dialog of the show titles of all TV Show episodes in 
       the user's library and asks the user to select one.

       Parameters:

       filterWatched: restrict results to specific series of unwatched episodes.

       Returns:
       selectedSeries: string containing selected series name or None if no choice made.
    '''
    # Empty list for holding series
    mySeries = []
    selectedSeries = None
    
    # Loop through our episodes library
    for episode in episodesJSON:

        # Let's get the episode show titles
        # If we're only looking at unwatched episodes then restrict list to 
        # those episodes
        if (filterWatched and episode["playcount"] == 0) or not filterWatched:
            
            series = episode["showtitle"]

            # Check if the series is a duplicate
            if not series in mySeries:

                # If not, add it to our list
                mySeries.append(series)
    
    # Sort the list alphabetically, ignoring leading 'The '                
    mySortedSeries = sorted(mySeries, key=lambda s: s.lower().replace('the ', '', 1))

    # Prompt user to select series
    selectSeries = xbmcgui.Dialog().select(localise(32024), mySortedSeries)
    
    # Check whether user cancelled selection
    if not selectSeries == -1:
        # get the user's chosen series
        selectedSeries = mySortedSeries[selectSeries]
        
    # Return the series (or None if no choice)
    return selectedSeries
    
    
def getUserPreference(title, message):
    '''Asks the user whether they want to restrict results.

       Returns:
       True:    Script should restrict films
       False:   Script can pick any film
    '''

    # Ask user whether they want to restrict selection
    a = xbmcgui.Dialog().yesno(title, 
                               message)
    
    # Deal with the output
    if a == 1: 
        
        # User wants restriction
        return True

    else:

        # No restriction needed
        return False
    
# get the full list of episodes from the user's library
episodesJSON = getEpisodeLibrary()
    
# ask user if they want to only play unwatched episodes    
unwatched = getUserPreference(localise(32021), localise(32022))  

# is skin configured to use one entry?
if promptUser and not filterSeries:

    # if so, we need to ask whether they want to select series
    filterSeries = getUserPreference(localise(32023), localise(32024))  

# did user ask to select series?
if filterSeries:

    # bring up series dialog
    selectedSeries = selectSeries(unwatched)

    # if not aborted
    if selectedSeries:

        # get the random episode...
        randomEpisode = getRandomEpisode(unwatched, True, selectedSeries)

    else:

        # User cancelled so there's no episode to play
        randomEpisode = None

else:
    # no series filter
    # get the random episode...
    randomEpisode = getRandomEpisode(unwatched, False)

if randomEpisode:

   # Play the episode 
    xbmc.executebuiltin('PlayMedia(' + randomEpisode + ',0,noresume)')

else:

    # No results found, best let the user know
    xbmc.executebuiltin('Notification(%s,%s,2000)' % (localise(32025),
                                                      localise(32026)))
