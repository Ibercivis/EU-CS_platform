def userinfo(claims, user):
    print("userinfo.............")
    print(user)
    # Populate claims dict.
    claims['name'] = user.email
    claims['given_name'] = user.name
    claims['family_name'] = user.name
    claims['email'] = user.email
    #claims['address']['street_address'] = '...'

    return claims
