import webapp2
import logging

from google.appengine.ext import db
from google.appengine.api import users

import json
import urllib
import Utils


class TaskCategory(db.Model):
    name = db.StringProperty(multiline=False)
    date = db.DateTimeProperty(auto_now_add=True)
    
class TaskItem(db.Model):
    """Models an individual TaskItem entry with an author, content, and date."""
    author = db.UserProperty()
    content = db.StringProperty(multiline=True)
    category = db.ReferenceProperty(TaskCategory)
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
                if task.category is not None:
                    if task.category.name == category.name:
                    
                        content = task.content
                        logging.error("task key is %s", task.key().id())
                        task = {"author":taskAuthor, "content":content, "category":Utils.to_dict(task.category), "taskId":task.key().id()}
                        tasksList.append(task)
                    
            categoriesJson.append({"category":category.name, "tasks":tasksList})
          
    
        self.response.out.write(json.dumps({"tasks":categoriesJson}))
        
class GetFlatTasks(webapp2.RequestHandler):
    def get(self):
        tasks = db.GqlQuery("SELECT * "
                                "FROM TaskItem "
                                "ORDER BY date DESC LIMIT 10")
        
        tasksList = []
        for task in tasks:
            content = task.content
            logging.error("task key is %s", task.key().id())
            task = {"content":task.content, "category":Utils.to_dict(task.category), "taskId":task.key().id()}
            tasksList.append(task)
                    
        self.response.out.write(json.dumps({"tasks":tasksList}))

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
        
class DeleteTaskFromList(webapp2.RequestHandler):
    def delete(self):
        jsonBody = json.loads(self.request.body)
        taskId = jsonBody['taskId']
#        category_name = jsonBody['category']
#        category = TaskCategory(key=category_key(category_name))
        task_k = db.Key.from_path('TaskItem', taskId)
        task = db.get(task_k)
        task.category = None
        task.put()
        
class DeleteTask(webapp2.RequestHandler):
    def delete(self):
        jsonBody = json.loads(self.request.body)
        taskId = jsonBody['taskId']
        task_k = db.Key.from_path('TaskItem', taskId)
        task = db.delete(task_k)
        
class AddTask(webapp2.RequestHandler):
    def post(self):
        jsonBody = json.loads(self.request.body)
        
        category_name = jsonBody['category']        
        category = TaskCategory(key=category_key(category_name))
        category.name = category_name
        category.put()
        
        task = TaskItem()            
        task.content = jsonBody['content']
        task.category = category
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
                               ('/deleteCategory', DeleteCategory),
                               ('/deleteTaskFromList', DeleteTaskFromList),
                               ('/deleteTask', DeleteTask),
                               ('/getFlatTasks', GetFlatTasks)],
                              debug=True)