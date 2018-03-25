from flask import Flask, request, g, render_template, flash, redirect, session, url_for
from model import *
from flask.ext.bootstrap import Bootstrap

app = Flask(__name__)
app.config['SECRET_KEY'] = 'adsfhgasfkjhkj'  
Bootstrap(app)

@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
    	a = query_admin(session['user_id'])
    	if a is None:
    		r = query_reader(session['user_id'])
    		g.user = r
    	else:
    		g.user = a

@app.route('/xiangxixinxi/<id>', methods = ['GET', 'POST'])
def xiangxixinxi(id):
	if request.method == 'POST':
		status = borrow_book(g.user.借书证号, int(id))
		# print(status)
		# print(g.user.姓名)
		# print(id)
		if status > 0:
			flash('借阅成功，请前往借书表查看')
			return render_template('user_index.html')
		else:
			flash('该书已没有库存，请借阅其他书籍！')
			return render_template('user_index.html')
	return render_template('xiangxixinxi.html')

@app.route('/super_admin_index', methods=['GET', 'POST'])
def super_admin_index():
	return render_template('super_admin_index.html')


@app.route('/user_admin_index', methods=['GET', 'POST'])
def user_admin_index():
	return render_template('user_admin_index.html')


@app.route('/book_admin_index', methods=['GET', 'POST'])
def book_admin_index():
	return render_template('book_admin_index.html')


@app.route('/user_index', methods=['GET', 'POST'])
def user_index():
	return render_template('user_index.html')


@app.route('/',methods=['GET','POST'])
def index():
	return render_template('index.html')













@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':
		if request.form['user_kind'] == 'admin':
			user = query_admin(request.form['user_id'])
			user = classToDict(user)
			if user is None:
				error = 'Invalid id'
			elif user['密码'] != request.form['user_password']:
				# elif not check_password_hash(user.密码, request.form['user_password']):
				error = 'Invalid password'
			else:
				flash('Hello %s' % user['姓名'])
				session['user_id'] = user['工号']
				if user['角色'] == '超级管理员':
					return redirect(url_for('super_admin_index'))
				if user['角色'] == '图书管理员':
					return redirect(url_for('book_admin_index'))
				if user['角色'] == '读者管理员':
					return redirect(url_for('user_admin_index'))
		elif request.form['user_kind'] == 'reader':
			user = query_reader(request.form['user_id'])
			user = classToDict(user)
			if user is None:
				error = 'Invalid id!'
			elif user['密码'] != request.form['user_password']:
				print(user['密码'])
				print(request.form['user_password'])
				print(type(user['密码']))
				print(type(request.form['user_password']))
				# elif not check_password_hash(user.密码, request.form['user_password']):
				error = 'Invalid password!'
			else:
				flash('Hello %s' % user['姓名'])
				session['user_id'] = user['借书证号']
				return redirect(url_for('user_index'))
		else:
			error = 'Please choose your role!'
		return render_template('login.html', error=error)
	return render_template('login.html')


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    flash('You were logged out')
    session.pop('user_id', None)
    return redirect(url_for('index'))














@app.route('/grant_manage', methods=['GET', 'POST'])
def grant_manage():
	types = 1
	if hasattr(g.user, '角色') is None:
		flash('您没有此权限！')
		# print('嘻嘻')
		return render_template('index.html')
	if g.user.角色 != '超级管理员':
		# print('哈哈')
		# print(g.user.角色)
		flash('您没有此权限！')
		return render_template('index.html')

	posts = query_all(Administrators)
	print(type(posts))
	if request.method == 'POST':
		if request.form['sub'] == "删除":
			id = request.form['id']
			print(id)
			delete_admin(id)

			posts = query_all(Administrators)
			# flash("删除成功！")
			return render_template('super_admin_index.html', 
				readonly="readonly", 
				types = types,
				posts=posts)

		if request.form['sub'] == "修改":
			flash("请输入您要修改的内容！")
			return render_template('super_admin_index.html',
			 readonly="", 
			 types = types, 
			 posts = posts)

		if request.form['sub'] == "确认":
			id = request.form['id']
			if request.form['sex'] not in ['男','女']:
				flash('性别输入非法，请重新添加')
				return render_template('super_admin_index.html', 
				readonly="readonly", 
				types=types, 
				posts=posts)
			if request.form['kind'] not in ['超级管理员', '图书管理员', '读者管理员']:
				flash('角色输入非法，请重新添加')
				return render_template('super_admin_index.html', 
				readonly="readonly", 
				types=types, 
				posts=posts)

			M = query_admin(id)
			if M:
				update_admin(
					request.form['id'],
					request.form['name'],
					request.form['sex'],
					request.form['pw'],
					request.form['kind'])
			else:
				add_admin(request.form['id'],	
					request.form['name'],
					request.form['sex'],
					request.form['pw'],
					request.form['kind'])

			posts = query_all(Administrators)
			flash("已经保存您的修改！")
			return render_template('super_admin_index.html', 
				readonly="readonly", 
				types=types, 
				posts=posts)

		if request.form['sub'] == "新增":
			print('add!')
			id = query_max_admin() + 1
			u = Administrators(工号=id, 姓名="", 性别="", 密码="",角色="")
			# posts = [u]
			# posts = posts.extend(query_all(Administrators))
			posts = [u]
			posts.extend(query_all(Administrators))
			flash("请输入您要添加的内容..")
			return render_template('super_admin_index.html', readonly="", types=types, posts=posts)


		if request.form['sub'] == "搜索":
			x = request.form['content']
			posts = query_admin_like(x)
			if posts:
				flash('查询成功！')
				return render_template('super_admin_index.html', types = types, posts = posts)
			else:
				flash('没有查询到您搜索的结果，请重新输入')
				return render_template('super_admin_index.html', types = types, posts = posts)

		if request.form['sub'] == "批量删除":
			id = request.form['tr']
			print(id)
			flash("批量删除")

	return render_template('super_admin_index.html', readonly="readonly", types = types, posts=posts)


@app.route('/users_manage', methods=['GET', 'POST'])
def users_manage():
	if hasattr(g.user, '角色') is None:
		flash('您没有此权限！')
		return render_template('index.html')
		# print(g.user.角色)
	if g.user.角色 not in ['超级管理员','读者管理员']:
		flash('您没有此权限！')
		return render_template('index.html')
	if g.user.角色 == '超级管理员':
		p = 'super'
	else:
		p = 'user'
	types = 2
	posts = query_all(Reader)
	
	if request.method == 'POST':
		if request.form['sub'] == "删除":
			id = request.form['id']
			print(id)
			delete_reader(id)

			posts = query_all(Reader)
			flash("删除成功！")
			return render_template('{0}_admin_index.html'.format(p),
				readonly="readonly", 
				types = types, 
				posts=posts)

		if request.form['sub'] == "修改":
			flash("请输入您要修改的内容！")
			return render_template('{0}_admin_index.html'.format(p),
			 readonly="", 
			 types = types, 
			 posts = posts)

		if request.form['sub'] == "确认":
			id = request.form['id']
			print(id)
			M = query_reader(id)
			print(M)
			if M:
				update_reader(
					request.form['id'],
					request.form['name'],
					request.form['sex'],
					request.form['pw'],
					request.form['kind'],
					request.form['major'],
					request.form['grade'],
					request.form['num'],
					request.form['tel'],
					request.form['remark']
					)
			else:
				add_reader(
					request.form['id'],
					request.form['name'],
					request.form['sex'],
					request.form['pw'],
					request.form['kind'],
					request.form['major'],
					request.form['grade'],
					request.form['num'],
					request.form['tel'],
					request.form['remark']
					)

			print('11')
			posts = query_all(Reader)
			flash("已经保存您的修改！")
			return render_template('{0}_admin_index.html'.format(p),
				readonly="readonly", 
				types=types, 
				posts=posts)

		if request.form['sub'] == "新增":
			print('add!')
			u = Reader(借书证号="", 姓名="", 性别="", 密码="",读者类型="", 专业="", 年级="", 借书量="", 联系方式="", 备注="")
			# posts = [u]
			# posts = posts.extend(query_all(Administrators))
			posts = [u]
			posts.extend(query_all(Reader))
			flash("请输入您要添加的内容..")
			return render_template('{0}_admin_index.html'.format(p), readonly="", types=types, posts=posts)


		if request.form['sub'] == "搜索":
			x = request.form['content']
			posts = query_reader_like(x)
			if posts:
				flash('查询成功！')
				return render_template('{0}_admin_index.html'.format(p), types = types, posts = posts)
			else:
				flash('没有查询到您搜索的结果，请重新输入')
				return render_template('{0}_admin_index.html'.format(p), types = types, posts = posts)


		if request.form['sub'] == "批量删除":
			id = request.form['tr']
			print(id)
			flash("批量删除")

	return render_template('{0}_admin_index.html'.format(p), readonly="readonly", types = types, posts=posts)


@app.route('/books_manage', methods=['GET', 'POST'])
def books_manage():
	"""
	全显示不行，一会写分页
	"""

	if hasattr(g.user, '角色') is None:
		flash('您没有此权限！')
		return render_template('index.html')
	if g.user.角色 not in ['超级管理员','图书管理员']:
		flash('您没有此权限！')
		return render_template('index.html')
	if g.user.角色 == '超级管理员':
		p = 'super'
	else:
		p = 'book'

	types = 3
	posts = query_all(Book)
	
	if request.method == 'POST':
		if request.form['sub'] == "删除":
			id = request.form['id']
			print(id)
			delete_book(id)

			posts = query_all(Book)
			flash("删除成功！")
			return render_template('{0}_admin_index.html'.format(p), 
				readonly="readonly", 
				types = types, 
				posts=posts)

		if request.form['sub'] == "修改":
			flash("请输入您要修改的内容！")
			return render_template('{0}_admin_index.html'.format(p),
			 readonly="", 
			 types = types, 
			 posts = posts)

		if request.form['sub'] == "确认":
			id = request.form['id']
			M = query_book(id)
			if M:
				update_book(
					request.form['id'],
					request.form['kind'],
					request.form['b_name'],
					request.form['r_name'],
					request.form['pub'],
					request.form['pub_time'],
					request.form['all_num'],
					request.form['avail_num'])
			else:
				add_book(
					request.form['id'],
					request.form['kind'],
					request.form['b_name'],
					request.form['r_name'],
					request.form['pub'],
					request.form['pub_time'],
					request.form['all_num'],
					request.form['avail_num'])

			posts = query_all(Book)
			flash("已经保存您的修改！")
			return render_template('{0}_admin_index.html'.format(p),
				readonly="readonly", 
				types=types, 
				posts=posts)

		if request.form['sub'] == "新增":
			print('add!')
			u = Book(图书ID="", 图书分类号="", 书名="", 作者="", 出版社="", 出版时间="",馆藏复本="",可借复本="")
			# posts = [u]
			# posts = posts.extend(query_all(Administrators))
			posts = [u]
			posts.extend(query_all(Book))
			flash("请输入您要添加的内容..")
			return render_template('{0}_admin_index.html'.format(p), readonly="", types=types, posts=posts)


		if request.form['sub'] == "搜索":
			if request.form['content']:
				x = request.form['content']
				posts = query_book_like(x)
				if posts:
					flash('查询成功！')
					return render_template('{0}_admin_index.html'.format(p), types = types, posts = posts)
				else:
					flash('没有查询到您搜索的结果，请重新输入')
					return render_template('{0}_admin_index.html'.format(p), types = types, posts = posts)
			flash('请输入您要查询的内容')


		if request.form['sub'] == "批量删除":
			id = request.form['tr']
			print(id)
			flash("批量删除")

	return render_template('{0}_admin_index.html'.format(p), readonly="readonly", types = types, posts=posts)


@app.route('/BR_manage', methods=['GET', 'POST'])
def BR_manage():
	types = 4
	if hasattr(g.user, '角色') is None:
		flash('您没有此权限！')
		return render_template('index.html')
	if g.user.角色 not in ['超级管理员','读者管理员']:
		flash('您没有此权限！')
		return render_template('index.html')
	if g.user.角色 == '超级管理员':
		p = 'super'
	else:
		p = 'user'
	posts = query_all_borrowbook()
	postt = query_all_returnbook()
	posto = query_all_overdate()
	print(posts)
	print(postt)
	if request.method == 'POST':
		if request.form['sub'] == '续借':
			if query_renew_num(int(request.form['b_id']),
				request.form['r_id']) >= 3:
				flash('超过次数，您已不能再续借')
				return render_template('{0}_admin_index.html'.format(p), types = types, posts = posts, postt = postt, posto = posto)
			renew_book(
				request.form['r_id'],
				int(request.form['b_id'])
				
				)
			posts = query_all_borrowbook()
			postt = query_all_returnbook()
			posto = query_all_overdate()
			flash('续借成功')
			return render_template('{0}_admin_index.html'.format(p), types = types, posts = posts, postt = postt, posto = posto)
		if request.form['sub'] == '还书':
			return_book(
				request.form['r_id'],
				int(request.form['b_id'])
				)
			posts = query_all_borrowbook()
			postt = query_all_returnbook()
			posto = query_all_overdate()
			flash('还书成功')
			return render_template('{0}_admin_index.html'.format(p), types = types, posts = posts, postt = postt, posto = posto)
		
		if request.form['sub'] == "搜索":
			if request.form['content']:
				x = request.form['content']
				posts = query_borrow_like(x)
				if posts:
					flash('查询成功！')
					return render_template('{0}_admin_index.html'.format(p), types = types, posts = posts)
				else:
					flash('没有查询到您搜索的结果，请重新输入')
					return render_template('{0}_admin_index.html'.format(p),types = types, posts = posts)
			flash('请输入您要查询的内容')



	return render_template('{0}_admin_index.html'.format(p), types = types, posts = posts, postt = postt, posto = posto)


@app.route('/super_show')
def super_show():
	types = 0
	if hasattr(g.user, '角色') is None:
		flash('您没有此权限！')
		return render_template('index.html')
	if g.user.角色 != '超级管理员':
		flash('您没有此权限！')
		return render_template('index.html')
	posta = query_all(Administrators)
	postu = query_all(Reader)
	postb = query_all(Book)
	postbr = query_all_borrowbook()
	return render_template('super_admin_index.html',
		types = types,
		posta = posta,
		postb = postb,
		postbr = postbr,
		postu = postu
	)


@app.route('/sys_log', methods=['GET', 'POST'])
def sys_log():
	types = 6
	if g.user.角色 == '超级管理员':
		if request.method == "POST":
			backup()
			flash('数据库备份在您的D盘根目录下')
			return render_template('super_admin_index.html', types = types)
		return render_template('super_admin_index.html', types = types)
	elif g.user.角色 == '图书管理员':
		if request.method == "POST":
			backup()
			flash('数据库备份在您的D盘根目录下')
			return render_template('book_admin_index.html', types = types)
		return render_template('book_admin_index.html', types = types)
	elif g.user.角色 == '读者管理员':
		if request.method == "POST":
			backup()
			flash('数据库备份在您的D盘根目录下')
			return render_template('user_admin_index.html', types = types)
		return render_template('user_admin_index.html', types = types)
	else:
		flash('您没有此权限！')
		return render_template('index.html')













@app.route('/book_show')
def book_show():
	types = 0
	posts = query_all(Book)
	return render_template('book_admin_index.html',
		types = types,
		posts = posts,
	)

@app.route('/search_book_admin', methods=['GET', 'POST'])
def search_book_admin():
	types = 1
	if hasattr(g.user, '角色') is None:
		flash('您没有此权限！')
		return render_template('index.html')
	if g.user.角色 in ['超级管理员','读者管理员']:
		flash('您没有此权限！')
		return render_template('index.html')

	if request.method == 'POST':
		if request.form['content']:
			types = 7
			name = request.form['content']
			posts = query_book_like(name)
			return render_template('book_admin_index.html', types = types, posts = posts)
	return render_template('book_admin_index.html',types = types)






@app.route('/user_show')
def user_show():
	types = 0
	if hasattr(g.user, '角色') is None:
		flash('您没有此权限！')
		return render_template('index.html')
	if g.user.角色 == '读者管理员':
		print(g.user.角色)
		postu = query_all(Reader)
		postbr = query_all_borrowbook()
		return render_template('user_admin_index.html',
			types = types,
			postbr = postbr,
			postu = postu
		)
	flash('您没有此权限！')
	return render_template('index.html')


@app.route('/search_user', methods=['GET', 'POST'])
def search_user():
	types = 3
	if hasattr(g.user, '角色') is None:
		flash('您没有此权限！')
		return render_template('index.html')
	if g.user.角色 in ['超级管理员','图书管理员']:
		flash('您没有此权限！')
		return render_template('index.html')

	if request.method == 'POST':
		if request.form['content']:
			types = 7
			name = request.form['content']
			posts = query_borrow_like(name)
			return render_template('user_admin_index.html', types = types, posts = posts)
	return render_template('user_admin_index.html',types = types)






@app.route('/search_book_index', methods = ['GET', 'POST'])
def search_book_index():
	"""
	同search_book
	"""
	types = 1

	if request.method == 'POST':
		if request.form['content']:
			types = 7
			name = request.form['content']
			posts = query_book_like(name)
			return render_template('index.html', types = types, posts = posts)
	return render_template('index.html',types = types)



@app.route('/index_info', methods = ['GET', 'POST'])
def index_info():
	return render_template('index.html')

@app.route('/new_info', methods = ['GET', 'POST'])
def new_info():
	types = 3
	return render_template('index.html', types = types)

@app.route('/lib_info', methods = ['GET', 'POST'])
def lib_info():
	types = 2
	return render_template('index.html', types = types)

@app.route('/tutorial', methods = ['GET', 'POST'])
def tutorial():
	types = 4
	return render_template('index.html', types = types)

@app.route('/english', methods = ['GET', 'POST'])
def english():
	types = 5
	return render_template('index.html', types = types)













@app.route('/user_info', methods=['GET', 'POST'])
def user_info():
	types = 0
	posts = query_reader(g.user.借书证号)
	if request.method == "POST":
		if request.form['sub'] == "修改":
			return render_template('user_index.html', types = types, posts = posts)
		elif request.form['sub'] == "保存":
			id = request.form['id']
			if request.form['sex'] not in ['男','女']:
				flash('性别输入非法，请重新添加')
				return render_template('user_index.html', 
				readonly="readonly", 
				types=types, 
				posts=posts)
			M = query_reader(id)
			if M:
				update_user_info(
					request.form['id'],
					request.form['name'],
					request.form['sex'],
					request.form['kind'],
					request.form['major'],
					request.form['grade'],
					request.form['tel'])

			posts = query_reader(g.user.借书证号)
			flash("已经保存您的修改！")
			return render_template('user_index.html', 
				readonly="readonly", 
				types=types, 
				posts=posts)

	return render_template('user_index.html', readonly = "readonly", types = types, posts = posts)


@app.route('/search_book_user', methods = ['GET', 'POST'])
def search_book_user():
	"""
	同search_book
	"""
	types = 1
	if request.method == 'POST':
		if request.form['content']:
			types = 7
			name = request.form['content']
			posts = query_book_like(name)
			return render_template('user_index.html', types = types, posts = posts)
	return render_template('user_index.html',types = types)



@app.route('/borrow_info', methods=['GET', 'POST'])
def borrow_info():
	types = 2
	id = g.user.借书证号
	posts = []
	posts.extend(query_borrow_info(id))
	if request.method == "POST":
		if request.form['sub'] == "续借":
			if query_renew_num(int(request.form['id']), id) >= 3:
				flash('您已超过最大续借次数，请及时还书')
			else:
				renew_book(id, int(request.form['id']))
				flash('续借成功！')	
				posts = []
				posts.extend(query_borrow_info(id))
				return render_template('user_index.html', types = types, posts = posts)
		if request.form['sub'] == "还书":
			return_book(id, int(request.form['id']))
			flash('还书成功！')	
			posts = []
			posts.extend(query_borrow_info(id))
			return render_template('user_index.html', types = types, posts = posts)

	return render_template('user_index.html', types = types, posts = posts)

@app.route('/renew_manage', methods=['GET', 'POST'])
def renew_manage():
	types = 3
	id = g.user.借书证号
	posts = []
	posts.extend(query_borrow_info(id))
	# print(posts[5])
	# day 
	if request.method == "POST":
		if request.form['sub'] == "续借":
			if query_renew_num(int(request.form['id']), id) >= 3:
				flash('您已超过最大续借次数，请及时还书')
			else:
				renew_book(id, int(request.form['id']))
				flash('续借成功！')	
				posts = []
				posts.extend(query_borrow_info(id))
				return render_template('user_index.html', types = types, posts = posts)
		if request.form['sub'] == "还书":
			return_book(id, int(request.form['id']))
			flash('还书成功！')	
			posts = []
			posts.extend(query_borrow_info(id))
			return render_template('user_index.html', types = types, posts = posts)

	return render_template('user_index.html', types = types, posts = posts)


@app.route('/overdue_payment', methods=['GET', 'POST'])
def overdue_payment():
	types = 4
	id = g.user.借书证号
	posts = []
	posts.append(query_overdate_info(id))
	print(posts[0])
	if posts != [[]]:
		flash('请及时交费')
		return render_template('user_index.html', posts = posts, types  =types)
	else:
		flash('您没有需要交费的项目！')

	return render_template('user_index.html', types = types )


@app.route('/history_info', methods = ['GET'])
def history_info():
	types = 10
	post = query_borrow_first(g.user.借书证号)
	if post == None:
		flash('您还没有借书记录')
		return render_template('user_index.html')
	else:
		num = reader_book_history_num(g.user.借书证号)[0][0]
		return render_template('user_index.html', post = post, types = types, num = num)


@app.route('/history_info_plus', methods = ['GET'])
def history_info_plus():
	types = 11
	posts = query_returnbook(g.user.借书证号)
	print(posts)
	posts.extend(query_borrow_info(g.user.借书证号))
	print(posts)
	return render_template('user_index.html', types = types, posts = posts)

if __name__ == '__main__':
	app.run()