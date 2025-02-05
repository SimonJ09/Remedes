# -*- encoding: utf-8 -*-


from apps.home import blueprint
from flask import render_template, request
#from flask_login import login_required
from jinja2 import TemplateNotFound


@blueprint.route('/')
#@login_required
def home():
    return render_template('home/index.html', segment='index')


@blueprint.route('/about')
#@login_required
def about():
    return render_template('home/about.html', segment='index')


@blueprint.route('/contact')
#@login_required
def contact():
    return render_template('home/contact.html', segment='index')


@blueprint.route('/support')
#@login_required
def support():
    return render_template('home/support.html', segment='index')


@blueprint.route('/<template>')
#@login_required
def route_template(template):

    try:

        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, segment=segment)

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500


# Helper - Extract current page name from request
def get_segment(request):

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None
