import csv
import logging
import requests
from google.cloud import firestore
from utils import settings


# client = firestore.Client()
    # cast_docs = client.collection(settings.Firestore.collection_casts) \
    #     .where(u'status', u'==', 1) \
    #     .get()
    # logging.info(f"(ticker_px_update) CASTS FOUND: {len(cast_docs)}")
    # client.collection(settings.Firestore.collection_tickers) \
    #     .document(exchange) \
    #     .set({
    #     'all': exchange_tickers,
    #     'status': 1,
    # })

auth_url = "https://auth.tdameritrade.com/auth?response_type=code&redirect_uri=https://anthracite-302814.firebaseapp.com/__/auth/handler&client_id=IRDIJ197IVSA9IYTJ2I6OCCX1VNVNADT%40AMER.OAUTHAP"

auth_response = "https://anthracite-302814.firebaseapp.com/__/auth/handler?code=luRjHNyILu95u%2B3vUIvLL2%2FXxQJwTbAow0gKmzqtWHh0RH78EUj4zPkjtl3jUNR8rObgA7IwtGSltfK83MTOzgA9fVpwjMumgqRWbggZo5cix5g8I01V55a2qnEFymIb%2FmS9JBlR3KGRIDDwptCJWJNtHoTGxtAXIqJ0ji29s8QbEy04RNka0FnpGciWyiaG%2F%2Fsh1fnqvz6lGdSEdm7f7pQMdmcdE%2B2MecMfAzgnET7jVwNrJA0dshRsxLUMBFfk4WyV2MHMrfZjsQ7fHArj6zD9%2BNzd%2FPrqtlulkF9NrTVjECW0i6buI2LCT4iebZCHfklsiqqIiSf0gZ9qEqefpXB0oAWNLy%2FEKCoFpG1BJG5xxb7ke01BXgo7QI6EvqFRvmIwTT9BqVdKL2M%2BKTfFH1fZSRQy7ZNpGxrvG7uopHl8H87ynO4QNxQbASt100MQuG4LYrgoVi%2FJHHvlHu6%2F1xNXpxFYCnosOAE9W9xWCF1wK28Qx50BBTLG5YuoMftegYI8ma15FEZS8%2FDUSntL3LkgdQ6btx8Ym5ZIpsI3xV56PF5SgQXkvJ0hKQu5Wfc1XVu7qJ9F3TcceN1gHXMGcemwvK7FLqx838eOnCjnYZJu%2Fx9D%2FvDDTt5JRB4fkPkhT8pahdqVS1dp7%2FuR%2FhGcPJDwZF2Qv9JxVyMerchoxa9zewPZtR%2FBFtx77RhIH1f2335VtimhijxDRP7Ybl2wF%2BRTiYe2z%2F4ilJOtQpmhJZJBu43M38atXg4Sp1mc66E7xFiLqALi9rL8l%2B6zvYcuCp5jU9KY4jrtAmDOd%2F%2BV%2FNkLY50I%2FYET47aSOV6FCDiVmoUFGpRLW%2BQ9CikUs6fpMqoqKyoBuonJNjq0rDEI5VBB1hDSFVgw8rN9XPEqemDDSYJLvnMBZzA%3D212FD3x19z9sWBHDJACbC00B75E"

initial_token_timestamp = 1614383440
token_response = {
  "access_token": "RdkQfySsFon94jsrJ+eYK3Bu5sriS6amfwMAvz73Ca0STB3TfbfzFSWhuVcYKyZA+GSERJN+HJzNmyM7EShW9DcWClhjlzMCt5zSozP8cj4rkWqSlM+ohnTsKbJ+fXOAk087mZSLf82Y+Mxj/YrTHXOFusDUiXjv9YcEOEb+QnVAdCb+Al3Xw6QmFoI2ByY79MLJ6zHqLqaWiGad/q/fE6EdcLk3ly/hPnuWmsjnFPJetJXfP5W6KqfbENPujxosi1JYs7oMEFcNeEF7q/WMNY297cg3KWtqbgPeLKfcjDRXPFvhMa7DnoTqof2s0YKiTD5A16fH8T2CMnLpoMjOBZxayHRiCaPDlb2yX2aTTSx/Ea1TYZZwiXT47fX+envlXEIzvl2ucPu7Z77nOyOPP+l1EwpdcyYexlhxdNYltSbEtPG2tRhzs4p7Vm7TDcQ0Bm7FMacf+F7Cyz0m5dW4oxKDS7/TFYAc/ftMxuoSUwOgn52PFKeSxW4NQNIc+XKvTT/5Zo0eDzk67+7Z5H3I7Wx2bG+100MQuG4LYrgoVi/JHHvlAGQwD5Ny9JNRXBP1i2ac0eYh8QXg/1dmCG2ouH3z/zjxHaHlurudkQ363CPZ6lmEtVLStPmo9hj6cTLQ0OMNUg4/+dLp8rkDJwb9qnpVVg6pHZEXae9H/YaXoV5eYg3vperou1aVCFMEcCIxf+7iARFzqz+SFDD1QYUO3DEEsDlWEmTfiGbsPY4Uz/qHFdy5nHSJ63cuKmYPGsAT34myxMCMV7m4hpw+bUd/xkoMUaM2ljjMZ31XeVXIW2iAsPps//bXsFNXfFhVtOSxWuvs0CiTkgIt09VS1TV47VsvNxYWjdQash4Y1Fu9V6kr/z6qMX/ESHx8GpXy8H9YYFi+g3iq08abIUNFukTSFtQpdhilcc4JSWHUQdlpLF+44UDiWAzK6f7G7HOkVOC8J454pWFdge7Z+xwiPDI3hBZilKZSTt5ybPigWrn3ofz0zJ34366dQCRPe6lD/omdNyZ3aUvaUI3O7dDNaG2nEciv8LPsjj8xo7z30C5CKUcu8Ipy1IVjM6rhMJwHIlNxP1okhpKEmuU=212FD3x19z9sWBHDJACbC00B75E",
  "refresh_token": "F+4xCDtM0VOJlf9d+dohEcAyg6c9RqFyjVz6cYA86FZKuviGI9LL+YwCzS/jylXXjH2VSe0Fw/xDTQ3HrYcXxxGKwKkfuQOT3+n6FT/fa9ct5ntufcBZcsod07Qj9tLm8UeB8vJgexxFfUWymVS+CA0b4GHNrSwd7F8lCZg9Z1W8Un/9Onv90gn20zMT5QLxgINsssryAt2pgzh0jBtuNM1UbAhwwt52GO+KA1yjoOn1qYtFMRUg8ZaBWnOuawuDQGX25GK6R9KOE7SoESRjTbiTVi/XVSQfNtycOYUD4n3PYfr0IjccCLvShRVaEDkMYFfFZUkAXc46jaykkcCNC5z/syYEfm83mqwUe5p1PZQ1uskT7UFa5UIGzO6q4FsVAhFOsOwN+cLue2ztp3nMIwo2D1BKrqkg2PsX+Yvyzp3tM+AQkGZ7roI4F7v100MQuG4LYrgoVi/JHHvlvDcmjHgMCqB7+MnE2sT9+DDrPp6OtenK4bjvAv34ubZGh9H+gvKAuL+ANP0T2K//2MWoCR6mLQouBs3vAFg6YVClHVyiIbBVYQiZHUi0pe0zRehCdk/V+MZrf/U5n7ccsYao0bU8bvHqREX4f4yFLTakVD01Wv56KlBFqsXt3xKRccg8RiaFzVplM4NnW5+v0h9b2e60EX3cSax1ptCCt7OknKGW+tYNr2EbxQ2Mq8xQfAoEr2ZJ1mHm3Fp3Hk5TTsKIM/3NE0Q6Bf0BqHcJj42QDwDMCYe52HLry1BJsH2mK+sQLRiZWKLQF3OmgyoV4lg1SE5rIfGZc4MA/7GCAGxjmHxMWRLDT9o4dUdfavkz6/5Y/OGBpDixvVsQj8pPOQueI2KOnI4hI+g9i2PBph1l9AV4sHn1yqgVju4MgwcMjbRINHc3rCz3AuY=212FD3x19z9sWBHDJACbC00B75E",
  "scope": "PlaceTrades AccountAccess MoveMoney",
  "expires_in": 1800,
  "refresh_token_expires_in": 7776000,
  "token_type": "Bearer"
}


def ameritrade():
    try:
        response = requests.get("https://api.robinhood.com/oauth2/token/")
        if response.status_code == 200:
            print(response)

        else:
            print(f"ERROR: {response}")

    except Exception:
        logging.error(f"(ticker_px_update) ERROR: {Exception}")



if __name__ == '__main__':
    ameritrade()
