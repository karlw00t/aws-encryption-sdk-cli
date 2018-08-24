from troposphere import Template
from troposphere.sqs import Queue

import json

def create_template():
    template = Template()

    template.add_resource(Queue('MrQueue'))

    return template.to_dict()

if __name__ == "__main__": 
    print(json.dumps(create_template()))
