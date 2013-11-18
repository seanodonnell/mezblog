# Taken from https://movieos.org/blog/2008/sanitizing-comments-with-python/
# Copyright Tom Insam

from BeautifulSoup import BeautifulSoup
import re

def sanitize(html):
    # allowable tags. Other tags are removed, but their child elements remain
    whitelist = ['em', 'i', 'strong', 'u', 'a', 'b', "p", "br", "code", "pre" ]

    # allow only these attributes on tags.
    #No other tags are allowed any attributes.
    attr_whitelist = { 'a':['href','title','hreflang']}

    # remove these tags, complete with contents.
    blacklist = [ 'script', 'style' ]

    attributes_with_urls = [ 'href', 'src' ]

    # BeautifulSoup is catching out-of-order and unclosed tags, so markup
    # can't leak out of comments and break the rest of the page.
    soup = BeautifulSoup(html)

    # now strip HTML we don't like.
    for tag in soup.findAll():

        if tag.name.lower() in blacklist:
            # blacklisted tags are removed in their entirety
            tag.extract()

        elif tag.name.lower() in whitelist:
            # tag is allowed. Make sure all the attributes are allowed.
            for attr in tag.attrs:
                # allowed attributes are whitelisted per-tag
                if tag.name.lower() in attr_whitelist and \
                    attr[0].lower() in attr_whitelist[ tag.name.lower() ]:
                    # some attributes contain urls..
                    if attr[0].lower() in attributes_with_urls:
                        # ..make sure they're nice urls
                        if not re.match(r'(https?|ftp)://', attr[1].lower()):
                            tag.attrs.remove( attr )

                    # ok, then
                    pass
                else:
                    # not a whitelisted attribute. Remove it.
                    tag.attrs.remove( attr )
        else:
            # not a whitelisted tag. I'd like to remove it from the tree
            # and replace it with its children. But that's hard. It's much
            # easier to just replace it with an empty span tag.
            tag.name = "span"
            tag.attrs = []

    # stringify back again
    safe_html = unicode(soup)

    # HTML comments can contain executable scripts,
    # depending on the browser, so we'll
    # be paranoid and just get rid of all of them
    # e.g. <!--[if lt IE 7]>
    # <script type="text/javascript">h4x0r();</script><![endif]-->
    # TODO - I rather suspect that this is the weakest part of the operation..
    safe_html = re.sub(r'<!--[.\n]*?-->','',safe_html)
    return safe_html
