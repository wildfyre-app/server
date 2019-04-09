from django.contrib import admin
from django.urls import reverse
from django.utils.encoding import force_text
from django.utils.html import format_html

from .models import Flag, FlagComment


class FlagCommentInline(admin.TabularInline):
    model = FlagComment
    fields = ('reporter', 'reason', 'comment', 'spite')
    extra = 0


class FlagStatusFilter(admin.filters.SimpleListFilter):
    title = 'Status'
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return (
            (-1, 'All'),
            (Flag.Status.REJECTED.value, 'Rejected'),
            (Flag.Status.ACCEPTED.value, 'Accepted'),
        )

    def choices(self, changelist):
        yield {
            'selected': self.value() is None,
            'query_string': changelist.get_query_string({}, [self.parameter_name]),
            'display': 'Pending',
        }
        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.value() == force_text(lookup),
                'query_string': changelist.get_query_string({self.parameter_name: lookup}, []),
                'display': title,
            }

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset.filter(status=Flag.Status.PENDING.value)
        else:
            try:
                value = int(self.value())
                if value > 0:
                    return queryset.filter(status=self.value())
            except ValueError:
                pass


@admin.register(Flag)
class FlagAdmin(admin.ModelAdmin):
    fields = ('object_author', 'url')
    readonly_fields = fields
    list_display = ('content_type', 'object', 'status', 'count', 'handler', 'object_author')
    inlines = [FlagCommentInline, ]

    list_filter = [FlagStatusFilter, ]

    def url(self, obj):
        if obj.content_type.model == "post":
            post = obj.object
        elif obj.content_type.model == "comment":
            post = obj.object.post
        else:
            return False

        return format_html(
            '<a href="{}">Go to Admin Page of Post</a>',
            reverse('admin:areas_post_change', args=(post.pk,)))

    def has_add_permission(self, request):
        return False

    def save_model(self, request, obj, form, change):
        if "_accept" in request.POST:
            obj.handler = request.user
            obj.status = Flag.Status.ACCEPTED.value
            if obj.object:
                obj.object.delete()

        elif "_reject" in request.POST:
            obj.handler = request.user
            obj.status = Flag.Status.REJECTED.value

        obj.save()
        return super().save_model(request, obj, form, change)
