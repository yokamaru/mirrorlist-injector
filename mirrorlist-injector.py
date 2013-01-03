#!/usr/bin/python
"""
Inject the unofficial mirror servers to the official mirror server list
"""
import web

from lxml import etree
import urllib2

repos = {
    ("fedora-17", "x86_64"): {
        "metalink": "http://mirrors.fedoraproject.org/metalink?repo=fedora-17&arch=x86_64",
        "injects": [
            {"protocol": "http",
             "type": "http",
             "preference": "100",
             "location": "JP",
             "url": "http://ftp.naist.jp/pub/Linux/fedora/releases/17/Everything/x86_64/os/repodata/repomd.xml",
             },
            ],
        },
    ("updates-released-f17", "x86_64"): {
                "metalink": "http://mirrors.fedoraproject.org/metalink?repo=updates-released-f17&arch=x86_64",
        "injects": [
            {"protocol": "http",
             "type": "http",
             "preference": "100",
             "location": "JP",
             "url": "http://ftp.naist.jp/pub/Linux/fedora/updates/17/x86_64/repodata/repomd.xml",
             },
            ],
        },
    }

urls = ("/metalink", "Metalink")

class Injector:
    def __init__(self, profile, input_params):
        self.profile = profile
        self.input_params = input_params

    """
    Check the local metalink cache is expired or not
    """
    def __is_metalink_expired(self):
        # FIXME not implemented yet
        return True

    """
    Retrieve the metalink file.

    If the cache is available, then use it. If not then download from
    official server.
    """
    def __retrieve_original_metalink(self):
        # FIXME should use "cache" mechanism
        if self.__is_metalink_expired():
            try:
                response = urllib2.urlopen(self.profile["metalink"])
                data = response.read()
                xml = etree.fromstring(data)
            except urllib2.URLError:
                raise InjectException()
            except etree.XMLSyntaxError:
                raise InjectException()
        else:
            pass

        return xml

    """
    Inject the specified unofficial mirror server to the official metalink.
    """
    def inject_metalink(self):
        ## Retrieve the official metalink file
        xml_root = self.__retrieve_original_metalink()

        ## Build the new element
        namespaces = xml_root.nsmap
        url_parents = xml_root.xpath(
            "/ns:metalink/ns:files/ns:file/ns:resources",
            namespaces={"ns": xml_root.nsmap[None]})
        if not url_parents:
            raise InjectException()
        url_parent = url_parents[0]

        for inject_config in self.profile["injects"]:
            element = etree.Element(
                "{{{0}}}url".format(namespaces[None]),
                nsmap = namespaces,
                )
            element.text = inject_config["url"]
            tags = ("protocol", "type", "preference", "location")
            for k in tags:
                element.set(k, inject_config[k])

            # Inject the built element
            url_parent.append(element)

        ## Return as a string
        return etree.tostring(xml_root)

class Metalink:
    """Generate the error message."""
    def __generate_error(self):
        # FIXME should use lxml or any other xml builder?
        xml_string = """
<metalink version="3.0" xmlns="http://www.metalinker.org/" type="dynamic">
<!--
We're sorry, but something went wrong.
-->
</metalink>
"""
        return xml_string

    """Handling the GET method"""
    def GET(self):
        # Get the input parameters
        input_params = web.input(repo = None, arch = None)

        try:
            profile_set = (input_params["repo"], input_params["arch"])

            if profile_set not in repos.keys():
                # If the valid profile is not specified then raise the
                # the exception.
                raise InjectException()

            # Inject
            injector = Injector(repos[profile_set], input_params)
            output = injector.inject_metalink()

            web.header('Content-Type', 'application/metalink+xml')
            return output
        except InjectException:
            web.header('Content-Type', 'application/metalink+xml')
            return self.__generate_error()

class InjectException(BaseException):
    pass

# for mod_wsgi
web.config.debug = False
app = web.application(urls, globals())
application = app.wsgifunc()

if __name__ == '__main__':
     # for debugging (e.g. $ python mirrorlist-injector.py 8000)
    app.run()
