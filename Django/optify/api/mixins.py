class GetSerializerPermissionClassMixin(object):

    def get_serializer_class(self):
        """
        A class which inhertis this mixins should have variable
        `serializer_action_classes`.
        Look for serializer class in self.serializer_action_classes, which
        should be a dict mapping action name (key) to serializer class (value),
        i.e.:
        class SampleViewSet(viewsets.ViewSet):
            serializer_class = DocumentSerializer
            serializer_action_classes = {
               'upload': UploadDocumentSerializer,
               'download': DownloadDocumentSerializer,
            }
            @action
            def upload:
                ...
        If there's no entry for that action then just fallback to the regular
        get_serializer_class lookup: self.serializer_class, DefaultSerializer.
        """     
        try:
            return self.serializer_action_classes[self.action]
        except (KeyError, AttributeError):
            return super().get_serializer_class()

    def get_permissions(self):
        try:            
            return [permission() for permission in self.permission_action_classes[self.action]]
        except (KeyError, AttributeError):
            return super().get_permissions()    

class GetQuerysetClassMixin(object):

    def get_queryset(self):       
        try:
            return self.gueryset_action_classes[self.action]
        except (KeyError, AttributeError):
            return super().get_queryset()              