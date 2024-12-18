import json
import logging

from django.forms import Media
from django.forms.widgets import Widget
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.conf import settings

logger = logging.getLogger(__name__)


class ReactJSONSchemaFormWidget(Widget):

    template_name = "django_reactive.html"
    default_css_classes = {
        "label": "control-label",
        "input": "form-control",
        "description": "field-description",
    }

    def __init__(
        self,
        schema=None,
        ui_schema=None,
        on_render=None,
        extra_css=None,
        extra_js=None,
        css_classes=None,
        **kwargs,
    ):
        self.schema = schema
        self.ui_schema = ui_schema
        self.on_render = on_render
        self.on_render_object = None
        self.extra_css = extra_css
        self.extra_js = extra_js
        default_css_classes = getattr(settings, "DJANGO_REACTIVE_CSS_CLASSES", {})
        self.css_classes = css_classes or default_css_classes or self.default_css_classes
        super().__init__(**kwargs)

    @property
    def media(self):
        css = ["css/django_reactive.css"]
        if self.extra_css:
            css.extend(self.extra_css)
        airgapped = getattr(settings, "DJANGO_REACTIVE_AIRGAPPED") in [
            "True",
            "true",
            "1",
        ]
        js = [
            "js/django_reactive.js",
        ] + (
            [
                "https://cdnjs.cloudflare.com/ajax/libs/react/18.3.1/umd/react.production.min.js",
                "https://cdnjs.cloudflare.com/ajax/libs/react-dom/18.3.1/umd/react-dom.production.min.js",
                "https://cdnjs.cloudflare.com/ajax/libs/react-jsonschema-form/1.8.1/react-jsonschema-form.min.js",
            ]
            if not airgapped
            else [
                "django-reactive/react.js",
                "django-reactive/react-dom.js",
                "django-reactive/react-jsonschema-form.js",
            ]
        )
        if self.extra_js:
            js.extend(self.extra_js)

        return Media(css={"all": css}, js=js)

    def mutate(self):
        kwargs = {}
        if self.on_render_object:
            kwargs["instance"] = self.on_render_object
        try:
            self.on_render(self.schema, self.ui_schema, **kwargs)
        except BaseException as exc:
            logger.error("Error applying JSON schema hooks: %s", exc, exc_info=True)

    def render(self, name, value, attrs=None, renderer=None):
        if self.on_render:
            self.mutate()

        context = {
            "data": value,
            "name": name,
            "schema": json.dumps(self.schema),
            "ui_schema": json.dumps(self.ui_schema) if self.ui_schema else "{}",
            "css_classes": json.dumps(self.css_classes) if self.css_classes else "{}",
        }

        return mark_safe(render_to_string(self.template_name, context))
