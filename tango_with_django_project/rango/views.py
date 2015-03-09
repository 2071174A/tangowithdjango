from django.shortcuts import render
from rango.models import Category, Page, UserProfile
from rango.forms import CategoryForm
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from datetime import datetime
from rango.forms import PageForm
from rango.bing_search import run_query
from django.template import RequestContext
from django.shortcuts import render_to_response




def index(request):

    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]

    context_dict = {'categories': category_list, 'pages': page_list}

    visits = request.session.get('visits')
    if not visits:
        visits = 1
    reset_last_visit_time = False

    last_visit = request.session.get('last_visit')
    if last_visit:
        last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")

        if (datetime.now() - last_visit_time).days > 0:
            # ...reassign the value of the cookie to +1 of what it was before...
            visits = visits + 1
            # ...and update the last visit cookie, too.
            reset_last_visit_time = True
    else:
        # Cookie last_visit doesn't exist, so create it to the current date/time.
        reset_last_visit_time = True

    if reset_last_visit_time:
        request.session['last_visit'] = str(datetime.now())
        request.session['visits'] = visits
    context_dict['visits'] = visits


    response = render(request,'rango/index.html', context_dict)

    return response


def about(request):
    if request.session.get('visits'):
        count = request.session.get('visits')
    else:
        count = 0

    context_dict = {'boldmessage': "Just like real life!",'visits':count}
    return render(request, 'rango/about.html', context_dict)


def category(request, category_name_slug):
    #initialise dict for searching by POST request
    context_dict = {}
    context_dict['result_list'] = None
    context_dict['query'] = None

    if request.method == 'POST':
        query = request.POST['query'].strip()

        if query:
            result_list = run_query(query) #get results from Bing API
            context_dict['result_list'] = result_list
            context_dict['query'] = query

    try:

        category = Category.objects.get(slug=category_name_slug)
        context_dict['category_name'] = category.name
        pages = Page.objects.filter(category=category).order_by('-views')
        context_dict['pages'] = pages
        context_dict['category'] = category
        context_dict['category_name_slug'] = category_name_slug

    except Category.DoesNotExist:
        pass

    if not context_dict['query']:
        context_dict['query'] = category.name

    return render(request, 'rango/category.html', context_dict)

@login_required()
def add_category(request):
    # A HTTP POST?
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        # Have we been provided with a valid form?
        if form.is_valid():
            # Save the new category to the database.
            form.save(commit=True)

            # Now call the index() view.
            # The user will be shown the homepage.
            return index(request)
        else:
            # The supplied form contained errors - just print them to the terminal.
            print form.errors
    else:
        # If the request was not a POST, display the form to enter details.
        form = CategoryForm()

    # Bad form (or form details), no form supplied...
    # Render the form with error messages (if any).
    return render(request, 'rango/add_category.html', {'form': form})


@login_required
def add_page(request, category_name_slug):

    try:
        cat = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
                cat = None

    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if cat:
                page = form.save(commit=False)
                page.category = cat
                page.views = 0
                page.generate_id()
                page.save()
                # probably better to use a redirect here.
                return category(request, category_name_slug)
        else:
            print form.errors
    else:
        form = PageForm()

    context_dict = {'form':form, 'category': cat}

    return render(request, 'rango/add_page.html', context_dict)

@login_required
def restricted(request):
        return render(request, 'rango/restricted.html', {})

@login_required
def changepassword(request):
    if request.method == 'POST':

        oldPassword = request.POST['oldPassword']
        newPassword = request.POST['newPassword']
        newPasswordConfirm = request.POST['newPasswordConfirm']

        if not authenticate(username = request.user.get_username(), password = oldPassword):
            return render(request, "rango/changepassword.html", {'wrong_info': 'current Password differs'})

        elif newPassword and newPassword != newPasswordConfirm:
            return render(request, "rango/changepassword.html", {'wrong_info':'New password does not match '})

        request.user.set_password(newPassword)
        request.user.save()

        return render(request, "rango/index.html", {'header_message': 'Password changed successfully'})
    else:
        return render(request,"rango/changepassword.html")



def search(request):

    result_list = []

    if request.method == 'POST':
        query = request.POST['query'].strip()

        if query:
            # Run our Bing function to get the results list!
            result_list = run_query(query)

    return render(request, 'rango/search.html', {'result_list': result_list})

def track_url(request):
    context=RequestContext(request)
    page_id=None
    if request.method == 'GET':
        if 'page_id' in request.GET:
            page_id = request.GET['page_id']
            if page_id:
                page=Page.objects.get(id=page_id)
                page.views+=1
                page.save()
                return HttpResponseRedirect(page.url)
    return render_to_response('rango/index.html',context)

def profile(request):
    context_dict = {}
    user = request.user

    try:
        profile = UserProfile.objects.get(user=user)
    except:
        profile = None

    context_dict['user'] = user
    context_dict['userprofile'] = profile
    return render(request, 'rango/profile.html', context_dict)