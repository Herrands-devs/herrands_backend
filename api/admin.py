from django.contrib import admin
from .models import Category, Subtype, File, ErrandTask, Conversation, Message, Earnings, Wallet

# Define custom admin classes if needed

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Subtype)
class SubtypeAdmin(admin.ModelAdmin):
    list_display = ['id','name', 'category', 'description']
    list_filter = ['category']
    search_fields = ['name', 'category__name']

@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ['file']
    search_fields = ['file']

@admin.register(ErrandTask)
class ErrandTaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'category', 'subtype', 'drop_off_address', 'status']
    list_filter = ['category', 'subtype', 'status']
    search_fields = ['id', 'drop_off_address', 'customer__email', 'agent__email']
    date_hierarchy = 'created'
    readonly_fields = ('id', 'created', 'updated')
    filter_horizontal = ('rejected_agents', 'files')
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'created', 'updated', 'category', 'subtype', 'status')
        }),
        ('Locations', {
            'fields': ('pick_up_address', 'pick_up_lat', 'pick_up_long', 'drop_off_address', 'drop_off_lat', 'drop_off_long')
        }),
        ('Customer and Agent', {
            'fields': ('customer', 'agent', 'rejected_agents')
        }),
        ('Details', {
            'fields': ('recipient_contact', 'item_description', 'grocery_list', 'grocery_estimated_price', 'describe_errand')
        }),
        ('Files', {
            'fields': ('files',)
        }),
        ('Status', {
            'fields': ('user_cancelled', 'state_within')
        }),
    )

    # Customize methods if needed

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if obj and obj.status != ErrandTask.REQUESTED:
            # Make some fields readonly once the status changes
            readonly_fields += ('category', 'subtype', 'customer', 'agent', 'rejected_agents')
        return readonly_fields

    def has_change_permission(self, request, obj=None):
        if obj and obj.status not in (ErrandTask.REQUESTED, ErrandTask.REJECTED):
            return False
        return super().has_change_permission(request, obj)

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['errand', 'customer', 'agent', 'start_time']
    search_fields = ['errand__id', 'customer__username', 'agent__username']
    date_hierarchy = 'start_time'

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'text', 'attachment', 'conversation_id', 'timestamp']
    search_fields = ['sender__username', 'conversation_id__errand__id']
    date_hierarchy = 'timestamp'

class EarningsAdmin(admin.ModelAdmin):
    list_display = ('wallet', 'amount', 'timestamp')
    list_filter = ('wallet__user__email', 'timestamp')
    search_fields = ('wallet__user__email', 'amount')
    date_hierarchy = 'timestamp'

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'timestamp')
    search_fields = ('user__email',)  # Add other fields for searching if needed
    list_filter = ('timestamp',) 

admin.site.register(Earnings, EarningsAdmin)
