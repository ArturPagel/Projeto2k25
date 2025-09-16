from flask import Flask, render_template, request, redirect, url_for, session, flash, render_template_string
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import mysql.connector
import os
from pony.orm import Database, Required, Optional, Set, PrimaryKey, db_session, commit, select

db = Database()
app = Flask(__name__)
app.secret_key = "gremio"