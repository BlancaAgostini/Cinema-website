from flask import Flask

def create_app():
    app = Flask(__name__)
    
    #app.config['STRIPE_PUBLIC_KEY'] = 'pk_live_51LLwkYKKfRH6nq6F6TRng1U2Nl80INiUdFhBzMU8BT733SEeM2IzbzLdA3fQNPT5coEkk4FAsOK0o093DQqHP9Ew00jwXFWpYn'
    #app.config['STRIPE_SECRET_KEY'] = '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'
    app.config['STRIPE_PUBLIC_KEY'] = 'pk_test_51LLwkYKKfRH6nq6FU8q2eYim5DXwgCEBVMd31w9hAX3Xbtv8ZUjypHUztFQitLWcnc6yWZjBLYv07ntIPPnhdSZB00BKKmTvP1'
    app.config['STRIPE_SECRET_KEY'] = 'sk_test_51LLwkYKKfRH6nq6FYChFWFAS1AtNd1FcwNEF8gDFoZeCLUHmU1QnPu3MeAq58cKgPPs1xNBRRJd0Gg1nhhbl5URs00lfFe36AX'

    from .views import views
    from .auth import auth
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    return app

