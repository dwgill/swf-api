from flask import Flask, request, jsonify, logging
import db
import os 
import requests
import steam
import steamspy
import datetime
import re

app = Flask(__name__)

if os.getenv('ENV', '') == 'DEV':
  from flask_cors import CORS
  cors = CORS(app, resources={r"/get-games*": {"origins": "*"}})

with app.app_context():
  db.initialize(app)

@app.route('/')
def index():
  return ok('hello world')

@app.route('/getsharedgames')
def get_shared_games():
  if not request.args.get('users'):
    return bad_request('missing parameter: users')
  params = request.args.get('users').split(',')

  if not params:
    return bad_request('invalid parameter: users')

  try:
    steam_users = list(get_steam_users_and_games(params))

    games_info_dict = build_game_info_dict(steam_users)

    shared_games_dict = build_shared_games_dict(steam_users)

    return ok({
      'game_details': games_info_dict,
      'shared_games': shared_games_dict,
      'users': {steam_user.steamid: steam_user.to_dict()
                for steam_user in steam_users},
    })

  except steam.IndeterminableSteamIdException as e:
    return bad_request('invalid user parameter: %s' % e)
  
  except steam.SteamApiException as e:
    endpoint, status_code, *request_args, response = e.args
    return not_found({
      'status_code': status_code,
      'endpoint': endpoint,
      'parameters': request_args,
      'response': response,
    })

  finally:
    db.commit()

def not_found(message):
  return jsonify({
    'success': False,
    'error': message,
  }), 404

def bad_request(message):
  return jsonify({
    'success': False,
    'error': message,
  }), 400

def ok(result):
  return jsonify({
    'success': True,
    'response': result,
  }), 200

def build_game_info_dict(steam_users):
  if len(steam_users) == 0:
    return dict()
  elif len(steam_users) == 1:
    (steam_user,) = steam_users
    return {
      int(steam_game.appid): steam_game.to_dict()
      for steam_game in steam_user.possessions\
        .filter_by(multiplayer=True)
    }
  else:
    first_user, *other_users = steam_users
    return { 
      int(steam_game.appid): steam_game.to_dict()
      for steam_game in first_user.possessions\
        .union(*map(lambda usr: usr.possessions, other_users))\
        .filter_by(multiplayer=True)
    }

def get_steam_users_and_games(inputs):
  today = datetime.datetime.now(datetime.timezone.utc)

  steam_or_vanity_ids = [get_steam_or_vanity_id_from_input(input)
                         for input in inputs]

  input_steamids = {userid for (userid, is_steamid)
                         in steam_or_vanity_ids
                         if is_steamid}

  input_vanityids = {userid for (userid, is_steamid)
                          in steam_or_vanity_ids
                          if not is_steamid}

  db_users_from_vanities = db.get_steam_users_from_vanities(input_vanityids)

  novel_vanityids = input_vanityids - {steam_user.vanityid for steam_user
                                       in db_users_from_vanities}

  resolved_vanityids = map(steam.resolve_vanity_id, novel_vanityids)

  input_steamids.update(resolved_vanityids)

  db_users_from_steamids = db.get_steam_users_from_steamids(input_steamids)

  novel_steamids = input_steamids - {steam_user.steamid for steam_user
                                     in db_users_from_steamids}

  new_steam_user_summaries = map(steam.get_user_summary, novel_steamids)

  new_steam_users = map(db.SteamUser.from_user_summary, new_steam_user_summaries)
  new_steam_users = list(map(db.merge, new_steam_users))

  new_steam_users_with_games = []
  for new_steam_user in new_steam_users:
    owned_appids = steam.get_appids_owned_by_user(new_steam_user.steamid) 
    try:
      steam_games = get_steam_games(owned_appids)
    except steam.SteamApiException as e:
      db.delete(new_steam_user)
      raise e
    for steam_game in steam_games:
      new_steam_user.possessions.append(steam_game)
    new_steam_users_with_games.append(db.merge(new_steam_user))

  db.commit()

  return db_users_from_vanities + db_users_from_steamids + new_steam_users_with_games

def get_steam_games(appids):
  result = []

  games_in_db = db.get_steam_games_from_appids(appids)

  for game in games_in_db:
    appids.remove(game.appid)
    app.logger.info('Found %s in db' % game)
    result.append(game)

  if not appids:
    return result

  for appid in db.without_nongame_appids(appids):
    try:
      steam_details = steam.get_game_details(appid)
    except steam.SteamApiException as e:
      if steam.derive_store_page(appid) is None:
        db.merge(db.NonGameApp(appid=appid)) 
        continue
      else:
        raise e

    if steam_details.get('type') not in ('game', 'dlc'):
      db.merge(db.NonGameApp(appid=appid)) 
      continue

    steamspy_details = steamspy.get_app_details(appid)
    steam_game = db.SteamGame.from_game_details(steam_details, steamspy_details)
    app.logger.info('Fetched data for %s' % steam_game)
    result.append(db.merge(steam_game))

  db.commit()
  return result

def get_common_multiplayer_games(steam_users):
  if len(steam_users) == 0:
    return set()
  elif len(steam_users) == 1:
    (the_only_user,) = steam_users
    return {steam_game.appid
            for steam_game
            in the_only_user.possessions.filter_by(multiplayer=True)}
  else:
    first_user, *other_users = steam_users
    intersection_q = first_user.possessions.filter_by(multiplayer=True)\
                     .intersect(*map(lambda user: user.possessions, other_users))
    return {steam_game.appid for steam_game in intersection_q}

def build_shared_games_dict(steam_users):
  steam_users = set(steam_users)
  result = dict()
  result['all'] = list(get_common_multiplayer_games(steam_users))

  if len(steam_users) < 2:
    return result

  result['almost'] = dict()
  for steam_user in steam_users:
    intersect_everyone_else = get_common_multiplayer_games(steam_users - {steam_user})
    everyone_has_but_me = intersect_everyone_else - get_common_multiplayer_games({steam_user})
    result['almost'][steam_user.steamid] = list(everyone_has_but_me)

  return result

def get_steam_or_vanity_id_from_input(input):
  input = str(input)
  input = input.replace('http://', '').replace('https://', '')

  if input.isdecimal():
    return (input, True)
  elif re.match(r'^[0-9a-zA-Z-_]+$', input):
    return (input, False)
  elif input.startswith('steamcommunity.com/'):
    user_id_or_vanity, is_steamid = parse_profile_url(input)
    return (user_id_or_vanity, is_steamid)
  else:
    raise steam.IndeterminableSteamIdException(input)

if __name__ == '__main__':
  if os.getenv('ENV', '') == 'DEV':
    app.run(debug=True)
  else:
    app.run()
  
