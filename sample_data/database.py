#!/usr/bin/env python

#Copyright (c) 2014 Dongkeun Lee
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish, dis-
# tribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the fol-
# lowing conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABIL-
# ITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
# SHALL THE AUTHOR BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

from peewee import *
import time

DATABASE = 'database_creativity.db'
database = SqliteDatabase(DATABASE)
#model defintion of database
class BaseModel(Model):
	class Meta:
		database = database

class Author(BaseModel):
	name = CharField()
	num_of_work = IntegerField(default=0)

class Email(BaseModel):
	author = ForeignKeyField(Author, related_name='authorEmail')
	email = CharField()
	date = DateField()
	
class Work(BaseModel):
	title = CharField()

class AuthorWork(BaseModel):
	author = ForeignKeyField(Author, related_name='authorWork')
	work = ForeignKeyField(Work, related_name='authorWork')

class Address(BaseModel):
	author = ForeignKeyField(Author, related_name='authorAddress')
	city = CharField()
	state = CharField()
	country = CharField()
	date = DateField()

class Cocitation(BaseModel):
	inputRelationship = ForeignKeyField(AuthorWork, related_name='inputRelationship')
	citingWork = ForeignKeyField(Work, related_name='citingWork')
	citedRelationship = ForeignKeyField(AuthorWork, related_name='citedRelationship')

class Queries(BaseModel):
	author = CharField()
	start = DateField()
	end = DateField()
	num_of_search = IntegerField()
	num_of_citing = IntegerField()
	num_of_cited = IntegerField()

def print_cocitation():
	AW1 = AuthorWork.alias()
	AW2 = AuthorWork.alias()
	for x in Cocitation.select(Cocitation.inputRelationship,Cocitation.citedRelationship,fn.Count(Cocitation.id).alias('countA')).join(AW1, on=(Cocitation.inputRelationship == AW1.id)).switch(Cocitation).join(AW2,on=(Cocitation.citedRelationship == AW2.id)).switch(Cocitation).group_by(AW2.author,AW1.author).order_by(fn.Count(Cocitation.id).desc()):
		try:
			inputR = AuthorWork.get(AuthorWork.id == x.inputRelationship.id)
			outputR = AuthorWork.get(AuthorWork.id == x.citedRelationship.id)
			print "\"{0}\",\"{1}\",\"{2}\"".format(inputR.author.id,outputR.author.id, x.countA)
		except Author.DoesNotExist:
			continue

def print_author():
	for x in Author.select():
		p_email = ""
		p_city = ""
		p_state = ""
		p_country = ""
		for y in Email.select().where(Email.author == x).order_by(Email.date.desc()):
			p_email = y.email
			break
		for y in Address.select().where(Address.author == x).order_by(Address.date.desc()):
			p_city = y.city
			p_state = y.state
			p_country = y.country
			break
		print "\"{0}\",\"{1}\",\"{2}\",\"{3}\",\"{4}\",\"{5}\",\"{6}\"".format(x.id,x.name.encode('utf-8'),x.num_of_work,p_email,p_city.encode('utf-8'),p_state.encode('utf-8'),p_country.encode('utf-8'))
			

#--------------------
#MAIN STARTS HERE
def main():

	#database connection
	database.connect()

	#for x in Queries.select():
	#	print x.author, x.start,x.end,x.num_of_search,x.num_of_citing,x.num_of_cited
	print_cocitation()
	print "---------"
	print_author()

	print "----ERROR CHECK----"
	for x in Cocitation.select():
		aa = AuthorWork.get(AuthorWork.id == x.inputRelationship.id)
		bb = AuthorWork.get(AuthorWork.id == x.citedRelationship.id)
		try:
			aaa = aa.author.id
		except Author.DoesNotExist:
			print "input",x.id
			continue
		try:
			bbb = bb.author.id
		except Author.DoesNotExist:
			print "cited",x.id
			continue
		if aa.author.id == bb.author.id:
			print "in & out",x.id
			print Author.get(Author.id == aa.author.id).title
			print Author.get(Author.id == bb.author.id).title
	print "DONE"
	
	#database connection closed
	database.close()

if __name__ == "__main__":
	main()
