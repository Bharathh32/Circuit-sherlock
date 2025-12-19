import firebase_admin
from firebase_admin import credentials, auth

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

email = "circuitadmin@gmail.com"
user = auth.get_user_by_email(email)
auth.set_custom_user_claims(user.uid, {"admin": True})

print("Admin promoted:", email)
