from jinja2 import Environment, FileSystemLoader
from datetime import datetime
import os, json
 
root = os.path.dirname(os.path.abspath(__file__))
templates_dir = os.path.join(root, 'templates')
env = Environment( loader = FileSystemLoader(templates_dir) )
template = env.get_template('index.html')

def GenerateHTMLReport(*args):
    filename = os.path.join(root, 'html', datetime.today().strftime('%Y-%m-%d-%H%M%S')+'-report.html')
    #print(args)
    with open(filename, 'w') as fh:
       fh.write(template.render(
            h1 = "Akamai Hostnames Coverage Report",
            list = args,
        ))

def GenerateJSONReport(*args):
    filename = os.path.join(root, 'json', datetime.today().strftime('%Y-%m-%d-%H%M%S')+'-report.json')
    #print(args)
    with open(filename, 'w') as fh:
       json.dump(args, fh, ensure_ascii=False, indent=4)

#data = ['1', '2', '3']
#d = ['22', '23', '24', '25', '26']
#GenerateHTMLReport(data, d)
