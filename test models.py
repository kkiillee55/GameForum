
# from itsdangerous import JSONWebSignatureSerializer as Serializer
# from models import Game,User,Platform
# from modules import db
# from datetime import  datetime
#
# #db.drop_all()
# db.create_all()
# #
# #
# for i in range(5):
#     game=Game(title=f'game{i}',release_date=datetime.utcnow())
#     user=User(first_name=str(i),last_name=str(i),email=str(i),password='123')
#     db.session.add(game)
#     db.session.add(user)
# #
# xbox=Platform(name='xbox')
# ps4=Platform(name='ps4')
# switch=Platform(name='switch')
# db.session.add(xbox)
# db.session.add(ps4)
# db.session.add(switch)
# db.session.commit()
# #
# u1=User.query.get(1)
# u2=User.query.get(2)
#
# g1=Game.query.get(1)
# g2=Game.query.get(2)
# g3=Game.query.get(3)
#
# u1.following_games.append(g1)
# u1.following_games.append(g3)
#
# u2.following_games.append(g2)
# u2.following_games.append(g3)
#
# db.session.commit()
#
#
# #
# g1=Game.query.get(1)
# g2=Game.query.get(2)
# g3=Game.query.get(3)
# p1=Platform.query.get(1)
# p2=Platform.query.get(2)
# # #
# g1.platforms.append(p1)
# g1.platforms.append(p2)
# g2.platforms.append(p2)
# g3.platforms.append(p1)
# db.session.commit()

# user=User.query.get(1)
# game=Game.query.get(3)
# post=Post(title='post1',content='ocntent of post 1',author=user,game=game)
# db.session.add(post)
# db.session.commit()

# from models import Post
# p=Post.query.get(1)
# p.comments

import os

# from smartystreets_python_sdk import StaticCredentials, ClientBuilder
# from smartystreets_python_sdk.us_autocomplete import Lookup as AutocompleteLookup, geolocation_type
#
#
# def run():
#     auth_id = "f60f4340-5505-4d20-3a6c-995a422618c7"
#     auth_token = "LLbO7xF0xFBL7AK80mQI"
#
#     # We recommend storing your secret keys in environment variables instead---it's safer!
#     # auth_id = os.environ['SMARTY_AUTH_ID']
#     # auth_token = os.environ['SMARTY_AUTH_TOKEN']
#
#     credentials = StaticCredentials(auth_id, auth_token)
#
#     client = ClientBuilder(credentials).build_us_autocomplete_api_client()
#     lookup = AutocompleteLookup('asf')
#
#     client.send(lookup)
#
#     print('*** Result with no filter ***')
#     print()
#     for suggestion in lookup.result:
#         print(suggestion.text)

    # Documentation for input fields can be found at:
    # https://smartystreets.com/docs/us-autocomplete-api#http-request-input-fields

    # lookup.add_city_filter('Ogden')
    # lookup.add_state_filter('IL')
    # lookup.add_prefer('Fallon, IL')
    # lookup.max_suggestions = 5
    # lookup.geolocate_type = geolocation_type.NONE
    # lookup.prefer_ratio = 0.333333
    # lookup.add_state_filter('IL')
    # lookup.max_suggestions = 5
    #
    # suggestions = client.send(lookup)  # The client will also return the suggestions directly
    #
    # print()
    # print('*** Result with some filters ***')
    # for suggestion in suggestions:
    #     print(suggestion.text)

#
# if __name__ == "__main__":
#     run()

import pymysql

conn=pymysql.connect(
    host='localhost',
    user='root',
    password='12345678',
    db='game',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor,
    autocommit=True,
)

with conn.cursor() as cursor:
    sql='update user set user.status="ACTIVE" where user.id=19;'
    cursor.execute(sql)
    print(cursor.fetchone())

