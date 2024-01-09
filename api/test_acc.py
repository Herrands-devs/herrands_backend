import os
from rave_python import Rave

FLW_PUBLIC_KEY = 'FLWPUBK_TEST-27d21cd18e97e16a388aef87fbb3c411-X'
FLW_SECRET_KEY = 'FLWSECK_TEST-fa9f76dea9dd1ae5f29784bc4bbfee46-X'
rave = Rave(FLW_PUBLIC_KEY, FLW_SECRET_KEY, usingEnv=False)
details = {
  "account_number": "0690000032",
  "account_bank": "044"
}
response = rave.Transfer.accountResolve(details)
print(response)
