from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from models import Category
from models import Page
from forms import CategoryForm
from forms import PageForm
from forms import UserForm, UserProfileForm
from datetime import datetime
from bing_search import run_query
from django.contrib.auth.models import User
from django.shortcuts import redirect

def index(request):

    #obtain the context from the HTTP request
    context = RequestContext(request)

    #retrieve the categories and order them by like and show only 5
    category_list = Category.objects.all()[:5]
    context_dict = {'categories': category_list}

    for category in category_list:
        category.url = decode(category.name)

    #retrieve the pages and order them by views
    page_list = Page.objects.order_by('-views')[:5]

    cat_list = get_category_list()
    for ca in cat_list:
        ca.url = decode(ca.name)

    context_dict['cat'] = cat_list

    #set the category list in a context_dict which is going to be passed to the template
    context_dict['pages'] = page_list

    # Obtain our Response object early so we can add cookie information.
    response = render_to_response('rango/index.html', context_dict, context)
    # Get the number of visits to the site.
    # We use the COOKIES.get() function to obtain the visits cookie.
    # If the cookie exists, the value returned is casted to an integer.
    # If the cookie doesn't exist, we default to zero and cast that.

    if request.session.get('last_visit'):
        # the session has a value for the last visit
        last_visit_time = request.session.get('last_visit')
        visits = request.session.get('visits', 0)

        if(datetime.now() - datetime.strptime(last_visit_time[:-7], "%Y-%m-%d %H:%M:%S")).days > 0:
            request.session['visits'] = visits + 1
            request.session['last_visit'] = str(datetime.now())
    else:
        #the get returns none/null and the session  does not have a value
        request.session['last_visit'] = str(datetime.now())
        request.session['visits'] = 1


    return render_to_response('rango/index.html', context_dict, context)

    #for category in category_list:
    #    category.url = decode(category.name)

    #return render_to_response('rango/index.html', context_dict, context)


def index2(request):
    context = RequestContext(request)
    context_dict = {'boldmessage2' : "This is message send through a python function!"}
    visits = int(request.COOKIES.get('visits', '0'))
    #check if there are visits if not set the count to zero
    if request.session.get('visits'):
        count = request.session.get('visits')
    else:
        count = 0
    context_dict['visits']= count
    cat_list = get_category_list()
    for ca in cat_list:
        ca.url = decode(ca.name)

    context_dict['cat'] = cat_list

    return render_to_response('rango/about.html', context_dict, context)

def category(request, category_name_url):
    #obtain the context from the HTTP request
    context = RequestContext(request)

    category_name = encode(category_name_url)

    cat_list = get_category_list()
    for ca in cat_list:
        ca.url = decode(ca.name)

    #create a dictionary to be passed to the template
    context_dict = {'category_name_url' : category_name_url}

    cat_list = get_category_list()
    for ca in cat_list:
        ca.url = decode(ca.name)

    context_dict['cat'] = cat_list

    try:
        #try to get find a category with the given name from the user
        category = Category.objects.get(name=category_name)

        #retrieve then all associated pages
        pages = Page.objects.filter(category=category)

        #add the results to the template context
        context_dict['pages'] = pages
        context_dict['category'] = category
    except Category.DoesNotExist:
        pass

    if request.method == 'POST':
        query = request.POST['query'].strip()
        if query:
            result_list = run_query(query)
            context_dict['result_list'] = result_list

    return render_to_response('rango/category.html', context_dict, context)

def encode(category_name_urlParam):
        return category_name_urlParam.replace('_', ' ')

def decode(categoryParam):
        return categoryParam.replace(' ', '_')

@login_required
def add_category(request):
    #Get the context from the request. If a user enters a certain url this function will be called
    context = RequestContext(request)
    cat_list = get_category_list()
    for ca in cat_list:
        ca.url = decode(ca.name)
    #if its a HTTP POST
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        # is the form valid?
        if form.is_valid():
            #save the category to the DB
            form.save(commit=True)

            #nov call the index() view
            return index(request)
        else:
        #errors about the supplied form
            print form.errors
    #if there is no POST request just show the form
    else:
        form = CategoryForm()

    return render_to_response('rango/add_category.html', {'form': form, 'cat': cat_list}, context)

@login_required
def add_page(request, category_name_url):
    context = RequestContext(request)

    category_name = decode(category_name_url)
    cat_list = get_category_list()
    for ca in cat_list:
        ca.url = decode(ca.name)
    #if its post method
    if request.method == 'POST':
        form = PageForm(request.POST)

        if form.is_valid():
            page = form.save(commit=False)

            #retrieve the associaited category
            try:
                cat = Category.objects.get(name=category_name)
                page.category = cat
            except Category.DoesNotExist:
                return render_to_response('rango/add_category.html', {}, context)
            #create default value for views
            page.views = 0

            #with this we can save our model instance
            page.save()

            #display the category of the page
            return category(request, category_name_url)
        else:
            print form.errors
    else:
        form = PageForm()

    return render_to_response('rango/add_page.html',
        {'category_name_url': category_name_url,
         'category_name': category_name, 'form' : form, 'cat': cat_list},
        context)


def register(request):

    # Like before, get the request's context.
    context = RequestContext(request)

    # A boolean value for telling the template whether the registration was successful.
    # Set to False initially. Code changes value to True when registration succeeds.
    registered = False

    # If it's a HTTP POST, we're interested in processing form data.
    if request.method == 'POST':
        # Attempt to grab information from the raw form information.
        # Note that we make use of both UserForm and UserProfileForm.
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        # If the two forms are valid...
        if user_form.is_valid() and profile_form.is_valid():
            # Save the user's form data to the database.
            user = user_form.save()

            # Now we hash the password with the set_password method.
            # Once hashed, we can update the user object.
            user.set_password(user.password)
            user.save()

            # Now sort out the UserProfile instance.
            # Since we need to set the user attribute ourselves, we set commit=False.
            # This delays saving the model until we're ready to avoid integrity problems.
            profile = profile_form.save(commit=False)
            profile.user = user

            # Did the user provide a profile picture?
            # If so, we need to get it from the input form and put it in the UserProfile model.
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            # Now we save the UserProfile model instance.
            profile.save()

            # Update our variable to tell the template registration was successful.
            registered = True

        # Invalid form or forms - mistakes or something else?
        # Print problems to the terminal.
        # They'll also be shown to the user.
        else:
            print user_form.errors, profile_form.errors

    # Not a HTTP POST, so we render our form using two ModelForm instances.
    # These forms will be blank, ready for user input.
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()
    cat_list = get_category_list()
    for ca in cat_list:
        ca.url = decode(ca.name)
    # Render the template depending on the context.
    return render_to_response(
            'rango/register.html',
            {'user_form': user_form, 'profile_form': profile_form, 'registered': registered, 'cat': cat_list},
            context)

def user_login(request):
    context = RequestContext(request)
    cat_list = get_category_list()
    for ca in cat_list:
        ca.url = decode(ca.name)
    #if post pull the relevant information
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

    #if its vallid
        user = authenticate(username=username, password=password)

        # if there is a user object the credentials are good
        if user:
            if user.is_active:
                # active and valid go to the homepage
                login(request, user)
                return HttpResponseRedirect('/rango/')
            else:
                return HttpResponseRedirect("Your Rango account is disabled")

        else:
            #bad login details
            print "Invalid login details: {0}, {1}".format(username, password)
            if username == '' or password == '':
                return HttpResponse("Empty password or username entered.")
            else:
                return HttpResponse("Invalid login details supplied. Wrong password or Username")

    # The request is not a HTTP POST, so display the login form.
    # This scenario would most likely be a HTTP GET.
    else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object...
        return render_to_response('rango/login.html', {'cat': cat_list}, context)

@login_required
def restricted(request):
    context = RequestContext(request)
    cat_list = get_category_list()
    for ca in cat_list:
        ca.url = decode(ca.name)

    return render_to_response('rango/restricted.html', {'cat': cat_list}, context)

@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)

    # Take the user back to the homepage.
    return HttpResponseRedirect('/rango/')

def search(request):
    cat_list = get_category_list()
    for ca in cat_list:
        ca.url = decode(ca.name)
    context = RequestContext(request)
    result_list = []

    if request.method == 'POST':
        query = request.POST['query'].strip()

        if query:
            result_list = run_query(query)

    return render_to_response('rango/search.html', {'result_list': result_list, 'cat': cat_list}, context)

#helper function
def get_category_list():
    #retrieve the categories and order them by like and show only 5
    category_list = Category.objects.all()

    return category_list

@login_required
def profile(request):
    context= RequestContext(request)
    cat_list = get_category_list()
    context_dict = {'cat_list': cat_list}
    u= User.objects.get(username=request.user)

    try:
        up = UserProfileForm.objects.get(user=u)
    except:
        up = None
    context_dict['user']=u
    context_dict['userprofile'] =up
    return render_to_response('rango/profile.html', context_dict, context)


def track_url(request):
    context = RequestContext(request)
    page_id = None
    url = '/rango/'

    if request.method == 'GET':
        if 'page_id' in request.GET:
            page_id = request.GET['page_id']
            try:
                page = Page.object.get(id=page_id)
                page.views = page.views + 1
                page.save()
                url = page.url
            except:
                pass
    return redirect(url)

@login_required
def like_category(request):
    context = RequestContext(request)
    cat_id = None
    if request.method == 'GET':
        cat_id = request.get['category_id']

    likes =0
    if cat_id:
        category = Category.objects.get(id=int(cat_id))
        if category:
            likes = category.likes + 1
            category.likes = likes
            category.save()

    return HttpResponse(likes)