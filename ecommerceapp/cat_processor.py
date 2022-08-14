from .models import *



def category_renderer(request):
    return {
        'category_all': Category.objects.all(),
        # 'favourite': ProfilePersonal.objects.get(user=request.user),

    }
    print(messags)