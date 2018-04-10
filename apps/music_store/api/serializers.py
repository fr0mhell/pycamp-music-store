from rest_framework import serializers

from apps.music_store.models import Album, LikeTrack, ListenTrack, Track


class AlbumSerializer(serializers.ModelSerializer):
    """Serializer for Music Albums

    """
    # all tracks related to the album
    tracks = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Track.objects.all()
    )

    class Meta:
        model = Album
        fields = (
            'id',
            'title',
            'image',
            'price',
            'tracks',
        )


class TrackSerializer(serializers.ModelSerializer):
    """Serializer for Music Tracks

    """
    # free_version gets data from full_version inside model
    free_version = serializers.ReadOnlyField()

    class Meta:
        model = Track
        fields = (
            'id',
            'title',
            'album',
            'price',
            'full_version',
            'free_version',
        )


class LikeTrackSerializer(serializers.ModelSerializer):
    """Serializer for Likes of music tracks

    """
    user = serializers.ReadOnlyField(source='user.pk')

    class Meta:
        model = LikeTrack
        fields = (
            'id',
            'track',
            'user',
            'created',
        )


class ListenTrackSerializer(serializers.ModelSerializer):
    """Serializer for Listennings of Music tracks

    """
    user = serializers.ReadOnlyField(source='user.pk')

    class Meta:
        model = ListenTrack
        fields = (
            'id',
            'track',
            'user',
            'created',
        )
