from flask_sqlalchemy import SQLAlchemy
import datetime
import os
import random
import steam
import steamspy
from sqlalchemy import and_

db = SQLAlchemy()

# == GENERAL METHODS FOR INTERFACING WITH THE DATABASE ==============

def initialize(app):
  db_path = os.getenv('DATABASE_PATH', './data.db')
  app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{path}'.format(path=db_path)
  app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
  db.init_app(app)
  db.create_all()

def add(instance):
  db.session.add(instance)

def add_all(instances):
  db.session.add_all(instances)

def delete(instance):
  db.session.delete(instance)

def merge(instance):
  return db.session.merge(instance)

def commit():
  db.session.commit()

def get_steam_games_from_appids(appids):
  today = get_today()
  appids = without_nongame_appids(appids)

  if appids:
    games_filtered = 0
    def games_filter(steam_game):
      nonlocal games_filtered
      if games_filtered < 5 and steam_game.stale_date < today:
        games_filtered += 1
        return False
      else:
        return True
    
    games_in_db = filter(games_filter, SteamGame.query.filter(SteamGame.appid.in_(appids)))
  else:
    games_in_db = []

  return games_in_db

def get_steam_users_from_vanities(vanityids):
  today = get_today()
  if not (isinstance(vanityids, set) or isinstance(vanityids, list)):
    vanityids = list(vanityids)

  if vanityids:
    users_in_db = SteamUser.query.filter(
      and_(
        SteamUser.vanityid.in_(vanityids),
        SteamUser.stale_date > today,
      )
    ).all()
  else:
    users_in_db = []
  
  return users_in_db

def get_steam_users_from_steamids(steamids):
  today = get_today()
  if not (isinstance(steamids, set) or isinstance(steamids, list)):
    steamids = list(steamids)

  if steamids:
    users_in_db = SteamUser.query.filter(
      and_(
        SteamUser.steamid.in_(steamids),
        SteamUser.stale_date > today,
      )
    ).all()
  else:
    users_in_db = []
  
  return users_in_db

def without_nongame_appids(appids):
  return set(map(int, appids)) - {non_game_app.appid for non_game_app
                                  in NonGameApp.query}

# == DATABASE TABLE & MODEL DEFINITIONS =============================

game_possessions = db.Table('game_possessions',
  db.Column('steamid', db.Integer, db.ForeignKey('steam_user.steamid')),
  db.Column('appid', db.Integer, db.ForeignKey('steam_game.appid'))
)

class SteamGame(db.Model):
  appid = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
  name = db.Column(db.Text, nullable=False)
  is_game = db.Column(db.Boolean, nullable=False)
  image_url = db.Column(db.Text)
  platforms = db.Column(db.Text)
  tags = db.Column(db.Text)
  genres = db.Column(db.Text)
  global_owners = db.Column(db.Integer, nullable=False)
  developer = db.Column(db.Text)
  publisher = db.Column(db.Text)
  store_page_url = db.Column(db.Text)
  free = db.Column(db.Boolean, nullable=False)
  price = db.Column(db.Integer)
  multiplayer = db.Column(db.Boolean, nullable=False)
  stale_date = db.Column(db.DateTime, nullable=False, index=True)

  def __repr__(self):
    return '<SteamGame %r>' % self.name

  @classmethod
  def from_game_details(cls, steam_details, steamspy_details):
    stales_soon = False

    appid=steamspy_details['appid']

    is_game = steam_details['type'] == 'game'

    # platforms e.g. 'windows;linux'
    platforms = ';'.join(platform.lower()
                         for (platform, is_on)
                         in steam_details.get('platforms', {}).items()
                         if is_on) or None

    # genres e.g. 'action;rpg'
    genres = ';'.join(genre_entry['description'].lower()
                      for genre_entry
                      in steam_details.get('genres', [])) or None

    # store_page_url e.g. 'http://store.steampowered.com/app/292030/'
    store_page_url = steam.derive_store_page(appid) or None

    # Price e.g. 1500 ($15)
    price = steam_details.get('price_overview',  {}).get('final')
    price = price or steam_details.get('price_overview', {}).get('initial')

    # If this game is on sale, we should invalidate this cache sooner
    stales_soon = stales_soon or steam_details.get('price_overview', {}).get('discount_percent', 0) > 0

    # Tags e.g. 'Local Multiplayer;Indie;Hack and Slash'
    tags = steamspy_details.get('tags', [])
    if isinstance(tags, dict):
      tags = tags.keys()
    tags = ';'.join(tag.lower() for tag in tags) or None

    is_multiplayer = steam.game_is_multiplayer(steam_details) or steamspy.game_is_multiplayer(steamspy_details)
    
    today = get_today()
    if stales_soon:
      stale_date = today + datetime.timedelta(days=1)
    elif not is_multiplayer:
      stale_date = today + random_timedelta_in_range(datetime.timedelta(weeks=24), datetime.timedelta(weeks=48))
    else:
      stale_date = today + random_timedelta_in_range(datetime.timedelta(weeks=4), datetime.timedelta(weeks=32))

    return cls(
      appid=int(appid),
      name=steam_details['name'],
      is_game=is_game,
      image_url=steam_details.get('header_image'),
      platforms=platforms,
      genres=genres,
      tags=tags,
      global_owners=steamspy_details['owners'],
      developer=steamspy_details.get('developer'),
      publisher=steamspy_details.get('publisher'),
      store_page_url=store_page_url,
      free=steam_details['is_free'],
      price=price,
      multiplayer=is_multiplayer,
      stale_date=stale_date,
    )

  def to_dict(self):
    return {
      'appid': self.appid,
      'name': self.name,
      'image_url': self.image_url,
      'platforms': self.platforms.split(';') if self.platforms else [],
      'tags': self.tags.split(';') if self.tags else [],
      'genres': self.genres.split(';') if self.genres else [],
      'global_owners': self.global_owners,
      'developer': self.developer,
      'publisher': self.publisher,
      'store_page_url': self.store_page_url,
      'free': self.free,
      'price': self.price,
    }

class SteamUser(db.Model):
  steamid = db.Column(db.Integer, primary_key=True, unique=True, nullable=True)
  vanityid = db.Column(db.Text, index=True)
  avatar_url = db.Column(db.Text)
  username = db.Column(db.Text)
  profile_url = db.Column(db.Text, nullable=False)
  realname = db.Column(db.Text)
  stale_date = db.Column(db.DateTime, nullable=False, index=True)
  possessions = db.relationship('SteamGame',
                               secondary=game_possessions,
                               backref='owners',
                               lazy='dynamic')

  def __repr__(self):
    if self.vanityid:
      return '<SteamUser %r>' % self.vanityid
    elif self.username:
      return '<SteamUser %r>' % self.username
    else:
      return '<SteamUser %r>' % self.steamid

  @classmethod
  def from_user_summary(cls, user_summary, *, steam_games=[]):
    today = get_today()
    stale_date = today + datetime.timedelta(days=3)
    vanityid = steam.get_vanity_from_user_sum(user_summary)

    return cls(
      steamid=user_summary['steamid'],
      vanityid=vanityid,
      avatar_url=user_summary.get('avatarfull'),
      username=user_summary.get('personaname'),
      profile_url=user_summary['profileurl'],
      realname=user_summary.get('realname'),
      stale_date=stale_date,
      possessions=steam_games,
    )

  def to_dict(self, *, include_games=False):
    result = {
      'steamid': self.steamid,
      'vanityid': self.vanityid,
      'avatar_url': self.avatar_url,
      'username': self.username,
      'profile_url': self.profile_url,
      'realname': self.realname,
    }

    if include_games:
      raise Exception('not implemented')
      result['games'] = [game.steamid for game in self.possessions]

    return result

class NonGameApp(db.Model):
  appid = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)

# == UTILITY METHODS ================================================
def random_timedelta_in_range(low, high):
  rand_delta_in_sec = random.randint(low.total_seconds(), high.total_seconds())
  return datetime.timedelta(seconds=rand_delta_in_sec)

def get_today():
  return datetime.datetime.now()
