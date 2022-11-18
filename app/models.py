from app import db

		

class Book(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	isbn = db.Column(db.String)
	title = db.Column(db.String)
	author = db.Column(db.String)
	owned = db.Column(db.String)
	have_read = db.Column(db.String)
	rating = db.Column(db.Integer)
	tags = db.Column(db.String)
	is_series = db.Column(db.String)
	no_in_series = db.Column(db.Integer)

	def __repr__(self):
		return self.title
