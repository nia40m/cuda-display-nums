import os
import re

from cudatext import *


split_re = re.compile(r"\B_\B", re.I)
dec_re = re.compile(r"^(0|([1-9][0-9]*))(u|l|ul|lu|ll|ull|llu)?$", re.I)
hex_re = re.compile(r"^0x([0-9a-f]+)(u|l|ul|lu|ll|ull|llu)?$", re.I)
oct_re = re.compile(r"^(0[0-7]+)(u|l|ul|lu|ll|ull|llu)?$", re.I)
bin_re = re.compile(r"^0b([01]+)(u|l|ul|lu|ll|ull|llu)?$", re.I)


def parse_number(text):
    # remove underscores in the number
    text = "".join(split_re.split(text))

    match = dec_re.match(text)
    if match:
        return {"number": int(match.group(1), 10), "base": 10}

    match = hex_re.match(text)
    if match:
        return {"number": int(match.group(1), 16), "base": 16}

    match = oct_re.match(text)
    if match:
        return {"number": int(match.group(1), 8), "base": 8}

    match = bin_re.match(text)
    if match:
        return {"number": int(match.group(1), 2), "base": 2}

def format_str(string, num, separator=" "):
    res = string[-num:]
    string = string[:-num]
    while len(string):
        res = string[-num:] + separator + res
        string = string[:-num]

    return res

def get_bits_positions(curr_bits_in_word):
    positions = ""
    start = 0

    while start < curr_bits_in_word:
        positions = "{: >5}".format(start) + positions

        start += 4

    return positions


def my_on_show(id_dlg, id_ctl, data='', info=''):
    ed.focus()

class Command:
    dlg_id = None

    def __init__(self):
        self.dlg_id = dlg_proc(0, DLG_CREATE)

    def hide_dlg(self):
        dlg_proc(self.dlg_id, DLG_HIDE)

    def on_scroll(self, ed_self):
        self.hide_dlg()

    def on_tab_change(self, ed_self):
        self.hide_dlg()

    def on_caret(self, ed_self):
        if len(ed_self.get_carets()) > 1:
            self.hide_dlg()
            return

        a = parse_number(ed_self.get_text_sel().strip())

        if a is None:
            self.hide_dlg()
            return

        # font name, size and color from current theme
        f_name, f_size = ed_self.get_prop(PROP_FONT)
        text_color = ed_self.get_prop(PROP_COLOR, value="EdTextFont")
        bg_color = ed_self.get_prop(PROP_COLOR, value="EdTextBg")
        pos_color = ed_self.get_prop(PROP_COLOR, value="EdGutterFont")
        # link_color = ed_self.get_prop(PROP_COLOR, value="EdLinks")

        # editor start x and y coordinations
        x, y, _, _ = ed_self.get_prop(PROP_COORDS)
        # text part x and y coordinations
        x_t, y_t, _, _ = ed_self.get_prop(PROP_RECT_TEXT)
        # current caret position
        x_1, y_p, x_2, _ = ed_self.get_carets()[0]
        # get the left position of selection
        x_p = max(x_1, x_2)
        # character size
        w_c, h_c = ed_self.get_prop(PROP_CELL_SIZE)
        # calculation of position
        x = x + x_t + x_p*w_c
        y = y + y_t + (y_p + 1)*h_c

        dlg_proc(self.dlg_id, DLG_PROP_SET, prop={
            'border':DBORDER_NONE,
            'topmost':True,
            'on_act':my_on_show,
            'autosize': True,
            'color': bg_color,
            'x': x,
            'y': y
        })

        dlg_proc(self.dlg_id, DLG_CTL_DELETE_ALL)

        temp = dlg_proc(self.dlg_id, DLG_CTL_ADD, prop="label")
        dlg_proc(
            self.dlg_id,
            DLG_CTL_PROP_SET,
            index=temp,
            prop={
                'font_name': f_name,
                'font_size': f_size,
                'font_color': text_color,
                'sp_r': 5,
                'cap': "Hex: " + format_str("{:x}".format(a["number"]), 2),
            }
        )

        ddd = dlg_proc(
            self.dlg_id,
            DLG_CTL_PROP_GET,
            index=temp
        )

        temp = dlg_proc(self.dlg_id, DLG_CTL_ADD, prop="label")
        dlg_proc(
            self.dlg_id,
            DLG_CTL_PROP_SET,
            index=temp,
            prop={
                'font_name': f_name,
                'font_size': f_size,
                'font_color': text_color,
                'sp_r': 5,
                'y': ddd["y"] + ddd["h"],
                'cap': "Dec: " + format_str("{}".format(a["number"]), 3, ","),
            }
        )

        ddd = dlg_proc(
            self.dlg_id,
            DLG_CTL_PROP_GET,
            index=temp
        )

        temp = dlg_proc(self.dlg_id, DLG_CTL_ADD, prop="label")
        dlg_proc(
            self.dlg_id,
            DLG_CTL_PROP_SET,
            index=temp,
            prop={
                'font_name': f_name,
                'font_size': f_size,
                'font_color': text_color,
                'sp_r': 5,
                'y': ddd["y"] + ddd["h"],
                'cap': "Oct: " + format_str("{:o}".format(a["number"]), 3)
            }
        )

        curr_bits_in_word = max(32, a["number"].bit_length() + ((-a["number"].bit_length()) & 0x3))

        ddd = dlg_proc(
            self.dlg_id,
            DLG_CTL_PROP_GET,
            index=temp
        )

        temp = dlg_proc(self.dlg_id, DLG_CTL_ADD, prop="label")
        dlg_proc(
            self.dlg_id,
            DLG_CTL_PROP_SET,
            index=temp,
            prop={
                'font_name': f_name,
                'font_size': f_size,
                'font_color': text_color,
                'sp_r': 5,
                'y': ddd["y"] + ddd["h"],
                'cap': "Bin: " + format_str(
                        format_str(
                            "{:0={}b}".format(a["number"], curr_bits_in_word),
                            4,
                            " "),
                        1,
                        ""
                    )
            }
        )

        ddd = dlg_proc(
            self.dlg_id,
            DLG_CTL_PROP_GET,
            index=temp
        )

        temp = dlg_proc(self.dlg_id, DLG_CTL_ADD, prop="label")
        dlg_proc(
            self.dlg_id,
            DLG_CTL_PROP_SET,
            index=temp,
            prop={
                'font_name': f_name,
                'font_size': f_size,
                'font_color': pos_color,
                'sp_l': 5,
                'sp_r': 5,
                'y': ddd["y"] + ddd["h"],
                'cap': " "*4 + get_bits_positions(curr_bits_in_word)
            }
        )

        dlg_proc(self.dlg_id, DLG_SHOW_NONMODAL)
