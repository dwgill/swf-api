import requests
import re
import os

STEAM_API_KEY = '576C821F7F6F425E341F9955224C9FEE'

# == API REQUESTS ============================================================

def get_game_details(appid):
  api_endpoint = 'https://store.steampowered.com/api/appdetails'
  request = requests.get(api_endpoint, params={
    'key': STEAM_API_KEY,
    'appids': appid,
  })
  result = request.json()
  if request.status_code == 200 and result and result[str(appid)]['success']:
      return result[str(appid)]['data']
  else:
    raise SteamApiException(api_endpoint, request.status_code, appid, result)

def resolve_vanity_id(vanityid):
  api_endpoint = 'https://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/'
  request = requests.get(api_endpoint, params={
    'key': STEAM_API_KEY,
    'vanityurl': vanityid,
  })
  result = request.json()
  if request.status_code == 200 and result and result['response']['success']:
    return str(result['response']['steamid'])
  else:
    raise SteamApiException(api_endpoint, request.status_code, vanityid, result)

def get_user_summary(steamid):
  api_endpoint = 'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002'
  request = requests.get(api_endpoint, params={
    'key': STEAM_API_KEY,
    'steamids': steamid,
  })
  result = request.json()
  if request.status_code == 200 and result and result['response']['players']:
    return result['response']['players'][0]
  else:
    raise SteamApiException(api_endpoint, request.status_code, steamid, result)

def get_appids_owned_by_user(steamid, include_free=False):
  api_endpoint = 'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001'
  request = requests.get(api_endpoint, params={
    'key': STEAM_API_KEY,
    'steamid': str(steamid),
    'include_played_free_games': include_free,
  })
  result = request.json()
  if request.status_code == 200 and result and result.get('response', {}).get('games', []):
    return [int(game_entry['appid']) for game_entry in result['response']['games']]
  else:
    raise SteamApiException(api_endpoint, request.status_code, steamid, include_free, result)

def check_appid_against_store(appid):
  store_app_page_re = re.compile(r'^https?://store.steampowered.com/app/(?P<appid>[0-9]+)(/\S+)?/?$')
  store_app_page_url = 'http://store.steampowered.com/app/' + str(appid)
  
  request = requests.head(store_app_page_url, allow_redirects=False)

  if request.status_code == 200:
    return appid

  if request.status_code == 302:
    match = store_app_page_re.match(request.headers.get('location', ''))
    if match:
      return match.group('appid')

  return None

def derive_store_page(appid):
  store_homepage_re = re.compile(r'^https?://store.steampowered.com/?$')
  store_page_url = 'http://store.steampowered.com/app/' + str(appid)

  request = requests.head(store_page_url, allow_redirects=False)

  # If it's an invalid store page url, we'll get redirected to the store homepage
  if request.status_code in {302, 200}: # 302 = redirect
    redirect_url = request.headers.get('location', '')
    if not store_homepage_re.match(redirect_url):
      return store_page_url

  return None

# == UTILITIES AND METHODS FOR ANALYSING RESPONSE DATA =======================

def game_is_multiplayer(steam_details):
  for category_entry in steam_details.get('categories', []):
    if category_entry['description'].lower() in _MULTIPLAYER_CATEGORIES:
      return True
  
  return False

def parse_profile_url(profile_url):
  '''
  Given a url of the form
      steamcommunity.com/id/<vanity_id> 
  or
      steamcommunity.com/profiles/<steam_id>
  Returns the user identifier (either a steamid or a vanity_id)
  and a bool indicated whether it is a steamid or not.
  '''
  if profile_url.endswith('/'):
    profile_url = profile_url[:-1]
  urlList = profile_url.split('/')
  if len(urlList) < 2:
    raise IndeterminableSteamIdException(profile_url)

  id_or_profile = urlList[-2] # either 'id' or 'profiles'
  steamid_or_vanityid = urlList[-1]
  if id_or_profile == 'id':
    return (steamid_or_vanityid.lower(), False)
  elif id_or_profile == 'profiles':
    return (steamid_or_vanityid, True)
  else:
    raise IndeterminableSteamIdException(profile_url)

def get_vanity_from_user_sum(user_summary):
  userid, is_steamid = parse_profile_url(user_summary['profileurl'])
  if not is_steamid:
    return userid
  else:
    return None

class SteamApiException(Exception):
  pass

class IndeterminableSteamIdException(Exception):
  pass

_MULTIPLAYER_CATEGORIES = {
  'multi-player',
  'multiplayer',
  'shared/split screen',
  r'shared\/split screen',
  'cross-platform multiplayer',
  'local multiplayer',
  'online multiplayer',
  'local multi-player',
  'online multi-player',
  'co-op',
  'local co-op',
  'online co-op',
  '4 player local',
  'split screen',
  'massively multiplayer',
  'mmorpg',
}
