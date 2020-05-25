from flask import Flask, render_template, request, Response
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'vnkdjnfjknfl1232#'
socketio = SocketIO(app)
userlist = dict()
inactive_list = dict()
TGREEN =  '\033[32m' # Green Text
TRED =  '\033[31m' # Red Text
ENDC = '\033[m'

sid_mapper = {}

def messageReceived(data):
	print('message was received!!!')
	print(data)


@socketio.on('join')
def welcome_call(json):
	json['app_id'] = request.sid 					# change to ip in prod.
	connection_id = json['pid']
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


@socketio.on('convo')
def handle_my_custom_event(json):
	print(TGREEN + 'received event from sid: '+ request.sid)
	
	print('convo', json, ENDC)


@socketio.on('disconnect')
def disconnected():
	print(TRED + request.sid + " disconnected", ENDC)
	connection = sid_mapper[request.sid]
	inactive_node = userlist[connection]
	inactive_list.update({connection: inactive_node})
	userlist.pop(connection)


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
