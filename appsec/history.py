from . import auth, db, model
from flask import (
    Blueprint, redirect, render_template, request, session, url_for
)
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import and_

bp = Blueprint('history', __name__)

@bp.route('/history', methods = ['GET'])
def history():
    user = auth.authenticated()
    if user:
        submissions = db.session.query(model.Submission).filter_by(user_id=user.id).all()
        return render_template('history.html',
                               submissions = submissions)
    else:
        return redirect(url_for('index'))

@bp.route('/history/<int:id>')
def submission(id):
    user = auth.authenticated()
    if user:
        try:
            submission = db.session.query(
                model.Submission
            ).filter(and_(
                model.Submission.id == id,
                model.Submission.user_id == user.id
            )).one()
            return render_template('submission.html',
                                   submission = submission,
                                   username = user.username)
        except NoResultFound:
            return redirect(url_for('history.history'))
    else:
        return redirect(url_for('index'))
