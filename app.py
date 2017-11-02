from flask import Flask, request, jsonify
import db
import os 
import requests
import steam
import steamspy
import datetime
from itertools import chain
from sqlalchemy import and_, or_

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
    steam_users = get_steam_users_and_games(params)

    return ok({
      'games': [steam_game.to_dict()
                for steam_game
                in get_common_steam_games(steam_users)],
      'users': [steam_user.to_dict() for steam_user in steam_users],
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

def get_steam_users_and_games(inputs):
  today = datetime.datetime.now(datetime.timezone.utc)

  steam_or_vanity_ids = [get_steam_or_vanity_id_from_input(input)
                         for input in inputs]

  novel_steamids = {userid for (userid, is_steamid)
                         in steam_or_vanity_ids
                         if is_steamid}

  novel_vanityids = {userid for (userid, is_steamid)
                          in steam_or_vanity_ids
                          if not is_steamid}

  db.commit()
  db_users_from_vanities = db.SteamUser.query.filter(
    and_(
      db.SteamUser.vanityid.in_(novel_vanityids),
      db.SteamUser.stale_date > today
    )
  ).all()

  for steam_user in db_users_from_vanities:
    novel_vanityids.remove(steam_user.vanityid)
    yield steam_user

  resolved_vanityids = map(steam.resolve_vanity_id, novel_vanityids)

  novel_steamids.update(resolved_vanityids)

  db_users_from_steamids = db.SteamUser.query.filter(
    and_(
      db.SteamUser.vanityid.in_(novel_steamids),
      db.SteamUser.stale_date > today
    )
  ).all()
  
  for steam_user in db_users_from_steamids:
    novel_steamids.remove(steam_user.steamid)
    yield steam_user

  new_steam_user_summaries = map(steam.get_user_summary, novel_steamids)

  new_steam_users = map(db.SteamUser.from_user_summary, new_steam_user_summaries)

  for new_steam_user in new_steam_users:
    owned_appids = steam.get_appids_owned_by_user(new_steam_user.steamid) 
    new_steam_user.possessions = list(get_steam_games(owned_appids))
    db.merge(new_steam_user)
    yield new_steam_user

def get_steam_games(appids):
  today = datetime.datetime.now(datetime.timezone.utc)
  if not isinstance(appids, set):
    appids = set(appids)
  
  games_in_db = db.SteamGame.query.filter(
    and_(
      db.SteamGame.appid.in_(appids),
      db.SteamGame.stale_date > today
    )
  )


  for game in games_in_db:
    appids.remove(game.appid)
    yield game

  if not appids:
    return

  irresolvable_appids = {irresolvable_game.appid
                         for irresolvable_game
                         in db.IrresolvableGame.query.all()}
  for appid in appids:
    if appid in irresolvable_appids:
      continue
    steam_details = steam.get_game_details(appid)
    steamspy_details = steamspy.get_app_details(appid)
    steam_game = db.SteamGame.from_game_details(steam_details, steamspy_details)
    db.merge(steam_game)
    yield steam_game

def get_common_steam_games(steam_users):
  game_sets = list(map(lambda steam_user: set(steam_user.possessions), steam_users))
  first_set, *rest = game_sets
  if not rest:
    return first_set
  else:
    return first_set.intersection(rest)

def get_steam_or_vanity_id_from_input(input):
  input = str(input)
  input = input.replace('http://', '').replace('https://', '')

  if input.isdecimal():
    return (input, True)
  elif input.isalnum():
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
  
