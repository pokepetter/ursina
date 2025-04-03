import tkinter as tk

class TextPeer(tk.Text):
    "boakly's implementation: https://stackoverflow.com/a/58290100/14507110"
    count = 0
    def __init__(self, master, textw, cnf={}, **kw):
        TextPeer.count += 1
        peerName = "peer-{}".format(TextPeer.count)
        if str(master) == ".":
            peerPath = ".{}".format(peerName)
        else:
            peerPath = "{}.{}".format(master, peerName)

        textw.tk.call(textw, 'peer', 'create', peerPath, *self._options(cnf, kw))
        tk.BaseWidget._setup(self, master, {'name': peerName})
