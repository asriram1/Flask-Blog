from blogserver import db
from blogserver import User, Post

#Clear database if stuff already exists

def clear_data():
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        print(f'Clear table {table}')
        db.session.execute(table.delete())
    db.session.commit()

clear_data()

db.create_all()
user_1 = User(username='Anirudh', email='anirudh@gmail.com', password='pass')
user_2 = User(username='Krishna', email='krishna@gmail.com', password='pass')
db.session.add(user_1)
db.session.add(user_2)
db.session.commit()

# # Bulk add
# objects = [user_1, user_2]
# db.session.bulk_save_objects(objects)
# db.session.commit()

print(User.query.all())
print(User.query.first())
print(User.query.filter_by(username="Anirudh").all())   
user = User.query.filter_by(username="Anirudh").first()
print(user.id)
user = User.query.get(1)
print(user)
print(user.posts)
post_1 = Post(title='Blog 1', content='First Post Content!',user_id = user.id)
post_2 = Post(title='Blog 2', content='Second Post Content!',user_id = user.id)
db.session.add(post_1)
db.session.add(post_2)
db.session.commit()
print(user.posts)
for post in user.posts:
    print(post.title)

post = Post.query.first()
print(post.user_id)
print(post.author)


#Removes all tables, rows etc.
db.drop_all()