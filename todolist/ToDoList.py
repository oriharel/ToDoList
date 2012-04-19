import webapp2
import logging

from google.appengine.ext import db
from google.appengine.api import users

import json


class TaskItem(db.Model):
    """Models an individual TaskItem entry with an author, content, and date."""
    author = db.UserProperty()
    content = db.StringProperty(multiline=True)
    category = db.StringProperty(multiline=True)
    date = db.DateTimeProperty(auto_now_add=True)
  
class TaskCategory(db.Model):
    name = db.StringProperty(multiline=False)
    date = db.DateTimeProperty(auto_now_add=True)


def category_key(category_name=None):
    """Constructs a datastore key for a TaskCategory entity with category_name."""
    return db.Key.from_path('TaskCategory', category_name or 'default_category')


class MainPage(webapp2.RequestHandler):
    def get(self):
        logging.error('here')
    
        categories = db.GqlQuery("SELECT * "
                                    "FROM TaskCategory "
                                    "ORDER BY date DESC LIMIT 10")
        tasks = db.GqlQuery("SELECT * "
                                "FROM TaskItem "
                                "ORDER BY date DESC LIMIT 10")
        categoriesJson = []
        for category in categories:
            logging.error('in category %s', category.name)
            tasksList = []
            taskAuthor = ''
            content = ''
            
            for task in tasks:
                if task.category == category.name:
                
                    content = task.content
                    task = {"author":taskAuthor, "content":content, "category":task.category}
                    tasksList.append(task)
                    
            categoriesJson.append({"category":category.name, "tasks":tasksList})
          
    
        self.response.out.write(json.dumps({"tasks":categoriesJson}))

class AddCategory(webapp2.RequestHandler):
    def post(self):
        category_name = self.request.get('name')
        category = TaskCategory(key=category_key(category_name))
        category.name = category_name
        category.put()
        
class DeleteCategory(webapp2.RequestHandler):
    def delete(self):
        category_name = self.request.get('name')
        db.delete(category_key(category_name))
        
class AddTask(webapp2.RequestHandler):
    def post(self):
        jsonBody = json.loads(self.request.body)
        logging.error('hey you')
        category_name = jsonBody['category']
        logging.error('category is %s', category_name)
        
        category = TaskCategory(key=category_key(category_name))
        task = TaskItem(parent=category)
        category.name = category_name
        category.put()
        if users.get_current_user():
            task.author = users.get_current_user()
    
        task.content = jsonBody['content']
        task.category = category_name
        task.put()

class GetCategories(webapp2.RequestHandler):
    def get(self):
    
        categories = db.GqlQuery("SELECT * "
                                "FROM TaskCategory "
                                "ORDER BY date DESC LIMIT 10")
        categoriesJson = []
        for category in categories:
            categoriesJson.append({'name':category.name})
          
        logging.error('cats are %s', categoriesJson)
        self.response.out.write(json.dumps({'categories':categoriesJson}))

app = webapp2.WSGIApplication([('/', MainPage),
                               ('/add', AddTask),
                               ('/categories', GetCategories),
                               ('/addCategory', AddCategory),
                               ('/tasks', MainPage),
                               ('/deleteCategory', DeleteCategory)],
                              debug=True)