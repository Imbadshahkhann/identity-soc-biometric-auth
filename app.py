from flask import Flask, render_template, jsonify, request
import database

app = Flask(__name__)

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/api/stats')
def api_stats():
    logs = database.get_auth_logs()
    users = database.get_all_users()
    
    total_users = len(users)
    successful_logins = len([log for log in logs if log['status'] == 'SUCCESS'])
    failed_logins = len([log for log in logs if 'FAIL' in log['status']])
    
    # Calculate suspicious activity
    suspicious_users = set()
    fail_counts = {}
    for log in logs:
        if 'FAIL' in log['status']:
            username = log['username']
            fail_counts[username] = fail_counts.get(username, 0) + 1
            if fail_counts[username] > 3:
                suspicious_users.add(username)
                
    recent_logs = logs[:15]
    graph_labels = [log['timestamp'].split()[1] if ' ' in log['timestamp'] else log['timestamp'] for log in recent_logs][::-1]
    graph_data = [1 if log['status'] == 'SUCCESS' else 0 for log in recent_logs][::-1]
    
    return jsonify({
        'total_users': total_users,
        'successful_logins': successful_logins,
        'failed_attempts': failed_logins,
        'suspicious_activity': list(suspicious_users),
        'graph_labels': graph_labels,
        'graph_data': graph_data,
        'logs': logs[:50]
    })

@app.route('/api/delete_user', methods=['POST'])
def api_delete_user():
    data = request.json
    username = data.get('username')
    if not username:
        return jsonify({'success': False, 'error': 'No username provided'}), 400
        
    success = database.delete_user(username)
    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': 'User not found or deletion failed'}), 404

@app.route('/api/users')
def api_users():
    users = database.get_all_users()
    return jsonify({'users': users})

if __name__ == '__main__':
    database.init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
