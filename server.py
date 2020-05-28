from flask import Flask, render_template, request, Response, redirect, url_for
from flask_socketio import SocketIO, send, emit
from datetime import datetime
import os, logging

app = Flask(__name__)
app.config['SECRET_KEY'] = 'vnkdjnfjknfl1232#'
debug_setting = os.environ.get('DEBUG', False)

socketio = SocketIO(app)
userlist = dict()
inactive_list = dict()
sid_mapper = {}
recovery_nodes_mapper = {}

logging.getLogger('socketio').setLevel(logging.ERROR)
logging.getLogger('engineio').setLevel(logging.ERROR)
logging.getLogger('werkzeug').setLevel(logging.ERROR)

logger = logging.getLogger('operations')
fileHandler = logging.FileHandler('operations.log')
formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] - %(message)s')
fileHandler.setFormatter(formatter)
logger.addHandler(fileHandler)
logger.setLevel(logging.INFO)

pingLogger = logging.getLogger('ping')
pingFileHandler = logging.FileHandler('ping.log')
pingFileHandler.setFormatter(formatter)
pingLogger.addHandler(pingFileHandler)
pingLogger.setLevel(logging.INFO)

ch = logging.StreamHandler() 			# Console Log Handler
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)
logger.addHandler(ch)
pingLogger.addHandler(ch)


@socketio.on('ping')
def handle_ping(timestamp):
	NODE_ID = sid_mapper[request.sid]
	pingLogger.info("Received alive ping from node %s", NODE_ID)


############################
#	Operations
############################
def find_neighbors(NODE_ID, inactive_node):
	logger.critical("Node %s disconnected. Looking up neighbors for recovery", NODE_ID)
	neighbors = inactive_node['neighbors'].copy()
	active_neighbors = []
	for neighbor in neighbors:
		if int(neighbor) in userlist:
			neighbor_node = userlist[int(neighbor)]
			if not neighbor_node['secondary_ip']:
				active_neighbors.append(neighbor)
	if active_neighbors:
		elected_id = active_neighbors[0]
		elected_node = userlist.get(int(elected_id))
		logger.info("Found neighbors : %s. Assigning %s for recovery", active_neighbors, elected_id)
		room = elected_node['sid']
		emit("recover", {'disconnected_node': NODE_ID, 'recovery_node': elected_id, 'ip':inactive_node['primary_ip'], 'netmask':inactive_node['primary_netmask'], 'active_neighbors': active_neighbors}, room=room)
	else:
		logger.critical("No active neighbors found")


@socketio.on('update node')
def update_node(json):
	if 'secondary_ip' in json:
		node_id = json['NODE_ID']
		secondary_ip = json['secondary_ip']
		secondary_netmask = json['secondary_netmask']
		userlist[node_id]['secondary_ip'] = secondary_ip
		userlist[node_id]['secondary_netmask'] = secondary_netmask
		logger.info("Recovery Success by node %s with new Virtual IP as: %s. Updating IP in records", node_id, userlist[node_id]['secondary_ip'])
		disconnected_node = json['disconnected_node']
		recovery_nodes_mapper.update({disconnected_node: node_id})
		print(recovery_nodes_mapper)
	else:
		disconnected_node = json['disconnected_node']
		active_neighbors = json['active_neighbors']
		recovery_ip = json['ip']
		active_neighbors.remove(str(json['recovery_node']))
		logger.warning("recovery failed. Refined active list is: %s", json['active_neighbors'])
		if active_neighbors:
			recovery_node_id = active_neighbors[0]
			logger.info("Assigning %s for recovery", recovery_node_id)
			recovery_node = userlist[int(recovery_node_id)]
			room = recovery_node['sid']
			emit("recover", {'disconnected_node': disconnected_node, 'recovery_node': recovery_node_id, 'ip':json['ip'], 'netmask':json['netmask'], 'active_neighbors': active_neighbors}, room=room)
		else:
			logger.critical("All failover recovery attempts failed")


@socketio.on('join')
def welcome_call(json):
	json['sid'] = request.sid
	connection_id = int(json['NODE_ID'])
	# connection_id = json['mac']
	sid_mapper.update({request.sid: connection_id})
	if connection_id in inactive_list.keys():
		inactive_list.pop(connection_id)
		userlist[connection_id] = json

		logger.info('Node {0} has rejoined with session ID: {1}'.format(connection_id, request.sid))
		if connection_id in recovery_nodes_mapper:
			logger.warning('Attempting restoration of IP...')
			recovery_node_id = recovery_nodes_mapper[connection_id]
			recovery_node = userlist[int(recovery_node_id)]
			room = recovery_node['sid']
			emit("restore", {'restore_node': connection_id, 'ip':json['ip']}, room=room)
		return
	logger.info('Node {0} has joined with session ID: {1}'.format(connection_id, request.sid))
	userlist[connection_id] = json
	return


@socketio.on('disconnect')
def disconnected():
	NODE_ID = sid_mapper[request.sid]
	inactive_node =	userlist.get(NODE_ID)
	find_neighbors(NODE_ID, inactive_node)
	inactive_list.update({NODE_ID: inactive_node})
	userlist.pop(NODE_ID)


""" 
	Flask server methods. Use brower to access each of these methods.
	'/' 		=> index method: Displays lists of active nodes as well as inactive nodes.
	'/clear' 	=> clear method. used to clear all inactive node records from the system memeory.
"""
@app.route('/')
def index():
	# emit('my event', {'title': "Ping to all users", 'hello': "received slack message"}, namespace='/', broadcast=True)
	registered_users = {'active': userlist, 'inactive': inactive_list, 'recovery mapper': recovery_nodes_mapper}
	return registered_users


@app.route('/clear')
def clear_lists():
	flask_logger = logging.getLogger('werkzeug')
	flask_logger.error("Deleting inactive Nodes")
	inactive_list.clear()
	return redirect(url_for("index"))


if __name__ == '__main__':
	logger = logging.getLogger("operations")
	pingLogger = logging.getLogger("ping")

	logger.info("recovery server active")
	socketio.run(app, debug = debug_setting)
