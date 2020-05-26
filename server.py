from flask import Flask, render_template, request, Response
from flask_socketio import SocketIO, send, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'vnkdjnfjknfl1232#'
socketio = SocketIO(app, logger=True, engineio_logger=True)
userlist = dict()
inactive_list = dict()
TGREEN = '\033[32m' # Green Text
TLOAD = '\033[33m'
TRED = '\033[31m' # Red Text
ENDC = '\033[m'
sid_mapper = {}


def messageReceived(data):
	print('message was received!!!')
	print(data)


############################
#	Operations
############################
def find_neighbors(NODE_ID, inactive_node):
	print(TRED + "Node " + str(NODE_ID) + " disconnected", ENDC)
	print(TLOAD + "Looking up neighbors...", ENDC)
	neighbors = inactive_node['neighbors'].copy()
	active_neighbors = []
	for neighbor in neighbors:
		if int(neighbor) in userlist:
			print("neighbor "+ neighbor + "is active")
			neighbor_node = userlist[int(neighbor)]
			if neighbor_node['secondary_ip']:
				print(neighbor_node['secondary_ip'])
				print("neighbor "+ neighbor + " unable to recover")
			else:
				active_neighbors.append(neighbor)
	if active_neighbors:
		print(TGREEN + "Found neighbors :")
		for neighbor in active_neighbors:
			print(neighbor, end=' ')
		print("\n\n", ENDC)
		elected_id = active_neighbors[0]
		elected_node = userlist.get(int(elected_id))
		print("Assigning " + elected_id + " for recovery")
		room = elected_node['sid']
		emit("recover", {'recovery_node': NODE_ID, 'ip':inactive_node['primary_ip']}, room=room, callback=update_node)
	else:
		print(TRED + "No active neighbors", ENDC)

def update_node(status, node_id, new_virtual_ip):
	if status:
		print(TGREEN + "updating secondary IP of " + userlist['node_id'] + "to " + new_virtual_ip, ENDC)
		userlist['node_id']['secondary_ip'] = new_virtual_ip


@socketio.on('join')
def welcome_call(json):
	json['sid'] = request.sid
	connection_id = int(json['NODE_ID'])
	# connection_id = json['mac']
	sid_mapper.update({request.sid: connection_id})
	if connection_id in inactive_list.keys():
		inactive_list.pop(connection_id)
		userlist[connection_id] = json

		print(TGREEN + '{0} has rejoined  with data: {1}'.format(request.sid, json), ENDC)
		return True
	# emit('join call', {'message': '{0} has joined'.format(request.sid)}, broadcast=True)
	print(TGREEN + '{0} has joined  with data: {1}'.format(request.sid, json), ENDC)
	userlist[connection_id] = json
	return True


@socketio.on('disconnect')
def disconnected():
	NODE_ID = sid_mapper[request.sid]
	inactive_node =	userlist.get(NODE_ID)
	find_neighbors(NODE_ID, inactive_node)
	inactive_list.update({NODE_ID: inactive_node})
	userlist.pop(NODE_ID)


@socketio.on('ping')
def handle_app_ping():
	NODE_ID = sid_mapper[request.sid]
	print(TGREEN + 'received ping from node: '+ str(NODE_ID), ENDC)


############################## 
#	Flask server methods
##############################
@app.route('/')
def index():
	# emit('my event', {'title': "Ping to all users", 'hello': "received slack message"}, namespace='/', broadcast=True)
	registered_users = {'active': userlist, 'inactive': inactive_list}
	return registered_users


@app.route('/clear')
def clear_lists():
	userlist.clear()
	inactive_list.clear()
	return "Success"


if __name__ == '__main__':
	print(TGREEN + "recovery server active", ENDC)
	socketio.run(app)
