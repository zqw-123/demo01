import os
import sys
from pathlib import Path

from flask import Flask
def create_app(test_config=None):
    # create and configure the app

    # __name__ 是当前 Python 模块的名称。应用需要知道在哪里设置路径， 使用 __name__ 是一个方便的方法。
    # instance_relative_config=True 告诉应用配置文件是相对于 instance folder 的相对路径。
    def resource_path_convert(relative_path):
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)
    # app = Flask(__name__,
    #    template_folder=resource_path_convert('templates'),
    #    static_folder=resource_path_convert('static'),
    #    static_url_path='/static',
    #    instance_relative_config=True)
    
    app = Flask(__name__,
        template_folder='templates',
        static_folder='static',
        static_url_path='/static',
        instance_relative_config=True) 
    
    # 设置一个应用的缺省配置
    app.config.from_mapping(
        # 是被 Flask 和扩展用于保证数据安全的。在开发过程中， 为了方便可以设置为 'dev' ，但是在发布的时候应当使用一个随机值来 重载它。
        SECRET_KEY='dev'
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        if not os.path.isdir(app.instance_path):
            os.makedirs(app.instance_path)
    except OSError as e:
        print(e)

    try:
        import route_blue
    except:
        sys.path.append(str(Path('.').resolve()))
        import route_blue
    app.register_blueprint(route_blue.bp)

    
    # make url_for('index') == url_for('blog.index')
    # in another app, you might define a separate main index here with
    # app.route, while giving the blog blueprint a url_prefix, but for
    # the tutorial the blog will be the main index
    app.add_url_rule("/", endpoint="index")
    
    
    
    import webbrowser
    webbrowser.open("http://127.0.0.1:5000")

    return app
    
if __name__ == '__main__':
    app = create_app()
    from wsgiref.simple_server import make_server
    server = make_server('127.0.0.1', 5000, app)
    server.serve_forever()
    app.run()