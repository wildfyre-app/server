from django.contrib import admin
from django.contrib.admin.options import IncorrectLookupParameters
from django.utils.encoding import force_text

from .models import Post, Comment


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    fields = ('author', 'text',)


class PostDraftFilter(admin.filters.SimpleListFilter):
    title = 'Draft'
    parameter_name = 'draft'

    def lookups(self, request, model_admin):
        return (
            ('all', 'All'),
            (1, 'Yes'),
        )

    def choices(self, changelist):
        yield {
            'selected': self.value() is None,
            'query_string': changelist.get_query_string({}, [self.parameter_name]),
            'display': 'No',
        }
        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.value() == force_text(lookup),
                'query_string': changelist.get_query_string({self.parameter_name: lookup}, []),
                'display': title,
            }

    def queryset(self, request, queryset):
        print(self.value())
        if self.value() is None or self.value() == '1':
            return queryset.filter(draft=bool(self.value()))
        if self.value() == 'all':
            return queryset.all()

        raise IncorrectLookupParameters()


class PostAdmin(admin.ModelAdmin):
    fields = ('active', 'author', 'anonym', 'text',)
    list_display = ('get_uri_key', 'author', 'anonym', 'draft', 'text', 'stack_outstanding', 'active',)
    inlines = [CommentInline, ]

    list_filter = ['anonym', 'created', PostDraftFilter, ]

    def get_queryset(self, request):
        qs = self.model.all_objects.get_queryset()

        # Copied from parent class
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs
