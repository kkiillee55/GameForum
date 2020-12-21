# from modules import db
# from models import Post,Game
#
# game=Game.query.filter_by(title='game0').first()
# limit=5
# offset=10
# posts=Post.query.filter_by().order_by(Post.date_posted.desc()).offset(offset).limit(limit).all()
# total_num_posts=Post.query.count()
# prefix='/api/game/game0/post?'
#
# def find_prev_page(total,offset,limit,prefix):
#     if offset-limit>=0:
#         return prefix+f'offset={offset-limit}&limit={limit}'
#     else:
#         return None
#
# def find_next_page(total,offset,limit,prefix):
#     if offset+limit>=total:
#         return None
#     else:
#         return prefix+f'offset={offset+limit}&limit={limit}'
#
# print('prev: ',find_prev_page(total_num_posts,offset,limit,prefix))
# print('curr: '+prefix+f'offset={offset}&limit={limit}')
# print('next: ',find_next_page(total_num_posts,offset,limit,prefix))

from datetime import datetime

t_str="Fri, 20 Nov 2020 23:59:51 GMT"
t=datetime.strptime(t_str,'%a, %d %b %Y %H:%M:%S GMT')
