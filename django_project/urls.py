from django.contrib import admin
from django.urls import path, include
from django.http import FileResponse, HttpResponseNotFound
import os

# ── Path to your project root folder ──
FRONTEND_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)

def serve_file(file_path, content_type='text/html'):
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), content_type=content_type)
    return HttpResponseNotFound(f'File not found: {file_path}')

# ── Serve index.html for home ──
def serve_index(request):
    return serve_file(os.path.join(FRONTEND_DIR, 'index.html'))

# ── Also serve index.html when someone types index.html directly ──
def serve_index_direct(request):
    return serve_file(os.path.join(FRONTEND_DIR, 'index.html'))

# ── Serve any page inside pages/ folder ──
def serve_page(request, page_name):
    return serve_file(os.path.join(FRONTEND_DIR, 'pages', page_name))

# ── Serve CSS files ──
def serve_css(request, file_name):
    return serve_file(
        os.path.join(FRONTEND_DIR, 'css', file_name),
        'text/css'
    )

# ── Serve JS files ──
def serve_js(request, file_name):
    return serve_file(
        os.path.join(FRONTEND_DIR, 'js', file_name),
        'application/javascript'
    )

# ── Serve image files ──
def serve_image(request, file_name):
    ext = file_name.lower().split('.')[-1]
    types = {
        'jpg': 'image/jpeg', 'jpeg': 'image/jpeg',
        'png': 'image/png',  'gif':  'image/gif',
        'svg': 'image/svg+xml', 'ico': 'image/x-icon',
        'webp': 'image/webp'
    }
    return serve_file(
        os.path.join(FRONTEND_DIR, 'images', file_name),
        types.get(ext, 'image/jpeg')
    )

urlpatterns = [
    # ── Django admin ──
    path('admin/', admin.site.urls),

    # ── API endpoints ──
    path('api/', include('travel_app.urls')),

    # ── Home page ──
    path('',             serve_index,        name='home'),
    path('index.html',   serve_index_direct, name='home_direct'),

    # ── All other pages ──
    path('pages/<str:page_name>', serve_page,  name='page'),
    path('css/<str:file_name>',   serve_css,   name='css'),
    path('js/<str:file_name>',    serve_js,    name='js'),
    path('images/<str:file_name>',serve_image, name='image'),
]