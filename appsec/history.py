from . import auth, db, model
from flask import (
    Blueprint, redirect, render_template, request, session, url_for
)
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import and_

bp = Blueprint('history', __name__)

@bp.route('/history', methods = ['GET', 'POST'])
def history():
    user = auth.authenticated()
    if user:
        # An admin is searching for a specific user's submissions
        if request.method == 'POST' and auth.is_admin(user):
            username = request.values['userquery']
            submissions = db.session.query(
                model.Submission
            ).join(model.User).filter(model.User.username == username).all()

        elif request.method == 'GET': # A user navigates to the history page
            query = db.session.query(model.Submission)
            if not auth.is_admin(user):
                query = query.filter_by(user_id = user.id)
            submissions = query.all()

        return render_template('history.html',
                               submissions = submissions,
                               is_admin = auth.is_admin(user))

    return redirect(url_for('index'))

@bp.route('/history/query<int:id>')
def submission(id):
    user = auth.authenticated()
    if user:
        try:
            query = db.session.query(
                model.Submission,
                model.User
            ).join(model.User, model.User.id == model.Submission.user_id)

            if auth.is_admin(user):
                query = query.filter(model.Submission.id == id)
            else:
                query = query.filter(and_(
                    model.Submission.id == id,
                    model.Submission.user_id == user.id
                ))

            submission, sub_user = query.one()
            return render_template('submission.html',
                                   submission = submission,
                                   username = sub_user.username)
        except NoResultFound:
            return redirect(url_for('history.history'))
    else:
        return redirect(url_for('index'))
