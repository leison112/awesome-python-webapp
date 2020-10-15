import coroweb
import models


@coroweb.get('/find_all')
def find_all1(*args):
    users = models.User.find_all()
    return users
