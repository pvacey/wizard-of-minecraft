import base64
import json
import re
import os
import googleapiclient.discovery
import dialogflow_v2 as dialogflow
import mcrcon
import time

PROJECT_ID = 'PLACEHOLDER_PROJECT_ID'
PASSWORD = "PLACEHOLDER_PASSWORD"
ZONE = "us-central1-f"


def log_handler(event, context):
    raw_event = json.loads(base64.b64decode(event['data']).decode('utf-8'))
    print(event)
    raw_message = raw_event['jsonPayload']['message']
    
    # chat messages
    tmp = re.findall('\]:\s<\w+>\s(.*)\\r', raw_message)
    if len(tmp) > 0:
    	text = tmp[0]
    	resp = ask_the_wizard(text)
    	handle_intent(resp)
    # disconnect message
    tmp = re.findall('\]:\s\w+ left the game', raw_message)
    if len(tmp) > 0:
    	shut_it_down()
    return

def shut_it_down():
    ip = lookup_instance()
    resp = execute_rcon("/list", ip)
    number = re.findall('There are (\d+) of a max 20 players online', resp)[0]
    if number == "0":
        execute_rcon("/stop", ip)
        time.sleep(10)
        return stop_instance()
    return
        
def execute_rcon(cmd, ip):
    # send response
    rcon = mcrcon.MCRcon(ip, PASSWORD)
    rcon.connect()
    response = rcon.command(cmd)
    rcon.disconnect()
    return response

def ask_the_wizard(text, session_id='123456', language_code='en-US'):

    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(PROJECT_ID, session_id)
    text_input = dialogflow.types.TextInput(
    	text=text, 
    	language_code=language_code
    )

    query_input = dialogflow.types.QueryInput(text=text_input)

    response = session_client.detect_intent(
    	session=session,
    	query_input=query_input
    )
    #print(response.query_result)
    intent = response.query_result.intent.display_name
    intent_value = ""
    if len(response.query_result.parameters) > 0:
    	tmp = list(response.query_result.parameters.keys())[0]
    	intent_value = response.query_result.parameters.__getitem__(tmp)
    
    # print('User text       : {}'.format(text))
    # print('Fulfillment text: {}\n'.format(response.query_result.fulfillment_text))
    
    return {
    	'intent': intent,
		'intent_value': intent_value,
		'response': response.query_result.fulfillment_text
	}
 
def handle_intent(intent):
	ip = lookup_instance()
	# handle different intents
	if intent['intent'] == 'Default Welcome Intent':
		# reply to user
		execute_rcon("/say " + intent['response'], ip=ip)
	
	elif intent['intent'] == 'change_weather':
		# change weather
		execute_rcon("/weather {}".format(intent['intent_value']), ip=ip)
		# reply to user
		execute_rcon("/say " + intent['response'], ip=ip)
		
	elif intent['intent'] == 'change_time':
		# change time
		execute_rcon("/time set {}".format(intent['intent_value']), ip=ip)
		# reply to user
		execute_rcon("/say " + intent['response'], ip=ip)
		
	else:
		execute_rcon("/say " + intent['response'], ip=ip)
    
def lookup_instance():
    # find the minecraft vm IP
    compute = googleapiclient.discovery.build('compute', 'v1')
    instances = compute.instances().list(project=PROJECT_ID, zone=ZONE, filter="name=minecraft-vm").execute()
    return instances['items'][0]['networkInterfaces'][0]['accessConfigs'][0]['natIP']

def stop_instance():
    # find the minecraft vm IP
    compute = googleapiclient.discovery.build('compute', 'v1')
    instance_id = compute.instances().list(project=PROJECT_ID, zone=ZONE, filter="name=minecraft-vm").execute()['items'][0]['id']
    return compute.instances().stop(project=PROJECT_ID, zone=ZONE, instance='minecraft-vm').execute()
    

if __name__ == "__main__":
    print('')
