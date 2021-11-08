from mozilla_django_oidc.auth import OIDCAuthenticationBackend


class MyOIDCAB(OIDCAuthenticationBackend):
    def create_user(self, claims):
        print("CLAIMs", claims)
        user = super(MyOIDCAB, self).create_user(claims)
        user.username = claims.get("preferred_username", "")
        user.is_staff = True
        user.first_name = claims.get("given_name", "")
        user.last_name = claims.get("family_name", "")
        user.groups.add(2)
        user.save()

        return user
