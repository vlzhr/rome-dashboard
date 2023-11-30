from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import daemon
from flask import Flask, jsonify, render_template
import atexit
import os
from service import prettify_number, prettify_apr, pretty_time, pretty_address, pretty_balances, get_pretty_apy


sched = BackgroundScheduler()

@sched.scheduled_job('interval', minutes=10, next_run_time=datetime.now())
def scheduled_job():
    daemon.update_rome_data()


app = Flask(__name__)


@app.route('/')
def index():
    last_stats = daemon.get_last_stats()
    return render_template("dashboard.html", d=last_stats["stats"], c=last_stats["constants"],
                           pretty=prettify_number, pretty_apr=prettify_apr, pretty_time=pretty_time,
                           get_pretty_apy=get_pretty_apy,
                           pretty_address=pretty_address, pretty_balances=pretty_balances)


@app.route('/api')
def api():
    return jsonify(daemon.get_last_stats())


sched.start()
app.run(port=int(os.environ.get('PORT', 5001)), host='0.0.0.0', debug=False)

# Shut down the scheduler when exiting the app
atexit.register(lambda: sched.shutdown())
