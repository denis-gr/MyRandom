#!/usr/bin/env python
import pathlib
import re
import sys

import django
from django.template.loader import render_to_string
import css_html_js_minify
import jsmin
import sass

START_URL = sys.argv[1] if len(sys.argv) > 1 else ""
PROJECT_DIR = pathlib.Path(".")
TEMPLATE_DIR = PROJECT_DIR / "_template"
CONTEXT = {
    "start_url": START_URL
}

django.conf.settings.configure(TEMPLATES=[
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_DIR],
    },
])
django.setup()


def json_minify(string, strip_space=True):
    tokenizer = re.compile('"|(/\*)|(\*/)|(//)|\n|\r')
    end_slashes_re = re.compile(r'(\\)*$')

    in_string = False
    in_multi = False
    in_single = False

    new_str = []
    index = 0

    for match in re.finditer(tokenizer, string):

        if not (in_multi or in_single):
            tmp = string[index:match.start()]
            if not in_string and strip_space:
                # replace white space as defined in standard
                tmp = re.sub('[ \t\n\r]+', '', tmp)
            new_str.append(tmp)
        elif not strip_space:
            # Replace comments with white space so that the JSON parser reports
            # the correct column numbers on parsing errors.
            new_str.append(' ' * (match.start() - index))

        index = match.end()
        val = match.group()

        if val == '"' and not (in_multi or in_single):
            escaped = end_slashes_re.search(string, 0, match.start())

            # start of string or unescaped quote character to end string
            if not in_string or (escaped is None or len(escaped.group()) % 2 == 0):  # noqa
                in_string = not in_string
            index -= 1  # include " character in next catch
        elif not (in_string or in_multi or in_single):
            if val == '/*':
                in_multi = True
            elif val == '//':
                in_single = True
        elif val == '*/' and in_multi and not (in_string or in_single):
            in_multi = False
            if not strip_space:
                new_str.append(' ' * len(val))
        elif val in '\r\n' and not (in_multi or in_string) and in_single:
            in_single = False
        elif not ((in_multi or in_single) or (val in ' \r\n\t' and strip_space)):  # noqa
            new_str.append(val)

        if not strip_space:
            if val in '\r\n':
                new_str.append(val)
            elif in_multi or in_single:
                new_str.append(' ' * len(val))

    new_str.append(string[index:])
    return ''.join(new_str)


for path in pathlib.Path(TEMPLATE_DIR).glob("**/*.*"):
    if path.name.startswith("_"):
        continue

    temp_path = pathlib.Path().joinpath(*path.parts[1:])
    temp_path.parent.mkdir(parents=True, exist_ok=True)
    new_path = temp_path

    is_text = True
    fun = lambda x: x
    if path.suffix == ".html":
        fun = css_html_js_minify.html_minify
    elif path.suffix == ".css":
        fun = css_html_js_minify.css_minify
    elif path.suffix == ".json" or path.suffix == ".webmanifest":
        fun = json_minify
    elif path.suffix == ".js":
        fun = jsmin.jsmin
    elif path.suffix == ".scss":
        fun = lambda x: sass.compile(string=x, output_style='compressed')
        new_path = temp_path.with_suffix(".css")
    else:
        is_text = False

    if is_text:
        with new_path.open("w") as output:
            output.write(fun(render_to_string(temp_path, context=CONTEXT)))
    else:
        with new_path.open("wb") as output, path.open("rb") as input:
            output.write(fun(input.read()))
