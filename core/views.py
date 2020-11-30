import random
import string


from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.views.generic import ListView, DetailView, View

from .forms import CheckoutForm, CouponForm, RefundForm, PaymentForm
from .models import Item, OrderItem, Order, Address, Payment, Coupon, Refund, UserProfile
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))


def products(request):
    context = {
        'productos': Item.objects.all()
    }
    return render(request, "products.html", context)


def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid


class CheckoutView(View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, realizo_pedido=False)
            form = CheckoutForm()
            context = {
                'form': form,
                'couponform': CouponForm(),
                'order': order,
                'DISPLAY_COUPON_FORM': True
            }

            direccion_de_envio_qs = Address.objects.filter(
                user=self.request.user,
                tipo_de_direccion='S',
                default=True
            )
            if direccion_de_envio_qs.exists():
                context.update(
                    {'default_direccion_de_envio': direccion_de_envio_qs[0]})

            direccion_de_facturacion_qs = Address.objects.filter(
                user=self.request.user,
                tipo_de_direccion='B',
                default=True
            )
            if direccion_de_facturacion_qs.exists():
                context.update(
                    {'default_direccion_de_facturacion': direccion_de_facturacion_qs[0]})
            return render(self.request, "checkout.html", context)
        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order")
            return redirect("core:checkout")

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, realizo_pedido=False)
            if form.is_valid():

                use_default_shipping = form.cleaned_data.get(
                    'use_default_shipping')
                if use_default_shipping:
                    print("Using the defualt shipping address")
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        tipo_de_direccion='S',
                        default=True
                    )
                    if address_qs.exists():
                        direccion_de_envio = address_qs[0]
                        order.direccion_de_envio = direccion_de_envio
                        order.save()
                    else:
                        messages.info(
                            self.request, "No default shipping address available")
                        return redirect('core:checkout')
                else:
                    print("User is entering a new shipping address")
                    direccion_de_envio1 = form.cleaned_data.get(
                        'direccion_de_envio')
                    direccion_de_envio2 = form.cleaned_data.get(
                        'direccion_de_envio2')
                    shipping_country = form.cleaned_data.get(
                        'shipping_country')
                    shipping_zip = form.cleaned_data.get('shipping_zip')

                    if is_valid_form([direccion_de_envio1, shipping_country, shipping_zip]):
                        direccion_de_envio = Address(
                            user=self.request.user,
                            direccion=direccion_de_envio1,
                            direccion2=direccion_de_envio2,
                            pais=shipping_country,
                            zip=shipping_zip,
                            tipo_de_direccion='S'
                        )
                        direccion_de_envio.save()

                        order.direccion_de_envio = direccion_de_envio
                        order.save()

                        set_default_shipping = form.cleaned_data.get(
                            'set_default_shipping')
                        if set_default_shipping:
                            direccion_de_envio.default = True
                            direccion_de_envio.save()

                    else:
                        messages.info(
                            self.request, "Please fill in the required shipping address fields")

                use_default_billing = form.cleaned_data.get(
                    'use_default_billing')
                same_direccion_de_facturacion = form.cleaned_data.get(
                    'same_direccion_de_facturacion')

                if same_direccion_de_facturacion:
                    direccion_de_facturacion = direccion_de_envio
                    direccion_de_facturacion.pk = None
                    direccion_de_facturacion.save()
                    direccion_de_facturacion.tipo_de_direccion = 'B'
                    direccion_de_facturacion.save()
                    order.direccion_de_facturacion = direccion_de_facturacion
                    order.save()

                elif use_default_billing:
                    print("Using the defualt billing address")
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        tipo_de_direccion='B',
                        default=True
                    )
                    if address_qs.exists():
                        direccion_de_facturacion = address_qs[0]
                        order.direccion_de_facturacion = direccion_de_facturacion
                        order.save()
                    else:
                        messages.info(
                            self.request, "No default billing address available")
                        return redirect('core:checkout')
                else:
                    print("User is entering a new billing address")
                    direccion_de_facturacion1 = form.cleaned_data.get(
                        'direccion_de_facturacion')
                    direccion_de_facturacion2 = form.cleaned_data.get(
                        'direccion_de_facturacion2')
                    billing_country = form.cleaned_data.get(
                        'billing_country')
                    billing_zip = form.cleaned_data.get('billing_zip')

                    if is_valid_form([direccion_de_facturacion1, billing_country, billing_zip]):
                        direccion_de_facturacion = Address(
                            user=self.request.user,
                            direccion=direccion_de_facturacion1,
                            direccion2=direccion_de_facturacion2,
                            pais=billing_country,
                            zip=billing_zip,
                            tipo_de_direccion='B'
                        )
                        direccion_de_facturacion.save()

                        order.direccion_de_facturacion = direccion_de_facturacion
                        order.save()

                        set_default_billing = form.cleaned_data.get(
                            'set_default_billing')
                        if set_default_billing:
                            direccion_de_facturacion.default = True
                            direccion_de_facturacion.save()

                    else:
                        messages.info(
                            self.request, "")

                payment_option = form.cleaned_data.get('payment_option')

                if payment_option == 'S':
                    return redirect('core:payment', payment_option='stripe')
                elif payment_option == 'P':
                    return redirect('core:payment', payment_option='paypal')
                else:
                    messages.warning(
                        self.request, "Invalid payment option selected")
                    return redirect('core:checkout')
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("core:order-summary")


class PaymentView(View):

    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, realizo_pedido=False)
        context = {
            'order': order
        }
        return render(self.request, "payment.html", context)

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, realizo_pedido=False)
        token = self.request.POST.get('stripeToken')
        amount = int(order.get_total() * 100)

        try:
            charge = stripe.Charge.create(
                amount=amount,  # cents
                currency="usd",
                source=token
            )

            # create the payment
            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.get_total()
            payment.save()

            # assign the payment to the order

            order.ordered = True
            order.payment = payment
            order.save()

            messages.success(self.request, "Your order was successful!")
            return redirect("/")

        except stripe.error.CardError as e:
            body = e.json_body
            err = body.get('error', {})
            messages.error(self.request, f"{err.get('message')}")
            return redirect("/")

        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            messages.error(self.request, "Rate limit error")
            return redirect("/")

        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            messages.error(self.request, "Invalid parameters")
            return redirect("/")

        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            messages.error(self.request, "Not authenticated")
            return redirect("/")

        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            messages.error(self.request, "Network error")
            return redirect("/")

        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            messages.error(
                self.request, "Something went wrong. You were not charged. Please try again.")
            return redirect("/")

        except Exception as e:
            # send an email to ourselves
            messages.error(
                self.request, "A serious error occurred. We have been notifed.")
            return redirect("/")



class HomeView(ListView):
    model = Item
    paginate_by = 10
    template_name = "home.html"


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, realizo_pedido=False)
            context = {
                'object': order
            }
            return render(self.request, 'order_summary.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("/")


class ItemDetailView(DetailView):
    model = Item
    template_name = "product.html"


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        realizo_pedido=False
    )
    order_qs = Order.objects.filter(user=request.user, realizo_pedido=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.productos.filter(item__slug=item.slug).exists():
            order_item.cantidad += 1
            order_item.save()
            messages.info(request, "This item quantity was updated.")
            return redirect("core:order-summary")
        else:
            order.productos.add(order_item)
            messages.info(request, "This item was added to your cart.")
            return redirect("core:order-summary")
    else:
        fecha_de_pedido = timezone.now()
        order = Order.objects.create(
            user=request.user, fecha_de_pedido=fecha_de_pedido)
        order.productos.add(order_item)
        messages.info(request, "This item was added to your cart.")
        return redirect("core:order-summary")


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        realizo_pedido=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.productos.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                realizo_pedido=False
            )[0]
            order.productos.remove(order_item)
            order_item.delete()
            messages.info(request, "Este artículo fue eliminado de su carrito.")
            return redirect("core:order-summary")
        else:
            messages.info(request, "Este artículo no estaba en tu carrito")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "No tienes un pedido activo")
        return redirect("core:product", slug=slug)


@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        realizo_pedido=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.productos.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                realizo_pedido=False
            )[0]
            if order_item.cantidad > 1:
                order_item.cantidad -= 1
                order_item.save()
            else:
                order.productos.remove(order_item)
            messages.info(request, "This item quantity was updated.")
            return redirect("core:order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("core:product", slug=slug)


def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.info(request, "This coupon does not exist")
        return redirect("core:checkout")


class AddCouponView(View):
    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(
                    user=self.request.user, realizo_pedido=False)
                order.coupon = get_coupon(self.request, code)
                order.save()
                messages.success(self.request, "Successfully added coupon")
                return redirect("core:checkout")
            except ObjectDoesNotExist:
                messages.info(self.request, "You do not have an active order")
                return redirect("core:checkout")


class RequestRefundView(View):
    def get(self, *args, **kwargs):
        form = RefundForm()
        context = {
            'form': form
        }
        return render(self.request, "request_refund.html", context)

    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST)
        if form.is_valid():
            pedidoid = form.cleaned_data.get('pedidoid')
            message = form.cleaned_data.get('message')
            email = form.cleaned_data.get('email')
            # edit the order
            try:
                order = Order.objects.get(pedidoid=pedidoid)
                order.reembolso_requerido = True
                order.save()

                # store the refund
                refund = Refund()
                refund.order = order
                refund.reason = message
                refund.email = email
                refund.save()

                messages.info(self.request, "Your request was received.")
                return redirect("core:request-refund")

            except ObjectDoesNotExist:
                messages.info(self.request, "This order does not exist.")
                return redirect("core:request-refund")
