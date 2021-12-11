"""Views for Personal Training App"""
import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db import IntegrityError
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator

from .models import User, Session, Setgroup, Set, Exercise, Routine
from .forms import SessionForm, ExerciseForm, RoutineForm

# NOTE: login_view, logout_view, and register are informed by CS50w projects' source code
# https://cs50.harvard.edu/web/2020/

@login_required
def index(request, pnum=1):
    """Home page only visible if user logged in"""
    # if user is staff, return all workouts
    if request.user.is_staff:
        sessions = Session.objects.all().order_by('-pk')
    else:
        # if user is client, return all workouts for this client
        sessions = Session.objects.filter(routine__client=request.user).order_by('-pk')
    # helper function below: return queryset list of 10
    data = pagehelper(sessions, pnum)
    return render(request, "train/index.html", {
        "data": data
    })

def login_view(request):
    """login view for non-authenticated users"""
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return redirect("index")
        else:
            return render(request, "train/login.html", {
                "message": "Invalid username and/or password."
            })

    # GET request method: display login form
    return render(request, "train/login.html")

def logout_view(request):
    """log out"""
    logout(request)
    return redirect("index")

def register(request):
    """register a new User"""
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        first = request.POST["first"]
        last = request.POST["last"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "train/register.html", {
                "message": "Passwords must match."
            })
        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password,
                                            first_name=first, last_name=last)
            user.save()
        except IntegrityError:
            return render(request, "train/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return redirect("index")
    # else request method GET
    return render(request, "train/register.html")

@staff_member_required(login_url="/login")
def newsession(request):
    """Trainer starts a new workout session"""
    # request method POST, create new workout session
    if request.method == "POST":
        form = SessionForm(request.POST)
        if form.is_valid:
            session = form.save()
            # create new Setgroup for each exercise in this routine
            allexercises = session.routine.exercises.all()
            for exercise in allexercises:
                Setgroup.objects.create(exercise=exercise, session=session)
            pk = session.pk
            return redirect("sessionview", pk=pk)

        # if invalid form - return form to user
        return render(request, "train/newsession.html", {
            "form": form
        })
    # if request method is GET, display form
    sessionform = SessionForm()
    return render(request, "train/newsession.html", {
        'form': sessionform
    })

@staff_member_required(login_url="/login")
def sessionview(request, pk):
    """A form to create sets for a specific workout session"""
    try:
        session = Session.objects.get(pk=pk)
    except Session.DoesNotExist:
        # if requested session doesn't exist, return error message
        return render(request, "train/error.html", {
            "message": "That workout session does not exist."
        })
    # all sets for each Setgroup
    setgroups = Setgroup.objects.filter(session=session)

    # if sets have already been logged for this session, redirect to EDIT page
    for group in setgroups:
        if Set.objects.filter(setgroup=group):
            request.session['sessionpk'] = pk
            return redirect("editsession")

    # if previous session using this routine exists, include
    try:
        prevsession = session.get_previous_by_timestamp(routine=session.routine)
    except Session.DoesNotExist:
        prevsession = None
    # exclude all the exercises that already have setgroups added to this Session
    exercises = Exercise.objects.exclude(setgroups__in=(Setgroup.objects.filter(session=session)))

    return render(request, "train/newsession2.html", {
        "setgroups": setgroups,
        "n": range(1, 4),
        "prevsession": prevsession,
        "session": session,
        "exercises": exercises
    })

@staff_member_required(login_url="/login")
def editsession(request):
    """Edit a previously logged session"""
    # if request method GET with session selected (either from template or newsession redirect)
    if 'sessionpk' in request.session or 'sessionpk' in request.GET:
        pk = request.GET.get('sessionpk', False) or request.session['sessionpk']
        # clear this value from the session so not passed to future pages
        if 'sessionpk' in request.session:
            del request.session['sessionpk']
        # get the Session instance from request
        try:
            session = Session.objects.get(pk=pk)
        except Session.DoesNotExist:
            return render(request, "train/error.html", {
                "message": "That workout session does not exist."
            })
        # exclude all the exercises that already have setgroups associated w this Session
        exercises = Exercise.objects.exclude(setgroups__in=(
                    Setgroup.objects.filter(session=session)))

        return render(request, "train/editsession2.html", {
            "session": session,
            "exercises": exercises
        })
    # if request method GET and no session selected
    clients = User.objects.filter(is_staff=False)
    return render(request, "train/editsession1.html", {
        "clients": clients
    })

@staff_member_required(login_url="/login")
def newroutine(request):
    """Create a new Routine"""
    if request.method == "POST":
        form = RoutineForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("routinelist")
        # if invalid form, return to user
        return render(request, "train/newroutine.html", {
            "form": form
        })
    # if request method GET
    form = RoutineForm()
    return render(request, "train/newroutine.html", {
        "form": form
    })

@staff_member_required(login_url="/login")
def routinelist(request):
    """Page that shows list of all routines"""
    routines = Routine.objects.all().order_by('-pk')
    return render(request, "train/routinelist.html", {
        "routines": routines
    })

@staff_member_required(login_url="/login")
def editroutine(request, pk):
    """Update a specific routine that's already been created"""
    if request.method == "POST":
        routine = Routine.objects.get(pk=pk)
        form = RoutineForm(request.POST, instance=routine)
        if form.is_valid():
            form.save()
            return redirect("routinelist")
        # if invalid form: return form to user
        return render(request, "train/editroutine.html", {
            "form": form,
            "routine": routine
        })
    # if GET request, prefill RoutineForm with previously saved info
    routine = Routine.objects.get(pk=pk)
    form = RoutineForm(instance=routine)
    # request method GET: show pre-filled routine form
    return render(request, "train/editroutine.html", {
        "form": form,
        "routine": routine
    })

@staff_member_required(login_url="/login")
def exerciseview(request):
    """Add a new exercise"""
    exerciselist = Exercise.objects.all().order_by('name')
    if request.method == "POST":
        form = ExerciseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("exerciseview")

        # if invalid form - return form to user
        return render(request, "train/exercises.html", {
            "form": form,
            "exerciselist": exerciselist
        })
    # else if request method GET
    form = ExerciseForm()
    return render(request, "train/exercises.html", {
        'form': form,
        "exerciselist": exerciselist
    })

@staff_member_required(login_url="/login")
def charts(request, pnum=1):
    """Display all previous sessions for any client"""
    users = User.objects.filter(is_staff=False)
    # hidden page number from pagination form, if exists
    if 'pnum' in request.GET:
        pnum = int(request.GET['pnum'])
    # if a specific client was selected from dropdown
    if 'client' in request.GET:
        client = request.GET['client']
        client = User.objects.get(pk=client)
        sessions = Session.objects.filter(routine__client=client).order_by('-pk')
        data = pagehelper(sessions, pnum)
        return render(request, "train/charts.html", {
                'users': users,
                'data': data,
                'client': client.pk
            })
    # if no client was selected from dropdown or pagination
    sessions = Session.objects.all().order_by('-pk')
    data = pagehelper(sessions, pnum)
    return render(request, "train/charts.html", {
            'users': users,
            'data': data
        })


# CLIENT VIEWS
##############

@login_required
def clientroutines(request, pnum=1):
    """ Client page to view routines and past workouts for specific routines"""
    client = request.user
    if client.is_staff:
        return redirect("routinelist")
    routines = Routine.objects.filter(client=client, archived=False)
    # if form contains pnum (from paginate)
    if 'pnum' in request.GET:
        pnum = int(request.GET['pnum'])
    # if form contains routine PK (from paginate or dropdown)
    if 'routine' in request.GET:
        routinepk = request.GET['routine']
        routineobj = Routine.objects.get(pk=routinepk)
        sessions = Session.objects.filter(routine=routineobj).order_by('-pk')
        data = pagehelper(sessions, pnum)
        return render(request, "train/clientroutines.html", {
            "routines": routines,
            "data": data,
            "routineobj": routineobj
        })
    # if no page number or routine selected: dropdown to select an active routine
    routines = Routine.objects.filter(client=client, archived=False)
    sessions = Session.objects.filter(routine__client=client).order_by('-pk')
    data = pagehelper(sessions, pnum)
    return render(request, "train/clientroutines.html", {
        "routines": routines,
        "data": data
    })


@login_required
def clientprogress(request):
    """ Client page to view their strength progress on specific exercises"""
    client = request.user
    if client.is_staff:
        return redirect("charts")
    # all exercises this client has ever completed (e.g. has finished Setgroups of)
    exercises = Exercise.objects.filter(setgroups__session__routine__client=client).distinct()
    return render(request, "train/clientprogress.html", {
        "exercises": exercises
    })

# API ROUTES
############

@csrf_exempt
def progressAPI(request, exercise):
    """API route to get a client's history of Sets for a requested exercise"""
    client = request.user
    # all sets in setgroups in sessions in routines belonging to this user
    sets = Set.objects.filter(setgroup__session__routine__client=client,
                              setgroup__exercise=exercise).order_by('-pk')
    return JsonResponse([setobj.serialize() for setobj in sets], safe=False)


@csrf_exempt
def postset(request):
    """API route to post a new set"""
    # posting a new set must be POST
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    # get data from json
    data = json.loads(request.body)
    grouppk = data.get("grouppk")
    setnum = data.get("setnum")
    weight = data.get("weight")
    time = data.get("time")

    try:
        setgroup = Setgroup.objects.get(pk=grouppk)
    except Setgroup.DoesNotExist:
        return JsonResponse({"error": "Setgroup does not exist."}, status=400)
    try:
        # see if there is already a set with this setnum for this setgroup
        setobj = Set.objects.get(setgroup=(Setgroup.objects.get(pk=grouppk)), setnum=setnum)
        # if so, UPDATE this set instead of create new
        setobj.weight = weight
        setobj.time = time
        setobj.save()
        return JsonResponse({"message": "Set updated."}, status=201)
    # if Set does't yet exist, save new set, return success message
    except Set.DoesNotExist:
        newset = Set(setgroup=setgroup, setnum=setnum, weight=weight, time=time)
        newset.save()
        return JsonResponse({"message": "Set saved."}, status=201)

@csrf_exempt
def setgroupinfo(request):
    """API route to add/update a Setgroup's note and exercise order"""
    # adding a note must be PUT
    if request.method != "PUT":
        return JsonResponse({"error": "PUT request required."}, status=400)
    # data from json
    data = json.loads(request.body)
    grouppk = data.get("grouppk")
    order = data.get("order")
    note = data.get("note")
    try:
        setgroup = Setgroup.objects.get(pk=grouppk)
    except Setgroup.DoesNotExist:
        return JsonResponse({"error": "Setgroup does not exist."}, status=400)
    # save Setgroup order and note, return success message
    setgroup.order = order
    setgroup.note = note
    setgroup.save()
    return JsonResponse({"message": "Note saved."}, status=201)

@csrf_exempt
def deletex(request):
    """API route to delete a whole Exercise from the database"""
    if request.method != "DELETE":
        return JsonResponse({"error": "DELETE request required."}, status=400)
    # data from json
    data = json.loads(request.body)
    pk = data.get("exercise")
    # try to delete this exercise
    try:
        Exercise.objects.get(pk=pk).delete()
    except Exercise.DoesNotExist:
        return JsonResponse({"error": "Exercise does not exist."}, status=400)
    return JsonResponse({"message": "Exercise deleted."}, status=201)

@csrf_exempt
def deletesession(request, sessionpk):
    """API route to delete a Session"""
    if request.method != "DELETE":
        return JsonResponse({"error": "DELETE request required."}, status=400)
    try:
        # delete this session: all sets and setgroups should CASCADE
        Session.objects.get(pk=sessionpk).delete()
    except Session.DoesNotExist:
        JsonResponse({"error": "Session does not exist."}, status=400)
    return JsonResponse({"message": "Session deleted."}, status=201)

@csrf_exempt
def checkcomplete(request, sessionpk):
    """API route to complete a Session"""
    try:
        session = Session.objects.get(pk=sessionpk)
    except Session.DoesNotExist:
        return JsonResponse({"error": "Session does not exist."}, status=400)
    # all setgroups associated with this session
    setgroups = Setgroup.objects.filter(session=session)
    # count how many Setgroups for this session have no Sets logged
    emptygroups = 0
    for setgroup in setgroups:
        if Set.objects.filter(setgroup=setgroup).exists():
            continue
        emptygroups += 1
    # if all the setgroups are empty: return "no sets" (session will be deleted)
    if emptygroups == setgroups.count():
        return JsonResponse({"message": "no sets"}, status=201)
    # if sets are logged, return the number of empty Setgroups
    return JsonResponse({"message": "has sets", "emptygroups": emptygroups}, status=201)

@csrf_exempt
def deleteempties(request, sessionpk):
    """Delete all empty Setgroups from a Session when it's completed"""
    try:
        session = Session.objects.get(pk=sessionpk)
    except Session.DoesNotExist:
        return JsonResponse({"error": "Session does not exist."}, status=400)
    # all setgroups associated with this session
    setgroups = Setgroup.objects.filter(session=session)
    for setgroup in setgroups:
        if Set.objects.filter(setgroup=setgroup).exists():
            continue
        # delete the setgroup if it has no sets
        setgroup.delete()
    return JsonResponse({"message": "empty setgroups deleted"}, status=201)

@csrf_exempt
def fetchsessions(request, client):
    """API Route: Fetch all past sessions for a user"""
    try:
        client = User.objects.get(pk=client)
    except User.DoesNotExist:
        return JsonResponse({"error": "Client does not exist."}, status=400)
    # get all sessions for selected client
    sessions = Session.objects.filter(routine__client=client).order_by('-pk')
    return JsonResponse([session.serialize() for session in sessions], safe=False)

@csrf_exempt
def updateset(request):
    """API Route: update a set from Edit Session Page"""
    if request.method != "PUT":
        return JsonResponse({"error": "PUT request required."}, status=400)
    # data from json
    data = json.loads(request.body)
    setpk = data.get("setpk")
    weight = data.get("weight")
    time = data.get("time")
    try:
        setobj = Set.objects.get(pk=setpk)
    except Set.DoesNotExist:
        return JsonResponse({"error": "Set does not exist"}, status=400)
    setobj.weight = weight
    setobj.time = time
    setobj.save()
    return JsonResponse({"message": "Set updated"}, status=201)

@csrf_exempt
def archive(request, routine):
    """API Route: archive or un-archive a routine"""
    if request.method != "PUT":
        return JsonResponse({"error": "PUT request required."}, status=400)
    try:
        routine = Routine.objects.get(pk=routine)
    except Routine.DoesNotExist:
        return JsonResponse({"error": "Routine does not exist."}, status=400)
    # if this routine is not archived, archive it
    if routine.archived is False:
        routine.archived = True
        response = {"message": "Routine archived"}
    # if routine is archived, un-archive
    else:
        routine.archived = False
        response = {"message": "Routine un-archived"}
    routine.save()
    return JsonResponse(response, status=201)

@csrf_exempt
def anotherexercise(request):
    """Add a new Setgroup to a Session"""
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    # variables from js
    data = json.loads(request.body)
    exercisepk = data.get("exerciseid")
    exerciseobj = Exercise.objects.get(pk=exercisepk)
    sessionpk = data.get("session")
    sessionobj = Session.objects.get(pk=sessionpk)
    routine = sessionobj.routine
    # this session's Setgroups
    setgrouplist = Setgroup.objects.filter(session=sessionobj)
    # check if this session already has this exercise
    for group in setgrouplist:
        if exerciseobj == group.exercise:
            return JsonResponse({"error": "Session already has this exercise"}, status=400)
    # add exercise to routine
    routine.exercises.add(exerciseobj)
    # add setgroup to session
    newgroup = Setgroup.objects.create(session=sessionobj, exercise=exerciseobj)
    # return setgroup id
    return JsonResponse({"setgroup": newgroup.pk, "name": exerciseobj.name}, status=201)

# HELPER FUNCTIONS
##################

def pagehelper(queryset, pnum):
    """return a dictionary for displaying 10 posts at a time,
    given any queryset, page number, and redirect route"""
    # https://docs.djangoproject.com/en/3.0/topics/pagination/
    paginator = Paginator(queryset, 5)
    sessions = paginator.get_page(pnum) # this particular list of 10 posts
    return {
        "sessions": sessions,
        "pnum": pnum,
        "prev_page": pnum - 1,
        "next_page": pnum + 1,
        "has_next": sessions.has_next()
    }
