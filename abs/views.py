from django.core.paginator import Paginator
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import UpdateView
from rest_framework.generics import RetrieveAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView, ListAPIView
from rest_framework.viewsets import ModelViewSet

from abs.models import Ad, Category, Location
from abs.serializers import AdDetailSerializer, AdCreateSerializer, AdUpdateSerializer, AdDestroySerializer, \
    CategorySerializer, LocationSerializer
from avito_project import settings


def code(request):
    return JsonResponse({"status": "ok"})


class AdListView(ListAPIView):
    models = Ad
    queryset = Ad.objects.all()

    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)

        categories = request.GET.getlist("cat", [])
        if categories:
            self.object_list = self.object_list.filter(category_id__in=categories)

        if request.GET.get("text", None):
            self.object_list = self.object_list.filter(name__icontains=request.GET.get("text"))

        if request.GET.get("location", None):
            self.object_list = self.object_list.filter(author__locations__name__icontains=request.GET.get('location'))

        if request.GET.get("price_form", None):
            self.object_list = self.object_list.filter(price__gte=request.GET.get("price_form"))

        if request.GET.get("price_to", None):
            self.object_list = self.object_list.filter(price__lte=request.GET.get("price_to"))

        self.object_list = self.object_list.select_related('author').order_by("-price")
        paginator = Paginator(self.object_list, settings.REST_FRAMEWORK['PAGE_SIZE'])
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        ads = []
        for ad in page_obj:
            ads.append({
                "id": ad.id,
                "name": ad.name,
                "author": ad.author.first_name,
                "price": ad.price,
                "description": ad.description,
                "is_published": ad.is_published,
                "category_id": ad.category_id,
                "image": ad.image.url if ad.image else None,
            })

        response = {
            "items": ads,
            "num_page": page_obj.paginator.num_pages,
            "total": page_obj.paginator.count
        }

        return JsonResponse(response, safe=False)


class AdDetailView(RetrieveAPIView):
    queryset = Ad.objects.all()
    serializer_class = AdDetailSerializer


class AdCreateView(CreateAPIView):
    queryset = Ad.objects.all()
    serializer_class = AdCreateSerializer


class AdUpdateView(UpdateAPIView):
    queryset = Ad.objects.all()
    serializer_class = AdUpdateSerializer


class AdDeleteView(DestroyAPIView):
    queryset = Ad.objects.all()
    serializer_class = AdDestroySerializer


@method_decorator(csrf_exempt, name='dispatch')
class AdImageView(UpdateView):
    model = Ad
    fields = ["name", "author", "price", "description", "image", "is_published", "category"]

    def post(self, request, *args, **kwargs):
        ad = self.get_object()

        ad.image = request.FILES.get("image", None)
        ad.save()
        response = AdDetailSerializer(ad).data

        return JsonResponse(response)


class CategoryListView(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CategoryDetailView(RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CategoryCreateView(CreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CategoryUpdateView(UpdateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CategoryDeleteView(DestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class LocationViewSet(ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
