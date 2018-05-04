from rest_framework import serializers

from apps.music_store.models import Album, Track, LikeTrack

__all__ = (
    'AlbumSerializer',
    'TrackSerializer',
)


class AlbumSerializer(serializers.ModelSerializer):
    """Serializer for Music Albums

    """
    # all tracks related to the album
    tracks = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Track.objects.all()
    )
    is_bought = serializers.SerializerMethodField()

    class Meta:
        model = Album
        fields = (
            'id',
            'author',
            'title',
            'image',
            'price',
            'tracks',
            'is_bought',
        )

    def get_is_bought(self, obj):
        request = self.context.get('request', None)
        if not request:
            return False

        user = request.user
        if not user.is_authenticated:
            return False

        return obj.is_bought(user)


class TrackSerializer(serializers.ModelSerializer):
    """Serializer for Music Tracks"""

    content = serializers.SerializerMethodField()
    is_bought = serializers.SerializerMethodField()

    is_liked = serializers.SerializerMethodField()
    count_likes = serializers.SerializerMethodField()

    class Meta:
        model = Track
        fields = (
            'id',
            'author',
            'title',
            'album',
            'price',
            'content',
            'is_bought',
            'is_liked',
            'count_likes',
        )

    def get_is_bought(self, obj):
        request = self.context.get('request', None)
        if not request:
            return False

        user = request.user
        if not user.is_authenticated:
            return False

        return obj.is_bought(user)

    def get_content(self, obj):
        """Get free or full version of track.

        Full version is provided when track is bought by user.
        Otherwise free version is provided.

        Args:
            obj (Track): an instance of Track.

        """
        request = self.context.get('request', None)
        if not request:
            return obj.free_version

        user = request.user
        if user.is_authenticated and obj.is_bought(user):
            return obj.full_version
        return obj.free_version

    def get_is_liked(self, obj):
        """Check if track is liked by authorized user"""
        request = self.context.get('request', None)
        if not request:
            return False

        user = request.user
        if not user.is_authenticated:
            return False

        return obj.is_liked(user)

    def get_count_likes(self, obj):
        """Get total number of 'likes' on the track"""
        request = self.context.get('request', None)
        if not request:
            return 0

        return obj.likes.count()
