import random
from cProfile import label
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import TemplateView, ListView, FormView, DetailView, UpdateView, CreateView
from redis import Redis

from apps.forms import EmailForm, LoginForm, ProfileModelForm, PhoneNumberForm, PasswordForm, PaymentModelForm
from apps.models import Category, Product, User, Region, District, Settings, Order, Stream, Payment
from root.settings import EMAIL_HOST_USER
from django.db.models import Sum, Count
from django.shortcuts import render

# Create your views here.

class HomeListView(ListView):
    queryset = Category.objects.all()
    context_object_name = 'categories'
    template_name = 'auth/block/base.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['products'] =Product.objects.all().order_by('-created_at')[:8]
        return data





class CategoriesView(ListView):
    queryset = Category.objects.all()
    context_object_name = 'categories'
    template_name = 'auth/categories/products-list.html'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        contex = super().get_context_data(**kwargs)
        if self.kwargs.get('slug'):
            contex['products'] = Product.objects.filter(category__slug=self.kwargs.get('slug'))

        else:
            contex['products'] = Product.objects.all().order_by('-created_at')

        return contex


class ProductDetail(DetailView):
    template_name = 'auth/categories/detail/product-detail.html'
    queryset = Product.objects.all()
    context_object_name = 'product'
    slug_url_kwarg = 'slug'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object(self.get_queryset())
        context['images'] = product.images.all()
        context['regions'] = Region.objects.all()
        return context


class ProfileListView(UpdateView):
    template_name = 'auth/block/profile-block.html'
    queryset = User.objects.all()
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('profile')
    form_class = ProfileModelForm

    def get_success_url(self):
        return reverse('profile', kwargs={'pk':self.request.user.pk})
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['regions'] = Region.objects.all()
        return data


def district_list(request):
        region_id = request.GET.get("region_id")
        districts = District.objects.filter(region_id=region_id)
        data = [{"id": i.pk, "name": i.name} for i in districts]
        return JsonResponse(data, safe=False)


class AccountView(LoginRequiredMixin, TemplateView):
    template_name = 'account/my_account.html'
    login_url = reverse_lazy('send_email')

class WebsiteInfoView(TemplateView):
    template_name = 'account/about_website.html'

class MarketView(ListView):
    template_name = 'account/market.html'
    queryset = Product.objects.all()
    context_object_name = 'products'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['categories'] = Category.objects.all()
        return data


class PhoneNumberChangeVIew(UpdateView):
    template_name = 'account/phone_number_change.html'
    queryset = User.objects.all()
    pk_url_kwarg = 'pk'
    form_class = PhoneNumberForm
    success_url = reverse_lazy('profile')

    def get_success_url(self):
        return reverse('profile', kwargs={'pk':self.request.user.pk})

class OrderView(View):

    def post(self, request, *args, **kwargs):
        order = {
            'name': request.POST.get('name'),
            'product_id': int(request.POST.get('product_id')),
            'phone_number': request.POST.get('phone_number'),
            'region_id': int(request.POST.get('region')),
            'user_id': int(request.POST.get('user')),
            'stream_id': request.POST.get('stream'),
        }
        delivery_price = Settings.objects.first()
        product = Product.objects.all()
        products = Product.objects.filter(id=order['product_id']).first()
        order['total'] = products.price + delivery_price.delivery_price
        Order.objects.create(**order)
        region = Region.objects.filter(id=order['region_id']).first()
        region.order_count += 1
        region.save()
        context={"products": product,'order':order}
        return render(request, 'auth/categories/detail/ready_for_order.html',context )


class PasswordChangeView(UpdateView):
    template_name = 'account/password-change.html'
    queryset = User.objects.all()
    pk_url_kwarg = 'pk'
    form_class = PasswordForm
    success_url = reverse_lazy('home')


class SendMailFormView(FormView):
    form_class =EmailForm
    template_name = 'auth/log-reg/register.html'
    success_url = reverse_lazy('check_email')

    def form_valid(self, form):
        email = form.cleaned_data.get("email")
        verify_code = random.randrange(10**5 , 10**6)
        send_mail(
            subject="Verification Code !!!",
            message=f"{verify_code}",
            from_email=EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False
        )
        redis = Redis()
        redis.set(email , verify_code)
        redis.expire(email , time=timedelta(minutes=5))



        return render(self.request , 'auth/log-reg/check_message.html' , {"email":email})


    def form_invalid(self, form):
        for error in form.errors.values():
            messages.error(self.request , error)
        return super().form_invalid(form)
#
# class VerifyCodeFormView(FormView):
#     form_class = VerifyForm
#     template_name = 'verify_form.html'
#     success_url = reverse_lazy("register")
#
#     def form_valid(self, form):
#         return render(self.request, 'register.html' , {"email" : form.cleaned_data.get("email")})
#     def form_invalid(self, form):
#         for error in form.errors.values():
#             messages.error(self.request , error)
#         return super().form_invalid(form)
#
class RegisterCreateView(View):
    def post(self, request, *args, **kwargs):
        email = request.POST.get('email')
        code = request.POST.get('code')
        query = User.objects.filter(email=email)
        if query.exists():
            user = query.first()
            login(request, user)
            return redirect('signin')
        redis = Redis(decode_responses=True)
        check_code = redis.get(email)
        if str(check_code) != str(code):
            messages.error(request, 'invalid password')
        User.objects.create_user(email=email)
        return redirect('signin')



#
class LoginFormView(FormView):
    form_class = LoginForm
    template_name = 'auth/log-reg/login.html'
    success_url = reverse_lazy("signin")

    def form_valid(self, form):
        user = form.user
        login(self.request , user)
        return super().form_valid(form)

    def form_invalid(self, form):
        for error in form.errors.values():
            messages.error(self.request, error)
        return super().form_invalid(form)

class ExitProfileView(View):

    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('home')

class StreamView(ListView):
    queryset = Stream.objects.all()
    context_object_name = 'streams'
    template_name = 'account/Oqim.html'

class SaveStreamCreteView(View):
    def post(self, request, *args, **kwargs):
        name = request.POST.get('name')
        user = request.user.pk
        product = request.POST.get('product_id')
        is_established = request.POST.get('is_established') == 'on'
        Stream.objects.create(name=name, user_id=user, product_id=product, is_established=is_established)
        return redirect('stream')

class StreamDetailView(DetailView):
    queryset = Stream.objects.all()
    template_name = 'auth/categories/detail/product-detail.html'
    context_object_name = 'stream'
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        stream = self.get_object(self.queryset)
        stream.visit_count += 1
        stream.save()
        product = self.get_object(self.queryset).product
        data['product'] = product
        data['images'] = product.images.all()
        data['regions'] = Region.objects.all()
        return data

class DeleteStreamView(View):
    def get(self, request, pk):
        Stream.objects.filter(pk=pk).delete()
        return redirect('stream')

# class Statistics(ListView):
#     template_name = 'account/statistic.html'
#     queryset = Stream.objects.all()
#     context_object_name = 'streams'
#
#     def get_context_data(self, **kwargs):
#         query = query.filter(owner=self.request.user).filter(created_at__range=filter_time).annotate(
#             new_count=Count('orders', filter=Q(orders__status=Order.StatusType.NEW)),
#             ready_to_delivery_count=Count('orders', filter=Q(orders__status=Order.StatusType.READY_TO_DELIVERY)),
#             delivering_count=Count('orders', filter=Q(orders__status=Order.StatusType.DELIVERING)),
#             delivered_count=Count('orders', filter=Q(orders__status=Order.StatusType.DELIVERED)),
#             not_pick_count=Count('orders', filter=Q(orders__status=Order.StatusType.NOT_PICK_UP_CALL)),
#             canceled_count=Count('orders', filter=Q(orders__status=Order.StatusType.CANCELED)),
#             archive_count=Count('orders', filter=Q(orders__status=Order.StatusType.ARCHIVE)),
#         ).values('name',
#                  'product__name',
#                  "visit_count",
#                  'new_count',
#                  'ready_to_delivery_count',
#                  'delivering_count',
#                  'delivered_count',
#                  'not_pick_count',
#                  'canceled_count',
#                  'archive_count')
#         return query


# class Statistics(TemplateView):
#     template_name = 'account/statistic.html'
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#
#
#         streams = Order.objects.values_list('stream_ordering', flat=True).distinct()
#
#         flow_data = []
#
#         for stream in streams:
#             orders = Order.objects.filter(stream_ordering=stream)
#             data = {
#                 "name": stream or "Noma'lum",
#                 "profit": orders.aggregate(Sum("total"))["total__sum"] or 0,
#                 "tashrif": orders.count(),
#                 "new": orders.filter(status=Order.StatusType.PENDING).count(),
#                 "accepted": orders.filter(status=Order.StatusType.SHIPPED).count(),
#                 "delivering": orders.filter(status=Order.StatusType.IN_TRANSIT).count(),
#                 "delivered": orders.filter(status=Order.StatusType.DELIVERED).count(),
#                 "returned": orders.filter(status=Order.StatusType.FAILED).count(),
#                 "hold": orders.filter(status=Order.StatusType.HOLD).count(),
#                 "archived": orders.filter(status=Order.StatusType.ARCHIVED).count()
#             }
#             flow_data.append(data)
#
#         context['flow_data'] = flow_data
#         return context

class Statistics(ListView):
    queryset = Stream.objects.all()
    context_object_name = 'streams'
    template_name = 'account/statistic.html'


    def get_queryset(self):
         data = super().get_queryset()
         query = data.filter(user=self.request.user).annotate(
             new_count=Count('orders', filter=Q(orders__status=Order.StatusType.NEW)),
             ready_to_delivery_count=Count('orders', filter=Q(orders__status=Order.StatusType.ACCEPTED)),
             delivering_count=Count('orders', filter=Q(orders__status=Order.StatusType.DELIVERING)),
             delivered_count=Count('orders', filter=Q(orders__status=Order.StatusType.DELIVERED)),
             returned=Count('orders', filter=Q(orders__status=Order.StatusType.RETURNED)),
             hold=Count('orders', filter=Q(orders__status=Order.StatusType.HOLD)),
             archive_count=Count('orders', filter=Q(orders__status=Order.StatusType.ARCHIVED)),
         ).values('name',
                  'product__name',
                  "visit_count",
                  'new_count',
                  'ready_to_delivery_count',
                  'delivering_count',
                  'delivered_count',
                  'returned',
                  'hold',
                  'archive_count')
         return query




def chart_view(request):
    labels = []
    data = []
    regions = Region.objects.all()
    for region in regions:
        labels.append(region.name)
        data.append(region.order_count)
    return render(request, 'account/diagram.html', {
        'labels': labels,
        'data': data
    })




class PaymentCreateView(CreateView):
    form_class = PaymentModelForm
    success_url = reverse_lazy('payment')
    template_name = 'account/payment_part.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['payments'] = Payment.objects.filter(user=self.request.user).order_by('-created_at')
        return data
    def form_invalid(self, form):
        for error in form.errors.values():
            messages.error(self.request, error)
        return super().form_invalid(form)











