import re
from imouto.utils import tob, url_encode, re_unescape


class URLSpec(object):
    def __init__(self, pattern, handler, kwargs=None, name=None):
        if not pattern.endswith('$'):
            pattern += '$'
        self.regex = re.compile(pattern)

        self.handler_class = handler
        self.kwargs = kwargs or {}
        self.name = name
        self._path, self._group_count = self._find_groups()

    def __repr__(self):
        return '%s(%r, %s, kwargs=%r, name=%r)' % \
            (self.__class__.__name__, self.regex.pattern,
             self.handler_class, self.kwargs, self.name)

    def _find_groups(self):
        """Returns a tuple (reverse string, group count) for a url.

        For example: Given the url pattern /([0-9]{4})/([a-z-]+)/, this method
        would return ('/%s/%s/', 2).
        """
        pattern = self.regex.pattern
        if pattern.startswith('^'):
            pattern = pattern[1:]
        if pattern.endswith('$'):
            pattern = pattern[:-1]

        if self.regex.groups != pattern.count('('):
            # The pattern is too complicated for our simplistic matching,
            # so we can't support reversing it.
            return (None, None)

        pieces = []
        for fragment in pattern.split('('):
            if ')' in fragment:
                paren_loc = fragment.index(')')
                if paren_loc >= 0:
                    pieces.append('%s' + fragment[paren_loc + 1:])
            else:
                try:
                    unescaped_fragment = re_unescape(fragment)
                except ValueError:
                    return (None, None)
                pieces.append(unescaped_fragment)

        return (''.join(pieces), self.regex.groups)

    def reverse(self, *args):
        if self._path is None:
            raise ValueError("Cannot reverse url regex " + self.regex.pattern)
        assert len(args) == self._group_count, "required number of arguments "\
            "not found"
        if not len(args):
            return self._path
        converted_args = []
        for a in args:
            converted_args.append(url_encode(tob(a), plus=False))
        return self._path % tuple(converted_args)
