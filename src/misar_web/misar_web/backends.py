from members.models import FilePermission, Member, MemberFile


class ObjectPermissionBackend:
    """
    A django backend for object permissions.
    """

    PERMISSION_MAPPING = {
        "view_memberfile": "view",
        "change_memberfile": "change",
        "share_memberfile": "share",
        "delete_memberfile": "delete",
        # Add more mappings as needed
    }

    def map_permission(self, permission: str):
        return self.PERMISSION_MAPPING.get(permission, None)

    def has_perm(
        self, user_obj: Member, permission: str, obj: MemberFile | None = None
    ):
        """
        Check if a user has a permission.
        """
        print(f"Checking if {user_obj} has Permission: {permission} for: {obj}")
        if obj is None:
            return False

        mapped_permission = self.map_permission(permission)

        if mapped_permission:
            return FilePermission.objects.filter(
                file=obj, user=user_obj, permission=mapped_permission
            ).exists()

        return False

    def authenticate(self, request, username=None, password=None):
        ...

