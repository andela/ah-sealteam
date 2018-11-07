from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    message = "You are now allowed to access edit or delete"

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the snippet.
        return obj.author == request.user


class NotArticleOwner(permissions.BasePermission):
    """This permission is used to ensure that the article
    author does not access rating of his article"""
    message = "You are not allowed to rate yourself"

    def has_object_permission(self, request, view, obj):
        # will only allow the article owner and everyone to access get
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author != request.user


class IsRaterOrReadOnly(permissions.BasePermission):
    """This permission is to enable rater owner to edit and delete his her ratings"""
    message = "You are not allowed to edit or delete this rate"

    def has_object_permission(self, request, view, obj):
        """Will check permission"""
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user