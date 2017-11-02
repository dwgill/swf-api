import requests

def get_app_details(appid):
  request = requests.get('https://steamspy.com/api.php', params={
    'request': 'appdetails',
    'appid': appid,
  })
  result = request.json()
  if request.status_code == 200 and result:
    return result
  else:
    raise Exception

def game_is_multiplayer(steamspy_details):
  tags = steamspy_details.get('tags', {})
  if isinstance(tags, dict):
    tags = tags.keys()
  for tag in tags:
    if tag.lower() in _multiplayer_tags:
      return True

  return False

_multiplayer_tags = {
  'multi-player',
  'multiplayer',
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
