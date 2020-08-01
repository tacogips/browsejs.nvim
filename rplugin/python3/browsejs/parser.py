class Css:
    def __init__(self, lines):
        self.lines = lines


class CustomTag:
    def __init__(self, lines):
        self.lines = lines


class Js:
    def __init__(self, lines):
        self.lines = lines


class Parser:
    def __init__(self, js=None, css=None, custom_tag=None):
        """
        TODO(tacogips) css and custom_tag never be filled for now.
        """
        self.js = js
        self.css = css
        self.custom_tag = custom_tag

    @classmethod
    def parse(cls, all_lines):
        ## TODO(tacogips) parse also css and html custom tag
        ## Considering custom tag and css will be write in js comment,
        ## (like rust doc)[https://doc.rust-lang.org/stable/rust-by-example/meta/doc.html]
        ##
        ## e.g.

        ## //
        ## //  This is normal js comment
        ## //
        ## /// Tripple slash suppose to be  special comment
        ## ///
        ## /// '''html
        ## ///  <div>
        ## ///    here is  custom tag
        ## ///  </div>
        ## ///
        ## /// '''
        ## ///
        ## /// ''' css
        ## /// .p {
        ##         /* styles here*/
        ##        ...
        ## /// }
        ## ///
        ## /// '''
        ## ///
        js = Js(all_lines)

        return cls(js=js)
