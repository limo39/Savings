from django.contrib import admin
from .models import Member, Contribution

class MemberAdmin(admin.ModelAdmin):
    list_display = ('id_number', 'mobile_number', 'email')
    list_filter = ('user__is_staff', 'user__is_active')
    search_fields = ('username', 'mobile_number', 'id_number', 'email')

admin.site.register(Member, MemberAdmin)


class ContributionAdmin(admin.ModelAdmin):
    list_display = ('member', 'amount', 'transaction_id', 'transaction_date')
    search_fields = ('member__username', 'transaction_id')

admin.site.register(Contribution, ContributionAdmin)
