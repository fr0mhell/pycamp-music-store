from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, permissions, viewsets, status
from rest_framework.decorators import detail_route
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.music_store.api.serializers import (
    AlbumSerializer,
    TrackSerializer,
    LikeTrackSerializer,
    ListenTrackSerializer,
    BoughtAlbumSerializer,
    BoughtTrackSerializer,
    PaymentAccountSerializer,
    PaymentMethodSerializer,
    PaymentTransactionSerializer,
    GlobalSearchSerializer
)
from apps.users.models import AppUser
from ...music_store.models import (
    Album,
    BoughtAlbum,
    BoughtTrack,
    LikeTrack,
    ListenTrack,
    Track,
    PaymentMethod,
    PaymentTransaction,
    PaymentNotFound,
    NotEnoughMoney,
    ItemAlreadyBought
)


class ItemsPagination(PageNumberPagination):
    """Pagination for lists of items"""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


# ##############################################################################
# PAYMENTS
# ##############################################################################

class PaymentMethodViewSet(viewsets.ModelViewSet):
    """View for PaymentMethods"""
    serializer_class = PaymentMethodSerializer
    permission_classes = (permissions.IsAuthenticated,)
    queryset = PaymentMethod.objects.all()

    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)


class PaymentTransactionViewSet(viewsets.mixins.ListModelMixin,
                                viewsets.GenericViewSet):
    """View for PaymentTransactions"""
    serializer_class = PaymentTransactionSerializer
    permission_classes = (permissions.IsAuthenticated,)
    queryset = PaymentTransaction.objects.all()
    pagination_class = ItemsPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user).order_by('-created')


# ##############################################################################
# ACCOUNTS
# ##############################################################################


class AccountView(generics.RetrieveAPIView):
    """View for AppUser to work with balance and selected payment methods"""

    serializer_class = PaymentAccountSerializer
    permission_classes = (permissions.IsAuthenticated,)
    queryset = AppUser.objects.all()

    def get_object(self):
        return super().get_queryset().get(pk=self.request.user.pk)


# ##############################################################################
# BOUGHT ITEMS
# ##############################################################################


class BoughtTrackViewSet(viewsets.mixins.ListModelMixin,
                         viewsets.GenericViewSet):
    """View to display the list of purchased user tracks"""
    serializer_class = BoughtTrackSerializer
    permission_classes = (permissions.IsAuthenticated,)
    queryset = BoughtTrack.objects.all()

    def get_queryset(self):
        user = self.request.user
        return super().get_queryset().filter(user=user)


class BoughtAlbumViewSet(BoughtTrackViewSet):
    """View to display the list of purchased user albums"""
    serializer_class = BoughtAlbumSerializer
    queryset = BoughtAlbum.objects.all()


# ##############################################################################
# ITEMS
# ##############################################################################

class ItemViewSet(viewsets.mixins.ListModelMixin,
                  viewsets.mixins.RetrieveModelMixin,
                  viewsets.GenericViewSet):

    @detail_route(
        methods=['post'],
        permission_classes=(permissions.IsAuthenticated,),
        url_path='buy',
        url_name='buy_with_default_payment',
    )
    def buy_item_with_default(self, request, **kwargs):
        """Method to buy item with using default payment method"""
        return self.buy_item(request, payment_id=None)

    @detail_route(
        methods=['post'],
        permission_classes=(permissions.IsAuthenticated,),
        url_path='buy/(?P<payment_id>[0-9]+)',
        url_name='buy',
    )
    def buy_item(self, request, payment_id=None, **kwargs):
        """Method to buy item with using payment `payment_id`"""
        user = request.user
        item = self.get_object()

        payment_method = PaymentMethod.objects.filter(
            owner=user,
            id=payment_id
        ).first()

        try:
            item.buy(user, payment_method)
        except (PaymentNotFound, NotEnoughMoney, ItemAlreadyBought) as e:
            return Response(
                data={'message': e.message},
                status=status.HTTP_400_BAD_REQUEST
            )
        if isinstance(item, Track):
            return Response(
                status=status.HTTP_200_OK,
                data={'content': item.full_version},
            )

        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_queryset(self):
        """Prevent display Albums and Tracks with null price"""
        return super().get_queryset().filter(price__isnull=False)


class AlbumViewSet(ItemViewSet):
    """Operations on music albums

    """
    # albums without price or with price < 0 are not displayed
    queryset = Album.objects.filter(price__gte=0)
    serializer_class = AlbumSerializer

    filter_backends = (filters.SearchFilter, DjangoFilterBackend)
    filter_fields = ('title', 'author', 'price')
    search_fields = ('title', 'author',)
    pagination_class = ItemsPagination


class TrackViewSet(ItemViewSet):
    """Operations on music tracks

    """
    # tracks without price or with price < 0 are not displayed
    queryset = Track.objects.filter(price__gte=0)
    serializer_class = TrackSerializer

    filter_backends = (filters.SearchFilter, DjangoFilterBackend)
    filter_fields = ('title', 'author', 'album', 'price')
    search_fields = ('title', 'author',)
    pagination_class = ItemsPagination

    @detail_route(
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated],
        url_path='like',
        url_name='like',
    )
    def like_unlike(self, request, **kwargs):
        """Like or Unlike the Track.

        When request method is POST, likes Track if it isn't liked.
        Otherwise does nothing.
        When method is DELETE, unlikes Track if it is liked.
        Otherwise does nothing.

        """
        user = request.user
        track = self.get_object()

        if request.method == 'POST':
            track.like(user=user)
            return Response(
                data={'message': 'You liked track! Great!'},
                status=status.HTTP_201_CREATED
            )
        if request.method == 'DELETE':
            track.unlike(user=user)
            return Response(
                data={'message': 'You disliked track! SAD!'},
                status=status.HTTP_200_OK
            )

    @detail_route(
        methods=['post'],
        permission_classes=[permissions.IsAuthenticated],
        url_path='listen',
        url_name='listen',
    )
    def listen(self, request, **kwargs):
        """Create an entry about user listen to the track.

        """
        user = request.user
        track = self.get_object()

        track.listen(user)
        return Response(
            data={'message': 'Yeah! Music!'},
            status=status.HTTP_200_OK
        )


# ##############################################################################
# LIKES
# ##############################################################################


class LikeTrackViewSet(viewsets.mixins.ListModelMixin,
                       viewsets.GenericViewSet):
    """Authorised user sees list of liked tracks.

    """
    queryset = LikeTrack.objects.all()
    serializer_class = LikeTrackSerializer
    permission_classes = (permissions.IsAuthenticated,)


# ##############################################################################
# LISTENS
# ##############################################################################


class ListenTrackViewSet(viewsets.mixins.ListModelMixin,
                         viewsets.GenericViewSet):
    """Authorised user sees list of listened tracks.

    """
    queryset = ListenTrack.objects.all()
    serializer_class = ListenTrackSerializer
    permission_classes = (permissions.IsAuthenticated,)


# ##############################################################################
# SEARCH
# ##############################################################################


class GlobalSearchList(APIView):
    """View for global searching.

    Search Tracks and Albums, which contain the value of get-parameter `query`
    in the `title` or `author` fields.

    """
    search_param = 'query'

    def get(self, request):
        query = request.query_params.get(self.search_param, None)
        if not query:
            raise ValidationError(f"Query parameter '{self.search_param}' "
                                  f"is required.")

        search_filter = Q(author__icontains=query) | Q(title__icontains=query)
        tracks = Track.objects.filter(search_filter)
        albums = Album.objects.filter(search_filter)
        result = GlobalSearchSerializer({'tracks': tracks, 'albums': albums})
        return Response(data=result.data, status=status.HTTP_200_OK)
