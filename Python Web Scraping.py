# Ameya Baxi (some collaboration with lab team members)
# COMP SCI 320: Data Science Programming II, Fall 2022
# Project 3: Find the Path!

# inheritance, graph search, web scraping
# project instructions: https://github.com/cs320-wisc/f22/tree/main/p3

# project: p3
# submitter: abaxi
# partner: none
# hours: 8

# import statements
import pandas as pd, os, time, requests
from collections import deque
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
        

class GraphSearcher:
    
    # GraphSearcher constructor
    def __init__(self):
        self.visited = set() # keeps track of visited nodes
        self.order = [] # tracks path

    def visit_and_get_children(self, node):
        """ Record the node value in self.order, and return its children
        param: node
        return: children of the given node
        """
        raise Exception("must be overridden in sub classes -- don't change me here!")

    # depth first search
    def dfs_search(self, node):
        
        # clear out visited set and order list
        self.visited = set()
        self.order = []
        
        # start recursive search
        self.dfs_visit(node)

    def dfs_visit(self, node):
        
        # check if node has already been visited
        if node in self.visited:
            return
        
        # add node to set
        else:
            self.visited.add(node)
        
        # get children of node
        self.children = self.visit_and_get_children(node)
        
        # call dfs_visit on each child using a loop
        for child in self.children:
            self.dfs_visit(child)
    
    # breadth first search
    def bfs_search(self, node):
        
        # clear out visited set and order list
        self.visited = set() 
        self.order = []
                
        todo = deque([node])

        while len(todo) > 0:
            curr = todo.popleft()
            if type(curr) != str:
                continue
            children = self.visit_and_get_children(curr)
            for child in children:
                if not child in self.visited:
                    todo.append(child) 
                    self.visited.add(child)
                    
            
class MatrixSearcher(GraphSearcher): # inherits from GraphSearcher class
    
    # MatrixSearcher constructor
    def __init__(self, df): 
        super().__init__() # calls GraphSearcher constructor
        self.df = df

    def visit_and_get_children(self, node):
        
        self.order.append(node)
        children = []
        
        # find children of node
        for n, has_edge in self.df.loc[node].items():
            if has_edge == 1:
                children.append(n)
                
        return children
    

class FileSearcher(GraphSearcher): # inherits from GraphSearcher class
    def __init__(self):
        super().__init__() # calls GraphSearcher constructor
    
    def visit_and_get_children(self, file):
        
        # read file
        with open(os.path.join('file_nodes', file)) as f:
            data = f.read()
        
        # record value
        if not data[:1] in self.order:
            self.order.append(data[:1])
        
        # record children
        data = data.replace('\n', '')
        children = data[1:].split(',')
        
        return children
        
    # concatenate values in self.order into a string
    def concat_order(self):
        
        string = ''
        
        for v in self.order:
            string += v
        
        return string

    
class WebSearcher(GraphSearcher): # inherits from GraphSearcher class
    def __init__(self, webdriver): # takes Chrome webdriver object as a parameter
        super().__init__() # calls GraphSearcher constructor
        self.driver = webdriver
        
    def visit_and_get_children(self, url):   
        children = []
        if not url in self.order: # preventing repetition of node_1 page in self.order
            self.order.append(url)
        self.driver.get(url)
        elements = self.driver.find_elements('tag name', 'a')
        for e in elements:
            children.append(e.get_attribute('href'))
        return children
    
    def table(self):
        self.fragments = pd.read_html(self.order[0])
        for o in self.order[1:]:
            df_list = pd.read_html(o)
            for df in df_list:
                self.fragments.append(df)
        concat_df = pd.concat(self.fragments, ignore_index = True)
        # adapted from https://www.statology.org/pandas-keep-columns/:
        concat_df_reduced = concat_df[['clue', 'latitude', 'longitude', 'description']]        
        return concat_df_reduced
    
    
def reveal_secrets(driver, url, travellog):
    
    # generate password from 'clues' column of travellog DataFrame
    password = ''
    for c in travellog['clue']:
        password += str((int(c)))
    
    # visit url with driver
    driver.get(url)
    
    # automate typing password in box and clicking 'GO'
    password_box = driver.find_element('id', 'password')
    password_box.send_keys(password)
    go_button = driver.find_element('id', 'attempt-button')
    go_button.click()
    
    # wait until page loads
    time.sleep(5)
    
    # click 'view location' button
    security_button = driver.find_element('id', 'securityBtn')
    security_button.click()
    
    # wait until page loads
    time.sleep(5)
    
    # save image
    # copied from https://code-maven.com/slides/python/dowload-image-using-requests
    # copied from https://stackoverflow.com/questions/16694907/download-large-file-in-python-with-requests/16696317#16696317
    img = requests.get('https://admissions.wisc.edu/wp-content/uploads/sites/462/2020/04/aerial_UW_16mm11_6543-800x533.jpg', stream = True)
    with open('Current_Location.jpg', 'wb') as f:
        for chunk in img.iter_content(chunk_size = 8192):   
            f.write(chunk)
    
    # get current location on page
    location = driver.find_element('id', 'location')
    location_text = location.text
    
    return location_text # return current location on page
    
