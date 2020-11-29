from django.contrib import admin

from .models import Item, OrderItem, Order, Payment, Coupon, Refund, Address, UserProfile


def make_refund_accepted(modeladmin, request, queryset):
    queryset.update(reembolso_requerido=False, reembolsado=True)


make_refund_accepted.short_description = 'Update orders to refund granted'


class OrderAdmin(admin.ModelAdmin):
    list_display = ['user',
                    'realizo_pedido',
                    'delivery_en_proceso',
                    'recibido',
                    'reembolso_requerido',
                    'reembolsado',
                    'direccion_de_envio',
                    'direccion_de_facturacion',
                    'payment',
                    'coupon'
                    ]
    list_display_links = [
        'user',
        'direccion_de_envio',
        'direccion_de_facturacion',
        'payment',
        'coupon'
    ]
    list_filter = ['realizo_pedido',
                   'delivery_en_proceso',
                   'recibido',
                   'reembolso_requerido',
                   'reembolsado']
    search_fields = [
        'user__username',
        'pedidoid'
    ]
    actions = [make_refund_accepted]


class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'street_address',
        'apartment_address',
        'country',
        'zip',
        'address_type',
        'default'
    ]
    list_filter = ['default', 'address_type', 'country']
    search_fields = ['user', 'street_address', 'apartment_address', 'zip']


admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order, OrderAdmin)
admin.site.register(Payment)
admin.site.register(Coupon)
admin.site.register(Refund)
admin.site.register(Address, AddressAdmin)
admin.site.register(UserProfile)
