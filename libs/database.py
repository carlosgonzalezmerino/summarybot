import os
import sqlite3


class DB(object):
	def __init__(self):
		self.database = os.environ.get("DATABASE")

		self.connection	= None
		self.cursor		= None
		self.lastid		= -1

	def __dictfactory(self, cursor, row):
		d = {}
		for idx, col in enumerate(cursor.description):
			d[col[0]] = row[idx]
		return d

	def __verify(*inputs):
		result = True
		for x in inputs:
			result = result and bool(x)

		return result

	def connect(self):
		try:
			self.connection = sqlite3.connect(self.database, detect_types=sqlite3.PARSE_DECLTYPES)
			self.connection.row_factory = self.__dictfactory
			self.cursor = self.connection.cursor()
		except sqlite3.Error as err:
			raise Exception("SQLite Error: {}".format(err))

		return

	def add(self, table, data):
		if not self.__verify(table, data):
			raise Exception("Bad input.")

		self.connect()
		for k in data.copy():
			if not bool(data[k]):
				del data[k]

		_keys, values = list(data.keys()), list(data.values())
		keys, params = ", ".join(_keys), ('?,'*len(values))[:-1]

		try:
			query = "INSERT INTO {} ({}) VALUES ({})".format(table, keys, params)
			self.cursor.execute(query, values)
			self.connection.commit()
			self.lastid = self.cursor.lastrowid
		except sqlite3.Error as err:
			raise Exception("SQLite Error: {}".format(err))

		self.close()	
		return

	def update(self, table, data, key, value):
		if not self.__verify(table, data, key, value):
			raise Exception("Bad input.")

		self.connect()
		assigments = []
		for index in data.copy():
			if not isinstance(data[index], int) and not bool(data[index]):
				data[index] = "NULL"
			assigment = "{}='{}'".format(index, data[index])
			assigments.append(assigment)

		dataset	= ",".join(assigments)
		try:
			query = "SELECT * FROM {} WHERE {}=\'{}\'".format(table, key, value)
			self.cursor.execute(query)
			result = self.cursor.fetchone()

			if result:
				query = "UPDATE {} SET {} WHERE {}=\'{}\'".format(table, dataset, key, value)
				self.cursor.execute(query)
				self.connection.commit()
				return

			err = "Not found any row with column '{}' equal to '{}' in '{}' table.".format(key, value, table)
			raise sqlite3.Error(err)
		except sqlite3.Error as err:
			raise Exception("SQLite Error: {}".format(err))

		self.close()
		return

	def delete(self, table, data):
		if not self.__verify(table, data):
			raise Exception("Bad input.")

		self.connect()

		filters = []
		for k in data.copy():
			if not bool(data[k]):
				del data[k]
			else:
				filters.append("{}=\'{}\'".format(k, data[k]))

		filter = " AND ".join(filters)
		query = "DELETE FROM {} WHERE {}".format(table, filter)
		try:
			self.cursor.execute(query)
			self.connection.commit()
		except sqlite3.Error as err:
			raise Exception("SQLite Error: {}".format(err))

		self.close()
		return

	def get(self, table, filters):
		if not self.__verify(table, filters):
			raise Exception("Bad input.")

		constrains = []
		for index in filters:
			constrains.append("{}=\'{}\'".format(index, filters[index]))

		where = " AND ".join(constrains)
		query, result = "SELECT * FROM {} WHERE {}".format(table, where), {}

		self.connect()
		try:
			self.cursor.execute(query)
			result = self.cursor.fetchone()
		except sqlite3.Error as err:
			raise Exception("SQLite Error: {}".format(err))

		self.close()
		return result

	def getAll(self, table, key=None, value=None):
		if not self.__verify(table):
			raise Exception("Bad input.")

		self.connect()
		query, results = "SELECT * FROM %s" % table, []
		
		if key:
			if not value:
				raise Exception("Bad input params.")

			query = "%s WHERE %s=\'?\'" % (query, key)

		try:
			self.cursor.execute(query, value)
			results = self.cursor.fetchall()
		except sqlite3.Error as err:
			raise Exception("SQLite Error: {}".format(err))

		self.close()
		return results
	
	def count(self, table, key, value):
		if not self.__verify(table, key, value):
			raise Exception("Bad input.")

		self.connect()
		query, result = "SELECT COUNT(*) FROM %s WHERE %s=\'%s\'" % (table, key, value), 0
		
		try:
			self.cursor.execute(query)
			row_result = self.cursor.fetchone()
			result = list(row_result.values())[0]
		except sqlite3.Error as err:
			raise Exception("SQLite Error: {}".format(err))

		self.close()
		return result

	def close(self):
		try:
			self.connection.close()
		except sqlite3.Error as err:
			raise Exception("SQLite Error: {}".format(err))

		return
