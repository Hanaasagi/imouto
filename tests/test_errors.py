# flake8: noqa

import pytest

from imouto.errors import *


def test_httperror():
   assert 'NotFound' in globals()
   assert issubclass(NotFound, HTTPError)

   with pytest.raises(NotFound) as e:
       raise NotFound()
   assert e.value.status_code == 404
   assert e.value.phrase == 'NOT FOUND'
