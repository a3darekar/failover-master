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
			neighbor_node = userlist[int(neighbor)]
			if not neighbor_node['secondary_ip']:
				active_neighbors.append(neighbor)
	if active_neighbors:
		print(TGREEN + "Found neighbors :")
		for neighbor in active_neighbors:
			print(neighbor, end=' ')
		print(ENDC)
		elected_id = active_neighbors[0]
		elected_node = userlist.get(int(elected_id))
		print("Assigning " + elected_id + " for recovery")
		room = elected_node['sid']
		emit("recover", {'disconnected_node': NODE_ID, 'recovery_node': elected_id, 'ip':inactive_node['primary_ip'], 'active_neighbors': active_neighbors}, room=room)
	else:
		print(TRED + "No active neighbors", ENDC)


@socketio.on('update node')
def update_node(json):
	if 'secondary_ip' in json:
		node_id = json['NODE_ID']
		secondary_ip = json['secondary_ip']
		print(TGREEN + "updating secondary IP of " + str(node_id) + "to " + secondary_ip, ENDC)
		userlist[node_id]['secondary_ip'] = secondary_ip
		print(TGREEN + "Recovery Success with new Virtual IP as: " + userlist[node_id]['secondary_ip'], ENDC)
	else:
		active_neighbors = json['active_neighbors']
		recovery_ip = json['ip']
		print(active_neighbors)
		active_neighbors.remove(str(json['recovery_node']))
		print(TRED + "recovery failed", ENDC)
		print(json['active_neighbors'])
		if active_neighbors:
			new_recovery_node = active_neighbors[0]
			print("Assigning " + new_recovery_node + " for recovery")
			emit("recover", {'disconnected_node': new_recovery_node, 'ip':json['ip'], 'active_neighbors': active_neighbors}, room=room)
		else:
			print(TRED + "All failover attempts failed.", ENDC)


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
	print(TLOAD + 'received ping from node: '+ str(NODE_ID), ENDC)


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
