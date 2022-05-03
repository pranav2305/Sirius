from django.shortcuts import render, redirect
from .forms import ClassCreationForm, CalendarCreationForm, NoticeCreationForm, CalendarUpdationForm, NoticeUpdationForm, ClassUpdationForm
from django.contrib.auth.decorators import login_required
from django.core.exceptions import BadRequest
from .models import Class, Notice, Event
from authorization.models import Membership, Permission, Role
from django.http import HttpResponseForbidden, HttpResponseBadRequest
from sirius.utils.perm import has_perm
from sirius.utils.console_context import get_console_data
from django.shortcuts import get_object_or_404
from team.models import Team


@login_required(login_url='user:signin')
def create_class(request, pk):
    if request.method == 'POST':
        data = request.POST.dict()
        data['team_id'] = pk
        form = ClassCreationForm(data)
        if form.is_valid() and pk:
            if not has_perm('C', 'C', request.user, pk):
                return HttpResponseForbidden()
            new_class = form.save(commit=False)
            # new_class.team_id = Team.objects.get(pk=pk)
            new_class.save()
            return redirect('team:session:timetable', pk=pk)
    else:
        form = ClassCreationForm()
    return render(request, 'create_class.html', {'form': form, 'console': get_console_data(pk, request.user)})

@login_required(login_url='user:signin')
def create_event(request, pk):
    if request.method == 'POST':
        form = CalendarCreationForm(request.POST)
        if form.is_valid() and pk:
            if not has_perm('C', 'E', request.user, pk):
                return HttpResponseForbidden()
            new_event = form.save(commit=False)
            new_event.team_id = Team.objects.get(pk=pk)
            new_event.save()
            return redirect('team:session:calendar', pk=pk)
    else:
        form = CalendarCreationForm()
    return render(request, 'create_event.html', {'form': form, 'console': get_console_data(pk, request.user)})

@login_required(login_url='user:signin')
def create_notice(request, pk):
    if request.method == 'POST':
        form = NoticeCreationForm(request.POST)
        if form.is_valid() and pk:
            if not has_perm('C', 'N', request.user, pk):
                return HttpResponseForbidden()
            new_notice = form.save(commit=False)
            new_notice.team_id = Team.objects.get(pk=pk)
            new_notice.user_id = request.user
            new_notice.save()
            return redirect('team:session:notice_board', pk=pk)
    else:
        form = NoticeCreationForm()
    return render(request, 'create_notice.html', {'form': form, 'console': get_console_data(pk, request.user)})

@login_required(login_url='user:signin')
def update_class(request, pk, c_pk):
    if request.method == 'POST':
        instance = get_object_or_404(Class, pk=c_pk)
        form = ClassUpdationForm(request.POST, instance=instance)
        if form.is_valid() and pk:
            if not has_perm('U', 'C', request.user, pk):
                return HttpResponseForbidden()
            form.save()
            return redirect('team:session:class_detail', pk=pk, c_pk=c_pk)
    else:
        instance = get_object_or_404(Class, pk=c_pk)
        form = ClassUpdationForm(instance=instance)
    return render(request, 'create_class.html', {'form': form, 'console': get_console_data(pk, request.user), 'c_pk': c_pk})

@login_required(login_url='user:signin')
def update_event(request, pk, e_pk):
    if request.method == 'POST':
        instance = get_object_or_404(Event, pk=e_pk)
        form = CalendarUpdationForm(request.POST, instance=instance)
        if form.is_valid() and pk:
            if not has_perm('U', 'E', request.user, pk):
                return HttpResponseForbidden()
            form.save()
            return redirect('team:session:calendar', pk=pk)
    else:
        instance = get_object_or_404(Event, pk=e_pk)
        form = CalendarUpdationForm(instance=instance)
    return render(request, 'create_event.html', {'form': form, 'console': get_console_data(pk, request.user), 'e_pk': e_pk})

@login_required(login_url='user:signin')
def update_notice(request, pk, n_pk):
    if request.method == 'POST':
        instance = get_object_or_404(Notice, pk=n_pk)
        form = NoticeUpdationForm(request.POST, instance=instance)
        if form.is_valid() and pk:
            if not has_perm('U', 'N', request.user, pk):
                return HttpResponseForbidden()
            new_notice = form.save(commit=False)
            new_notice.user_id = request.user
            new_notice.save()
            return redirect('team:session:notice_board', pk=pk)
    else:
        instance = get_object_or_404(Notice, pk=n_pk)
        form = NoticeUpdationForm(instance=instance)
    return render(request, 'create_notice.html', {'form': form, 'console': get_console_data(pk, request.user), 'n_pk': n_pk})

@login_required(login_url='user:signin')
def delete_class(request, pk, c_pk):
    if not has_perm('D', 'C', request.user, pk):
        return HttpResponseForbidden()
    class_ = Class.objects.get(pk=c_pk)
    if class_:
        if int(class_.team_id.pk) != int(pk):
            return HttpResponseBadRequest('Invalid request')
        class_.delete()
        return redirect('team:session:timetable', pk=pk)
    return HttpResponseBadRequest()

@login_required(login_url='user:signin')
def delete_event(request, pk, e_pk):
    if not has_perm('D', 'E', request.user, pk):
        return HttpResponseForbidden()
    event = Event.objects.get(pk=e_pk)
    if event:
        if int(event.team_id.pk) != int(pk):
            return HttpResponseBadRequest('Invalid request')
        event.delete()
        return redirect('team:session:calendar', pk=pk)
    return HttpResponseBadRequest()

@login_required(login_url='user:signin')
def delete_notice(request, pk, n_pk):
    if not has_perm('D', 'N', request.user, pk):
        return HttpResponseForbidden()
    notice = Notice.objects.get(pk=n_pk)
    if notice:
        if int(notice.team_id.pk) != int(pk):
            return HttpResponseBadRequest('Invalid request')
        notice.delete()
        return redirect('team:session:notice_board', pk=pk)
    return HttpResponseBadRequest()

@login_required(login_url='user:signin')
def timetable(request, pk):
    if not has_perm('R', 'C', request.user, pk):
        return HttpResponseForbidden()
    classes = Class.objects.filter(team_id=pk).order_by('start_time')
    return render(request, 'timetable.html', {
        'classes': classes, 
        'console': get_console_data(pk, request.user),
        'days': Class.day.field.choices
    })

@login_required(login_url='user:signin')
def calendar(request, pk):
    if not has_perm('R', 'E', request.user, pk):
        return HttpResponseForbidden()
    events = Event.objects.filter(team_id=pk).values('pk','start', 'end', 'title', 'description')
    return render(request, 'calendar.html', {'events': events, 'console': get_console_data(pk, request.user)})

@login_required(login_url='user:signin')
def notice_board(request, pk):
    if not has_perm('R', 'N', request.user, pk):
        return HttpResponseForbidden()
    notices = Notice.objects.filter(team_id=pk).values('pk','title', 'description', 'created_at')
    return render(request, 'notice_board.html', {'notices': notices, 'console': get_console_data(pk, request.user)})

@login_required(login_url='user:signin')
def class_detail(request, pk, c_pk):
    if not has_perm('R', 'C', request.user, pk) and not has_perm('U', 'C', request.user, pk) and not has_perm('D', 'C', request.user, pk):
        return HttpResponseForbidden()
    class_ = get_object_or_404(Class, pk=c_pk)
    if int(class_.team_id.pk) != int(pk):
        return HttpResponseBadRequest('Invalid request')
    return render(request, 'class_detail.html', {'class': class_, 'console': get_console_data(pk, request.user)})

@login_required(login_url='user:signin')
def event_detail(request, pk, e_pk):
    if not has_perm('R', 'E', request.user, pk) and not has_perm('U', 'E', request.user, pk) and not has_perm('D', 'E', request.user, pk):
        return HttpResponseForbidden()
    event = get_object_or_404(Event, pk=e_pk)
    if int(event.team_id.pk) != int(pk):
        return HttpResponseBadRequest('Invalid request')
    return render(request, 'event_detail.html', {'event': event, 'console': get_console_data(pk, request.user)})

