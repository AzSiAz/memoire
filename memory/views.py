from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.contrib import messages
from .models import Memory, UserProfile
from django.db.models import Q
from pgvector.django import CosineDistance

import json

def memory_list(request: HttpRequest) -> HttpResponse:
    """Display a list of memories for the selected user."""
    # Get the username from the request
    username = request.GET.get('username')
    query = request.GET.get('query')
    channel_id = request.GET.get('channel_id')
    server_id = request.GET.get('server_id')
    
    memories = Memory.objects.all()
    
    if channel_id and channel_id != 'None':
        memories = memories.filter(channel_id=channel_id)

    if server_id and server_id != 'None':
        memories = memories.filter(server_id=server_id)

    if username and username != 'None':
        user = get_object_or_404(UserProfile, username=username)
        memories = memories.filter(user=user)

    if query and query != 'None':
        from .embeddings import compute_embedding
        query_embedding = compute_embedding(query)[0]
        memories = memories.annotate(distance=CosineDistance("embeddings", query_embedding)).order_by("-distance")
    else:
        memories = memories.order_by('-created_at')
    
    paginator = Paginator(memories, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    print(page_obj.object_list)
    
    return render(request, 'memory/memory_list.html', {
        'page_obj': page_obj,
        'username': username if username != 'None' else '',
        'query': query if query != 'None' else '',
        'channel_id': channel_id if channel_id != 'None' else '',
        'server_id': server_id if server_id != 'None' else '',
    })

def memory_detail(request: HttpRequest, memory_id: str) -> HttpResponse:
    """Display details of a specific memory."""
    memory = get_object_or_404(Memory, id=memory_id)
    return render(request, 'memory/memory_detail.html', {
        'memory': memory,
    })

def memory_add(request: HttpRequest) -> HttpResponse:
    """Display the memory add page."""
    return render(request, 'memory/memory_add.html')

@require_http_methods(["POST"])
def create_memory(request: HttpRequest) -> JsonResponse:
    """Create a new memory."""
    try:
        data = json.loads(request.body)
        username = data['username']
        user, created = UserProfile.objects.get_or_create(username=username)
        
        from .embeddings import compute_embedding
        
        memory = Memory.objects.create(
            user=user,
            channel_id=data.get('channel_id'),
            server_id=data.get('server_id'),
            content=data['content'],
            embeddings=compute_embedding(data['content'])[0],
            metadata=data.get('metadata', {})
        )
        return JsonResponse({'id': str(memory.id)})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@require_http_methods(["POST"])
def search_memories(request: HttpRequest) -> JsonResponse:
    """Search memories using vector similarity."""
    try:
        data = json.loads(request.body)
        query = data['query']
        username = data.get('username')
        channel_id = data.get('channel_id')
        server_id = data.get('server_id')
        
        memories = Memory.objects.all()
        
        if channel_id:
            memories = memories.filter(channel_id=channel_id)
        if server_id:
            memories = memories.filter(server_id=server_id)

        if username:
            user = get_object_or_404(UserProfile, username=username)
            memories = memories.filter(user=user)

        if query:
            # Compute query embedding
            from .embeddings import compute_embedding
            query_embedding = compute_embedding(query)[0]
            memories = memories.annotate(distance=CosineDistance("embeddings", query_embedding)).order_by("distance")[:3]
        
        return JsonResponse({
            'memories': [{
                'id': str(m.id),
                'content': m.content,
                'metadata': m.metadata,
                'created_at': m.created_at.isoformat(),
                'distance': m.distance,
                'channel_id': m.channel_id,
                'server_id': m.server_id,
                'user': m.user.username if m.user else None
            } for m in memories]
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@require_http_methods(["POST", "GET"])
def profile_view(request: HttpRequest, username: str) -> HttpResponse:
    """View and edit user profile."""
    if not username:
        return JsonResponse({'error': 'username is required'}, status=400)
        
    profile = get_object_or_404(UserProfile, username=username)
    if request.method == 'POST':
        profile.custom_info.update(request.POST.get('custom_info', {}))
        profile.save()
        return JsonResponse({'status': 'success'})
    return render(request, 'memory/profile.html', {'profile': profile})

@require_http_methods(["GET"])
def user_profile_list(request: HttpRequest) -> HttpResponse:
    """Display a list of all user profiles."""
    profiles = UserProfile.objects.all().order_by('username')
    paginator = Paginator(profiles, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'memory/user_profile_list.html', {
        'page_obj': page_obj,
    })

@require_http_methods(["GET"])
def user_profile_list_api(request: HttpRequest) -> JsonResponse:
    """API endpoint to get a list of all user profiles."""
    try:
        profiles = UserProfile.objects.all().order_by('username')
        return JsonResponse({
            'profiles': [{
                'id': str(p.id),
                'username': p.username,
                'custom_info': p.custom_info,
                'created_at': p.created_at.isoformat(),
                'updated_at': p.updated_at.isoformat(),
                'memory_count': p.memories.count()
            } for p in profiles]
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@require_http_methods(["GET"])
def user_profile_api(request: HttpRequest, username: str) -> JsonResponse:
    """API endpoint to get a specific user profile."""
    try:
        profile = get_object_or_404(UserProfile, username=username)
        return JsonResponse({
            'id': str(profile.id),
            'username': profile.username,
            'custom_info': profile.custom_info,
            'created_at': profile.created_at.isoformat(),
            'updated_at': profile.updated_at.isoformat(),
            'memory_count': profile.memories.count()
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
