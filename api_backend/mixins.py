from rest_framework import serializers


def ModelPresenter(model, fields, outer_properties=None):
    """
    Metaclass for class generation
    class NewClass(DefaultModelSerializer):
        outer_properties...

        class Meta:
            model = model
            fields = fields
    """

    class Serializer(serializers.HyperlinkedModelSerializer):
        pass

    Meta = type('Meta', (), {'fields': fields, 'model': model})
    outer_properties = outer_properties or {}
    outer_properties.update({'Meta': Meta})
    return type(model.__class__.__name__ + 'Presenter', (Serializer,), outer_properties)
