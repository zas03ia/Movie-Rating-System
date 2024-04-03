from django.shortcuts import redirect

def user(view_func):
    def wrapper(request, *args, **kwargs):
        if request.session.get('user'):
            # User is authenticated, allow access to the view
            return view_func(request, *args, **kwargs)
        else:
            return redirect('home')
            
    return wrapper