from hashlib import md5
from sqlalchemy import Table, Column, String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, or_, ForeignKey
from sqlalchemy.orm import scoped_session, sessionmaker, relationship, backref
from datetime import datetime
import pyodbc


# 要求用到数据库sql..
Base = declarative_base()
CONN_URL = 'mssql+pyodbc://sa:666666@xixi'
engine = create_engine(CONN_URL)
Session = scoped_session(sessionmaker(bind=engine))

def GetSession():
	"""
	创建数据库连接
	"""
	return Session()


from contextlib import contextmanager
@contextmanager
def session_scope():
	"""
	创建上下文管理，处理事务，操作失败回滚
	"""
	session = GetSession()
	# 这样session关了也可以赋值了？
	session.expire_on_commit = False
	try:
		yield session
		session.commit()
	except Exception:
		# print("发生异常",Exception) 
		# traceback.print_exc() 
		session.rollback()
		raise
	finally:
		session.close()


# class BorrowBook(Base):
# 	__tablename__ = 'borrowbook'

# 	姓名 = Column(String(50))
# 	书名 = Column(String(50))
# 	借阅日期 = Column(DateTime)
# 	应还日期 = Column(DateTime)
# 	续借次数 = Column(Integer)
# 	图书ID = Column('b_id', Integer, ForeignKey('book.图书ID'))
# 	借书证号 = Column('r_id', String(15), ForeignKey('reader.借书证号'))

# 	def __repr__(self):
# 		return '<%r borrow %r>' % (self.姓名, self.书名)

# BorrowBook = Table('as', Base.metadata,
# 		 Column('姓名', String(50)),
# 	 Column('书名',String(50)),
# 	 Column('借阅日期',DateTime),
# 	  Column('应还日期',DateTime),
# 	  Column('续借次数',Integer),
# 	Column('图书ID', Integer, ForeignKey('book.图书ID')),
# 	Column('借书证号', String(15), ForeignKey('reader.借书证号'))
# 	)


# class ReturnBook(Base):
# 	__tablename__ = 'returnbook'

# 	姓名 = Column(String(50))
# 	书名 = Column(String(50))
# 	借阅日期 = Column(DateTime)
# 	归还日期 = Column(DateTime, nullable = False)
# 	借阅次数 = Column(Integer, nullable = False)
# 	图书ID = Column('b_id', Integer, ForeignKey('book.图书ID'))
# 	借书证号 = Column('r_id', String(15), ForeignKey('reader.借书证号'))

# 	def __repr__(self):
# 		return '<%r borrow %r>' % (self.姓名, self.书名)


class Reader(Base):
	__tablename__ = 'reader'

	借书证号 = Column(String(15), primary_key = True, nullable = False)
	密码 = Column(String(20), nullable = False)
	姓名 = Column(String(50), nullable = False)
	性别 = Column(String(10), nullable = False)
	读者类型 = Column(String(20), nullable = False)
	专业 = Column(String(50))
	年级 = Column(String(50))
	借书量 = Column(Integer, nullable = False)
	联系方式 = Column(String(20), nullable = False)
	备注 = Column(String(50))
	# borrowbooks = relationship('borrowbooks', secondary=BorrowBook, backref = 'reader')

	# 打印表
	def __repr__(self):
		return '<user.姓名: %r>' % (self.姓名)

class Book(Base):
	__tablename__ = 'book'

	图书ID = Column(Integer, primary_key = True, nullable = False)
	图书分类号 = Column(String(10), nullable = False)
	书名 = Column(String(50), nullable = False)
	作者 = Column(String(50), nullable = False)
	出版社 = Column(String(50), nullable = False)
	出版时间 = Column(String(20), nullable = False)
	馆藏复本 = Column(Integer, nullable = False) 
	可借复本 = Column(Integer, nullable = False)
	# BorrowBook = relationship('borrowbooks', secondary = BorrowBook, backref = 'book')


	# 打印表
	def __repr__(self):
		return '<book.图书ID: %r>' % (self.图书ID)

class Administrators(Base):
	__tablename__ = 'administrators'

	工号 = Column(String(10), primary_key = True,nullable = False)
	姓名 = Column(String(50), nullable = False)
	性别 = Column(String(4), nullable = False)
	密码 = Column(String(50), nullable = False)
	角色 = Column(String(50), nullable = False)

	def __repr__(self):
		return '<admin.姓名: %r>' % (self.姓名)




def classToDict(obj):
	if obj is None:
		return None

	is_list = obj.__class__ == [].__class__
	is_set = obj.__class__ == set().__class__

	if is_list or is_set:
		obj_arr = []
		for o in obj:
			dict = {}
			dict.update(o.__dict__)
			obj_arr.append(dict)
		return obj_arr
	else:
		dict = {}
		dict.update(obj.__dict__)
		return dict


def query_all(obj):
	with session_scope() as session:
		Ma = session.query(obj).all()
		posts = []
		time = 0
		for m in Ma:
			if time > 50:
				break
			time = time + 1
			data = classToDict(m)
			posts.append(data)
		return posts


def query_admin(id = None):
	"""
	使用事务查询
	"""
	with session_scope() as session:
		# print('xixi')
		# print(session.query(Administrators).filter(Administrators.工号 == id))
		return session.query(Administrators).filter(Administrators.工号 == id).first()

def delete_admin(id = None):
	with session_scope() as session:
		a = session.query(Administrators).filter(Administrators.工号 == id).first()
		session.delete(a)

def add_admin(id, name, sex, pw, kind):
	with session_scope() as session:
		a = Administrators(工号=id, 姓名=name, 性别=sex, 密码=pw, 角色=kind)
		session.add(a)

def update_admin(id, name, sex, pw, kind):
	with session_scope() as session:
		session.query(Administrators).filter(Administrators.工号 == id).update({
				'姓名': name,
				'性别': sex,
				'密码': pw,
				'角色': kind
					})

def query_reader(id = None):
	with session_scope() as session:
		return session.query(Reader).filter(Reader.借书证号 == id).first()

def delete_reader(id = None):
	with session_scope() as session:
		session.delete(session.query(Reader).filter(Reader.借书证号 == id).first())

def add_reader(id, name, sex, pw, kind, major, grade, num, tel, remark):
	with session_scope() as session:
		session.add(Reader(借书证号=id,密码=pw,姓名=name,	性别=sex,读者类型	=kind,
			专业=major,年级=grade,借书量=num,联系方式=tel,备注=remark))

def update_reader(id, name, sex, pw, kind, major, grade, num, tel, remark):
	with session_scope() as session:
		session.query(Administrators).filter(Administrators.工号 == id).update({
				'密码': pw,
				'姓名': name,
				'性别': sex,
				'读者类型': kind,
				'专业': major,
				'年级': grade,
				'借书量': num,
				'联系方式':tel,
				'备注': remark
					})

def query_book(id = None):
	"""
	使用事务查询
	"""
	with session_scope() as session:
		# print('xixi')
		# print(session.query(Administrators).filter(Administrators.工号 == id))
		return session.query(Book).filter(Book.图书ID == id).first()

def delete_book(id = None):
	with session_scope() as session:
		a = session.query(Book).filter(Book.图书ID == id).first()
		session.delete(a)

def add_book(id, kind, b_name, r_name, pub, pub_time, all_num, avail_num):
	with session_scope() as session:
		a = Book(图书ID=id, 图书分类号=kind, 书名=b_name,
		作者=r_name, 出版社=pub, 出版时间=pub_time, 馆藏复本=all_num, 可借复本=avail_num)
		session.add(a)

def update_book(id, kind, b_name, r_name, pub, pub_time, all_num, avail_num):
	with session_scope() as session:
		session.query(Book).filter(Book.图书ID == id).update({
				'图书分类号': kind,
				'书名': b_name,
				'作者': r_name,
				'出版社': pub,
				'出版时间': pub_time,
				'馆藏复本': all_num,
				'可借复本':avail_num
					})


def query_book_like(name = None):
	"""
	使用存储过程根据书名查找所有书
	"""
	with session_scope() as session:
		return session.execute("exec Reader_Index_Book '%s'" % name).fetchall()


def query_all_borrowbook():
	with session_scope() as session:
		return session.execute("select * from BorrowView").fetchall()


def query_all_returnbook():
	with session_scope() as session:
		return session.execute("select * from ReturnBook").fetchall()

def query_returnbook(id = None):
	with session_scope() as session:
		return session.execute("select * from ReturnBook where 借书证号= '{}'".format(id)).fetchall()

# print(query_returnbook('0000008'))


def query_all_overdate():
	with session_scope() as session:
		return session.execute("select * from OverDate").fetchall()

# print(query_all_borrowbook())
# print(query_all_returnbook())

def reader_book_history_num(id = None):
	"""
	查询学生历史借阅数量
	"""
	with session_scope() as session:
		return session.execute("select dbo.Number_of_Book_Borrowed('%s')"% id).fetchall()

def backup():
	back_path = 'D:/MBOOK_' + datetime.now().strftime("%Y%m%d") + '.bak'  
	conn =pyodbc.connect(DRIVER='{SQL Server}',SERVER='DESKTOP-8ON6IN4',PORT='1433',DATABASE='MBOOK',autocommit=True)
	# conn.autocommit()
	cur = conn.cursor()
	sql = "BACKUP DATABASE [{0}] TO DISK = N'{1}'".format('MBOOK', back_path) 
	# sql = "select * from book"
	print(sql)
	cur.execute(sql)
	while cur.nextset():  
		pass  
	# print(cur.fetchone())
	# conn.autocommit(False)
	cur.close()

def restore():
	"""
	some pro
	"""
	back_path = 'D:/MBOOK_' + datetime.now().strftime("%Y%m%d") + '.bak'  
	conn =pyodbc.connect(DRIVER='{SQL Server}',SERVER='DESKTOP-8ON6IN4',PORT='1433',DATABASE='MBOOK',autocommit=True)
	# conn.autocommit()
	cur = conn.cursor()
	sql = "restore DATABASE [{0}] TO DISK = N'{1}'".format('MBOOK', back_path) 
	# sql = "select * from book"
	print(sql)
	cur.execute(sql)
	while cur.nextset():  
		pass  
	# print(cur.fetchone())
	# conn.autocommit(False)
	cur.close()



def query_admin_like(x):
	with session_scope() as session:
		sql = "select * from Administrators where concat(工号, 姓名,性别,角色) like '%{0}%' ".format(x)
		return session.execute(sql).fetchall()


def query_reader_like(x):
	with session_scope() as session:
		sql = "select * from Reader where concat(借书证号,姓名,性别,读者类型,专业,年级,联系方式,备注) like '%{0}%' ".format(x)
		return session.execute(sql).fetchall()

# print(query_reader_like('q'))

# def query_book_like(x):
	# pass

def query_borrow_like(x):
	with session_scope() as session:
		sql = "select * from BorrowView where concat(借书证号,姓名,图书ID,书名,借阅日期,应还日期) like '%{0}%' ".format(x)
		return session.execute(sql).fetchall()
# print(query_borrow_like('q'))

def query_return_like(x):
	with session_scope() as session:
		sql = "select * from ReturnBook where concat(借书证号,姓名,图书ID,书名) like '%{0}%' ".format(x)
		return session.execute(sql).fetchall()


def query_overdate_like(x):
	with session_scope() as session:
		sql = "select * from OverDate where concat(借书证号,姓名,图书ID) like '%{0}%' ".format(x)
		return session.execute(sql).fetchall()

def query_overdate_info(x):
	with session_scope() as session:
		sql = "select * from OverDate where 借书证号={0}".format(x)
		return session.execute(sql).fetchall()





def query_max_admin():
	with session_scope() as session:
		sql = "select max(工号) from Administrators"
		return int(session.execute(sql).fetchall()[0][0])

# print(type(int(query_max_admin())))

def query_renew_num(b_id = None, r_id = None):
	with session_scope() as session:
		# print(type(b_id))
		# print(type(r_id))
		a = session.execute("select 续借次数 from BorrowBook where 图书ID=%d and 借书证号 = '%s'"%(b_id, r_id)).fetchall()
		return a[0][0]
# print(query_renew_num(1, '1')[0][0])


def renew_book(r_id = None, b_id = None):
	with session_scope() as session:
		# print(type(b_id))
		# print(type(r_id))
		return session.execute('exec P_RenewBook "{0}",{1}'.format(r_id, b_id)).rowcount
# print(renew_book('0000008', 2449))
# print(query_renew_num(2449, '0000008'))

def borrow_book(r_id = None, b_id = None):
	with session_scope() as session:
		return session.execute("exec PBorrowBook '{0}', {1}".format(r_id, b_id)).rowcount

# print(borrow_book('105', 51))

def return_book(r_id = None, b_id = None):
	with session_scope() as session:
		return session.execute("exec P_Return_Book '{0}', {1}".format(r_id, b_id)).rowcount

# print(return_book('105', 55))




def update_user_info(id, name, sex, kind, major, grade, tel):
	with session_scope() as session:
		sql = "update Reader set 姓名='{0}',性别='{1}',读者类型='{2}',专业='{3}',年级='{4}',联系方式='{5}' where 借书证号={6}".format(name, sex, kind, major, grade, tel,id)
		session.execute(sql)
# renew_book(1, '1')


def query_borrow_info(id):
	with session_scope() as session:
		sql = "select * from BorrowBook where 借书证号={0}".format(id)
		return session.execute(sql).fetchall()		

# print(query_borrow_info('105'))


def query_borrow_first(id):
	with session_scope() as session:
		sql = "select * from BorrowBook where 借书证号={0} order by 借阅日期".format(id)
		return session.execute(sql).fetchone()		

# print(query_borrow_first('2'))

# update_user_info('1', '1', '男', '教师', '1', '1', '1')

# backup()

# print(reader_book_history_num('0000005'))   #[(1,)]

# print(query_book_like("毛泽东"))

# add_book(10000008, 'sb', '男', '1006', '管理员','1', 4,3)
# update_book(10000008, 'sbbb', '男', '1006', '管理员','d', 4,2)
# print(query_book(10000008))
# delete_book(10000008)
# print(query_book(10000008))


# add_admin('10008', 'sb', '男', '10008', '超级管理员')
# update_admin('1008', 'sbb', '男', '1006', '管理员')
# print(query_admin('10008').角色)
# delete_admin('1008')
# print(query_admin('1008'))


# add_reader('0000020', 'w', '女', '教师', '','', '',0,'','')
# print(query_reader('0000020'))
# delete_reader('0000020')
# # delete_reader('0000002')
# print(query_reader('0000020'))

# print(query_all(Administrators))

