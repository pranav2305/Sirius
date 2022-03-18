from django.shortcuts import render, redirect
from .forms import TeamCreationForm
from django.contrib.auth.decorators import login_required
from team.models import Team, JoinRequest, Invite
from authorization.models import Membership
from django.contrib.auth import get_user_model

@login_required(login_url='user:sign_in')
def create_team(request):
    if request.method == 'POST':
        form = TeamCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/')
    else:
        return render(request, 'create_team.html')

@login_required(login_url='user:sign_in')
def team_info(request, pk):
    parents = []
    team = Team.objects.get(pk=pk)
    temp = team.parent_id
    while temp != None:
        parents.append(Team.objects.get(pk=temp).values('name', 'pk'))
        temp = temp.parent_id
    members = Membership.objects.filter(team_id=pk).values('created_at', 'alumni', 'user_id__pk', 'user_id__first_name', 'user_id__last_name', 'user_id__email', 'role_id__pk', 'role_id__name')
    children = Team.objects.filter(parent_id=pk).values('name', 'pk')
    return render(request, 'team_info.html', {'team': team, 'members': members, 'children': children, 'parents': parents})

@login_required(login_url='user:sign_in')
def send_invite(request, pk, user):
    if request.method == 'POST':
        if Invite.objects.filter(status = 'P', team_id=pk, invited=user).exists():
            return redirect('team:team_info', pk=pk)
        invite = Invite(team_id=Team.objects.get(pk=pk), created_by=request.user, invited=get_user_model().objects.get(pk=user))
        invite.save()
        return redirect('team:team_info', pk=pk)
    return redirect('team:team_info', pk=pk)

@login_required(login_url='user:sign_in')
def send_join_request(request, pk):
    if request.method == 'POST':
        if JoinRequest.objects.filter(status='P', team_id=pk, user_id=request.user).exists():
            return redirect('team:team_info', pk=pk)
        request = JoinRequest(team_id=Team.objects.get(pk=pk), user_id=request.user)
        request.save()
        return redirect('team:team_info', pk=pk)
    return redirect('team:team_info', pk=pk)

@login_required(login_url='user:sign_in')
def invites(request, pk):
    invites = Invite.objects.filter(team_id=pk, status='P').values('invited__first_name', 'invited__last_name', 'invited__email', 'invited__pk', 'created_at', 'status', 'pk', 'created_by__first_name', 'created_by__last_name', 'created_by__email', 'created_by__pk')
    return render(request, 'invites.html', {'invites': invites})

@login_required(login_url='user:sign_in')
def join_requests(request, pk):
    requests = JoinRequest.objects.filter(team_id=pk, status='P').values('user_id__first_name', 'user_id__last_name', 'user_id__email', 'user_id__pk', 'created_at', 'status', 'pk')
    return render(request, 'join_requests.html', {'requests': requests})

@login_required(login_url='user:sign_in')
def accept_invite(request, pk):
    if request.method == 'POST':
        invite = Invite.objects.get(pk=pk)
        invite.status = 'A'
        invite.save()
        membership = Membership(team_id=invite.team_id, user_id=invite.invited)
        membership.save()
        return redirect('team:team_info', pk=invite.team_id.pk)

@login_required(login_url='user:sign_in')
def accept_join_request(request, pk):
    if request.method == 'POST':
        join_request = JoinRequest.objects.get(pk=pk)
        join_request.status = 'A'
        join_request.save()
        membership = Membership(team_id=join_request.team_id, user_id=join_request.user_id)
        membership.save()
        return redirect('team:team_info', pk=request.team_id.pk)

@login_required(login_url='user:sign_in')
def decline_invite(request, pk):
    if request.method == 'POST':
        invite = Invite.objects.get(pk=pk)
        invite.status = 'R'
        invite.save()
        return redirect('user:dashboard', pk=invite.team_id.pk)

@login_required(login_url='user:sign_in')
def decline_join_request(request, pk):
    if request.method == 'POST':
        join_request = JoinRequest.objects.get(pk=pk)
        join_request.status = 'R'
        join_request.save()
        return redirect('user:dashboard', pk=join_request.team_id.pk)
