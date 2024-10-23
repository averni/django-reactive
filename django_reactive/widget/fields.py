from .widgets import ReactJSONSchemaFormWidget

try:
    # DJANGO 3.1
    from django.forms import JSONField
except ImportError:
    from django.contrib.postgres.forms.jsonb import JSONField


class ReactJSONSchemaFormField(JSONField):
    widget = ReactJSONSchemaFormWidget

    def __init__(
        self,
        schema=None,
        ui_schema=None,
        on_render=None,
        extra_css=None,
        extra_js=None,
        css_classes=None,
        schma_url=None,
        **kwargs,
    ):
        self.schema = schema
        self.ui_schema = ui_schema
        self.on_render = on_render
        self.extra_css = extra_css
        self.extra_js = extra_js
        self.css_classes = css_classes
        self.schma_url = schma_url
        super().__init__(**kwargs)
