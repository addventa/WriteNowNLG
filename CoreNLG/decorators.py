# -*- coding: utf-8 -*-
"""
created on 18/12/2018 11:35
@author: fgiely
"""
import copy
import functools
import re

from lxml import html

from CoreNLG import Errors
from CoreNLG.NoInterpret import interpretable_char_reverse


def handle_capitalize(splitters, *args):

    capitalized_text = list()
    for i, a in enumerate(args):
        new_string = a
        matchs = list()
        if i == 0:
            match = re.search(r"(^<[^>]*>)(<[^>]*>)*( *\n*)*[a-z]", new_string)
            if match is not None:
                matchs.append(match)
        matchs += re.finditer("".join(["(\\" + "|\\".join(splitters), ")( *\n*)*(<[^>]*>)*( *\n*)*[a-z]"]), new_string)
        for match in matchs:
            new_string = new_string[:match.span()[1] - 1] + new_string[match.span()[1] - 1].upper() + new_string[match.span()[1]:]
        capitalized_text.append(new_string)
    return capitalized_text


def contraction(splitters, current, contract, *text):

    if len(splitters) > current:
        splitted = list()
        for arg in text:
            for elem in arg.split(splitters[current]):
                splitted.append(elem)
                splitted.append(splitters[current])
            splitted.pop(-1)
        splitted = contraction(splitters, current + 1, contract, *splitted)
        return splitted
    else:
        splitted = list(text)
        new_sent = list()
        is_replaced = False
        for i in range(len(splitted)):
            if is_replaced:
                is_replaced = False
                continue
            try:
                w = splitted[i]
            except IndexError:
                break
            try:
                replacers = contract[w.lower()]
                for rep, comp_pattern in replacers.items():
                    if len(splitted) > i + 1:
                        w1 = splitted[i + 1]
                    else:
                        break
                    if w1 == " " and len(splitted) > i + 2:
                        w1 = splitted[i + 2]
                    else:
                        break
                    for e in comp_pattern:
                        try:
                            if isinstance(e, tuple):
                                comp_w1 = e[0]
                                replace = e[1]
                            else:
                                comp_w1 = e
                                replace = w1
                            if len(comp_w1) == 1 and w1[0].lower() == comp_w1:
                                is_replaced = True
                                if w[0].isupper():
                                    rep = rep[0].upper() + "".join(rep[1:])
                                new_sent.append(rep + replace[0] + "".join(w1[1:]))
                                splitted.pop(i)
                                break
                            elif w1.lower() == comp_w1:
                                is_replaced = True
                                if w[0].isupper():
                                    rep = rep[0].upper() + "".join(rep[1:])
                                new_sent.append(rep + replace)
                                splitted.pop(i)
                                break

                        except IndexError:
                            pass
                    if is_replaced:
                        break
            except KeyError:
                pass
            if not is_replaced or len(splitted) == i:
                new_sent.append(w)
        return "".join(new_sent)


def space_after(text, chars):
    """Takes as parameters the HTML string ('text') and the characters to be considered for spaces handling ('chars').
    It adds a space after and removes a space before when 'chars' are encountered while parsing 'text'.
    The function eventually suppresses unneeded whitespaces, thanks to 'handle_spaces'."""
    " ".join(text.split())  # Useless
    for char in chars:
        text = text.replace(char, char + " ")
        text = text.replace(" " + char, char)
        text = handle_spaces(text)
    return text


def space_before(text, chars):
    """Cf. 'space_after.__doc__', as the arguments and the algorithm are the same.
    The difference is that it removes spaces placed after a 'chars' character, and adds spaces before if there is none."""
    " ".join(text.split())  # Useless
    for char in chars:
        text = text.replace(char, " " + char)
        text = text.replace(char + " ", char)
        text = handle_spaces(text)
    return text


def space_before_after(text, chars):
    """"""
    for char in chars:
        text = text.replace(char, " " + char + " ")
    return text


def no_space(text, chars):
    """"""
    for char in chars:
        text = text.replace(" " + char, "" + char)
        text = text.replace(char + " ", char + "")
    return text


def handle_dots(text):
    matchs = re.finditer(r"\.+((<[^>]*>)*([^a-zA-Z0-1])*)*\.+", text)
    nb_remove = 0
    re_check = False
    for match in matchs:
        nb_dots = len(re.findall("\.", match.group()))
        if nb_dots == 2 or nb_dots > 3:
            if nb_dots > 3:
                re_check = True
            text = text[:match.span()[1] - 1 - nb_remove] + text[match.span()[1] - nb_remove:]
            nb_remove += 1
        elif nb_dots == 3:
            cleaned_dots = match.group().replace(" ", "")
            if not match.group() == cleaned_dots:
                text = text[:match.span()[0] - nb_remove] + cleaned_dots + text[match.span()[1] - nb_remove:]
                nb_remove += len(match.group()) - len(cleaned_dots)
    if re_check:
        text = handle_dots(text)
    return text


def handle_spaces(text):
    """Chained whitespaces are removed and replaced by a single space.
    Exception when between two containers separated by whitespaces: there is no space.
    Eg. '..._<html>_<head>_...' => '..._<html><head>_...' """
    ret_splitted = text.split(" ")

    # ret_splitted = [e for e in ret_splitted if e not in ('', ' ')]
    ret = list()
    for i in range(len(ret_splitted)):
        e = ret_splitted[i]
        if len(e) > 0:
            if e[0] == "<" and e[-1] == ">" and "<" not in e[1:]:
                if len(ret) > 0:
                    last = ret[-1]
                    ret.pop(-1)
                    ret.append("".join([last, e]))
                else:
                    ret.append(e)
            else:
                ret.append(e)
    return " ".join(ret)


def beautifier(f_ret, ponct, contract):
    f_ret = handle_spaces(f_ret)
    ignore_chars = [
        " ",
        ",",
        "'",
        "!",
        ";",
        ":",
        "/",
        '"',
        "?",
        "(",
        ")",
        ".",
        "<",
        ">",
    ]
    f_ret = contraction(
        ignore_chars, 0, contract, contraction(ignore_chars, 0, contract, f_ret)
    )
    f_ret = " ".join(handle_capitalize(copy.copy(ponct["capitalize"]), f_ret))
    f_ret = space_after(f_ret, copy.copy(ponct["space_after"]))
    f_ret = space_before(f_ret, copy.copy(ponct["space_before"]))
    f_ret = space_before_after(f_ret, copy.copy(ponct["space_before_and_after"]))
    f_ret = no_space(f_ret, copy.copy(ponct["no_spaces"]))
    f_ret = handle_dots(f_ret)
    f_ret = handle_spaces(f_ret)
    for key, value in interpretable_char_reverse.items():
        f_ret = f_ret.replace("#" + key + "#", value)

    return f_ret


def debug_printer(f):
    @functools.wraps(f)
    def debug_printer_f(*args, **kwargs):
        f_ret = f(*args, **kwargs)
        arguments = list()
        for arg in args[1:]:
            if isinstance(arg, list):
                arguments.append([a for a in arg])
            elif isinstance(arg, html.HtmlElement):
                arguments.append(html.tostring(arg).decode("utf-8"))
            else:
                arguments.append(arg)

        args[0].logger.debug(
            "function {} called with param args{}, kwargs{}".format(
                f.__name__, arguments, kwargs
            )
        )
        if isinstance(f_ret, html.HtmlElement):
            args[0].logger.info(
                "function {} return : \n{}\n".format(
                    f.__name__, html.tostring(f_ret, encoding="utf-8").decode("utf-8")
                )
            )
        else:
            args[0].logger.info("function {} return : \n{}\n".format(f.__name__, f_ret))
        if args[0].active_all_printers:
            print(
                "fonction {}, arguments : {}\n{}".format(
                    f.__name__, args[1:], f_ret.text_content()
                )
            )
        return f_ret

    return debug_printer_f


def args_checker(f):
    @functools.wraps(f)
    def args_checker_f(*args, **kwargs):
        if len(args) > 1 and isinstance(args[1], list):
            e = Errors.ArgsNotUnpackedError
            args[0].logger.error("function {} return : {!s}".format(f.__name__, e))
            raise e
        return f(*args, **kwargs)

    return args_checker_f


def remove_technical_span(f):
    @functools.wraps(f)
    def remove_technical_span_f(*args, **kwargs):
        text = f(*args, **kwargs)
        for span in text.xpath("//span[@class='to_delete']"):
            span.drop_tag()
        return text

    return remove_technical_span_f
