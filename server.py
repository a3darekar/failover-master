from flask import Flask, render_template, request, Response, redirect, url_for, jsonify
from flask_socketio import SocketIO, send, emit
from datetime import datetime
import os, logging, time
from logger_config import logger, pingLogger

app = Flask(__name__)
app.config['SECRET_KEY'] = 'vnkdjnfjknfl1232#'

socketio = SocketIO(app)
userlist = {}
inactive_list = {}
sid_mapper = {}
recovery_node_mapper = {}
recovery_init_time = {}

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
		logger.info("Recovery Success by node %s with new Virtual IP as: %s. Updating records...", node_id, userlist[node_id]['secondary_ip'])
		disconnected_node = json['disconnected_node']
		recovery_time_delta = time.time() - recovery_init_time[disconnected_node]
		logger.warning("Total time taken for node recovery: %.2f seconds", recovery_time_delta)
		recovery_node_mapper.update({disconnected_node: node_id})
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


@socketio.on('restore node')
def restore_node(json):
	if json['status']:
		node_id = json['NODE_ID']
		secondary_ip = json['secondary_ip']
		secondary_netmask = json['secondary_netmask']
		userlist[node_id]['secondary_ip'] = secondary_ip
		userlist[node_id]['secondary_netmask'] = secondary_netmask
		logger.info("Recovery Success by node %s with new Virtual IP as: %s. Updating records...", node_id, userlist[node_id]['secondary_ip'])
		restored_node = json['restore_node']
		recovery_time_delta = time.time() - recovery_init_time[restored_node]
		logger.warning("Total time taken for restoring IP: %.2f seconds", recovery_time_delta)
		recovery_node_mapper.pop(int(restored_node))
	else:
		logger.critical("IP restoration attempts failed")


@socketio.on('join')
def welcome_call(json):
	json['sid'] = request.sid
	connection_id = int(json['NODE_ID'])
	sid_mapper.update({request.sid: connection_id})
	if connection_id in inactive_list.keys():
		inactive_list.pop(connection_id)
		userlist[connection_id] = json

		logger.info('Node {0} has rejoined with session ID: {1}'.format(connection_id, request.sid))
		if connection_id in recovery_node_mapper:
			logger.warning('Attempting restoration of IP...')
			recovery_init_time[connection_id] = time.time()
			recovery_node_id = recovery_node_mapper[connection_id]
			recovery_node = userlist[int(recovery_node_id)]
			room = recovery_node['sid']
			emit("restore", {'restore_node': connection_id}, room=room)
		return
	logger.info('Node {0} has joined with session ID: {1}'.format(connection_id, request.sid))
	userlist[connection_id] = json
	return


@socketio.on('disconnect')
def disconnected():
	NODE_ID = sid_mapper[request.sid]
	for k in recovery_node_mapper.copy():
		if recovery_node_mapper[k] == NODE_ID:
			del recovery_node_mapper[k]
	inactive_node =	userlist.get(NODE_ID)
	recovery_init_time[NODE_ID] = time.time()
	find_neighbors(NODE_ID, inactive_node)
	inactive_list.update({NODE_ID: inactive_node})
	userlist.pop(NODE_ID)


""" 
	Flask server methods. Use brower to access each of these methods.
	'/' 		=> index method: Displays lists of active nodes as well as inactive nodes.
	'/clear' 	=> clear method. used to clear all inactive node records from the system memeory.
"""
@app.route('/json')
def index():
	registered_users = {'active': userlist, 'inactive': inactive_list, 'recovery_mapper': recovery_node_mapper}
	return jsonify(registered_users)

@app.route('/')
def monitor():
	context = {'active': userlist, 'inactive': inactive_list, 'recovery_mapper': recovery_node_mapper}
	context = jsonify(context)
	return render_template('index.html', context = context)


@app.route('/clear')
def clear_lists():
	flask_logger = logging.getLogger('werkzeug')
	flask_logger.error("Deleting inactive Nodes")
	inactive_list.clear()
	return redirect(url_for("index"))

if __name__ == "__main__":
	gunicorn_logger = logging.getLogger('gunicorn.error')
	logger.handlers = gunicorn_logger.handlers
	logger.info("recovery server active")
	socketio.run(app)