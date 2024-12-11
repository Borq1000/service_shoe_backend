from rest_framework import serializers
from .models import Service, Attribute, ServiceAttribute, Option, ServiceOption

class ServiceAttributeSerializer(serializers.ModelSerializer):
    attribute = serializers.StringRelatedField()

    class Meta:
        model = ServiceAttribute
        fields = ['attribute', 'value']

class ServiceOptionSerializer(serializers.ModelSerializer):
    option = serializers.StringRelatedField()

    class Meta:
        model = ServiceOption
        fields = ['option', 'value']

class ServiceSerializer(serializers.ModelSerializer):
    attributes = ServiceAttributeSerializer(source='serviceattribute_set', many=True, read_only=True)
    options = ServiceOptionSerializer(source='serviceoption_set', many=True, read_only=True)
    image = serializers.ImageField(use_url=True)  # Добавьте это поле

    class Meta:
        model = Service
        fields = ['id', 'name', 'description', 'price', 'attributes', 'options', 'image', 'slug']

class AttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attribute
        fields = ['id', 'name']

class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['id', 'name']
