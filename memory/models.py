from django.db import models
from pgvector.django import VectorField, HnswIndex
import uuid
from .embeddings import compute_embedding

DIMS = 768  # nomic-embed-text dimensions

class UserProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, auto_created=True)
    username = models.CharField(max_length=255, unique=True)
    custom_info = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.username}"

class Memory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, auto_created=True)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='memories')
    channel_id = models.CharField(max_length=255, null=True)  # Discord channel ID
    server_id = models.CharField(max_length=255, null=True)   # Discord server ID
    content = models.TextField()
    metadata = models.JSONField()
    embeddings = VectorField(dimensions=DIMS)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    summary = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='summarized_memories')
    
    class Meta:
        indexes = [
            HnswIndex(
                name='memory_embeddings_hnsw_idx',
                fields=['embeddings'],
                opclasses=['vector_cosine_ops'],
                m=16,
                ef_construction=64,
            ),
            models.Index(fields=['user', 'channel_id', 'server_id']),
            models.Index(fields=['summary_id'])
        ]
        
    def __str__(self):
        return f"Memory for {self.user.username} in {self.channel_id}"
    
    def save(self, *args, **kwargs):
        if not self.embeddings:
            self.embeddings = compute_embedding(self.content)[0]
        super().save(*args, **kwargs)
	
