from flask import Blueprint, render_template

errors = Blueprint('errors', __name__)


@errors.app_errorhandler(404)
def error_404(error):
    """Routing to custom 404 page in case of 404 error"""
    return render_template('errors/404.html'), 404

@errors.app_errorhandler(403)
def error_403(error):
    """Routing to custom 403 page in case of 403 error"""
    return render_template('errors/403.html'), 403

@errors.app_errorhandler(500)
def error_500(error):
    """Routing to custom 500 page in case of 500 error"""
    return render_template('errors/500.html'), 500

