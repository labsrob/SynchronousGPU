
import matplotlib.pyplot as plt

# -------------------------------------------------------------------[]
#
# class panzoom:
#     def __init__(self, ax, base_scale=1.2):
#         self.a3 = ax
#         self.base_scale = base_scale
#         self.press = None
#         self.fig = ax.figure
#
#         # connect events-----
#         self.press_event = None
#         self.fig.canvas.mpl_connect("scroll_event", self.on_scroll)
#         self.fig.canvas.mpl_connect("button_press_event", self.on_press)
#         self.fig.canvas.mpl_connect("button_release_event", self.on_release)
#         self.fig.canvas.mpl_connect("motion_notify_event", self.on_motion)
#
#     def zoom(self, event):
#         """Zoom in/out with scroll wheel."""
#         if event.inaxes != self.a3:
#             return
#
#         # Zoom factor
#         scale_factor = 1.2 if event.button == "up" else 1 / 1.2
#
#         xlim = self.a3.get_xlim()
#         ylim = self.a3.get_ylim()
#
#         xdata, ydata = event.xdata, event.ydata
#
#         # Compute new limits
#         new_xlim = [
#             xdata - (xdata - xlim[0]) * scale_factor,
#             xdata + (xlim[1] - xdata) * scale_factor,
#         ]
#         new_ylim = [
#             ydata - (ydata - ylim[0]) * scale_factor,
#             ydata + (ylim[1] - ydata) * scale_factor,
#         ]
#
#         self.a3.set_xlim(new_xlim)
#         self.a3.set_ylim(new_ylim)
#         self.canvas.draw_idle()
#
#     def on_press(self, event):
#         """Store initial click for panning."""
#         if event.inaxes != self.a3 or event.button != 1:  # left mouse
#             return
#         self.press_event = (event.xdata, event.ydata, self.a3.get_xlim(), self.a3.get_ylim())
#
#     def on_release(self, event):
#         """Reset pan state."""
#         self.press_event = None
#
#     def on_motion(self, event):
#         """Pan on mouse drag."""
#         if self.press_event is None or event.inaxes != self.a3 or event.button != 1:
#             return
#
#         xpress, ypress, xlim, ylim = self.press_event
#         dx = event.xdata - xpress
#         dy = event.ydata - ypress
#
#         self.a3.set_xlim(xlim[0] - dx, xlim[1] - dx)
#         self.a3.set_ylim(ylim[0] - dy, ylim[1] - dy)
#         # self.canvas.draw_idle()
#         self.a3.figure.canvas.draw_idle()

# --------------------- End of pan zoom method ------------------------------[]
class PanZoom:
    def __init__(self, ax, base_scale=1.2):
        self.ax = ax
        self.base_scale = base_scale
        self.press = None
        self.fig = ax.figure

        # connect events
        self.fig.canvas.mpl_connect("scroll_event", self.on_scroll)
        self.fig.canvas.mpl_connect("button_press_event", self.on_press)
        self.fig.canvas.mpl_connect("button_release_event", self.on_release)
        self.fig.canvas.mpl_connect("motion_notify_event", self.on_motion)

    def on_scroll(self, event):
        if event.inaxes != self.ax:
            return
        cur_xlim = self.ax.get_xlim()
        cur_ylim = self.ax.get_ylim()
        xdata, ydata = event.xdata, event.ydata

        # zoom in / out
        if event.button == "up":
            scale_factor = 1 / self.base_scale
        elif event.button == "down":
            scale_factor = self.base_scale
        else:
            return

        new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
        new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor

        relx = (cur_xlim[1] - xdata) / (cur_xlim[1] - cur_xlim[0])
        rely = (cur_ylim[1] - ydata) / (cur_ylim[1] - cur_ylim[0])

        self.ax.set_xlim([xdata - new_width * (1 - relx), xdata + new_width * relx])
        self.ax.set_ylim([ydata - new_height * (1 - rely), ydata + new_height * rely])
        self.ax.figure.canvas.draw_idle()

    def on_press(self, event):
        if event.inaxes != self.ax or event.button != 1:  # left click
            return
        self.press = (event.x, event.y,
                      self.ax.get_xlim(), self.ax.get_ylim())

    def on_release(self, event):
        self.press = None
        self.ax.figure.canvas.draw_idle()

    def on_motion(self, event):
        if self.press is None or event.inaxes != self.ax:
            return
        xpress, ypress, xlim, ylim = self.press
        dx = event.x - xpress
        dy = event.y - ypress
        scale_x = (xlim[1] - xlim[0]) / self.ax.bbox.width
        scale_y = (ylim[1] - ylim[0]) / self.ax.bbox.height
        self.ax.set_xlim(xlim[0] - dx * scale_x, xlim[1] - dx * scale_x)
        self.ax.set_ylim(ylim[0] - dy * scale_y, ylim[1] - dy * scale_y)
        self.ax.figure.canvas.draw_idle()

# Example usage ---------------------------------------[]
fig, ax = plt.subplots()
ax.plot(range(100), [i**0.5 for i in range(100)])

pz = PanZoom(ax)    # activate pan + zoom
plt.show()