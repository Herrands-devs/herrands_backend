from rest_framework.permissions import BasePermission

class DeleteUser(BasePermission):
     def has_permission(self, request, view):
        # Check if the user has both 'accounts.delete_user' and 'accounts.manage_support' permissions
        return (
            request.user.has_perm('accounts.delete_user')
        )

class SuspendUser(BasePermission):
     def has_permission(self, request, view):
        return (
            request.user.has_perm('accounts.suspend_user')
        )
     
class DeleteErrands(BasePermission):
     def has_permission(self, request, view):
        return (
            request.user.has_perm('accounts.delete_errands')
        )
     
class CancelErrands(BasePermission):
     def has_permission(self, request, view):
        return (
            request.user.has_perm('accounts.cancel_errands')
        )
     
class CancelPayout(BasePermission):
     def has_permission(self, request, view):
        return (
            request.user.has_perm('accounts.cancel_payout')
        )
     
class DeletePayout(BasePermission):
     def has_permission(self, request, view):
        return (
            request.user.has_perm('accounts.delete_payout')
        )
     
class ManageSupport(BasePermission):
     def has_permission(self, request, view):
        return (
            request.user.has_perm('accounts.manage_support')
        )
     
class AddNewAdmin(BasePermission):
     def has_permission(self, request, view):
        return (
            request.user.has_perm('accounts.add_new_admin')
        )