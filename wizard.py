import base64
import json
import re
import os
import googleapiclient.discovery
import dialogflow_v2 as dialogflow
import mcrcon

PROJECT_ID = 'minecraft-212921'
ZONE = "us-central1-f"


def log_handler(event, context):
    raw_event = json.loads(base64.b64decode(event['data']).decode('utf-8'))
    raw_message = raw_event['jsonPayload']['message']
    text = re.findall('\]:\s<\w+>\s(.*)\\r', raw_message)[0]
    resp = ask_the_wizard(text)
    handle_intent(resp)

def execute_rcon(cmd, ip):
    # send response
    rcon = mcrcon.MCRcon(ip, "WTFISTHIS")
    rcon.connect()
    response = rcon.command(cmd)
    rcon.disconnect()
    #print(response)

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
    
if __name__ == "__main__":
	ip = lookup_instance()
	execute_rcon('/time 0000',ip)
#	resp = ask_the_wizard('can you make it sunny again?')
#	handle_intent(resp)
#	print(json.dumps(resp, indent=2))
#	
	
#	resp = ask_the_wizard('hello')
#	handle_intent(resp)
#	print(json.dumps(resp, indent=2))


#	resp = detect_intent_texts('minecraft-212921', '123456', 'can you make it rain?')
#	print(resp['intent'])
#	print(resp['intent_value'])
#	print('----')
#	resp = detect_intent_texts('minecraft-212921', '123456', 'will you make it sunny please?')
#	print(resp['intent'])
#	print(resp['intent_value'])
#	print('----')
#	resp = detect_intent_texts('minecraft-212921', '123456', 'hi')
#	print(resp['intent'])
#	print(resp['intent_value'])
#	print('----')