#!/usr/bin/env python
# # -*- coding: utf-8 -*-
""" === utils_load_db_csv.py: script for converting people database from csv to sqlite format with updated dates from wikipedia === """
import os
import csv
from time import time
from datetime import datetime
from sqlalchemy import Column,String,Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import Sequence
from sqlalchemy.types import TypeDecorator, Unicode

# import pywikibot with user-config.py in utils directory
old_path = os.getcwd() # remember current working directory
os.chdir(os.getcwd() + "/utils") # change it to /utils
import pywikibot # initialize pywikibot
os.chdir(old_path) # set previous working directory

class CoerceUTF8(TypeDecorator):
    """Safely coerce Python bytestrings to Unicode
    before passing off to the database."""

    impl = Unicode

    def process_bind_param(self, value, dialect):
        if isinstance(value, str):
            value = value.decode('utf-8')
        return value

def Load_Data(file_name):
    """ load item list from csv file """
    with open(file_name, 'r') as f:
        reader = csv.reader(f,  delimiter=';')
        next(reader)
        item_list = list(reader)
    return item_list

Base = declarative_base() # initialize declarative sqlite database

class Faces(Base):
    #Tell SQLAlchemy what the table name is and if there's any table-specific arguments it should know about
    __tablename__ = 'faces'
    __table_args__ = {'sqlite_autoincrement': True}
    #tell SQLAlchemy the name of column and its attributes:
    id = Column(Integer, primary_key=True) 
    decade = Column(Integer)
    gender = Column(String)
    name = Column(String)
    birth = Column(Integer)
    death = Column(Integer)
    quote = Column(CoerceUTF8)
    descr = Column(CoerceUTF8)
    path = Column(String)
    wiki = Column(String)
    info = Column(String)
    source = Column(String)

def getWikiAge(site, wikiName):
    """ parse birth and death year from wikiData based on wikipedia name """
    page = pywikibot.Page(site, wikiName) # initialized pywikibot for wikipedia site
    item = pywikibot.ItemPage.fromPage(page)  # this can be used for any page object
    item_dict = item.get()
    clm_dict = item_dict["claims"]
    birth_year = 0
    death_year = 0
    birth_year = clm_dict["P569"][0].getTarget().year
    if "P570" in clm_dict: # check if person has year of death
        death_year = clm_dict["P570"][0].getTarget().year
    return tuple((birth_year, death_year))

if __name__ == "__main__":
    """rewrite sqlite database for famous people with updated years of living from wikipedia"""
    t = time()
    #Create the database
    engine = create_engine('sqlite:///static/db/faces.db')
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)  
    #Create the session
    session = sessionmaker()
    session.configure(bind=engine)
    s = session() 
    site = pywikibot.Site('en', 'wikipedia')
    try:
        file_name = "static/db/db_people.csv" # load database from csv file and convert it to sqlite table format
        data = Load_Data(file_name)
        for i in data:
            wikiName = i[7].rsplit('/', 1)[1]
            dates = getWikiAge(site, wikiName) # get birth and death years from pywikibot
            print(i[0] + ". " + i[3] + " (" + str(dates[0]) + " - " + str(dates[1]) + ")")
            record = Faces(**{
                'id' : i[0],
                'decade' : i[1],
                'gender' : i[2],
                'name' : i[3],
                'birth' : dates[0],
                'death' : dates[1],
                'quote' : i[4],
                'descr' : i[5],
                'path' : i[6],
                'wiki' : i[7],
                'info' : i[8],
                'source' : i[9]
            })
            s.add(record) #Add all the records
        s.commit() #Attempt to commit all the records
    except:
        s.rollback() #Rollback the changes on error
    finally:
        s.close() #Close the connection
    print "Time elapsed: " + str(time() - t) + " s." #0.091s
