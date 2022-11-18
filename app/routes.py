from flask import jsonify, render_template, request, redirect, url_for, make_response
from app import app
from app.models import Book
from app import db
import datetime
import json

def convert_tags(book_entry : dict):
	taglist = []
	keys = book_entry.keys()
	tagstr = ''
	for key in keys:
		if 'tag' in key:
			taglist.append(book_entry[key])
	for i in range(len(taglist)):
		if i == len(taglist) - 1:
			tagstr += taglist[i]
		else:
			tagstr += taglist[i] + ', '
	return tagstr

def check_for_empty(book : dict):
	book_entry = {
		'title' : book['title'],
		'author' : book['author'],
		'owned' : book['owned'],
		'have_read' : book['have_read'],
		'rating' : book['rating'],
		'is_series' : book['is_series'],
		'no_in_series' : book['no_in_series'],
		'tags' : book['tags']
	}
	for key in book_entry.keys():
		if book_entry[key] == '':
			if key == 'rating' or 'no_in_series':
				book[key] = 0
			elif key == 'owned' or 'have_read' or 'is_series':
				book[key] = 'False'
			else:
				book[key] = 'NONE'
	return book 

@app.route('/')
def home():
	books = Book.query.all()
	return render_template('frontpage.html',
                           page_title='Bookworms-R-Us! 📖',
                           page_description='A library for a little book worm!',
						   no_of_books=len(books),
						   books=books, method='none')

@app.route('/add-book')
def add_book():
	return render_template('add-book.html',
						   page_title='Add a New Book! 📖',
                           page_description='Always better to have more books!',
						   method='add')

@app.route('/update-book', methods=['POST'])
def update_book():
	return render_template('add-book.html',
						   page_title='Update a Book! 📖',
                           page_description='Make sure that everything is in its place!',
						   method='update',
						   book=request.form.to_dict())

@app.route('/search')
def search_book():
	return render_template('add-book.html',
						   page_title='Search for a Book! 📖',
                           page_description='Hope you find something good!',
						   method='search')

@app.route('/search-results', methods=['POST'])
def search_results():
	content = request.form.to_dict()
	content['tags'] = convert_tags(content)
	tags = content['tags']
	taglist = tags.split(',')
	book_list = []
	books = Book.query.all()
	for book in books:
		print(book)
		found_by_tag = False
		for tag in taglist:
			if tag.lower() in book.tags.lower() and tag != '':
				print("Adding {} to list from {}".format(book, tag))
				book_list.append(book)
				found_by_tag = True
				break
		if book.title.lower() == content['title'].lower() or \
			book.author.lower() == content['author'].lower() or \
				book.owned == content['owned'] or \
					book.have_read == content['have_read'] or \
						book.rating == content['rating'] or \
							book.is_series == content['is_series'] or \
								book.no_in_series == content['no_in_series'] and not found_by_tag:
				book_list.append(book)
				print("Adding {} to list from {}".format(book, content))
				continue
	print(book_list)
	return render_template('frontpage.html',
                           page_title='Bookworms-R-Us! 📖',
                           page_description='Search Results Away!',
						   no_of_books=len(book_list),
						   books=book_list, method='search')

@app.route('/exim')
def exim():
	return render_template('exim.html',
							page_title='Bookworms Export / Import 📖',
							page_description="Export, import capabilities of Bookworm!")

@app.route('/api/update/book', methods=['POST'])
def api_update_book():
	book = request.form.to_dict()
	book['tags'] = convert_tags(book)
	book = check_for_empty(book)
	db.session.query(Book). \
		filter(Book.title == str(book['title'])). \
			update({
				'title' : book['title'],
				'author' : book['author'],
				'owned' : book['owned'],
				'have_read' : book['have_read'],
				'rating' : book['rating'],
				'is_series' : book['is_series'],
				'no_in_series' : book['no_in_series'],
				'tags' : book['tags']
			})
	db.session.commit()
	return redirect(url_for('home'))

@app.route('/api/delete/book', methods=['POST'])
def api_delete_book():
	book = request.form.to_dict()
	book_entry = Book.query.filter_by(title=book['title']).first()
	print(book)
	db.session.delete(book_entry)
	db.session.commit()
	return redirect(url_for('home'))

@app.route('/api/add/book', methods=['POST'])
def api_add_book():
	book = request.form.to_dict()
	book['tags'] = convert_tags(book)
	book = check_for_empty(book)
	print(book)
	book_entry = Book(title=book['title'],
		author=book['author'],
		owned=book['owned'],
		have_read=book['have_read'],
		rating=book['rating'],
		is_series=book['is_series'],
		no_in_series=book['no_in_series'],
		tags=book['tags'])
		
	db.session.add(book_entry)
	db.session.commit()
	return redirect(url_for('home'))

@app.route('/api/database/import', methods=['POST'])
def import_db():
	if request.method != 'POST':
		return "Illegal use of API!"
	else:
		dbfile = request.files['dbfile']
		if dbfile:
			db_data = json.load(dbfile)
			bulk_upload_to_database(db_data)
			print(db_data)
			print(db_data.keys())
		return redirect(url_for('exim'))


def bulk_upload_to_database(db_data : dict):
	print(50 *'/')
	for table in db_data.keys():
		if table == 'books':
			print("BOOKS")
			for book in db_data[table]:
				print(book)
				is_in = Book.query.filter_by(title=book['title']).first()
				if type(is_in) != Book:
					b = Book(
						title=book['title'],
						author=book['author'],
						owned=book['owned'],
						have_read=book['have_read'],
						rating=book['rating'],
						is_series=book['is_series'],
						no_in_series=book['no_in_series'],
						tags=book['tags']
					)
					print("Found new book: {}, updating now!".format(b.title))
					db.session.add(b)
					db.session.commit()

def to_dict(books : list):
	book_list = []
	for book in books:
		print(book)
		book_list.append({
			'title' : book.title,
			'author' : book.author,
			'owned' : book.owned,
			'have_read' : book.have_read,
			'rating' : book.rating,
			'is_series' : book.is_series,
			'no_in_series' : book.no_in_series,
			'tags' : book.tags 
		})
	return book_list

@app.route('/api/database/export')
def export_db():
	books = Book.query.all()
	print(books, ' : ', type(books))
	books = to_dict(books)
	payload = {
		'books' : books
	}
	response = make_response(jsonify(payload))
	now = datetime.datetime.now()
	now = now.strftime('%d_%m_%Y')
	response.headers['Content-Disposition'] = 'attachment; filename=EXPORT_{}.json'.format(now)
	response.mimetype = 'text/json'
	return response		