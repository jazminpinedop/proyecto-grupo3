from django.db.models.signals import post_save
from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.shortcuts import reverse
from django_countries.fields import CountryField


CATEGORY_CHOICES = (
    ('T', 'Tecnología'),
    ('H', 'Hogar'),
    ('V', 'Vestimenta')
)

LABEL_CHOICES = (
    ('A', 'primary'),
    ('M', 'info'),
    ('R', 'danger')
)

ADDRESS_CHOICES = (
    ('B', 'Billing'),
    ('S', 'Shipping'),
)


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
                  #username, first_name, last_name, email, password entre otros
    stripe_customer_id = models.CharField(max_length=50, blank=True, null=True)
    compra_habilitada = models.BooleanField(default=False)
    telefono = models.IntegerField(max_length=9)
    dni = models.IntegerField(max_length=8)

    def __str__(self):
        return self.user.username


class Item(models.Model):
    nombre = models.CharField(max_length=100)
    precio = models.FloatField()
    precio_con_descuento = models.FloatField(blank=True, null=True)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=2)
    label = models.CharField(choices=LABEL_CHOICES, max_length=1)
    slug = models.SlugField()
    descripcion = models.TextField()
    imagen = models.ImageField()

    def __str__(self):
        return self.nombre

    def get_absolute_url(self):
        return reverse("core:product", kwargs={
            'slug': self.slug
        })

    def get_add_to_cart_url(self):
        return reverse("core:add-to-cart", kwargs={
            'slug': self.slug
        })

    def get_remove_from_cart_url(self):
        return reverse("core:remove-from-cart", kwargs={
            'slug': self.slug
        })


class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    realizo_pedido = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.cantidad} of {self.item.nombre}"

    def get_total_item_price(self):
        return self.cantidad * self.item.precio

    def get_total_discount_item_price(self):
        return self.cantidad * self.item.precio_con_descuento

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        if self.item.precio_con_descuento:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    pedidoid = models.CharField(max_length=20, blank=True, null=True)
    productos = models.ManyToManyField(OrderItem)
    fecha_de_pedido = models.DateTimeField()
    realizo_pedido = models.BooleanField(default=False)
    direccion_de_envio = models.ForeignKey(
        'Address', related_name='direccion_de_envio', on_delete=models.SET_NULL, blank=True, null=True)
    direccion_de_facturacion = models.ForeignKey(
        'Address', related_name='direccion_de_facturacion', on_delete=models.SET_NULL, blank=True, null=True)
    pago = models.ForeignKey(
        'Payment', on_delete=models.SET_NULL, blank=True, null=True)
    coupon = models.ForeignKey(
        'Coupon', on_delete=models.SET_NULL, blank=True, null=True)
    delivery_en_proceso = models.BooleanField(default=False)
    recibido = models.BooleanField(default=False)
    reembolso_requerido = models.BooleanField(default=False)
    reembolsado = models.BooleanField(default=False)

    '''
    1. Item added to cart
    2. Adding a billing address
    (Failed checkout)
    3. Payment
    (Preprocessing, processing, packaging etc.)
    4. Being delivered
    5. recibido
    6. Refunds
    '''

    def __str__(self):
        return self.user.username

    def get_total(self):
        total = 0
        for order_item in self.productos.all():
            total += order_item.get_final_price()
        if self.coupon:
            total -= self.coupon.monto
        return total


class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    direccion = models.CharField(max_length=100)
    direccion2 = models.CharField(max_length=100)
    pais = CountryField(multiple=False)
    zip = models.CharField(max_length=100)
    tipo_de_direccion = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    default = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'Direcciones'


class Payment(models.Model):
    pago_id = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, blank=True, null=True)
    monto = models.FloatField()
    fecha_y_hora= models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class Coupon(models.Model):
    code = models.CharField(max_length=15)
    monto = models.FloatField()

    def __str__(self):
        return self.code


class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()

    def __str__(self):
        return f"{self.pk}"


def userprofile_receiver(sender, instance, created, *args, **kwargs):
    if created:
        userprofile = UserProfile.objects.create(user=instance)


post_save.connect(userprofile_receiver, sender=settings.AUTH_USER_MODEL)
